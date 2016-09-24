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
    def __init__(self, x, y, width, height, color):
        self.color = color
        self.dynamic = False
        self.rect = pygame.Rect(x, y, width, height)
    def update(self, dt):
        pass
    def draw(self, screen, camera):
        position = camera.apply(self)
        pygame.draw.rect(screen, self.color, (position[0], position[1], self.rect.width, self.rect.height))
    def get_corners(self):
        return [self.rect.topleft, self.rect.topright, self.rect.bottomright, self.rect.bottomleft]
#includes any objects that are simply scenery
class StaticObject(GameObject):
    def __init__(self, x, y, width, height, color):
        GameObject.__init__(self, x, y, width, height, color)
    def update(self, dt):
        GameObject.update(self, dt)
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)

#includes any objects that collide with player
class DynamicObject(GameObject):
    def __init__(self, x, y, width, height, color):
        GameObject.__init__(self, x, y, width, height, color)
        self.dynamic = True 
        self.grav = 1
        self.vel = pygame.math.Vector2(0,0)
        self.old_vel = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(x,y)
        self.fric = pygame.math.Vector2(0.01,0.01)
    def update(self, dt, entities):
        #update the corners array
        self.pos += (self.old_vel + self.vel) * 0.5 * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        GameObject.update(self, dt)
        for entity in entities:
            if entity != self:
                vec = physics.collide(self, entity)
                if vec:
                    self.pos -= vec
                    self.rect.x = self.pos.x
                    self.rect.y = self.pos.y
                    
                    #correct the velocity based on the vec return --- Nathan Brink
                    self.vel -= pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
                    
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)