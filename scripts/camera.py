''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''
import pygame, sys

class Camera(object):
    '''
    create a viewport for the game
    '''
    def __init__(self, width, height, target): #http://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame/14357169#14357169
        self.viewport = pygame.Rect(target.rect.x, target.rect.y, width, height)
        self.target = target
    def apply(self, entity):
        '''
        applies camera logic to entities
        '''
        position_x = entity.rect.x - self.viewport.x
        position_y = entity.rect.y - self.viewport.y
        return (position_x, position_y)
    def update(self):
        '''
        updates camera position
        '''
        self.viewport.centerx = self.target.rect.centerx 
        self.viewport.centery = self.target.rect.centery
    def resize(self, screen):
        '''
        resizes the camera
        '''
        screen_size = screen.get_size()
        self.viewport.width = screen_size[0]
        self.viewport.height = screen_size[1]
    