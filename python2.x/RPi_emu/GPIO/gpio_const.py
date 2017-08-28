'''
Created on 18.04.2017

@author: blbltheworm
'''

#modi of the PINs
OUT     = 0
IN      = 1
SERIAL  = 40
SPI     = 41
I2C     = 42
HARD_PWM= 43
UNKNOWN = -1

LOW     = 0
HIGH    = 1

BOARD   = 10
BCM     = 11

#there is no emulation of the physical pull up/down resistors, thus PUD_DOW is treated as LOW, while PUD_UP is treated as HIGH
PUD_DOWN= LOW#21
PUD_UP  = HIGH#22

RISING  = 31
FALLING = 32
BOTH    = 33