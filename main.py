import camera_hw
import notification
import gas_sensor
import RPi. GPIO as GPIO
import time
from tcam import TCam

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)
cam= TCam(is_hw=True)
cam.connect()
def main():
    while True:
        if (gas_sensor.Gas(GPIO)):
            notification.notification(f"Gas leak", f"Gas leak")
        #tempMax=cam.camera(cam2)
        tempMax=camera_hw.get_data(cam)
        if tempMax !=False:  #(camera_hw.get_data(cam))
            notification.notification(f"Hot Surface, check the area!!!"+str(tempMax)+"C",f"Fire") #
        
        
        time.sleep(1)
        
            
        
main()        
