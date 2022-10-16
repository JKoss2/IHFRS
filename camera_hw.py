#!/usr/bin/env python3
#
# Print spot meter value
#
import base64
import array
# from palettes import ironblack_palette
from PIL import Image as im
import numpy as np
import argparse
from tcam import TCam
import sys
import argparse
import time
from queue import Queue

def get_data(cam):

    stat=cam.connect()
    #
    # Connect to tCam
    #
   # try:
    #    stat = cam.connect(ip)
    #except:
     #   print(f"queue empty")
      #  return 
    if stat["status"] != "connected":
        print(f"Could not connect to Tcam")
        #cam.shutdown()
        return False
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
    rsp_vals = rsp["cci_reg"]
    dec_data = base64.b64decode(rsp_vals["data"])
    reg_array = array.array('H', dec_data)
    #
    # Convert the json response into an array of 2 16-bit words
    #  Index  : Value
    #    0    : Response[15:0]
    #    1    : Response[31:16]
    #
    #while True:
    #stat = cam.connect(ip)
    #if stat["status"] != "connected":
     #   print(f"Could not connect to {ip}")
      #  cam.shutdown()
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
        
        return tempMax
             
    else:
        print(f"Temperature Max= {tempMax} C")
        print(f"spot average = {temp} C")
        print(f"Temperature Min= {tempMin} C")
        
        return  False
   
            
        




