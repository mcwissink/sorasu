''' CS 108
Created Fall 2016
child of DynamicObject that attacks player
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
                  {'name': 'Speed', 'init': 10, 'max': 50, 'min': 0, 'step': 1},
                  {'name': 'Jump', 'init': 10, 'max': 30, 'min': 1, 'step': 1},
                  {'name': 'Engage', 'init': 10, 'max': 50, 'min': 1, 'step': 1}]
    def __init__(self, x, y, offsets, attributes):
        DynamicObject.__init__(self, x, y, offsets, attributes)
        self.speed = attributes[1]
        self.jump = attributes[2]
        self.engage = attributes[3]
        self.type = 'enemy'
        self.color = (0,0,255)
        self.jump_height = self.jump * 50
        self.max_vel = 200*self.speed
        self.accel = 100*self.speed
        self.radius = self.engage * 100
        #stuff for ai movement
        self.offset = (0, 0)
        self.timer = 100
        if self.speed == 0:
            self.frozen = True
        
    def update(self, dt, entities):
        '''updates the enemy'''
        DynamicObject.update(self, dt, entities)
        #self.player is set in the level load function
        if abs(self.player.rect.centerx - self.rect.centerx) < self.radius:
            '''Left and right movement'''
            if self.player.rect.centerx > self.rect.centerx: # Right movement
                if abs(self.vel.x) < self.max_vel:
                    self.vel.x += abs(self.accel-self.vel.x) * dt
            elif self.player.rect.centerx < self.rect.centerx: # Left movement
                if abs(self.vel.x) < self.max_vel:
                    self.vel.x -= abs(self.accel+self.vel.x) * dt
            '''jumping movement'''
            if self.player.rect.y-self.rect.y > 500 or self.vel.x < 0:
                if self.onground:
                    self.vel.y -= self.jump_height
                if self.onwall:
                    self.vel.y = -self.jump_height
                    self.vel.x += self.jump_height * self.onwall
    
    def on_collide(self, entities, entity):
        '''called on collision'''
        if entity.type == 'player':
            if self.player.deadly: #kill enemy
                entities.remove(self)
            else: #reduce health otherwise
                self.player.health -= 1
  
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(DynamicObject.to_dictionary(self),
                {'attributes' : [self.mass, self.speed, self.jump, self.engage]}) 