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
        '''base init for all entities'''
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
        '''base update - other objects expand on this'''
        pass
    def draw(self, screen, camera):
        '''basic draw function'''
        #translates points and draws polygon
        translate_points = camera.apply(self.get_corners())
        pygame.draw.polygon(screen, self.color, translate_points, 0)
    def debug_draw(self, screen, camera):
        '''debug draw for eraser tool'''
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
    ATTRIBUTES = [{'name': 'Friction', 'init': 1, 'max': 2, 'min': 0, 'step': 0.1}]
    def __init__(self, x, y, offsets, attributes):
        '''Static Objects are used for platforms - they don't move'''
        GameObject.__init__(self, x, y, offsets)
        self.friction = attributes[0]
        self.type = 'static'
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Static Objects''' 
        #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {
                'attributes' : [self.friction]})

#includes any objects that are simply scenery
class SceneryObject(GameObject):
    #these are the parameters that you can edit in the editor
    ATTRIBUTES = [{'name': 'Parallax X', 'init': 1, 'max': 2, 'min': 0, 'step': 0.01}, #always make sure parallax is first
                  {'name': 'Parallax Y', 'init': 1, 'max': 2, 'min': 0, 'step': 0.01}, #always make sure parallax is first
                  {'name': 'Scale', 'init': 0.1, 'max': 5, 'min': 0, 'step': 0.1}]
    def __init__(self, x, y, offsets, attributes):
        '''scenery objects are for effects and stuff'''
        GameObject.__init__(self, x, y, offsets)
        self.parallax_x = attributes[0]
        self.parallax_y  = attributes[1]
        self.scale = attributes[2]
        self.type = 'scenery'
        if self.parallax_x <= 1:
            color_adjust = 255-255*self.parallax_x
        else:
            color_adjust = 0
        self.color = (color_adjust,color_adjust,color_adjust)
    def draw(self, screen, camera):
        '''draw function with parallax'''
        #translates points and draws polygon
        translate_points = camera.apply(self.get_corners(), (self.parallax_x, self.parallax_y))
        pygame.draw.polygon(screen, self.color, translate_points, 0)
    
    def debug_draw(self, screen, camera):
        '''debug draw with parallax'''
        #translates points and draws rect
        position = camera.apply_single((self.rect.x, self.rect.y), (self.parallax_x, self.parallax_y))
        pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.rect.width, self.rect.height), 2)
        
    def get_alpha_surface(self, surface, alpha=120, red=255, green=255, blue=255, mode=pygame.BLEND_RGBA_MULT):
        """    
        Allocate a new surface with user-defined values (0-255)
        for red, green, blue and alpha.
        http://www.pygame.org/docs/ref/surface.html for the different blend modes
        Thanks to Claudio Canepa <ccanepacc@gmail.com>.
        """
        blend = pygame.Surface(surface.get_size(), pygame.SRCALPHA, 32)
        blend.fill((red,green,blue,alpha))
        blend.blit(surface, (0,0), surface.get_rect(), mode)
        return blend
    
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Static Objects''' 
        #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {
                'attributes' : [self.parallax_x, self.parallax_y, self.scale]})

#includes any objects that collide with player
class DynamicObject(GameObject):
    #these are the parameters that you can edit in the editor
    ATTRIBUTES = [{'name': 'Mass', 'init': 10, 'max': 100, 'min': 1, 'step': 1}]
    #create universal gravity constant
    GRAVITY = 2000
    def __init__(self, x, y, offsets, attributes):
        '''Dynamic Objects move and collide - parent of the player'''
        GameObject.__init__(self, x, y, offsets)
        #set variables
        self.mass = attributes[0]
        self.friction = 1
        self.inv_mass = 1/self.mass
        self.spawn = (x, y)
        self.type = 'dynamic'
        self.dynamic = True 
        self.vel = pygame.math.Vector2(0,0)
        self.pos = pygame.math.Vector2(x,y)
        self.grav = self.GRAVITY
        self.bounce = 0.5
        self.air_fric = 0.5
        self.fric = 0
        self.collision_ground = False #flag for collisions
        self.collision_wall = False #flag for collisions
        self.onground = False
        self.onwall = 0
        #adjust collision
        self.adjust_collision()
        
    def update(self, dt, entities):
        '''updates and applies physics'''
        #move the character
        self.pos += self.vel * 0.5 * dt
        if abs(self.vel.x) > 0.1:
            self.vel.x -= math.copysign(1, self.vel.x) * self.fric
        else:
            self.vel.x = 0
        self.vel.y += self.grav * dt #halfs the gravity if on wall
        self.move()
        #physics check
        self.collision_ground = False
        self.collision_wall = False
        for entity in entities:
            if entity != self:
                if self.wall_rect.colliderect(entity):
                    self.collision_wall = True
                if self.rect.colliderect(entity):
                    if physics.collide_test(self, entity):
                        self.collision_ground = True
                    vec = physics.collide(self, entity)
                    if vec:
                        self.pos -= vec
                        self.move()
                        #correct the velocity based on the vec return --- Nathan Brink
                        res_vec = pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
                        if entity.dynamic:
                            phy_vec = physics.resolve_collision(self, entity)
                            if not phy_vec:
                                self.vel -= res_vec
                        else:
                            self.vel -= res_vec
                        if res_vec[1] > 0:
                            self.onground = True
                            self.fric = entity.friction
                        else:
                            if res_vec[0] < 0:
                                self.onwall = 1
                            else:
                                self.onwall = -1
        if not self.collision_ground:
            #reset ground variables if there is no collision 
            self.fric = self.air_fric
            self.onground = False
        if not self.collision_wall or self.onground:
            #reset wall variables if not wall collision
            self.onwall = 0

    def move(self):
        '''moves the object'''
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.wall_rect.centerx = self.rect.centerx
        self.wall_rect.centery = self.rect.centery
    
    def reset(self):
        '''resets the variable and sends it to the spawn point'''
        self.vel *= 0
        self.rect.x = self.spawn[0]
        self.rect.y = self.spawn[1]
        self.pos[0] = self.rect.x
        self.pos[1] = self.rect.y
    
    def adjust_collision(self):
        ''''inflate the rect for reading of onground and onwall'''
        self.rect.height += 2
        #setup a new rectangle for wall collision check
        self.wall_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width+6, 3)
        self.test_offset = self.offsets[:]
        for i in range(len(self.test_offset)):
            self.test_offset[i] = (self.test_offset[i][0], self.test_offset[i][1]+2) 
    
    def get_corners_test(self):
        '''get corners for the floor check'''
        return [(self.rect.x + offset[0], self.rect.y + offset[1]) for offset in self.test_offset]
    
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {
                'attributes' : [self.mass]})        