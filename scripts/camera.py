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
        self.viewport = pygame.Rect(0, 0, width, height)
        self.target = target
    def apply(self, points):
        '''
        applies camera logic to multiple points
        '''
        for i in range(len(points)):
            points[i] = (points[i][0] - self.viewport.x, points[i][1] - self.viewport.y)
        return points
    def apply_single(self, point):
        '''
        applies camera logic to single point
        '''
        translate_point = (point[0] - self.viewport.x, point[1] - self.viewport.y)
        return translate_point
    
    def apply_inverse(self, mouse):
        '''
        applies camera logic to entities
        '''
        position_x = mouse[0] + self.viewport.x
        position_y = mouse[1] + self.viewport.y
        return (position_x, position_y)
    
    def update(self, keys, dt):
        '''
        updates camera position
        '''
        if self.target == 'free':
            '''Left and right movement'''
            if keys['right'] and not keys['left']: # Right movement
                self.viewport.centerx += 1000 * dt
            elif keys['left'] and not keys['right']: # Left movement
                self.viewport.centerx -= 1000 * dt
            '''Up and down movement'''
            if keys['up'] and not keys['down']: # Jump, wall jump 
                self.viewport.centery -= 1000 * dt
            elif keys['down'] and not keys['up']: # Fall faster when user is pressing down
                self.viewport.centery += 1000 * dt
        else:
            self.viewport.centerx = self.target.rect.centerx 
            self.viewport.centery = self.target.rect.centery

    def resize(self, screen):
        '''
        resizes the camera
        '''
        screen_size = screen.get_size()
        self.viewport.width = screen_size[0]
        self.viewport.height = screen_size[1]
    