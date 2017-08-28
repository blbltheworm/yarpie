# YARPIE
yet another raspberry pi emulator


**** What is YARPie ****
YARPie is a python module capable of emulating the GPIO port of a Raspberry Pi on your PC (currently only rev. 3, i.e. the 40 pin header of A+/B+ and above).
It is designed to test/develop your projects without having access to a Raspberry Pi. It comes with a full implementation of RPi.GPIO 0.6.3 and a way to emulate i2c-devices as well. Pygame is used to display and control the emulated GPIO pins + i2c-devices. Using YARPie requires only minimal changes to your existing python script. Implemantations of other Pi revisions as well as a SPI-module as well as a python 3.x-version are planed. For details and examples have a look at "manual.pdf".


**** How to install and use ****
The current version was developed for python 2.7. To install YARPie:

- Install pygame
- copy the "RPi_emu" sub folder from the "python2.x" folder inside your python2.x modules folder (e.g. "/usr/lib/python2.7/" ) or your project folder.

To use YARPie:
If your projects only uses the GPIO pins simply replace "import RPi.GPIO as GPIO" by "import RPi_emu.GPIO as GPIO" and run your script.
For details and more advanced usage of YARPie have a look at "manual.pdf" and/or the provided examples.

**** License ****

See LICENSE file
