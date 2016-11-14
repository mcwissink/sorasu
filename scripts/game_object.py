''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import physics
import utilities

#base class for all object in game
class GameObject(object):
    #these are the parameters that you can edit in the editor
    def __init__(self, x, y, offsets):
        self.type = 'scenery'
        self.color = (0,0,0)
        self.dynamic = False
        self.offsets = offsets
        self.select_offset = (0, 0) #used for dragging
        #this is a collision bounding box for select and improved collision checks
        x_offsets = [offset[0] for offset in offsets]
        y_offsets = [offset[1] for offset in offsets]
        self.rect = pygame.Rect(x ,y ,max(x_offsets), max(y_offsets))
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
    def to_dictionary(self):
        '''creates a dictionary of variables for saving'''
        return {
                'x' : self.rect.x, 
                'y': self.rect.y,
                'offsets' : self.offsets
               }

#includes any objects that are simply scenery
class StaticObject(GameObject):
    #these are the parameters that you can edit in the editor
    ATTRIBUTES = {'Friction':0.1}
    def __init__(self, x, y, offsets, friction=0.1):
        GameObject.__init__(self, x, y, offsets)
        self.type = 'static'
        self.friction = friction
    def update(self, dt):
        pass
    def draw(self, screen, camera):
        GameObject.draw(self, screen, camera)
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Static Objects''' 
        #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {
                'friction' : self.friction})

#includes any objects that collide with player
class DynamicObject(GameObject):
    #these are the parameters that you can edit in the editor
    ATTRIBUTES = {'Mass':10}
    #create universal gravity constant
    GRAVITY = 100
    def __init__(self, x, y, offsets, mass=10):
        GameObject.__init__(self, x, y, offsets)
        self.spawn = (x, y)
        self.type = 'dynamic'
        self.dynamic = True 
        self.vel = pygame.math.Vector2(0,0)
        self.old_vel = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(x,y)
        self.mass = mass
        self.grav = self.GRAVITY*self.mass
        self.fric = pygame.math.Vector2(0.01,0.01)
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
                        res_vec = pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
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
    
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {
                'mass' : self.mass})
    def reset(self):
        '''resets the variable and sends it to the spawn point'''
        self.vel *= 0
        self.rect.x = self.spawn[0]
        self.rect.y = self.spawn[1]
        self.pos[0] = self.rect.x
        self.pos[1] = self.rect.y