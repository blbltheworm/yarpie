import RPi_emu.GPIO as GPIO
import time
import random #random is used to provide a random number as light level

random.seed()
bus = GPIO.SMBus(0)
address = 0x70
#SRF08 REQUIRES 5V

#Generate Autoreplies for range registers
GPIO.add_autoreply(address, 2, 5)
GPIO.add_autoreply(address, 3, 1)

def write(value):
	bus.write_byte_data(address, 0, value)
	GPIO.add_autoreply(address, 1, random.randrange(0, 255, 1)) #provide a random number to register 1 (light level)
	return -1

def lightlevel():
	light = bus.read_byte_data(address, 1)
	return light

def range():
	range1 = bus.read_byte_data(address, 2)
	range2 = bus.read_byte_data(address, 3)
	range3 = (range1 << 8) + range2
	return range3

while True:
	write(0x51)
	time.sleep(0.7)
	lightlvl = lightlevel()
	rng = range()
	print(lightlvl)
	print(rng)
