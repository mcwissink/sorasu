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
        #this is a collision bounding box
        self.rect = pygame.Rect(x, y, width, height)
    def update(self, dt):
        pass
    def draw(self, screen, camera):
        position = camera.apply((self.rect.x, self.rect.y))
        #pygame.draw.polygon(screen, self.color, [camera.apply(self.points[0]), camera.apply(self.points[1]), camera.apply(self.points[2])], 0)
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
        self.vel = pygame.math.Vector2(0,0)
        self.old_vel = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(x,y)
        self.grav = 1500
        self.fric = pygame.math.Vector2(0.01,0.01)
        self.bounce = 1
        self.onground = False
        self.onwall = 0
    def update(self, dt, entities):
        #reset variables
        self.onground = False
        self.onwall = 0
        #move the character
        self.vel.y += self.grav * dt
        self.pos += (self.old_vel + self.vel) * 0.5 * dt
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        GameObject.update(self, dt)
        #physics check
        for entity in entities:
            if entity != self:
                if self.rect.colliderect(entity):
                    vec = physics.collide(self, entity)
                    if vec:
                        self.pos -= vec
                        self.rect.x = self.pos.x
                        self.rect.y = self.pos.y
                        
                        #correct the velocity based on the vec return --- Nathan Brink
                        res_vec = self.bounce * pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
                        self.vel -= res_vec
                        if res_vec[1] > 0:
                            self.onground = True
                        elif res_vec[1] == 0 :
                            if res_vec[0] < 0:
                                self.onwall = 1
                            else:
                                self.onwall = -1
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)