#!/usr/bin/env python3

# Main Imports TODO: Move imports to __init__.py?
import logging
import os
import signal
import sys
import time

# Multi-Processing Related Imports
from multiprocessing import Event, Process, Queue

# TCAM Related Imports
import argparse
import array
import base64
from tcam import TCam

# HomeKit Integration Related Imports
from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR

# Smoke Sensor Related Imports
import RPi.GPIO as GPIO

# Other Imports
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
# from twilio.rest import Client
# import notification

# Setup for Smoke Sensor
SMOKEPIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SMOKEPIN, GPIO.IN)

# Declare and initialize global variables FIXME: Pass updated parameters/values between processes. Use Queue for this
smokeProcess = None
tcamProcess = None
hkProcess = None
temp = 0
smokeStatus = 0


# Logger Setup
def init_logger():
    logger_format = "%(asctime)s %(levelname)-8.8s [%(funcName)24s():%(lineno)-3s] %(message)s"
    formatter = logging.Formatter(logger_format)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = init_logger()

# Main SIGINT / SIGTERM Handlers
main_stop_event = Event()

# TODO: Add SIGTERM / SIGINT Handlers
def main_sigint_handler(signum, frame):
    logger.debug('')
    main_stop_event.set()


def main_sigterm_handler(signum, frame):
    logger.debug('')
    main_stop_event.set()


# Children SIGINT / SIGTERM Handlers (let Main process handle this)
def children_sigint_handler(signum, frame):
    logger.debug('')


def children_sigterm_handler(signum, frame):
    logger.debug('')


def stop_procs(self):  # TODO: Add graceful shutdowns

    self.shutdown_event.set()

    end_time = time.time() + self.STOP_WAIT_SECS
    num_terminated = 0
    num_failed = 0

    # -- Wait up to STOP_WAIT_SECS for all processes to complete
    for proc in self.procs:
        join_secs = max(0.0, min(end_time - time.time(), STOP_WAIT_SECS))
        proc.proc.join(join_secs)

    # -- Clear the procs list and _terminate_ any procs that
    # have not yet exited
    while self.procs:
        proc = self.procs.pop()
        if proc.proc.is_alive():
            proc.terminate()
            num_terminated += 1
        else:
            exitcode = proc.proc.exitcode
            if exitcode:
                num_failed += 1

    return num_failed, num_terminated


class IHFRSSensor(Accessory):  # TODO: Move to module

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the services that this Accessory will support with add_preload_service here
        temp_service = self.add_preload_service('TemperatureSensor')
        smoke_service = self.add_preload_service('SmokeSensor')

        self.temp_char = temp_service.get_characteristic('CurrentTemperature')
        self.smoke_char = smoke_service.get_characteristic('SmokeDetected')

    @Accessory.run_at_interval(5)
    async def run(self):
        self.temp_char.set_value(temp)
        self.smoke_char.set_value(smokeStatus)


def get_accessory(driver):
    return IHFRSSensor(driver, 'IHFRS')


def homekit_process():  # TODO: Move to module
    driver = AccessoryDriver(port=34985)
    driver.add_accessory(accessory=get_accessory(driver))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()


def smoke_process():  # TODO: Move to module
    while not shutdown_event.is_set():
        try:
            if GPIO.input(SMOKEPIN):
                smokeStatus = 0
                print("Checking for Gas/Smoke")
            elif GPIO.input(not SMOKEPIN):
                smokeStatus = 1
                print("SMOKE DETECTED!!!!")
                print("SMOKE DETECTED!!!!")
                print("SMOKE DETECTED!!!!")
                #           Debounce for Smoke Detection
                time.sleep(3)
        except queue.Empty:
            continue
        time.sleep(3)


def tcam_process():  # TODO: Move to module
    #
    # Connect to tCam
    #
    cam = TCam(is_hw=True)
    stat = cam.connect()
    if stat["status"] != "connected":
        print(f"Could not connect to Tcam")
        #         notification.notification(f"Camera disconnected, check connection!", f"Camera disconnected")
        cam.shutdown()

        # sys.exit()

    #
    # OEM Mask
    #
    COMMAND_OEM_MASK = 0x4000

    #
    # Request the RAD T-Linear resolution (RAD 0x0EC4)
    #    Response is 0 for 0.1 C (Low Gain), 1 for 0.01 C (High Gain)
    #
    rsp = cam.get_lep_cci(COMMAND_OEM_MASK | 0x0EC4, 2)
    cam.set_spotmeter(0, 159, 0, 119)
    #
    # Convert the json response into an array of 2 16-bit words
    #  Index  : Value
    #    0    : Response[15:0]
    #    1    : Response[31:16]
    #
    while True:
        stat = cam.connect()
        if stat["status"] != "connected":
            print(f"Could not connect to Tcam")
            # notification.notification(f"Camera disconnected, check connection!", f"Camera disconnected")
            cam.shutdown()
        rsp_vals = rsp["cci_reg"]
        dec_data = base64.b64decode(rsp_vals["data"])
        reg_array = array.array('H', dec_data)
        if reg_array[0] == 0:
            res = 0.1
        else:
            res = 0.01

        print(f"T-Linear resolution = {res}")

        #
        # Request the RAD Spotmeter Value (RAD 0xED0)
        #
        rsp = cam.get_lep_cci(COMMAND_OEM_MASK | 0x0ED0, 4)

        #
        # Convert the json response into an array of 4 16-bit words
        #  Index  : Value
        #    0    : Spotmeter Value
        #    1    : Spotmeter Max Value
        #    2    : Spotmeter Min Value
        #    3    : Spotmeter Population
        #
        rsp_vals = rsp["cci_reg"]
        dec_data = base64.b64decode(rsp_vals["data"])
        reg_array = array.array('H', dec_data)

        #
        # Convert the Spotmeter Value into degrees C
        #   Temp = (Spotmeter Value / (1 / T-Linear Resolution)) - 273.15

        temp = (reg_array[0] / (1 / res)) - 273.15
        tempMax = (reg_array[1] / (1 / res)) - 273.15
        tempMin = (reg_array[2] / (1 / res)) - 273.15

        if tempMax > 40:
            print(f"HOT DETECTED!!!")
            print(f"Temperature Max= {tempMax} C")
            print(f"Temperature Min= {tempMin} C")
            print(f"Temperature spot= {temp} C")
            # notification.notification(f"Hot spot detected, please check the area!!! Max temperature = {tempMax} C", f"Fire")

        else:
            print(f"Temperature Max= {tempMax} C")
            print(f"spot average = {temp} C")
            print(f"Temperature Min= {tempMin} C")

        time.sleep(3)


if __name__ == "__main__":
    try:
        # Define Processes
        smokeProcess = Process(target=smoke_process)
        tcamProcess = Process(target=tcam_process)
        hkProcess = Process(target=homekit_process)

        # Start Processes
        smokeProcess.start()
        tcamProcess.start()
        hkProcess.start()

    except KeyboardInterrupt:
        smokeProcess.terminate()
        tcamProcess.terminate()
        hkProcess.terminate()
        print("Interrupted.")
