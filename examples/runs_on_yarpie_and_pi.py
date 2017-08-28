"""
    A small example to demonstrate YARPie.
    Run it on your PC or on your Pi. Both will work without chaning a line of code.
    On the Pi you need: Two LEDs connected (GPIO 11 and GPIO 12), a button (GPIO 18)
    as well as an i2c-device.
    
    This little example waits for GPIO 18 to go HIGH if it does it reads a byte from a register of your i2c-device
    (both are specified in "address" and "register"). If this value is larger than a defined treshold
    the LED on GPIO 11 will be turned on until the button is released.
    If the value is smaller the second LED will be light up.
"""

import random
import time

#load RPi.GPIO if running on a Pi and YARPie if running on a PC
try:
    import RPi.GPIO as GPIO
    import smbus
    bus = smbus.SMBus(1)
    print "Running on a Raspberry Pi."
except ImportError: #no RPi.GPIO = no Pi  
    import RPi_emu.GPIO as GPIO
    bus = GPIO.SMBus(1)
    print "Running in YARPie."

#address and register of the connected i2c-device
address  = 0x21
register = 0x01
treshold = 128

def read(): #this function will be called to read a value from the i2c-device
    #create an autoreply if running with YARPie
    if GPIO.RPI_INFO == "GPIO-emu":
        GPIO.add_autoreply(address, register, random.randrange(0,2*treshold,1))

    return bus.read_byte_data(address, register)

random.seed()

GPIO.setmode(GPIO.BCM)

#check pin configuration (fust for fun)
for i in range(55):
    try:
        func = GPIO.gpio_function(i)
        if func == GPIO.OUT:
            print "pin %d: output (%d)" % (i, func)
        elif func == GPIO.IN:
            print "pin %d: input (%d)" % (i, func)
        elif func == GPIO.SERIAL:
            print "pin %d: serial (%d)" % (i, func)
        elif func == GPIO.SPI:
            print "pin %d: spi (%d)" % (i, func)
        elif func == GPIO.I2C:
            print "pin %d: i2c (%d)" % (i, func)
        elif func == GPIO.HARD_PWM:
            print "pin %d: hardware pwm (%d)" % (i, func)
        elif func == GPIO.UNKNOWN:
            print "pin %d: unknown (%d)" % (i, func)
    except:
        pass
    
# pin 18 (GPIO 24) will be used to trigger a read-function from an i2c-device
GPIO.setup(18, GPIO.IN, GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

while 1:
    GPIO.wait_for_edge(18, GPIO.RISING)
    val = read()
    print val
    if val > treshold:
        GPIO.output(11, GPIO.HIGH)
    else:
        GPIO.output(12, GPIO.HIGH)
        
    GPIO.wait_for_edge(18, GPIO.FALLING)
    GPIO.output(11, GPIO.LOW)
    GPIO.output(12, GPIO.LOW)
