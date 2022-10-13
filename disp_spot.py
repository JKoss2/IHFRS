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

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)


parser = argparse.ArgumentParser()

parser.prog = "disp_spot"
parser.description = f"{parser.prog} - an example program to print the spotmeter value from the CCI interface\n"
parser.usage = "disp_spot.py [--ip=<ip address of camera>]"
parser.add_argument("-i", "--ip", help="IP address of the camera")

if __name__ == "__main__":

    #
    # Parse command line
    #
    args = parser.parse_args()

    if not args.ip:
        ip = "192.168.99.127"
    
    else:
        ip = args.ip

    #
    # Connect to tCam
    #
    cam = TCam()
    stat = cam.connect(ip)
    if stat["status"] != "connected":
        print(f"Could not connect to {ip}")
        cam.shutdown()
        sys.exit()

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
        rsp_vals = rsp["cci_reg"]
        dec_data = base64.b64decode(rsp_vals["data"])
        reg_array = array.array('H', dec_data)
        if reg_array[0] == 0:
        	res = 0.1
        else:
        	res = 0.01
        
        

       # print(f"T-Linear resolution = {res}")
    
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
                port = 587
                timeout = 15
                smtpServer = 'smtp.gmail.com'
                account_sid = "AC31331230a20f77ec7624c5e38311cea6"
                # Your Auth Token from twilio.com/console
                auth_token  = "7a93ef0412569dcc84ea0289247c6e9f"
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    to="+15615631884",
                    from_="+16815324346",
                    body=f"Hot Surface, check the area!!! = {tempMax} C")
                print(message.sid)
                with smtplib.SMTP(host=smtpServer, port=port,timeout=timeout) as server:

                        context = ssl._create_unverified_context()
                        server.starttls(context=context)
                        fromAddress = 'raspigroup15@gmail.com'
                        password = 'quqtojujdlqxszrr'
                        server.login(fromAddress, password)  # Your email address & password here
                        htmlMessage = 'Hot surface spotted'
                        subject = 'Possible Fire'
                        message = MIMEMultipart("alternative")
                        message["Subject"] = subject
                        message["From"] = fromAddress
                        message["To"] = 'sergeykunaev94@gmail.com'
                        part1 = MIMEText(htmlMessage, 'plain')
                        message.attach(part1)
                        if htmlMessage is not None:
                                part2 = MIMEText(htmlMessage, "html")
                                message.attach(part2)
                                recipients='sergeykunaev94@gmail.com'
                                server.sendmail(fromAddress,recipients,message.as_string())
 
        else:
            print(f"Temperature Max= {tempMax} C")
            print(f"spot average = {temp} C")
            print(f"Temperature Min= {tempMin} C")
        if GPIO.input(4):
            pass
        else:
            print("GAS leak")
            account_sid = "AC31331230a20f77ec7624c5e38311cea6"
                # Your Auth Token from twilio.com/console
            auth_token  = "7a93ef0412569dcc84ea0289247c6e9f"
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to="+15615631884",
                from_="+16815324346",
                body=f"GAS LEAK")
            auth_token  = "7a93ef0412569dcc84ea0289247c6e9f"
            
        time.sleep(1)
        
    



