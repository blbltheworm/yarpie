'''
Created on 19.04.2017

@author: blbltheworm
'''

import pygame

class pygameGadget(object):
    def __init__(self, x, y, width, height, color = (224, 222, 220), fontname="arial", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240)):
        #Font-settings
        self._fontname = fontname
        self._fontsize = fontsize
        self.fontcolor = fontcolor
        self.font = pygame.font.SysFont(fontname, fontsize)
        
        #store dimensions
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        self.color = color #color of the Gadget
        self.bgcolor = bgcolor #color of the underlying screen
        self.hasfocus = False
        self.hide = False #if True Gadget will not be drawn and no events will be detected
     
        #callbacks for left, middle, right-click
        self.callback = [None, None, None]
        self.callback_args = [None, None, None]
        
    #modify an existing Gadget (position, size, color,...)   
    def change(self, x = None, y = None, width = None, height = None, color = None, fontname = None, fontsize = None, fontcolor = None, bgcolor = None):
        if x: self.x = x
        if y: self.y = y
        if width: self.width = width
        if height: self.height = height
        if color: self.color = color
        if fontname: self._fontname = fontname
        if fontsize: self._fontsize = fontsize
        if fontcolor: self.fontcolor = fontcolor
        if bgcolor: self.bgcolor = bgcolor
        
        self.font = pygame.font.SysFont(self._fontname, self._fontsize)
        
        
    def set_callback(self,callback, eventbutton = 1, args = None):
        """
            Calls the function callback in case of a mouse click
            eventbutton: 1= left, 2= middle, 3= right click
        """
        self.callback[eventbutton-1] = callback
        self.callback_args[eventbutton-1] = args
        
#Only works with monospace fonts!
#If past from clipboard should be implemented the pygame-modul pygame.scrap can be used
class InputGadget(pygameGadget):
    
    def __init__(self,x,y,width,height=0, color = (255, 255, 255), fontname="monospace", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240)):
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)

        self._createbackground()
        
        self.text = ""
        self._textpos = 0 #0: vor dem ersten Zeichen, len(self.text): nach dem letzten

    def change(self,x = None,y = None,width = None,height = None, color = None, fontname = None, fontsize = None, fontcolor = None, bgcolor = None):
        pygameGadget.change(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)

        self._createbackground()
        
    def _createbackground(self):
        tmpchar = self.font.render("A", True, self.fontcolor) #render a character to get its width
        self._charwidth = tmpchar.get_width() #charwidth is used to determine the position of the cursor if clicked on the textinput-gadget
        
        #store dimensions
        if self.height == 0:
            self.height = tmpchar.get_height()+4
        
        #create GUI-graphics
        self._background = pygame.Surface((self.width, self.height))
        self._surface = pygame.Surface((self.width, self.height))
        poly = [[2, 0], [self.width-2, 0], [self.width-1, 2], [self.width-1, self.height-3], [self.width-3, self.height-1], [2, self.height-1], [0, self.height-3], [0,2]]
        self._background.fill(self.bgcolor)
        pygame.draw.polygon(self._background, self.color, poly)
        pygame.draw.polygon(self._background, (173, 169, 165), poly, 1)
        
    def check_events(self, events):
        
        if self.hide: #Gadget is not visible
            return
        
        #First check if user has clicked on the inputtext-gadget to set focus
        for event in events:        
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
                    self.hasfocus = True
                    #determine cursorposition
                    self._textpos = (x - self.x - 4) // self._charwidth
                    if self._textpos > len(self.text):
                        self._textpos = len(self.text)
                else:
                    self.hasfocus = False
        
        #analyse Key-events if gadget has focus
        if self.hasfocus:
            for event in events:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.hasfocus = False
                    elif event.key == pygame.K_HOME:
                        self._textpos = 0
                    elif event.key == pygame.K_END:
                        self._textpos = len(self.text) 
                    elif event.key == pygame.K_LEFT:
                        if self._textpos > 0:
                            self._textpos-=1
                    elif event.key == pygame.K_RIGHT:
                        if self._textpos < len(self.text):
                            self._textpos+=1
                    elif event.key == pygame.K_DELETE:
                        if self._textpos < len(self.text):
                            self.text = self.text[:self._textpos] + self.text[self._textpos+1:]
                    elif event.key == pygame.K_BACKSPACE:
                        if self._textpos > 0:
                            self.text = self.text[:self._textpos-1] + self.text[self._textpos:]
                            self._textpos -= 1
                    elif event.key == pygame.K_RETURN:
                        pass
                    elif event.key == pygame.K_SPACE:
                        pass
                    elif event.key in range(pygame.K_0, pygame.K_9+1): #Keys 0 - 9 
                        self.text = self.text[:self._textpos] + chr(event.key) + self.text[self._textpos:]
                        self._textpos += 1
                    elif event.key in range(pygame.K_KP0, pygame.K_KP9+1): #keypad 0 - 9
                        self.text = self.text[:self._textpos] + chr(event.key-208) + self.text[self._textpos:]
                        self._textpos += 1
                    elif event.key in range(pygame.K_a, pygame.K_f+1): #keys A - F
                        self.text = self.text[:self._textpos] + chr(event.key-32) + self.text[self._textpos:]
                        self._textpos += 1
                    #else:
                        #print( event.key )
        
    def draw(self, screen):
        if self.hide: #Gadget is not visible
            return
        
        self._surface.blit(self._background,(0, 0))
            
        if self.hasfocus:
            if len(self.text) < self._textpos:
                self._textpos = len(self.text)
                
            if len(self.text) == 0:
                pygame.draw.line(self._surface, (0, 0, 0), [4,4], [4,self.height-4], 1)
            else:
                if self._textpos == 0:
                    imgtext = self.font.render(self.text, True, self.fontcolor)
                    self._surface.blit(imgtext, (4, (self.height-imgtext.get_height()) // 2))
                    pygame.draw.line(self._surface, (0, 0, 0), [4,4], [4,self.height-4], 1)
                elif self._textpos == len(self.text):
                    imgtext = self.font.render(self.text, True, self.fontcolor)
                    self._surface.blit(imgtext, (4, (self.height-imgtext.get_height()) // 2))
                    pygame.draw.line(self._surface, (0, 0, 0), [4+imgtext.get_width(),4], [4+imgtext.get_width(),self.height-4], 1)
                else:
                    imgtext = self.font.render(self.text[:self._textpos], True, self.fontcolor)
                    imgtext2 = self.font.render(self.text[self._textpos:], True, self.fontcolor)
                    self._surface.blit(imgtext, (4, (self.height-imgtext.get_height()) // 2))
                    self._surface.blit(imgtext2, (4+imgtext.get_width(), (self.height-imgtext.get_height()) // 2))
                    pygame.draw.line(self._surface, (0, 0, 0), [4+imgtext.get_width(),4], [4+imgtext.get_width(),self.height-4], 1)
        else:
            if len(self.text):
                imgtext = self.font.render(self.text, True, self.fontcolor)
                self._surface.blit(imgtext, (4, (self.height-imgtext.get_height()) // 2))
        
        screen.blit(self._surface,(self.x, self.y))
    
class ListItem(object):
    """
        sub-class storing informations for listitems of the ListGadget-class
    """
    def __init__(self, text, fontcolor, color):
        self.text = text
        self.fontcolor = fontcolor
        self.color = color
        
class ListGadget(pygameGadget):
    """
    Gadget showing a scrollable List
    """
    def __init__(self, x, y, width, height, color = (255, 255, 255), fontname="monospace", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240), reverse=False):
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)

        self._ruler = pygame.Surface((19,6)) #marker of the scroll bar
        self.lines = [] #list of ListItem-class containing text and colorinfos of the related listitem
        self._curline = 0 #id of the line currently shown at the buttom of the ist
        self._curfield = 0 #registers Mouse down. 1: list-field, 2: button arrow up, 3: button arrow down, 4: scrollbar
        self._curitem = -1 #id of the currently highlighted line (value between 0 and _maxlines-1, -1 = no selection
        self.reverse = reverse #False: first Element on the top, last on the bottom of the list. True: the other way round
        
        self._createbackground() #draw graphics

    def change(self,x = None,y = None,width = None,height = None, color = None, fontname = None, fontsize = None, fontcolor = None, bgcolor = None, reverse = None):
        pygameGadget.change(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)

        if reverse:
            self.reverse = reverse

        self._createbackground()

        
    def _createbackground(self):
        tmpchar = self.font.render("A", True, self.fontcolor) #render a character to get its width
        self._charheight = tmpchar.get_height() #charheight is used to determine the position of the cursor if clicked on the listitem-gadget
        self._maxlines = (self.height-8) // self._charheight #number of lines fitting in the list
        
        self._background = pygame.Surface((self.width, self.height)) #background (e.g. shape of the gadget, buttons, ...)
        self._surface = pygame.Surface((self.width, self.height)) #everything is drawn on the surface before drawing it on the screen

        #list field
        poly = [[2, 0], [self.width-21, 0], [self.width-19, 2], [self.width-19, self.height-3], [self.width-21, self.height-1], [2, self.height-1], [0, self.height-3], [0,2]]
        self._background.fill(self.bgcolor)
        pygame.draw.polygon(self._background, self.color, poly)
        pygame.draw.polygon(self._background, (173, 169, 165), poly, 1)
        
        #scroll bar
        color = (204, 201, 201)#(173, 169, 165) #(225, 223, 221)
        #scroll bar frame
        pygame.draw.rect(self._background,color, [self.width-18, 17, 17, self.height-35],2)
        pygame.draw.rect(self._background,color, [self.width-18, 0, 17, 17],2)
        pygame.draw.rect(self._background,color, [self.width-18, self.height-18, 17, 17],2)
        
        #scroll bar triangles
        color = (204, 201, 201)
        poly = [[self.width-9, 5], [self.width-5, 10], [self.width-13, 10]]
        pygame.draw.polygon(self._background, color, poly)
        poly = [[self.width-9, self.height-6], [self.width-5, self.height-11], [self.width-13, self.height-11]]
        pygame.draw.polygon(self._background, color, poly)
        
        #scroll bar ruler
        color = (204, 201, 201)
        self._ruler.fill(color)
        color = (173, 169, 165)
        pygame.draw.circle(self._ruler, color, [3,3], 3, 1)
        pygame.draw.circle(self._ruler, color, [18-3,3], 3, 1)
        color = (204, 201, 201)
        pygame.draw.rect(self._ruler, color,[3, 0, 18-6, 6])
        color = (173, 169, 165)
        pygame.draw.line(self._ruler, color, [3,0], [18-3,0],1)
        pygame.draw.line(self._ruler, color, [3,5], [18-3,5],1)
        
    
    def _drawitems(self, first, length):
        """
            draw all items between self.lines[first] to self.lines[first+length-1] on self._surface. 
        """
        cury = 4
        if self.reverse: #first item on the bottom, last on the top
            for i in range(0, length):
                if self.hasfocus and self._curitem == first+length -1 - i:
                    pygame.draw.rect(self._surface, (232, 242, 254), [2, cury, self.width-22, self._charheight])
                else:
                    pygame.draw.rect(self._surface, self.lines[length-1-i].color, [2, cury, self.width-22, self._charheight])
                imgline = self.font.render(self.lines[length-1-i].text, True, self.lines[length-1-i].fontcolor)
                self._surface.blit(imgline, (4, cury))
                cury += self._charheight
        else: #first item on the top, last on the bottom
            for i in range(0, length):
                if self.hasfocus and self._curitem ==first + i:
                    pygame.draw.rect(self._surface, (232, 242, 254), [2, cury, self.width-22, self._charheight])
                else:
                    pygame.draw.rect(self._surface, self.lines[first+i].color, [2, cury, self.width-22, self._charheight])
                imgline = self.font.render(self.lines[first+i].text, True, self.lines[first+i].fontcolor)
                self._surface.blit(imgline, (4, cury))
                cury += self._charheight
                
    def draw(self, screen):
        if self.hide: #Gadget is not visible
            return
        
        self._surface.blit(self._background,(0, 0))
        
        if self.lines: #draw currently shown listitems
            cury = 4 #position where the next line is drawn
            if len(self.lines) <= self._maxlines:
                self._drawitems(0, len(self.lines))
            else:
                self._drawitems(self._curline, self._maxlines)
                
                cury = (self.height-35-6)*self._curline//(len(self.lines)-self._maxlines)
                if self.reverse:
                    self._surface.blit(self._ruler, (self.width-18, self.height - 18-6 - cury))
                else:
                    self._surface.blit(self._ruler, (self.width-18, 18 + cury))

                    
        screen.blit(self._surface,(self.x, self.y))

    def check_events(self, events):
        if self.hide: #Gadget is not visible
            return
        
        #First check if user has clicked on the List-gadget
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y and y <= self.y + 18:
                    #button scroll-up
                    self._curfield = 2
                elif x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y+self.height-18 and y <= self.y + self.height:
                    #button scroll-down
                    self._curfield = 3
                elif x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y+18 and y <= self.y + self.height-18:
                    #scroll bar
                    self._curfield = 4
                elif x >= self.x and x <= self.x+self.width-18 and y >= self.y and y <= self.y + self.height:
                    #list-area
                    self._curfield = 1
                else:
                    self._curfield = 0
            elif event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y and y <= self.y + 18:
                    #button scroll-up
                    self.hasfocus = True
                    if self._curfield == 2: #Mousedown + up = click
                        if self.reverse:
                            if self._curline < (len(self.lines)-self._maxlines):
                                self._curline += 1
                                if self._curitem > -1 and self._curitem >0:
                                    self._curitem -= 1
                        else:
                            if self._curline > 0:
                                self._curline -= 1
                                if self._curitem > -1 and self._curitem < self._maxlines:
                                    self._curitem += 1
                elif x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y+self.height-18 and y <= self.y + self.height:
                    #button scroll-down
                    self.hasfocus = True
                    if self._curfield == 3: #Mousedown + up = click
                        if self.reverse:
                            if self._curline > 0:
                                self._curline -= 1
                                if self._curitem > -1 and self._curitem < self._maxlines:
                                    self._curitem += 1
                        else:
                            if self._curline < (len(self.lines)-self._maxlines):
                                self._curline += 1
                                if self._curitem > -1 and self._curitem >0:
                                    self._curitem -= 1
                elif x >= self.x+self.width-18 and x <= self.x+self.width and y >= self.y+18 and y <= self.y + self.height-18:
                    #scroll bar
                    self.hasfocus = True
                    if self._curfield == 4: #Mousedown + up = click
                        pass
                elif x >= self.x and x <= self.x+self.width-18 and y >= self.y and y <= self.y + self.height:
                    #list-area
                    self.hasfocus = True
                    if self._curfield == 1: #Mousedown + up = click
                        self._curitem = (y-self.y-4) // self._charheight #row which has focus -> value between 0 and _maxlines-1
                        
                        if event.button in [1, 2, 3]: #Call callback-Function for mouseclick (1: left, 2:middle, 3:right)
                            if not self.callback[event.button-1] is None:
                                if self.callback_args[event.button-1] is None:
                                    self.callback[event.button-1]()
                                else:
                                    self.callback[event.button-1](self.callback_args[event.button-1])        

                else:
                    self.hasfocus = False
                    self._curitem = -1 #currently selected item
                
                self._curfield = 0 #reset Mousedown registration to deteckt clicks on one item
                
    def get_curid(self):
        """
            returns the id of the currently selected item
        """
        return self._curitem
    
    def add_line(self, text, fontcolor = None, color = None):
        if fontcolor is None:
            fontcolor = self.fontcolor
            
        if color is None:
            color = self.color
        
        self.lines.append(ListItem(text, fontcolor, color))
        
        
        if len(self.lines) > self._maxlines:
            self._curline = len(self.lines) - self._maxlines
    
    def edit_line(self, cid, text = None, fontcolor = None, color = None):
        """
            Modify an existing line, identified by its cid
        """
    
        if text:
            self.lines[cid].text = text
        
        if fontcolor:
            self.lines[cid].fontcolor = fontcolor
        
        if color:
            self.lines[cid].fontcolor = color
        
    
    def del_line(self, cid):
        del self.lines[cid] 


class ButtonGadget(pygameGadget):
    def __init__(self, caption, x, y, width, height, color = (224, 222, 220), fontname="arial", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240)):
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)

        self.caption = caption
                
        #callbacks for left, middle, right-click
        self.callback = [None, None, None]
        self.callback_args = [None, None, None]
        
        self._createbackground()
    
    #change an existing Gadget (position, size, color, caption, ...)
    def change(self, caption = None, x = None, y = None, width = None, height = None, color = None, fontname = None, fontsize = None, fontcolor = None, bgcolor = None):
        pygameGadget.change(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)
        
        if caption: self.caption = caption
        
        self._createbackground()
    
    def _createbackground(self):
        
        self._imgcaption = self.font.render(self.caption, True, self.fontcolor) #create label-text
        
        self._up = pygame.Surface((self.width, self.height))   #toggled Button
        self._down = pygame.Surface((self.width, self.height)) #released Button

        self._up.fill(self.bgcolor)
        
        poly = [[2, 0], [self.width-3, 0], [self.width-1, 2], [self.width-1, self.height-3], [self.width-3, self.height-1], [2, self.height-1], [0, self.height-3], [0,2]]
        pygame.draw.polygon(self._up, self.color, poly)
        pygame.draw.polygon(self._up, (173, 169, 165), poly,1)
        
        self._down.blit(self._up, (0,0))
        self._up.blit(self._imgcaption, ((self.width - self._imgcaption.get_width()) // 2, (self.height - self._imgcaption.get_height()) // 2))
        self._down.blit(self._imgcaption, ((self.width - self._imgcaption.get_width()) // 2+2, (self.height - self._imgcaption.get_height()) // 2+2))
    
    def check_events(self, events):
        if self.hide: #Gadget is not visible
            return
        
        #First check if user has clicked on the List-gadget
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
                    if self.hasfocus and event.button in [1, 2, 3]: #DOWN + UP = Click -> Call callback-Function
                        if not self.callback[event.button-1] is None:
                            if self.callback_args[event.button-1] is None:
                                self.callback[event.button-1]()
                            else:
                                self.callback[event.button-1](self.callback_args[event.button-1])        
                
                self.hasfocus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
                    self.hasfocus = True
                else:
                    self.hasfocus = False  
                    
    def draw(self,screen):
        if self.hide: #Gadget is not visible
            return
        
        if self.hasfocus: #button down
            screen.blit(self._down,(self.x, self.y))
        else:
            screen.blit(self._up,(self.x, self.y))
            

class _PanelGadgetPanel(object):
    def __init__(self,caption, color, font, fontcolor):
        self.caption = caption
        self.color = color
        self._imgcaption = font.render(caption, True, fontcolor)
        self.gadgets = [] #list of Gadgets that will be shown/ of this panel is active
        #create_panel_img()

    def create_panel_img(self, height):
        self.width = self._imgcaption.get_width()+8
        self.imgpanel = pygame.Surface((self.width, height))
        
        #create GUI-graphics
        poly = [[0, height-1], [0, 2], [2, 0], [self.width-3, 0], [self.width-1, 2], [self.width-1, height-1]]
        self.imgpanel.fill((255, 255, 255))
        pygame.draw.polygon(self.imgpanel, self.color, poly)
        pygame.draw.polygon(self.imgpanel, (173, 169, 165), poly,1)
        pygame.draw.line(self.imgpanel, self.color, [1, height-1], [self.width-2, height-1])
        self.imgpanel.blit(self._imgcaption,(4,4))
        
class PanelGadget(pygameGadget):
    
    def __init__(self, x, y, width, height, panelcaptions, color = (242, 241, 240), fontname="arial", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240)):
        """
            panelcaptions: List of Captions for the different panels ["A", "B", "C"] creates three panels labeled A, B; C
        """
        
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)
        
        self._panels = [] 
        self.curpanel = 0
        
        self.pheight = 0
        #pheight is the hight of the text of the highest panel-caption
        #this value is used to define where the field-are of the panel begins
        curpheight = 0
        for panel in panelcaptions:
            self._panels.append(_PanelGadgetPanel(panel, color, self.font, self.fontcolor))
            curpheight = self._panels[-1]._imgcaption.get_height()
            if self.pheight < curpheight:
                self.pheight = curpheight
        
        self.pheight += 8 #there are 4 Pixels of space above and below the caption
        
        #create the image of the panel-caption
        for panel in self._panels:
            panel.create_panel_img(self.pheight)
        
        self._background = pygame.Surface((width, height))
        self._createbackground()

    def _createbackground(self):
        
        poly = [[0, self.pheight], [self.width-3, self.pheight], [self.width-1, self.pheight+2], [self.width-1, self.height-3], [self.width-3, self.height-1],[2, self.height-1], [0, self.height-3]]
        self._background.fill(self.bgcolor)
        pygame.draw.polygon(self._background, self.color, poly)
        pygame.draw.polygon(self._background, (173, 169, 165), poly,1)
        #pygame.draw.line(self.imgpanel, (224, 222, 220), [1, height-1], [width-2, height-1])
        curx = 0
        count = 0
        for panel in self._panels:
            
            self._background.blit(panel.imgpanel, (curx, 0))
            if count == self.curpanel:
                pygame.draw.line(self._background, self.color, [curx+1, self.pheight], [curx + panel.imgpanel.get_width()-2, self.pheight])
            curx += (panel.imgpanel.get_width() + 1)
            count += 1
        
    def selectpanel(self, cid):
        """
        cid: id of the panel currently selected
        """
        #hide Gadgets of the current panel
        for gadget in self._panels[self.curpanel].gadgets:
            gadget.hide = True
        
        #show gadgets of the new panel
        for gadget in self._panels[cid].gadgets:
            gadget.hide = False
                
        self.curpanel = cid
        self._createbackground() #redraw Background with new selection

    def embed_gadgets(self, panel_id, gadgets):
        """
            if a gadget is embeded in a panel it will only be shown while the register with the id panel_id is active 
            gadgets may eighter be a singe gadget or a list of gadgets
        """
        
        if isinstance(gadgets, list):
            for gadget in gadgets:
                self._panels[panel_id].gadgets.append(gadget)
                if self.curpanel == panel_id: #show Gadget only if panel_id is active
                    gadget.hide = False
                else:
                    gadget.hide = True
        else:
            self._panels[panel_id].gadgets.append(gadgets)
            if self.curpanel == panel_id: #show Gadget only if panel_id is active
                gadgets.hide = False
            else:
                gadgets.hide = True

    def draw(self, screen):
        screen.blit(self._background,(self.x, self.y))
        
    def check_events(self, events):
        if self.hide: #Gadget is not visible
            return
        
        #First check if user has clicked on the List-gadget
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                #check whether user clicked on the panel registers 
                if y >= self.y and y <= self.y + self.pheight:
                    curx = 0
                    count = 0
                    #check which register the mouse is over
                    for panel in self._panels:
                        if x >= self.x + curx and x <= self.x + curx + panel.width:
                            self.selectpanel(count)
                        else:
                            count += 1
                            curx += (panel.width + 1)

class TextGadget(pygameGadget):
    
    def __init__(self, x, y, width = 0, height = 0, caption= " ", color = (242, 241, 240), fontname="arial", fontsize=12, fontcolor = (0, 0, 0)):
        """
            Create a simple Label, just displaying text without any interactions
        """
        
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, color)
        #TextGadget does not use bgcolor
        
        #pheight is the hight of the text of the highest panel-caption
        #this value is used to define where the field-are of the panel begins
        self.caption = caption
        
        self._createbackground()

    def change(self, x = None, y = None, width = None, height = None, caption = None, color = None, fontname = None, fontsize = None, fontcolor = None):
        """
            Create a simple Label, just displaying text without any interactions
        """
        
        pygameGadget.change(self, x, y, width, height, color, fontname, fontsize, fontcolor, color)
        #TextGadget does not use bgcolor
        
        if caption:
            self.caption = caption
                
        self._createbackground()
        
    def _createbackground(self):
        
        self._imgcaption = self.font.render(self.caption, True, self.fontcolor)
        
        if self.width == 0:
            self.width = self._imgcaption.get_width()
        if self.height == 0:
            self.height = self._imgcaption.get_height()
        
        self._surface = pygame.Surface((self.width, self.height))
        self._surface.fill(self.color)
        self._surface.blit(self._imgcaption, ((self.width - self._imgcaption.get_width())//2, (self.height - self._imgcaption.get_height())//2))
    
    
    def draw(self, screen):
        screen.blit(self._surface, (self.x, self.y))
        
class RadioGadget(pygameGadget):
    
    def __init__(self, x, y, width=0, height=0, caption= " ", color = (255, 255, 255), fontname="arial", fontsize=12, fontcolor = (0, 0, 0), bgcolor = (242, 241, 240)):
        """
            
        """
        
        pygameGadget.__init__(self, x, y, width, height, color, fontname, fontsize, fontcolor, bgcolor)
        
        self.state = False #0=inactive, 1=actice
        self.caption = caption
        self.size = 12 #diameter of the radio-circle
        
        self._imgcaption = self.font.render(caption, True, fontcolor)
        
        if height == 0:
            if self._imgcaption.get_height() < self.size:
                self.height = self.size
            else:
                self.height = self.size
                
        if width == 0:
            self.width = self._imgcaption.get_width() + self.size + 2
        
        self._surface = pygame.Surface((self.width, self.height))
        self._imgstate = [pygame.Surface((self.size, self.size)), pygame.Surface((self.size, self.size))] #0=inactive, 1=actice
        
        self._createbackground()
    
    def _createbackground(self):
        
        for i in range(2):
            self._imgstate[i].fill(self.bgcolor)
            pygame.draw.circle(self._imgstate[i], self.color, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self._imgstate[i], (173, 169, 165),(self.size // 2, self.size // 2), self.size // 2, 1)
        
        pygame.draw.circle(self._imgstate[i], (173, 169, 165),(self.size // 2, self.size // 2), self.size // 2 - 3)
    
    def draw(self, screen):
        self._surface.fill(self.bgcolor)
        
        self._surface.blit(self._imgstate[self.state], (0, (self.height - self._imgcaption.get_height())//2))
        self._surface.blit(self._imgcaption, (self.size+2, (self.height - self._imgcaption.get_height())//2))
        
        screen.blit(self._surface, (self.x, self.y))

    def check_events(self, events):
        if self.hide: #Gadget is not visible
            return
        
        #First check if user has clicked on the List-gadget
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
                    #button up
                    if self.hasfocus: #DOWN + UP = Click -> Call callback-Function
                        self.state = True       
                
                self.hasfocus = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if x >= self.x and x <= self.x+self.width and y >= self.y and y <= self.y + self.height:
                    #button up
                    self.hasfocus = True
                else:
                    self.hasfocus = False  
            
            
class RadioGadgetGroup(object):
    """
    class to group different RadioGadgets together 
    """

    def __init__(self, radiogadgets):
        self._gadgetlist = radiogadgets #group of RadioGadgets belonging together
        self.cid = 0 #ID of the Element in gadgetlist which is currently active
        
        #set first element active, all other inactive
        radiogadgets[0].state = True
        for i in range(1, len(radiogadgets)):
            radiogadgets[i].state = False
    
    def set_callback(self,callback, args = None):
        """
            Calls the function callback if the status of the buttons is changed between elements
        """
        self.callback = callback
        self.callback_args = args
        
    def add_gadget(self, radiogadget):
        """
        add a RadioGadget to the list
        """
        if isinstance(channel, list) or isinstance(channel, tuple):
            for gadgets in radiogadget:
                self._gadgetlist.append(gadget)
                gadget.state = False
        else:
            self._gadgetlist.append(radiogadget)
            radiogadget.state = False
        
    def check_events(self, events):
        
        #check whether one of the Gadgets was activated (user has clicked on it)
        counter = 0
        for gadget in self._gadgetlist:
            tmpstatus = gadget.state
            gadget.check_events(events)
            if tmpstatus == False and gadget.state == True:
                break
            counter += 1
        
        #set all other gadgets of the group inactive
        if counter < len(self._gadgetlist):
            for i in range(len(self._gadgetlist)):
                if i != counter:
                    self._gadgetlist[i].state = False

            self.cid = counter #store the position of the currently active item in the list
            
            # Call callback-Function for Change-Event
            if not self.callback is None:
                if self.callback_args is None:
                    self.callback()
                else:
                    self.callback(counter, self.callback_args)        

            
    def draw(self, screen):
        #draw all RadioGadgets allocated to the RadioGadgetList
        for gadget in self._gadgetlist:
            gadget.draw(screen)