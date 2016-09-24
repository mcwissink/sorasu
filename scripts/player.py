''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''
import pygame, sys, math
from scripts.game_object import DynamicObject

class Player(DynamicObject):
    ''' 
    Player game object for moving your character around
    '''
    def __init__(self, x, y, width, height, color, mask):
        DynamicObject.__init__(self, x, y, width, height, color, mask)
        self.past_up = self.past_down = self.past_left = self.past_right = True # Past key presses
        
    def input(self, keys):
        '''
        Takes input to check for keypresses
        (dictionary)
        '''  
        '''Left and right movement'''
        if keys['right'] and not keys['left']: # Right movement
            self.vel.x += 1
        elif keys['left'] and not keys['right']: # Left movement
            self.vel.x -= 1
        '''Up and down movement'''
        if keys['up'] and not keys['down']: # Jump, wall jump left, wall jump right, and hover
            self.vel.y -= 1
        elif keys['down'] and not keys['up']: # Fall faster when user is pressing down
            self.vel.y += 1
        #Store past key presses
        self.past_up = True if (keys['up']) else False
        self.past_down = True if (keys['down']) else False
        self.past_left = True if (keys['left']) else False
        self.past_right = True if (keys['right']) else False
    def update(self, dt, entities):
        DynamicObject.update(self, dt, entities)