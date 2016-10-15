''' CS 108
Created Fall 2016
contains game logic and draw calls
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import random
import game_object
import button
from camera import Camera
from player import Player

class EditorState():
    def __init__(self):
        '''
        initiate the game
        '''
        self.switch_state = 0
        pygame.mouse.set_visible(True) # Make the mouse invisible
        self.buttons = [] #containter for buttons
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.gameEntities = [] #blocks and other objects that collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses
        self.camera = Camera(900, 600, 'free')
        #drawing variables
        self.init_mouse_x = self.init_mouse_y = 0
        self.current_draw = None
        self.end_draw = False
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        if self.end_draw:
            mouse = self.camera.apply_inverse(pygame.mouse.get_pos())
            self.current_draw.rect.size = (mouse[0] - self.init_mouse_x, mouse[1] - self.init_mouse_y)
        self.camera.update(self.keys, dt)
        
    def draw(self, draw, screen):
        '''
        loop through objects and draw them
        '''
        screen.fill(pygame.Color(255, 255, 255))
        for entity in self.backGroundEntities:
            entity.draw(screen, self.camera)
        for entity in self.gameEntities:
            entity.draw(screen, self.camera)
        for entity in self.foreGroundEntities:
            entity.draw(screen, self.camera)
        for entity in self.buttons:
            entity.draw(screen)
        
    def eventHandler(self, event):
        '''
        handles user inputs
        '''
        #check for key down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.keys['up'] = True
            if event.key == pygame.K_s:
                self.keys['down'] = True
            if event.key == pygame.K_a:
                self.keys['left'] = True
            if event.key == pygame.K_d:
                self.keys['right'] = True
        #check if for key up
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.keys['up'] = False
            if event.key == pygame.K_s:
                self.keys['down'] = False
            if event.key == pygame.K_a:
                self.keys['left'] = False
            if event.key == pygame.K_d:
                self.keys['right'] = False
        #check if mouse downs
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.init_mouse_x, self.init_mouse_y = self.camera.apply_inverse(pygame.mouse.get_pos())
            pygame.mouse.last_click = self.checkButtons(pygame.mouse.get_pos())
            if not self.end_draw:
                draw_entity = game_object.StaticObject(self.init_mouse_x, self.init_mouse_y, 0, 0,(0,0,0))
                self.current_draw = draw_entity
                self.gameEntities.append(draw_entity)
                self.end_draw = True
            else:
                self.end_draw = False
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            pygame.mouse.current_button = self.checkButtons(pygame.mouse.get_pos())
    
    def checkButtons(self, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in self.buttons:
            if button.rect.collidepoint(mouse):
                return button