#!/usr/bin/env python3

# Main Imports TODO: Move imports to __init__.py?
import logging
import os
import signal
import sys
import time

# Multi-Processing Related Imports
from multiprocessing import Event, Process, Queue, Value

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

# Setting File Config/Reader
from configparser import ConfigParser

# Settings Webpage Module
from UserGUI.settings_webpage import user_gui_main

# Other Imports
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
# from twilio.rest import Client
# import notification


# Declare and initialize variables
smokeProcess = None
tcamProcess = None
hkProcess = None
webSettingsProcess = None


class IHFRSSensor(Accessory):

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
        self.temp_char.set_value(shTemp.value)
        self.smoke_char.set_value(shSmoke.value)


def get_accessory(driver):
    return IHFRSSensor(driver, 'IHFRS')


def web_process():
    while True:
        time.sleep(5)
        break


def homekit_process():
    # Setup Preference Reader
    config_reader = ConfigParser()
    config_reader.read("config.ini")

    # homekit_settings = config_reader["HomekitSettings"]
    # hk_port = homekit_settings["port"]

    driver = AccessoryDriver(port=34985)  # TODO: Uncomment 2 lines above and change to variable
    driver.add_accessory(accessory=get_accessory(driver))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()


def smoke_process():  # TODO: Move to module
    # Setup for Smoke Sensor
    SMOKEPIN = 4
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SMOKEPIN, GPIO.IN)

    while True:
        if GPIO.input(SMOKEPIN) == GPIO.HIGH:
            shSmoke.value = 0
            print("Checking for Gas/Smoke")
        elif GPIO.input(SMOKEPIN) == GPIO.LOW:
            shSmoke.value = 1
            print("SMOKE DETECTED!!!!")
            print("SMOKE DETECTED!!!!")
            print("SMOKE DETECTED!!!!")
            #           Debounce for Smoke Detection
            time.sleep(3)
        time.sleep(3)


def tcam_process():
    # Setup Preference Reader
    config_reader = ConfigParser()
    config_reader.read("config.ini")

    # TCAM_settings = config_reader["TCAMSettings"]
    # alert_value = TCAM_settings["tempAlertValue"]

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

        temp_avg = (reg_array[0] / (1 / res)) - 273.15
        temp_max = (reg_array[1] / (1 / res)) - 273.15
        temp_min = (reg_array[2] / (1 / res)) - 273.15

        shTemp.value = temp_max
        shAlarm.value = 0

        print(f"Temperature Max= {temp_max} C")
        print(f"Temperature Min= {temp_min} C")
        print(f"Temperature spot= {temp_avg} C")

        alert_value = 40
        if temp_max >= alert_value:  # TODO: Uncomment 2 lines at top and change to variable
            shAlarm.value = 1
            print(f"HOT DETECTED!!!")

        time.sleep(3)


if __name__ == "__main__":
    try:
        shTemp = Value('d', 0.00)
        shSmoke = Value('i', 0)
        shAlarm = Value('i', 0)

        # Define Processes'
        smokeProcess = Process(target=smoke_process)
        tcamProcess = Process(target=tcam_process)
        hkProcess = Process(target=homekit_process)
        webSettingsProcess = Process(target=user_gui_main)

        # Start Processes
        smokeProcess.start()
        tcamProcess.start()
        hkProcess.start()
        webSettingsProcess.start()

    except KeyboardInterrupt:
        smokeProcess.terminate()
        tcamProcess.terminate()
        hkProcess.terminate()
        webSettingsProcess.terminate()
        print("Interrupted.")
