#!/usr/bin/env python3
#
# Print spot meter value
#

import argparse
import array
import base64
from tcam import TCam
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import smtplib
# from twilio.rest import Client
import RPi. GPIO as GPIO
# import notification

# HomeKit Integration
from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
from pyhap.const import CATEGORY_SENSOR

# Import Multi-Processing
from multiprocessing import Process

# Setup for Smoke Sensor
SMOKEPIN = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(SMOKEPIN, GPIO.IN)

class IHFRSSensor(Accessory):

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add the services that this Accessory will support with add_preload_service here
        temp_service = self.add_preload_service('TemperatureSensor')
        smoke_service = self.add_preload_service('SmokeSensor')

        self.temp_char = temp_service.get_characteristic('CurrentTemperature')
        self.smoke_char = smoke_service.getcharacteristic('SmokeDetected')

        # Having a callback is optional, but you can use it to add functionality.
        self.temp_char.setter_callback = self.temperature_changed

    @Accessory.run_at_interval(5)
    async def run(self):
        self.temp_char.set_value(temp)
        self.smoke_char.set_value(smokeStatus)

def get_accessory(driver):
    return IHFRSSensor(driver, 'IHFRS')

def HomeKitProcess():
    driver = AccessoryDriver(port= 34985)
    driver.add_accessory(accessory=get_accessory(driver))
    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()

def SmokeProcess():
    smokeStatus = 0
    while True:
        if GPIO.input(SMOKEPIN):
            print("Checking for Gas/Smoke")
        else:
            smokeStatus = 1
            print("SMOKE DETECTED!!!!")
            print("SMOKE DETECTED!!!!")
            print("SMOKE DETECTED!!!!")
#           Debounce for Smoke Detection
            time.sleep(3)
        time.sleep(3)

def TCAMProcess():
        #
    # Connect to tCam
    #
    cam = TCam(is_hw=True)
    stat = cam.connect()
    if stat["status"] != "connected":
        print(f"Could not connect to Tcam")
#         notification.notification(f"Camera disconnected, check connection!", f"Camera disconnected")
        cam.shutdown()

        #sys.exit()

    #
    # OEM Mask
    #
    COMMAND_OEM_MASK = 0x4000

    #
    # Request the RAD T-Linear resolution (RAD 0x0EC4)
    #    Response is 0 for 0.1 C (Low Gain), 1 for 0.01 C (High Gain)
    #
    rsp = cam.get_lep_cci(COMMAND_OEM_MASK | 0x0EC4, 2)
    cam.set_spotmeter(0,159,0,119)
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

        temp = (reg_array[0] / (1/ res)) - 273.15
        tempMax = (reg_array[1] / (1/ res)) - 273.15
        tempMin = (reg_array[2] / (1/ res)) - 273.15

        if tempMax>40:
                print(f"HOT DETECTED!!!")
                print(f"Temperature Max= {tempMax} C")
                print(f"Temperature Min= {tempMin} C")
                print(f"Temperature spot= {temp} C")
#                 notification.notification(f"Hot spot detected, please check the area!!! Max temperature = {tempMax} C", f"Fire")

        else:
            print(f"Temperature Max= {tempMax} C")
            print(f"spot average = {temp} C")
            print(f"Temperature Min= {tempMin} C")


        time.sleep(3)


if __name__ == "__main__":

    # SmokeThread
    Process(target=SmokeProcess).start()

    # TCAM Thread
    Process(target=TCAMProcess).start()

    # Homekit SmokeThread
    Process(target=HomeKitProcess).start()
