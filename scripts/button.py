''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math

#base class for all object in game
class Button():
    def __init__(self, x, y, width, height, color, text):
        '''
        initialize button
        '''
        self.color = color
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(None, 30)
        self.label = self.font.render(text, 1, (255, 255, 255))
    
    def draw(self, screen):
        '''
        draw the button
        '''
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))
        screen.blit(self.label, (self.rect.x, self.rect.y))
    