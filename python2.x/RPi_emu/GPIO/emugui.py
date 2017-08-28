'''
Created on 18.04.2017

@author: blbltheworm
'''
import pygame
import pygamegadgets #InputGadget, Panel, Buttons and List
import threading
import time
from gpio_const import *

VERSION = '0.0.1'

class cGP(object):
    """
        Class storing GPIO-PIN-Informations
    """

    def __init__(self, mode=OUT, state=LOW):
        self._mode = mode
        self._state = state
        self._edge = 0   #-1: falling edge, +1: rising edge, 0: nothing
        self.wait_for_edge = 0 #required to handle GPIO.wait_for_edge(), same values as _edge
        self.pwm = False #true if GPIO is used as pwm and pwm is running
        self.pwm_dc = 0  #PWM-dutycycle (0.0 <= pwm_dc <= 1.0
        self.pwm_freq = 0 #PWM-frequency in Hz
        self.was_setup = False #is set to True if GPIO.setup() was called for the related GPIO. This is important to raise an error if a pin is used without beeing setup
    
    def setio(self, mode):
        """
            Define as input or output.
        """
        self._mode = mode
        
    def getio(self):
        """
            Return whether this GPIO-PIN is an Input/output/i2c/...
        """
        return self._mode
    
    def setstate(self, state):
        """
            Set the pin HIGH/LOW and detect rising/falling edges.
        """
        if self._state == 0 and state == 1: #rising edge created
            self._edge = 1
        elif self._state == 1 and state == 0: #falling edge created
            self._edge = -1
            
        self._state = state
        
    def getstate(self):
        """
            Return HIGH/LOW.
        """
        return self._state
    
    def getedge(self): 
        """
            Returns whether there was a rising or falling edge and resets the edge to zero so it is only detected once.
        """
        tmpedge = self._edge
        if tmpedge != 0:
            if self.wait_for_edge == BOTH or (self.wait_for_edge == RISING and tmpedge == 1) or (self.wait_for_edge == FALLING and tmpedge == -1):
                self.wait_for_edge = 0
            self._edge = 0
            return tmpedge
        else:
            return 0


class i2c_autoreply(object):
    """
        This Subclass is used to provide an automated answer by an emulated i2c-device
        i.e. the programmer can use GPIO.add_autoreply() to create an automated answer (data) that will
        be returned by the emulator if the python script calls a read_byte_data(device, register) or similar. 
    """
    def __init__(self, device, register, data):
        self.device = device
        self.register = register
        self.data = data
        
        
class event_detect(object):
    """
        Emulates interrupts for edge-detection.
    """
    def __init__(self, id, bouncetime, edge, func):
        self.bouncetime = bouncetime #duration after an detected event until which no further events will be detected
        self.silence    = 0          # if time.time() < silence a detected event will be ignored (silence = time of last event + bouncetime
        self.id         = id         #ID of the GP-Array
        self.edge       = edge       #stores whether a rising/falling/both event should be detected
        self.func       = func       #function called if event is detected
        self.detected   = False      #used to handle GPIO.event_detected(channel)


class cGuiElements(object):
    """
        Subclas handling Gadgets (Buttons/Textinput/Panels/List) of the GUI
    """
    def __init__(self):
        """
            Create the Gadgets used by the emulator
        """
        self.panel = pygamegadgets.PanelGadget(360, 15, 420, 550, ["I2C", "I2C-Autoreply",])
        self.btnSend = [] #Button to send Data to the RPi
        self.strSend = [] #InputGadget displaying the data to be send
        self.lstData = [] #ListGadget displaying send and received data
        self.radFormatlist = [] #Radiobuttons to choose the format (DEC, HEX, OCT, BIN) if the input string
        self.radFormat = [] #List of Radiobuttons
        self.strI2cdev = [] #List of InputGadgets displaying the device-ID
        self.lblI2c = []    #List of Labels to show ":" between Device-ID and Send-field for I2C
                
        #create one Input/Button/List per I2C, I2C-Autoreply
        for i in range(2):                
            self.strSend.append(pygamegadgets.InputGadget(420, 60, 300, 25))
            self.strI2cdev.append(pygamegadgets.InputGadget(380, 60, 30, 25))
            self.lblI2c.append(pygamegadgets.TextGadget(412, 60, height = 25, caption = ":"))
            #connect Gadgets to panel, so they are onely shown if the panel is active
            self.panel.embed_gadgets(i, [self.strI2cdev[-1], self.lblI2c[-1]]) 
                
            self.radFormatlist.append([pygamegadgets.RadioGadget(380, 90, 86, 25, "HEX"),
                                     pygamegadgets.RadioGadget(380 + 86, 90, 86, 25, "DEC"),
                                     pygamegadgets.RadioGadget(380 + 86*2, 90, 86, 25, "OCT"),
                                     pygamegadgets.RadioGadget(380 + 86*3, 90, 86, 25, "BIN")])
            self.radFormat.append(pygamegadgets.RadioGadgetGroup(self.radFormatlist[-1]))
            self.btnSend.append(pygamegadgets.ButtonGadget("send", 725, 60, 35, 25))
            if i != 1:
                self.lstData.append(pygamegadgets.ListGadget(380, 120, 380, 430))
            else:
                self.lstData.append(pygamegadgets.ListGadget(380, 120, 380, 405))
                self.lblautoinfo = pygamegadgets.TextGadget(380, 525, height = 25, caption = "Right click on auto-event item to delete it.")
                self.strI2creg = pygamegadgets.InputGadget(420, 60, 30, 25)
                self.panel.embed_gadgets(i, [self.lblautoinfo, self.strI2creg]) #ensures that only the Gadgets related to the corresponding method (I2C,...) are shown
                
                
            self.panel.embed_gadgets(i, [self.strSend[i], self.btnSend[i], self.lstData[i]]) #ensures that only the Gadgets related to the corresponding method (I2C,...) are shown

        #adjust apearance of i2c-autodetect-panel
        self.strSend[1].change(x = 460, width = 260)
        self.lblI2c[1].change(caption = ":(           )", width = 45)
        self.btnSend[1].change(caption = "add")
    
    def draw(self, screen):
        """
            Draw Gadgets to screen.
        """
        self.panel.draw(screen)
        if self.panel.curpanel < 2:
            self.strI2cdev[self.panel.curpanel].draw(screen)
            self.lblI2c[self.panel.curpanel].draw(screen)
        if self.panel.curpanel == 1:
            self.lblautoinfo.draw(screen)
            self.strI2creg.draw(screen)
        self.strSend[self.panel.curpanel].draw(screen)
        self.btnSend[self.panel.curpanel].draw(screen)
        self.radFormat[self.panel.curpanel].draw(screen)
        self.lstData[self.panel.curpanel].draw(screen)
        
    def check_events(self, events):
        """
            Check for Gadget-events (click, text input, ...)
        """
        self.panel.check_events(events)
        self.strI2cdev[self.panel.curpanel].check_events(events)

        self.strI2creg.check_events(events)
        self.radFormat[self.panel.curpanel].check_events(events)
        self.strSend[self.panel.curpanel].check_events(events)
        self.btnSend[self.panel.curpanel].check_events(events)
        self.lstData[self.panel.curpanel].check_events(events)       
        
class emugui(threading.Thread):
    """
        Main class emulating the GPIO and i2c and draws the main window.
    """
    def __init__(self, xoffset = 150, yoffset = 20):
        
        threading.Thread.__init__(self)
                
        self._xoffset = xoffset
        self._yoffset = yoffset
        
        #maps BCM-Ports to physical pins: boardmap[BCM] = channel
        self.boardmap = {2: 3, 3: 5, 4: 7, 5: 29, 6: 31, 7: 26, 8: 24, 9: 21, 10: 19, 11: 23, 12: 32, 13: 33, 14: 8, 15: 10, 16: 36, 17: 11, 18: 12, 19: 35, 20: 38, 21: 40, 22: 15, 23: 16, 24: 18, 25: 22, 26: 37, 27: 13}
        #maps physical pins to BCM-Ports: bcmmap[channel] = BCM
        self.bcmmap   = {3: 2, 5: 3, 7: 4, 29: 5, 31: 6, 26: 7, 24: 8, 21: 9, 19: 10, 23: 11, 32: 12, 33: 13, 8: 14, 10: 15, 36: 16, 11: 17, 12: 18, 35: 19, 38: 20, 40: 21, 15: 22, 16: 23, 18: 24, 22: 25, 37: 26, 13: 27}


        self.events = [] #emulates the event_detection
        self.i2c_replys = [] #emulates i2c-devices by coding automatic replies to read-calls for a specified device/register
        
        #create the 26 GPIO-Pins of the P1-Header other GPIO-Pin are not included in the emulator
        self.GP = [] #array of class cGP to address the 26 GPIO-Pins (_GP[0] = GPIO2, _GP[1] = GPIO3, ...
        
        for i in range(26):
            self.GP.append(cGP(IN))
        
        self._setup_standard() #generates the standard configuration of the GPIO-pins after boot

        # Initialise pygame and create screen, surfaces and Gadgets (Input/Buttons/Lists...)    
        pygame.init()
        self._screen = pygame.display.set_mode((800, 600))
        self.gadgets = cGuiElements() #subclass handling Input/Buttons/Lists/...
        
        pygame.display.set_caption('YARPI-emu v' + VERSION)
        
        #Images to display GPIO-states in GUI
        self._icons = [pygame.image.load("./RPi_emu/GPIO/OFF.png"), 
                 pygame.image.load("./RPi_emu/GPIO/ON.png"),
                 pygame.image.load("./RPi_emu/GPIO/3v3.png"),
                 pygame.image.load("./RPi_emu/GPIO/5v.png"),
                 pygame.image.load("./RPi_emu/GPIO/GND.png"),
                 pygame.image.load("./RPi_emu/GPIO/empty.png"),
                 pygame.image.load("./RPi_emu/GPIO/IN-LOW.png"),
                 pygame.image.load("./RPi_emu/GPIO/IN-HIGH.png"),
                 pygame.image.load("./RPi_emu/GPIO/PWM.png")]
        
        for icon in self._icons:
            icon.convert()
        
        #load the background image
        self._bgimage = pygame.image.load("./RPi_emu/GPIO/Background.png")
        self._bgimage.convert()
        
        self.font = pygame.font.SysFont("arial", 10)
        
        pygame.mouse.set_visible(1)
        pygame.key.set_repeat(1, 30)
        
    def _setup_standard(self):
        """
            set the correct standard mode and state of the BCM-Pins (also for pins not connected to the P1-Header)
        """
        for i in range(26):
            if (i+2) in [2,3]:
                self.GP[i].setio(I2C)
                self.GP[i].setstate(HIGH)
                self.GP[i].was_setup = True
            elif (i+2) in [4, 5, 6, 7,8]:
                self.GP[i].setstate(HIGH)
            elif (i+2)in [14, 15]:
                self.GP[i].setio(SERIAL)
                self.GP[i].was_setup = True
            elif (i+2)in [22, 31, 32, 38, 41]:
                self.GP[i].setio(OUT)
                self.GP[i].was_setup = True
        
        self.boardmode = -1 #Boardmode has to be set by user to BCM or BOARD
        
    
    def _check_events(self): 
        """
            emulates interrupt handling via add_event_detect
        """
        
        #detect edges
        tmpedge = range(26)
        for i in range(26): #rising/falling edge is stored as getedge() resets edge after calling if getedge() is called within the event loop and more then one callback is defined only the first one will be called
            tmpedge[i] = self.GP[i].getedge()

        if not self.events: #list is empty
            return
        
        for event in self.events:           
            if tmpedge[event.id] != 0:
                if time.time() > event.silence:
                    if (event.edge == BOTH) or (event.edge == RISING and tmpedge[event.id] == 1) or (event.edge == FALLING and tmpedge[event.id] == -1):
                        event.silence = time.time() + event.bouncetime / 1000.0
                        event.detected = True #used with GPIO.event_detected(channel)
                        if not event.func is None:
                            if self.boardmode == BCM:
                                event.func(event.id+2)
                            elif self.boardmoe == BOARD:
                                event.func(self.boardmap[event.id+2])

    def add_event(self, id, edge, bouncetime, callback):
        """
            Add an event (=edge detection) to the list.
            id: GPIO-channeln, edge: RISING/FALLING/BOTH, 
            bouncetime: min. time between two detections, callback: callback-function.
        """
        self.events.append(event_detect(id, bouncetime, edge, callback))
    
    def remove_event(self, id):
        """
            Remove all events (=edge detection) connected to the channel named if from the list. 
        """
        
        if not self.events: #list is empty
            return
        
        last = 0
        while 1: #loop until all events related to channel are deleted
            for i in range(last, len(self.events)):
                if self.events[i].id == id:
                    break
            else:
                break
            last = i
            del self.events[i]
            
    
    def _drawGPIO(self):
        """
            Draw the emulated P1-header on the screen.
        """
        
        self._screen.fill((255, 255, 255))
        self._screen.blit(self._bgimage, (0,0))
        
        #this might be a bit confusing but pos runs from 0 to 39 and describes the index of the drawn GPIO-PIN.
        #unfortunately the labeling of the physical pins starts at 1, thus the bcmmap with the key pos+1 has to
        #be used to find the corresponding BCM-Port
        for pos in range(40):
            if not pos in [0, 16, 1, 3, 5, 8, 13, 19, 24, 29, 33, 38, 26, 27]: #Only draw GPIO-PINS, 3.3V, 5V, etc. are already drawn in the background picture
                if self.GP[self.bcmmap[pos+1]-2].getio() == IN:
                    if self.GP[self.bcmmap[pos+1]-2].getstate() == LOW:
                        self._screen.blit(self._icons[6], (self._xoffset+(pos % 2)*25 , self._yoffset + (pos / 2)*25))
                    elif self.GP[self.bcmmap[pos+1]-2].getstate() == HIGH:
                        self._screen.blit(self._icons[7], (self._xoffset+(pos % 2)*25 , self._yoffset + (pos / 2)*25))
                    #else:
                    #    print( self.GP[self.bcmmap[pos+1]-2].getstate())
                else:
                    if self.GP[self.bcmmap[pos+1]-2].getstate() == LOW:
                        self._screen.blit(self._icons[0], (self._xoffset+(pos % 2)*25 , self._yoffset + (pos / 2)*25))
                    elif self.GP[self.bcmmap[pos+1]-2].getstate() == HIGH:
                        self._screen.blit(self._icons[8], (self._xoffset+(pos % 2)*25 , self._yoffset + (pos / 2)*25))
                        if self.GP[self.bcmmap[pos+1]-2].pwm: #display duteycycle and frequency
                            line1 = self.font.render(("%d Hz, %.1f") % (self.GP[self.bcmmap[pos+1]-2].pwm_freq, self.GP[self.bcmmap[pos+1]-2].pwm_dc), True, (128, 128, 128))
                            self._screen.blit(line1, (75 - ((pos+1) % 2) * line1.get_width() + (pos % 2)*(200) , self._yoffset + (pos / 2)*25 + 12 - line1.get_height() // 2))
                        else:
                            self._screen.blit(self._icons[1], (self._xoffset+(pos % 2)*25 , self._yoffset + (pos / 2)*25))    
    
    def run(self): 
        """
            Mainloop of the emulated GPIO. Is called when the emulator class is initialized.
        """
        
        self._running = True
    
        # create clock to reduce framerate
        clock = pygame.time.Clock()
        
        while self._running:
            clock.tick(30) #reduce framerate to 30 fps
    
            # get all events and check them 
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self._running = False
                
                if event.type == pygame.MOUSEBUTTONUP:
                    #check for clicks on GPIO-Pins and change state if it is an input
                    x, y = pygame.mouse.get_pos()
                    if x >= self._xoffset and x <= self._xoffset+50 and y >= self._yoffset and y <= self._yoffset + 25*20:
                        x = (x - self._xoffset) / 25
                        y = (y - self._yoffset) / 25
                        if self.GP[self.bcmmap[(2*y+x)+1]-2].getio() == IN:
                            self.GP[self.bcmmap[(2*y+x)+1]-2].setstate(1-self.GP[self.bcmmap[(2*y+x)+1]-2].getstate())
                
                #quit emulator if ESC is pressed
                #if event.type == pygame.KEYDOWN:
                #    if event.key == pygame.K_ESCAPE:
                #        self._running = False
    
            self.gadgets.check_events(events) #check events of Button/Textinput/...
            
            #draw everiting on the screen
            self._drawGPIO()
            self.gadgets.draw(self._screen)
            self._check_events()
            pygame.display.flip()

        pygame.quit()
        
    def stop(self):
        """
            Ends the Emulated GPIO and closes the window. 
            This function is called by GPIO.cleanup()
        """
        self._running = False