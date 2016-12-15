''' CS 108
Created Fall 2016
child of DynamicObject that the user can control
@author: Mark Wissink (mcw33)
'''
import pygame, sys, math
import utilities
from game_object import DynamicObject
from pygame.tests import camera_test

class Player(DynamicObject):
    def __init__(self, x, y, offsets, attributes):
        ''' Player game object for moving your character around'''
        DynamicObject.__init__(self, x, y, offsets, attributes)
        self.type = 'player'
        self.color = (100,0,0)
        self.max_vel = 3000
        self.accel = 2000
        self.past_up = self.past_down = self.past_left = self.past_right = True # Past key presses
        self.dash_time = 15 #time spend dashing
        self.dash_cool_down = 100 #time until dash can be used
        self.dash_timer = 0 #timer for dash
        self.dash_boost = 2000 #amount of boost recieved
        self.can_dash = True
        self.deadly = False
        self.health = 25
        
    def input(self, keys, dt):
        '''Takes input to check for keypresses(dictionary)'''  
        '''Left and right movement'''
        dashed = False
        if keys['dash'] and self.can_dash:
            dashed = True
        if keys['right'] and not keys['left']: # Right movement
            if dashed:
                self.dash(1,0)
            elif abs(self.vel.x) < self.max_vel:
                self.vel.x += abs(self.accel-self.vel.x) * dt
        elif keys['left'] and not keys['right']: # Left movement
            if dashed:
                self.dash(-1,0)
            elif abs(self.vel.x) < self.max_vel:
                self.vel.x -= abs(self.accel+self.vel.x) * dt
        '''Up and down movement'''
        if keys['up'] and not keys['down']: # Jump, wall jump
            if dashed:
                self.dash(0, -1)
            elif not self.past_up:
                if self.onground:
                    self.vel.y -= 1000
                elif self.onwall:
                    self.vel.y = -1000
                    self.vel.x += 1000 * self.onwall
        elif keys['down'] and not keys['up']: # Fall faster when user is pressing down
            if dashed:
                self.dash(0, 1)
            else:
                self.vel.y += 3000 *dt
        #Store past key presses
        self.past_up = True if (keys['up']) else False
        self.past_down = True if (keys['down']) else False
        self.past_left = True if (keys['left']) else False
        self.past_right = True if (keys['right']) else False
        self.past_dash = True if (keys['dash']) else False
        
    def update(self, dt, entities):
        '''update the player and the time for dash'''            
        DynamicObject.update(self, dt, entities)
        if self.dash_timer < 0: #if the timer is zero
            if self.deadly: #on dash cooldown
                self.color = (100,0,0) #revert to old color
                self.deadly = False
                self.vel.x *= 0.2 #slow player down
                self.vel.y *= 0.2
                self.dash_timer = self.dash_cool_down
            else: #reset can dash
                self.can_dash = True
        else:
            self.dash_timer -= 100 * dt #tie the timer to real time
    
    def draw(self, screen, camera):
        DynamicObject.draw(self, screen, camera)
        #draw the health bar and dash bar
        pygame.draw.rect(screen, (200,0,0), (10, 10, max(0, 100 * (self.health/25)), 10), 0)
        pygame.draw.rect(screen, (0,0,0), (10, 10, 100, 10), 2)
        pygame.draw.rect(screen, (0,0,200), (10, 30, 100/(1+(self.dash_timer/self.dash_cool_down)), 10), 0)
        pygame.draw.rect(screen, (0,0,0), (10, 30, 100, 10), 2) 
        
    def dash(self, x=0, y=0):
        '''dashes the character in a direction, its is also an attack'''
        if x:
            self.vel.x = self.dash_boost * x
            self.vel.y = 0
        if y:
            self.vel.y = self.dash_boost * y
            self.vel.x = 0
        self.can_dash = False
        self.deadly = True
        self.color = self.color = (255,0,0)
        self.dash_timer = self.dash_time   
    
    def on_collide(self, entities, entity):
        '''called on collision'''
        if entity.type == 'enemy':
            if self.deadly and not entity.frozen: #kill enemy
                entities.remove(entity)
            else: #reduce health otherwise
                self.health -= 1
               
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(DynamicObject.to_dictionary(self),
                {})