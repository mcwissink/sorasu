''' CS 108
Created Fall 2016
contains game logic and draw calls
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math,json
import random
import game_object
import button
import utilities
from camera import Camera
from player import Player

class GameState():
    def __init__(self, file_name=None):
        '''
        initiate the game
        '''
        pygame.mouse.set_visible(False) # Make the mouse invisible
        self.gameEntities = [] #blocks and other objects that collide
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        self.buttons = []
        #load the file
        self.file_name = file_name
        if file_name is not None:
            self.load_game(file_name)
        
        self.player = Player(100, -100, [(10,10),(-10,10),(-10,-10),(10,-10)], (255,0,0))
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses
        self.camera = Camera(900, 600, self.player)
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        #send key inputs to player
        self.player.input(self.keys, dt)
        for entity in self.backGroundEntities:
            entity.update(dt)
        for entity in self.gameEntities:
            if (entity.dynamic):
                entity.update(dt, self.gameEntities)
            else:
                entity.update(dt)
        for entity in self.foreGroundEntities:
            entity.update(dt)
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
        handles keyboard events
        '''
        #check for key down
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.keys['up'] = True
            if event.key == pygame.K_DOWN:
                self.keys['down'] = True
            if event.key == pygame.K_LEFT:
                self.keys['left'] = True
            if event.key == pygame.K_RIGHT:
                self.keys['right'] = True
        #check if for key up
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.keys['up'] = False
            if event.key == pygame.K_DOWN:
                self.keys['down'] = False
            if event.key == pygame.K_LEFT:
                self.keys['left'] = False
            if event.key == pygame.K_RIGHT:
                self.keys['right'] = False
        #check if mouse downs
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.mouse.last_click = self.checkButtons(pygame.mouse.get_pos())
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            pygame.mouse.current_button = self.checkButtons(pygame.mouse.get_pos())
            if pygame.mouse.last_click == pygame.mouse.current_button and pygame.mouse.current_button != None:
                pygame.mouse.current_button.onClick(self.switch_state, MenuState())
        
    def checkButtons(self, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in self.buttons:
            if button.rect.collidepoint(mouse):
                return button
    
    
    #for saving and loading the game
    def to_dictionary(self):
        ''' 
        changes the game into a dictionary for saving
        '''
        return {
                'dynamicEntities' : [entity.to_dictionary() for entity in self.gameEntities if entity.dynamic],
                'staticEntities' : [entity.to_dictionary() for entity in self.gameEntities if not entity.dynamic],
                'backGroundEntities' : [scenery.to_dictionary() for scenery in self.backGroundEntities],
                'foreGroundEntities' : [scenery.to_dictionary() for scenery in self.foreGroundEntities]
                }
    def from_dictionary(self, dictionary):
        '''
        load level from a dictionary
        '''
        dynamic = [game_object.DynamicObject(self.texture_cache, **{key: value for (key, value) in i.items()}) for i in dictionary['dynamicEntities']]
        static = [game_object.StaticObject(self.texture_cache, **{key: value for (key, value) in i.items()}) for i in dictionary['staticEntities']]
        self.gameEntities = dynamic + static
        self.scenery_background = [game_object.GameObject(self.texture_cache, **{key: value for (key, value) in i.items()}) for i in dictionary['backGroundEntities']]
        self.scenery_foreground = [game_object.GameObject(self.texture_cache, **{key: value for (key, value) in i.items()}) for i in dictionary['foreGroundEntities']]
    
    def load_game(self, file_name):
        '''
        loads game from text file
        '''
        if file_name is not None:
            with open('../levels/' + file_name +'.txt') as file:
                self.from_dictionary(json.loads(file.read()))