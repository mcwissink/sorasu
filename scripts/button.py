''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math

#base class for all object in game
class Button():
    def __init__(self, x, y, font, color, size, text, center=False):
        '''
        initialize button
        '''
        #store necessary variables
        #if centered, use x and y as offsets
        self.color = color
        self.text = text
        self.font = font
        self.label = self.font.render(self.text, 1, self.color)
        width, height = font.size(self.text)
        self.rect = pygame.Rect(x, y, width, height)
        #center the button
        self.rect.centerx = self.rect.x
        self.rect.centery = self.rect.y
        
    def draw(self, screen, camera):
        '''
        draw the button
        '''
        screen.blit(self.label, camera.apply_single((self.rect.x, self.rect.y)))