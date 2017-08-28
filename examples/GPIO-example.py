import RPi_emu.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN)
while(1):
	GPIO.output(23, GPIO.input(24))
	time.sleep(0.1)
