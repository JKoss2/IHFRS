import RPi. GPIO as GPIO

def Gas(GPIO):
    if GPIO.input(4):
        print("Gas check")
        return False
    else:
        print("GAS leak")
        return True