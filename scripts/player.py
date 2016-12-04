''' CS 108
Created Fall 2016
child of DynamicObject that the user can control
@author: Mark Wissink (mcw33)
'''
import pygame, sys, math
import utilities
from game_object import DynamicObject

class Player(DynamicObject):
    ''' 
    Player game object for moving your character around
    '''
    def __init__(self, x, y, offsets, attributes):
        DynamicObject.__init__(self, x, y, offsets, attributes)
        self.type = 'player'
        self.color = (255,0,0)
        self.max_vel = 3000
        self.accel = 2000
        self.past_up = self.past_down = self.past_left = self.past_right = True # Past key presses
        
    def input(self, keys, dt):
        '''s
        Takes input to check for keypresses
        (dictionary)
        '''  
        '''Left and right movement'''
        if keys['right'] and not keys['left']: # Right movement
            if abs(self.vel.x) < self.max_vel:
                self.vel.x += abs(self.accel-self.vel.x) * dt
        elif keys['left'] and not keys['right']: # Left movement
            if abs(self.vel.x) < self.max_vel:
                self.vel.x -= abs(self.accel+self.vel.x) * dt
        '''Up and down movement'''
        if keys['up'] and not keys['down'] and not self.past_up: # Jump, wall jump
            #if not self.past_up: #make sure the key is pressed and not held 
            if self.onground:
                self.vel.y -= 1000
            if self.onwall:
                self.vel.y = -1000
                self.vel.x += 1000 * self.onwall
        elif keys['down'] and not keys['up']: # Fall faster when user is pressing down
            self.vel.y += 3000 *dt
        #Store past key presses
        self.past_up = True if (keys['up']) else False
        self.past_down = True if (keys['down']) else False
        self.past_left = True if (keys['left']) else False
        self.past_right = True if (keys['right']) else False
        
    def update(self, dt, entities):
        DynamicObject.update(self, dt, entities)
        
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(DynamicObject.to_dictionary(self),
                {})