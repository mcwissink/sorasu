''' CS 108
Created Fall 2016
Objects used in game
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
                {'attributes' : [self.friction]})

#includes any objects that are simply scenery
class SceneryObject(GameObject):
    #these are the parameters that you can edit in the editor
    ATTRIBUTES = [{'name': 'Parallax', 'init': 1, 'max': 2, 'min': 0, 'step': 0.01},
                  {'name': 'Scale', 'init': 1, 'max': 2, 'min': 0.1, 'step': 0.1},
                  {'name': 'Rotation', 'init': 0, 'max': 360, 'min': 0, 'step': 5},
                  {'name': 'Image', 'init': -1, 'max': 4, 'min': -1, 'step': 1}] #always make sure parallax is first
    def __init__(self, texture_cache, x, y, offsets, attributes):
        '''scenery objects are for effects and stuff'''
        GameObject.__init__(self, x, y, offsets)
        self.parallax = attributes[0]
        self.scale = attributes[1]
        self.rotation = attributes[2]
        self.image_dir = attributes[3]
        #setup image
        self.hasImage = True
        if type(self.image_dir).__name__ == 'int':
            if self.image_dir == -1:
                self.hasImage = False
            else:
                self.image_dir = texture_cache.image_list[self.image_dir]
        if self.hasImage:
            surface = texture_cache.load(self.image_dir)
            width, height = surface.get_size()
            self.rect.width = int(width * self.scale)
            self.rect.height = int(height * self.scale)
            surface = pygame.transform.scale(surface, (self.rect.width, self.rect.height))
            surface = pygame.transform.rotate(surface, self.rotation)
            self.image = surface
        self.type = 'scenery'
        if self.parallax <= 1:
            color_adjust = 255-255*self.parallax
        else:
            color_adjust = 0
        self.color = (color_adjust,color_adjust,color_adjust)
        if self.hasImage:
            self.image = self.colorize(self.color)
        
    def draw(self, screen, camera):
        '''draw function with parallax'''
        #translates points and draws polygon
        if self.hasImage:
            translate = camera.apply_single((self.rect.x, self.rect.y), self.parallax)
            screen.blit(self.image, translate)
        else:   
            translate_points = camera.apply(self.get_corners(), self.parallax)
            pygame.draw.polygon(screen, self.color, translate_points, 0)
    
    def debug_draw(self, screen, camera):
        '''debug draw with parallax'''
        #translates points and draws rect
        position = camera.apply_single((self.rect.x, self.rect.y), self.parallax)
        pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.rect.width, self.rect.height), 2)
        
    def colorize(self, newColor):
        """
        Create a "colorized" copy of a surface (replaces RGB values with the given color, preserving the per-pixel alphas of
        original).
        :param image: Surface to create a colorized copy of
        :param newColor: RGB color to use (original alpha values are preserved)
        :return: New colorized Surface instance
        """
        surface = self.image.copy()
    
        # zero out RGB values
        surface.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
        # add in new RGB values
        surface.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)
    
        return surface
    
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Static Objects''' 
        #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {'attributes' : [self.parallax, self.scale, self.rotation, self.image_dir]})

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
        self.frozen = False
        #adjust collision
        self.adjust_collision()
        
    def update(self, dt, entities):
        '''updates and applies physics'''
        if self.frozen: #dont do anything
            return
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
                        self.on_collide(entities, entity)
                        self.pos -= vec
                        self.move()
                        #correct the velocity based on the vec return --- Nathan Brink
                        res_vec = pygame.math.Vector2(physics.normalize(vec)) * physics.dot_product(physics.normalize(vec), self.vel)
                        if entity.dynamic and not res_vec[1] > 0:
                            phy_vec = physics.resolve_collision(self, entity)
                            if not phy_vec: #sometimes phy_vec returns false
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
    def on_collide(self, entities, entity):
        '''called when object collides'''
        pass

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
        self.rect.height += 4
        #setup a new rectangle for wall collision check
        self.wall_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width+6, 6)
        self.test_offset = self.offsets[:]
        for i in range(len(self.test_offset)):
            self.test_offset[i] = (self.test_offset[i][0], self.test_offset[i][1]+2) 
    
    def get_corners_test(self):
        '''get corners for the floor check'''
        return [(self.rect.x + offset[0], self.rect.y + offset[1]) for offset in self.test_offset]
    
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {'attributes' : [self.mass]})        