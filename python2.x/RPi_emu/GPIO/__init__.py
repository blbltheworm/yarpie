import time
import emugui
from threading import Thread #GUI is run as Thread to be independent of the main-code

from gpio_const import *
        
VERSION = '0.0.2'
RPI_INFO = 'GPIO-emu'

#  0 = Compute Module, 1 = Rev 1, 2 = Rev 2, 3 = Model B+ 
RPI_REVISION = 3
_warnings = True #variable storing the setwarnings()

class PWM(object):
    """
    PWM-Information is also stored in gpioemu.GP-class
    """
    def __init__(self, channel, frequency):
        self._frequency = frequency
        self._pwm = False #stores if PWM is running or not
        
        if _gpioemu.boardmode == BCM:
            if channel in _gpioemu.boardmap:
                self._id = channel-2
            else: #channel is no GPIO-channel
                if _warnings: print( "ValueError: The channel sent is invalid on a Raspberry Pi" )
                return
        elif _gpioemu.boardmode == BOARD:
            if channel in _gpioemu.bcmmap:
                self._id = _gpioemu.bcmmap[channel-1]-2
            else: #channel is no GPIO-channel
                if _warnings: print( "ValueError: The channel sent is invalid on a Raspberry Pi" )
                return
                
        _gpioemu.GP[self._id].pwm_freq = frequency
        _gpioemu.GP[self._id].pwm = False
    
    def start(self, dc):
        self._dc = dc
        _gpioemu.GP[self._id].pwm_dc = dc
        _gpioemu.GP[self._id].pwm = True
        _gpioemu.GP[self._id].setstate(HIGH)
    
    def ChangeFrequency(self, freq):
        self._frequency = freq
        _gpioemu.GP[self._id].pwm_freq = freq
        
    def ChangeDutyCycle(self, dc):
        self._dc = dc
        _gpioemu.GP[self._id].pwm_dc = dc
    
    def stop(self):
        self._pwm = False
        _gpioemu.GP[self._id].pwm = False
        _gpioemu.GP[self._id].setstate(LOW)

def _getid(channel): #determines the id of the related Element of GP-Array in _gpioemu
    if _gpioemu.boardmode == -1:
        if _warnings: print( "RuntimeError: Please set pin numbering mode using GPIO.setmode(GPIO.BOARD) or GPIO.setmode(GPIO.BCM)." )
        return -1
    
    if _gpioemu.boardmode == BCM:
        if channel in _gpioemu.boardmap:
            return channel-2
        else: #channel is no GPIO-channel
            #print str(channel) + " is no BCM-Port"
            if _warnings: print( "ValueError: The channel sent is invalid on a Raspberry Pi" )
    elif _gpioemu.boardmode == BOARD:
        if channel in _gpioemu.bcmmap:
            return _gpioemu.bcmmap[channel]-2
        else: #channel is no GPIO-channel
            #print str(channel) + " is no physical pin"
            if _warnings: print( "ValueError: The channel sent is invalid on a Raspberry Pi" )
    
    return -1
    
def setmode(boardmode):
    if _gpioemu.boardmode == -1:
        _gpioemu.boardmode = boardmode
        if boardmode != BCM and boardmode != BOARD:
            if _warnings: print( "ValueError: An invalid mode was passed to setmode()" )
    else:
        if _warnings: print( "ValueError: A different mode has already been set!" )

def getmode():
    return _gpioemu.boardmode

def output(channel, state):
    if isinstance(channel, tuple):
        channel = list(channel)
    
    if isinstance(channel, list):
        if isinstance(state, tuple):
            states = list(state)
        i = 0
        for i in range(len(channel)):
            _output(channel[i], state)
    else:
        _output(channel, state)

def _output(channel, state):
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        #no error message as it was already promted by _getid()
        return    
    
    if _gpioemu.GP[cid].was_setup:
        _gpioemu.GP[cid].setstate(state)
    else:
        if _warnings: print( "RuntimeError: The GPIO channel has not been set up as an OUTPUT" )
        return
    
    
def input(channel):
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        #no error message as it was already promted by _getid()
        return
    
    if _gpioemu.GP[cid].was_setup:
        return _gpioemu.GP[cid].getstate()
    else:
        if _warnings: print( "RuntimeError: You must setup() the GPIO channel first" )
        return

#setup supports setting up a list of channels as well as a singe channel
def setup(channel, mode, initial = LOW, pull_up_down=PUD_DOWN):    
    if isinstance(channel, list) or isinstance(channel, tuple):
        for item in channel:
            _setup(item, mode, initial, pull_up_down)
    else:
        _setup(channel, mode, initial, pull_up_down)

#sets up a singe channel
def _setup(channel, mode, initial = LOW, pull_up_down=PUD_DOWN):
    """
    ATTENTION: Currently there is no difference between PUD_DOWN and LOW (PUD_UP/HIGH).
    The emulator does not emulate an Pull up/down resistor, it is only able to set a pin HIGH or LOW
    """
    
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        #no error message as it was already promted by _getid()
        return
    
    if _gpioemu.GP[cid].was_setup:
        if _warnings: print( "This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings." )
    
    _gpioemu.GP[cid].was_setup = True
    _gpioemu.GP[cid].setio(mode)
    if mode == OUT:
        _gpioemu.GP[cid].setstate(initial)
    else:
        _gpioemu.GP[cid].setstate(pull_up_down)


def wait_for_edge(channel, edge, timeout=0):
    #get the ID of the GP-Array related to channel
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        return
    
    if _gpioemu.GP[cid].was_setup:
        _gpioemu.GP[cid].wait_for_edge = edge
    else:
        if _warnings: print( "RuntimeError: You must setup() the GPIO channel as an input first" )
        return
    
    
    #wait for edge
    #_gpioemu.GP[id].wait_for_edge will be set to 0 if condition is fullfilled
    if timeout == 0:
        while _gpioemu.GP[cid].wait_for_edge:
            time.sleep(0.01)
    else:
        etime = time.time() + timeout/1000.0
        while _gpioemu.GP[cid].wait_for_edge:
            time.sleep(0.01)
            if etime < time.time():
                return
    
    return channel

def add_event_detect(channel, edge, callback=None, bouncetime=0):
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        return
    
    _gpioemu.add_event(cid, edge, bouncetime, callback)

#adds a new event_detect and uses the edge of the first event related to this channel it can find
def add_event_callback(channel, callback):
    
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        return
    
    for event in _gpioemu.events:
        if event.cid == cid:
            _gpioemu.add_event(cid, event.edge, event.bouncetime, callback)
            return
    

def remove_event_detect(channel):
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        return
    
    _gpioemu.remove_event(cid)

def event_detected(channel):
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        return
    
    for event in _gpioemu.events:
        if event.cid == cid and event.detected:
            event.detected = False
            return channel

def gpio_function(channel):
#GPIO.IN, GPIO.OUT, GPIO.SPI, GPIO.I2C, GPIO.HARD_PWM, GPIO.SERIAL, GPIO.UNKNOWN
#sofar only IN and OUT are implemented
    cid = _getid(channel)
    
    if cid == -1: #no valid GPIO-pin
        if _warnings: print( "ValueError: The channel sent is invalid on an emulated Raspberry Pi, only P1-Header is included." )
        return
    else:
        return _gpioemu.GP[cid].getio()

def getmode():
    return _gpioemu.boardmode

def cleanup(dummy = None):
    """
    This function is used to stop the emulator
    
    NOT YET IMPLEMENTED:
    
    To clean up at the end of your script:

    GPIO.cleanup()

    It is possible that don't want to clean up every channel leaving some set up when your program exits. You can clean up individual channels, a list or a tuple of channels:

    GPIO.cleanup(channel)
    GPIO.cleanup( (channel1, channel2) )
    GPIO.cleanup( [channel1, channel2] )
    """
    _gpioemu.stop()

def setwarnings(state):
    _warnings = (state != 0)


"""

BEGIN SMBUS-Emulation
Note: In this emulated version of the Raspberry Pi the smbus is part of the GPIO-library
and no individual module.

"""

def add_autoreply(device, register, data):
    """
        Function that can be used by the programmer to generate an emulated i2c-device giving 
        predefined answers if the python script tries to read data from the given device and register.
        The autoreply can eigher be created/deleted within the python code or manually from the 
        I2C-Autoreply-panel of the emulator window. 
        
        data is a single value or a list of values.
    """
    #check whether for the given device/register already an autoreply exists. If so, replace it
    for i in range(len(_gpioemu.i2c_replys)):
        if _gpioemu.i2c_replys[i].device == device and _gpioemu.i2c_replys[i].register == register:
            #modify reply
            _gpioemu.i2c_replys[i].data = data
            if isinstance(data, list):
                _gpioemu.gadgets.lstData[1].edit_line(i,text=(("Autoreply for 0x%X (0x%X) of length %d") % (device, register, len(data))))
            else:
                _gpioemu.gadgets.lstData[1].edit_line(i,text=(("Autoreply for 0x%X (0x%X): 0x%X") % (device, register, data)))
            return
    else: #add new reply
        _gpioemu.i2c_replys.append(emugui.i2c_autoreply(device, register, data))
        #Add Autoreply to the ListItemGadget of the i2c-autoreply panel
        if isinstance(data, list):
            _gpioemu.gadgets.lstData[1].add_line(("Autoreply for 0x%X (0x%X) of length %d") % (device, register, len(data)))
        else:
            _gpioemu.gadgets.lstData[1].add_line(("Autoreply for 0x%X (0x%X): 0x%X") % (device, register, data))
#        _gpioemu.gadgets.lstData[1].add_line(("Autoreply for 0x%X (0x%X): 0x%X") % (device, register, data))


def remove_autoreply(device, register):
    """
        Removes a reply defined via add_autoreply().
    """
    for i in range(len(_gpioemu.i2c_replys)):
        if _gpioemu.i2c_replys[i].device == device and _gpioemu.i2c_replys[i].register == register:
            break
    else: #nothing to remove
        return
    
    del _gpioemu.i2c_replys[i]

def _btn_autoreply_click():
    """
        This function is called if the user clicks on the "Add-Button" in the i2c-autoreply-panel.
        It adds the device and data given in the InputGadgets to the autoreply list.
    """
    try:
        #convert text from strSend[0] to integer value (text="" will be interpreted as 0)
        #_gpioemu.curnumsys[1] is the current number system defined via the _gpioemu.gadgets.radFormat[1] Radio-Buttons
        if _gpioemu.gadgets.strSend[1].text:
            val = int(_gpioemu.gadgets.strSend[1].text, _gpioemu.curnumsys[1])
        else:
            val = 0
 
        device = int(_gpioemu.gadgets.strI2cdev[1].text, _gpioemu.curnumsys[1])
        reg = int(_gpioemu.gadgets.strI2creg.text, _gpioemu.curnumsys[1]) #register
        
    except: #temporary error treatment, has to be improved
        _gpioemu.gadgets.strSend[1].text = ""
        _gpioemu.gadgets.strI2cdev[1].text = ""
        _gpioemu.gadgets.strI2creg.text = ""
        return
        #_gpioemu.gadgets.lstData[0].add_line("Invalid input format, retry.", fontcolor = (0, 0, 255))
    
    _gpioemu.gadgets.strSend[1].text = ""
    _gpioemu.gadgets.strI2cdev[1].text = ""
    _gpioemu.gadgets.strI2creg.text = ""
    add_autoreply(device, reg, val)

def _lst_autoreply_rclick():
    """
        This function is called if the user right clicks on the ListItemGadget in the i2c-autoreply-panel.
        It deletes the selected autoreply.
    """

    curid = _gpioemu.gadgets.lstData[1].get_curid() #get selected item
    
    if curid != -1:
        del _gpioemu.i2c_replys[curid]              #delete from autoreply-list
        _gpioemu.gadgets.lstData[1].del_line(curid) #delete from ListItemGadget

def _radio_change(cid, curradio):
    """
        This function is called if the user changes the state of the RadioButtons in the i2c/autoi2c-panels.
        It changes the number system applied to the values in the Inputboxes in this panel and convertst the current values to the new number system 
        cid: 0=Hex, 1=Dec, 2=Oct, 3=Bin
        curradio: 0=i2c-panel, 1=autoi2c-panel
    """
        
    #check which will be the new number system
    if cid == 0: #HEX
        numsys = 16
        convstr = "{0:x}"
    elif cid == 1: #DEC
        numsys = 10
        convstr = "{0:d}"
    elif cid == 2: #OCT
        numsys = 8
        convstr = "{0:o}"
    elif cid == 3: #BIN
        numsys = 2
        convstr = "{0:b}"
        

    
    #convert values
    try:
        val = int(_gpioemu.gadgets.strSend[curradio].text, _gpioemu.curnumsys[curradio]) #data
        _gpioemu.gadgets.strSend[curradio].text = convstr.format(val)
    except:
        pass #not able to convert value -> leave it
    
    try:
        val = int(_gpioemu.gadgets.strI2cdev[curradio].text, _gpioemu.curnumsys[curradio]) #device
        _gpioemu.gadgets.strI2cdev[curradio].text = convstr.format(val)
    except:
        pass #not able to convert value -> leave it
    
    if curradio == 1:
        try:
            val = int(_gpioemu.gadgets.strI2creg.text, _gpioemu.curnumsys[curradio]) #register
            _gpioemu.gadgets.strI2creg.text = convstr.format(val)
        except:
            pass #not able to convert value -> leave it
    
    #store new number system
    _gpioemu.curnumsys[curradio] = numsys
    
class SMBus(object):
    """
        class to emulate the i2c-bus.
        Note: The revision is ignored so the emulated smbus will always work even if you provide the wrong
        revision of your Pi.
    """
    
    def __init__(self, rev): 
        """
            There is nothing to do if initializing the emulated SMBus.
            rev is a dummy which is not needed for the emulation but has to be given as the real SMBUS-module requires it.
        """
        
        print( "Emu Reminder: This emulator ignores the bus number. You are using bus %d, ensure this is the bus you are using on your Raspberry-Pi as well." % (rev) )
    
    def write_byte_data(self, device, register, data):
        if data > 255: #datablock is too long
            _gpioemu.gadgets.lstData[0].add_line(("write Byte to 0x%X (0x%X): 0x%X, data too long") % (device, register, data), (0, 0, 255))
        else:
            _gpioemu.gadgets.lstData[0].add_line(("write Byte to 0x%X (0x%X): 0x%X") % (device, register, data))
 
    def write_byte(self, device, cmd):
        _gpioemu.gadgets.lstData[0].add_line(("write Byte to 0x%X: 0x%X") % (device, cmd))
 
    def read_byte(self, device):
        _gpioemu.gadgets.lstData[0].add_line(("wait for Byte on 0x%X") % (device), fontcolor = (255, 0, 0))
        #check if an autoreply is defined, if not wait for manual input
        for autoreply in _gpioemu.i2c_replys:
            if autoreply.device == device:
                if isinstance(autoreply.data, list):
                    val = autoreply.data[0] % 256
                else:
                    val = autoreply.data % 256
                _gpioemu.gadgets.lstData[0].add_line(("autoreply: read Byte from 0x%X: 0x%X") % (device, val), fontcolor = (255, 131, 48))
                return val
        
        if _gpioemu.curnumsys[0] == 16:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:x}".format(device)
        elif _gpioemu.curnumsys[0] == 10:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:d}".format(device)
        elif _gpioemu.curnumsys[0] == 8:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:o}".format(device)
        elif _gpioemu.curnumsys[0] == 2:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:b}".format(device)
            
        _gpioemu.gadgets.strSend[0].hasfocus = True
        _gpioemu.gadgets.panel.selectpanel(0)
        
        while 1:
            #wait till send-button was clicked
            while not _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01) 
            
            while _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01)
        
            try:
                #convert text from strSend[0] to integer value (text="" will be interpreted as 0)
                #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                if _gpioemu.gadgets.strSend[0].text:
                    val = int(_gpioemu.gadgets.strSend[0].text, _gpioemu.curnumsys[0])
                else:
                    val = 0

                
                #check whether the user provided a valid value 
                if val > 255:
                    _gpioemu.gadgets.lstData[0].add_line("A byte was required but you provided a value >255, retry.", fontcolor = (0, 0, 255))
                else:
                    #if the device-InputGadget does not match the requested device ID the input will be ignores
                    #(maybe there is another thread running looking for another device) 
                    #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                    if int(_gpioemu.gadgets.strI2cdev[0].text, _gpioemu.curnumsys[0]) == device:
                        break
            except: #temporary error treatment, has to be improved
                _gpioemu.gadgets.lstData[0].add_line("Invalid input format, retry.", fontcolor = (0, 0, 255))
            
        _gpioemu.gadgets.lstData[0].add_line(("read Byte from 0x%X: 0x%X") % (device, val), fontcolor = (255, 131, 48))
        _gpioemu.gadgets.strSend[0].text = ""
        return val
 
    def read_byte_data(self, device, register):
        _gpioemu.gadgets.lstData[0].add_line(("wait for Byte on 0x%X (0x%X)") % (device, register), fontcolor = (255, 0, 0))
        #check if an autoreply is defined, if not wait for manual input
        for autoreply in _gpioemu.i2c_replys:
            if autoreply.device == device and autoreply.register == register:
                if isinstance(autoreply.data, list):
                    val = autoreply.data[0] % 256
                else:
                    val = autoreply.data % 256
                _gpioemu.gadgets.lstData[0].add_line(("autoreply: read Byte from 0x%X (0x%X): 0x%X") % (device, register, val), fontcolor = (255, 131, 48))
                return val
        
        if _gpioemu.curnumsys[0] == 16:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:x}".format(device)
        elif _gpioemu.curnumsys[0] == 10:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:d}".format(device)
        elif _gpioemu.curnumsys[0] == 8:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:o}".format(device)
        elif _gpioemu.curnumsys[0] == 2:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:b}".format(device)
            
        _gpioemu.gadgets.strSend[0].hasfocus = True
        _gpioemu.gadgets.panel.selectpanel(0)
        
        while 1:
            #wait till send-button was clicked
            while not _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01) 
            
            while _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01)
        
            try:
                #convert text from strSend[0] to integer value (text="" will be interpreted as 0)
                #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                if _gpioemu.gadgets.strSend[0].text:
                    val = int(_gpioemu.gadgets.strSend[0].text, _gpioemu.curnumsys[0])
                else:
                    val = 0
                
                #check whether the user provided a valid value 
                if val > 255:
                    _gpioemu.gadgets.lstData[0].add_line("You provided a value >255, retry.", fontcolor = (0, 0, 255))
                else:
                    #if the device-InputGadget does not match the requested device ID the input will be ignores
                    #(maybe there is another thread running looking for another device)
                    #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons 
                    if int(_gpioemu.gadgets.strI2cdev[0].text, _gpioemu.curnumsys[0]) == device:
                        break
            except: #temporary error treatment, has to be improved
                _gpioemu.gadgets.lstData[0].add_line("Invalid input format, retry.", fontcolor = (0, 0, 255))
            
        _gpioemu.gadgets.lstData[0].add_line(("read Byte from 0x%X (0x%X): 0x%X") % (device, register, val), fontcolor = (255, 131, 48))
        _gpioemu.gadgets.strSend[0].text = ""
        return val

    def write_word_data(self, device, register, data):
        if data >= 256**2: #datablock is too long
            _gpioemu.gadgets.lstData[0].add_line(("write Word to 0x%X (0x%X): 0x%X, data too long") % (device, register, data), (0, 0, 255))
        else:
            _gpioemu.gadgets.lstData[0].add_line(("write Word to 0x%X (0x%X): 0x%X") % (device, register, data))
 
    def read_word_data(self, device, register):
        _gpioemu.gadgets.lstData[0].add_line(("wait for Word on 0x%X (0x%X)") % (device, register), fontcolor = (255, 0, 0))
        #check if an autoreply is defined, if not wait for manual input
        for autoreply in _gpioemu.i2c_replys:
            if autoreply.device == device and autoreply.register == register:
                if isinstance(autoreply.data, list):
                    val = autoreply.data[0]  % (256**2)
                else:
                    val = autoreply.data % (256**2)
                _gpioemu.gadgets.lstData[0].add_line(("autoreply: read Word from 0x%X (0x%X): 0x%X") % (device, register, val), fontcolor = (255, 131, 48))
                return val
        
        if _gpioemu.curnumsys[0] == 16:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:x}".format(device)
        elif _gpioemu.curnumsys[0] == 10:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:d}".format(device)
        elif _gpioemu.curnumsys[0] == 8:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:o}".format(device)
        elif _gpioemu.curnumsys[0] == 2:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:b}".format(device)
            
        _gpioemu.gadgets.strSend[0].hasfocus = True
        _gpioemu.gadgets.panel.selectpanel(0)
        
        while 1:
            #wait till send-button was clicked
            while not _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01) 
            
            while _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01)
        
            try:
                #convert text from strSend[0] to integer value (text="" will be interpreted as 0)
                #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                if _gpioemu.gadgets.strSend[0].text:
                    val = int(_gpioemu.gadgets.strSend[0].text, _gpioemu.curnumsys[0])
                else:
                    val = 0

                #check whether the user provided a valid value 
                if val >= 256**2:
                    _gpioemu.gadgets.lstData[0].add_line("You provided a value >65535, retry.", fontcolor = (0, 0, 255))
                else:
                    #if the device-InputGadget does not match the requested device ID the input will be ignores
                    #(maybe there is another thread running looking for another device) 
                    #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                    if int(_gpioemu.gadgets.strI2cdev[0].text, _gpioemu.curnumsys[0]) == device:
                        break
            except: #temporary error treatment, has to be improved
                _gpioemu.gadgets.lstData[0].add_line("Invalid input format, retry.", fontcolor = (0, 0, 255))
            
        _gpioemu.gadgets.lstData[0].add_line(("read Word from 0x%X (0x%X): 0x%X") % (device, register, val), fontcolor = (255, 131, 48))
        _gpioemu.gadgets.strSend[0].text = ""
        return val

        
    def write_i2c_block_data(self, device, register, data):

        _gpioemu.gadgets.lstData[0].add_line(("write block of %d Bytes to 0x%X (0x%X):") % (len(data),device, register))        
        strdata = ""
        count = 0
        for item in data:
            strdata += (("0x%X, ") % (item))
            count += 1
            if count == 8:
                _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
                strdata = ""
                count = 0
        else:
            _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
    
    def read_i2c_block_data(self, device, register):
        _gpioemu.gadgets.lstData[0].add_line(("wait for block on 0x%X (0x%X)") % (device, register), fontcolor = (255, 0, 0))
        
        #check if an autoreply is defined, if not wait for manual input
        for autoreply in _gpioemu.i2c_replys:
            if autoreply.device == device and autoreply.register == register:
                _gpioemu.gadgets.lstData[0].add_line(("autoreply: read block of %d Bytes from 0x%X (0x%X):") % (len(autoreply.data)//2, device, register), fontcolor = (255, 131, 48))
                strdata = ""
                count = 0
                for item in autoreply.data:
                    strdata += (("0x%X, ") % (item))
                    count += 1
                    if count == 8:
                        _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
                        strdata = ""
                        count = 0
                else:
                    _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
                return autoreply.data
        
        #wait for user input
        if _gpioemu.curnumsys[0] == 16:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:x}".format(device)
        elif _gpioemu.curnumsys[0] == 10:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:d}".format(device)
        elif _gpioemu.curnumsys[0] == 8:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:o}".format(device)
        elif _gpioemu.curnumsys[0] == 2:
            _gpioemu.gadgets.strI2cdev[0].text = "{0:b}".format(device)
            
        _gpioemu.gadgets.strSend[0].hasfocus = True
        _gpioemu.gadgets.panel.selectpanel(0)
        
        while 1:
            #wait till send-button was clicked
            while not _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01) 
            
            while _gpioemu.gadgets.btnSend[0].hasfocus:
                time.sleep(0.01)
        
            try:
                #convert text from strSend[0] to integer value (text="" will be interpreted as 0)
                #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                if _gpioemu.gadgets.strSend[0].text:
                    val = int(_gpioemu.gadgets.strSend[0].text, _gpioemu.curnumsys[0])
                else:
                    val = 0
                
                #if the device-InputGadget does not match the requested device ID the input will be ignores
                #(maybe there is another thread running looking for another device) 
                #_gpioemu.curnumsys[0] is the current number system defined via the _gpioemu.gadgets.radFormat[0] Radio-Buttons
                if int(_gpioemu.gadgets.strI2cdev[0].text, _gpioemu.curnumsys[0]) == device:
                    break
            except: #temporary error treatment, has to be improved
                _gpioemu.gadgets.lstData[0].add_line("Invalid input format, retry.", fontcolor = (0, 0, 255))
        
        data = ("%X" %  val)
        if len(data) % 2: #can not be split into blocks of 2, thus a leading 0 is added
            data = "0" + data
        _gpioemu.gadgets.lstData[0].add_line(("read block of %d Bytes from 0x%X (0x%X):") % (len(data)//2, device, register), fontcolor = (255, 131, 48))
        count = 0
        strdata = ""
        for i in range(0, len(data), 2):
            strdata += ("0x" + data[i:i+2] + ", ")
            if count == 8:
                _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
                strdata = ""
                count = 0
        else:
            _gpioemu.gadgets.lstData[0].add_line("   " + strdata[:-2])
            
        _gpioemu.gadgets.strSend[0].text = ""
        return val
    

#start the GUI of the emulator as soon as the GPIO-module is imported
_gpioemu = emugui.emugui()
_gpioemu.gadgets.btnSend[1].set_callback(_btn_autoreply_click)    #Add Eventfunction to button "add" in i2c-autoreply-panel on left click
_gpioemu.gadgets.lstData[1].set_callback(_lst_autoreply_rclick, 3)#Add Eventfunction to ListItemGadget in i2c-autoreply-panel on right click
_gpioemu.gadgets.radFormat[0].set_callback(_radio_change, args=0)         #Add Eventfunction to Radio-Buttons in i2c-panel on left click
_gpioemu.gadgets.radFormat[1].set_callback(_radio_change, args=1)         #Add Eventfunction to Radio-Buttons in i2c-panel on left click
_gpioemu.start()
