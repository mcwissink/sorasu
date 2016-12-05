''' CS 108
Created Fall 2016
child of DynamicObject that the user can control
@author: Mark Wissink (mcw33)
'''
import pygame, sys, math
import utilities
import random
from game_object import DynamicObject

class Enemy(DynamicObject):
    ''' 
    enemy for attacking player
    '''
    ATTRIBUTES = [{'name': 'Mass', 'init': 10, 'max': 100, 'min': 1, 'step': 1},
                  {'name': 'Speed', 'init': 10, 'max': 50, 'min': 1, 'step': 1},
                  {'name': 'Jump', 'init': 10, 'max': 30, 'min': 1, 'step': 1}]
    def __init__(self, x, y, offsets, attributes):
        DynamicObject.__init__(self, x, y, offsets, attributes)
        self.speed = attributes[1]
        self.jump = attributes[2]
        self.type = 'enemy'
        self.color = (0,0,255)
        self.jump_height = self.jump * 50
        self.max_vel = 200*self.speed
        self.accel = 100*self.speed
        
        #stuff for ai movement
        self.offset = (0, 0)
        self.timer = 100

    def update(self, dt, entities):
        '''Left and right movement'''
        if self.player.rect.centerx > self.rect.centerx: # Right movement
            if abs(self.vel.x) < self.max_vel:
                self.vel.x += abs(self.accel-self.vel.x) * dt
        elif self.player.rect.centerx < self.rect.centerx: # Left movement
            if abs(self.vel.x) < self.max_vel:
                self.vel.x -= abs(self.accel+self.vel.x) * dt
        #control for jumping
        if self.player.rect.y-self.rect.y > 500 or self.vel.x < 0:
            if self.onground:
                self.vel.y -= self.jump_height
            if self.onwall:
                self.vel.y = -self.jump_height
                self.vel.x += self.jump_height * self.onwall
        DynamicObject.update(self, dt, entities)
        
        
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(DynamicObject.to_dictionary(self),
                {'attributes' : [self.mass, self.speed, self.jump]}) 