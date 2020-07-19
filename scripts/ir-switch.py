import RPi.GPIO as GPIO

def ir_filter(mode):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(8, GPIO.OUT)
    if mode == 1:
        GPIO.output(8, GPIO.LOW)
        print("Day mode")
    elif mode == 0:
        GPIO.output(8, GPIO.HIGH)
        print("Night mode")


ir_filter(0)
