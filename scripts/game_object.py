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
    def __init__(self, x, y, offsets, color):
        self.color = color
        self.dynamic = False
        self.offsets = offsets
        self.select_offset = (0, 0) #used for dragging
        '''fix this because x and y dont update'''
        #this is a collision bounding box set in the editor script
        self.rect = pygame.Rect(x ,y ,0 , 0)
    def update(self, dt):
        pass
    def draw(self, screen, camera):
        #translates points and draws polygon
        translate_points = camera.apply(self.get_corners())
        pygame.draw.polygon(screen, self.color, translate_points, 0)
    def debug_draw(self, screen, camera):
        #translates points and draws rect
        position = camera.apply_single((self.rect.x, self.rect.y))
        pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.rect.width, self.rect.height), 2)
    def get_corners(self):
        '''apply offsets from x and y'''
        return [(self.rect.x + offset[0], self.rect.y + offset[1]) for offset in self.offsets]

#includes any objects that are simply scenery
class StaticObject(GameObject):
    def __init__(self, x, y, offsets, color):
        GameObject.__init__(self, x, y, offsets, color)
    def update(self, dt):
        pass
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)

#includes any objects that collide with player
class DynamicObject(GameObject):
    def __init__(self, x, y, offsets, color):
        GameObject.__init__(self, x, y, offsets, color)
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
                if self.rect.colliderect(entity): #Doesn't work is shape has negative values for width and height
                    vec = physics.collide(self, entity)
                    if vec:
                        self.pos -= vec
                        self.rect.x = self.pos.x
                        self.rect.y = self.pos.y
                        
                        #correct the velocity based on the vec return --- Nathan Brink
                        res_vec = self.bounce * pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
                        self.vel -= res_vec
                        if entity.dynamic:
                            entity.vel += res_vec
                        if res_vec[1] > 0:
                            self.onground = True
                        elif res_vec[1] == 0 :
                            if res_vec[0] < 0:
                                self.onwall = 1
                            else:
                                self.onwall = -1
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)