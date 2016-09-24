''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import physics

#base class for all object in game
class GameObject(object):
    def __init__(self, x, y, width, height, color, mask):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.dynamic = False
        self.mask = mask
        self.rect = pygame.Rect(x, y, width, height)
        self.corners = [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]
    def update(self, dt):
        self.corners = [self.rect.topleft, self.rect.topright, self.rect.bottomleft, self.rect.bottomright]
        self.rect.x = self.x
        self.rect.y = self.y
    def draw(self, screen, camera):
        position = camera.apply(self)
        pygame.draw.rect(screen, self.color, (position[0], position[1], self.width, self.height))

#includes any objects that are simply scenery
class StaticObject(GameObject):
    def __init__(self, x, y, width, height, color, mask):
        GameObject.__init__(self, x, y, width, height, color, mask)
    def update(self, dt):
        GameObject.update(self, dt)
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)

#includes any objects that collide with player
class DynamicObject(GameObject):
    def __init__(self, x, y, width, height, color, mask):
        GameObject.__init__(self, x, y, width, height, color, mask)
        self.dynamic = True 
        self.vel = pygame.math.Vector2(0,0)
        self.old_vel = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(x,y)
        self.grounded = 0
    def update(self, dt, entities):
        self.pos += (self.old_vel + self.vel) * 0.5 * dt
        self.grounded = 0
        for entity in entities:
            if physics.collide(self, entity):
                print('collision')
        self.x = self.pos.x
        self.y = self.pos.y
        GameObject.update(self, dt)
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)