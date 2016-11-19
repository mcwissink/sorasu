''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
from test.test_importlib.import_.test_packages import ParentModuleTests

def buttons_init(parent):
    ''''creates the necessary variables for the buttons'''
    parent.buttons = []
    parent.button_hover = None #used for highlighting buttons
    parent.last_click = None #used for remembering buttons
    parent.current_button = None #used to store current button

def buttons_update(parent, buttons):
    '''updates the buttons'''
    if not parent.last_click:
        for button in buttons:
            button.update(pygame.mouse.get_pos())
            
def buttons_draw(parent, screen, buttons):
    '''draws the buttons'''
    for entity in buttons:
        entity.draw(screen, parent.camera) 
       
def buttons_mousedown(parent, buttons):
    '''update the buttons when mouse is pressed the buttons'''
    if not parent.last_click:
                parent.last_click = checkButtons(buttons, pygame.mouse.get_pos())
                if parent.last_click:
                    parent.last_click.font.set_bold(True)
                    parent.last_click.label = parent.last_click.font.render(parent.last_click.text, 1, (255,0,0))

def buttons_mouseup(parent, buttons):
    '''update the buttons when mouse is released the buttons'''
    if parent.last_click:
        parent.current_button = checkButtons(buttons, pygame.mouse.get_pos())
        if parent.last_click == parent.current_button and parent.current_button != None:
            if parent.current_button.returning:
                return parent.current_button.onClick() # specifically for the state changing buttons
            else:
                parent.current_button.onClick()
            parent.last_click.font.set_bold(False)
            parent.last_click.label = parent.last_click.font.render(parent.last_click.text, 1, parent.last_click.color)
        else:
            parent.last_click.font.set_bold(False)
            parent.last_click.label = parent.last_click.font.render(parent.last_click.text, 1, parent.last_click.color)
    parent.last_click = None

def checkButtons(buttons, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in buttons:
            if button.rect.collidepoint(mouse):
                return button
    
#base class for all object in game
class Button():
    def __init__(self, x, y, font, color, size, text, align, returning=False, value='', attr=''):
        '''
        initialize button
        '''
        #store necessary variables
        #if centered, use x and y as offsets
        self.offset = (x, y)
        self.align = align # percent value for positioning on screen
        self.hover = 0 # for coloring the button 
        self.returning = returning #used if a button has to return a state
        self.color = color
        self.text = text
        self.value = value #if the buttun has a changing value
        self.attr = attr #for remembering what attribute is being stored
        self.font = font
        self.label = self.font.render(self.text, 1, self.color)
        width, height = font.size(self.text)
        self.rect = pygame.Rect(x, y, width, height)

    def update(self, mouse):
        '''updates the button'''
        #this resets the color only once, instead of everyframe
        if self.rect.collidepoint(mouse):
            self.label = self.font.render(self.text + str(self.value), 1, (255,0,0))
            self.hover = 1
        elif self.hover == 0 or self.value != '':
            self.label = self.font.render(self.text + str(self.value), 1, self.color)
            self.hover = 2
        self.hover = 0
    
    def draw(self, screen, camera):
        '''
        draw the button
        '''
        screen.blit(self.label, (self.rect.x, self.rect.y))
        
    def realign(self, camera):
        '''
        realigns the button based on the percent given to align
        '''
        self.rect.x = camera.viewport.width*self.align[0] + self.offset[0]
        self.rect.y = camera.viewport.height*self.align[1] + self.offset[1]