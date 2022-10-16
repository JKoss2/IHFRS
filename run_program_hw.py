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
from twilio.rest import Client
import RPi. GPIO as GPIO
import notification

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

if __name__ == "__main__":

    #
    # Parse command line
    

    #
    # Connect to tCam
    #
    cam = TCam(is_hw=True)
    stat = cam.connect()
    if stat["status"] != "connected":
        print(f"Could not connect to Tcam")
        cam.shutdown()
        while True:
            if GPIO.input(4):
                print("Camera not connected")
                print(f"Gas Check")
            else:
                
                notification.notification(f"Gas leak", f"Gas leak")
            time.sleep(3)
            
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
            cam.shutdown()
            while True:
                if GPIO.input(4):
                    print("Camera not connected") 
                    print("Gas check")
                else:
                    notification.notification(f"Gas leak", f"Gas leak")
                time.sleep(3)
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
                notification.notification(f"Fire= {tempMax} C", f"Fire")
 
        else:
            print(f"Temperature Max= {tempMax} C")
            print(f"spot average = {temp} C")
            print(f"Temperature Min= {tempMin} C")
        if GPIO.input(4):
            print("Gas check")
        else:
            notification.notification(f"Gas leak", f"Gas leak")

            
        time.sleep(3)
        
    




