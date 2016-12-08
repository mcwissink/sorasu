''' CS 108
Created Fall 2016
camera class for a viewport
@author: Mark Wissink (mcw33)
'''
import pygame, sys

class Camera(object):
    def __init__(self, width, height, target): #http://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame/14357169#14357169
        '''create a viewport for the gam'''
        self.viewport = pygame.Rect(0, 0, width, height)
        try:
            self.target = target
        except:
            self.target = 0
    def apply(self, points, parallax=1):
        '''position relative to parallax'''
        for i in range(len(points)):
            translate_x = points[i][0] - self.viewport.x * parallax + self.viewport.width//2
            translate_y = points[i][1] - self.viewport.y * parallax + self.viewport.height//2
            points[i] = (translate_x, translate_y)
        return points

    def apply_single(self, point, parallax=1):
        '''applies camera logic to single point'''
        translate_x = point[0] - self.viewport.x * parallax + self.viewport.width//2
        translate_y = point[1] - self.viewport.y * parallax + self.viewport.height//2
        return (int(translate_x), int(translate_y))
    
    def apply_inverse(self, mouse, parallax=1):
        '''applies camera logic to entities'''
        translate_x = mouse[0] + self.viewport.x * parallax - self.viewport.width//2
        translate_y = mouse[1] + self.viewport.y * parallax - self.viewport.height//2
        return (int(translate_x), int(translate_y))

    def update(self, keys, dt):
        '''updates camera position'''
        if self.target == 0: #free movement
            '''Left and right movement'''
            if keys['right'] and not keys['left']: # Right movement
                self.viewport.x += 1000 * dt
            elif keys['left'] and not keys['right']: # Left movement
                self.viewport.x -= 1000 * dt
            '''Up and down movement'''
            if keys['up'] and not keys['down']: # Up movement
                self.viewport.y -= 1000 * dt
            elif keys['down'] and not keys['up']: # Down movement
                self.viewport.y += 1000 * dt
        elif self.target == 1: #fixed
            self.viewport.x = 0
            self.viewport.y = 0
        else:
            self.viewport.x = self.target.rect.centerx
            self.viewport.y = self.target.rect.centery

    def resize(self, screen):
        '''resizes the camera'''
        screen_size = screen.get_size()
        self.viewport.width = screen_size[0]
        self.viewport.height = screen_size[1]
    