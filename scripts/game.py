''' CS 108
Created Fall 2016
contains game logic and draw calls
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import random
import game_object
from camera import Camera
from player import Player

class GameState():
    def __init__(self):
        '''
        initiate the game
        '''
        pygame.mouse.set_visible(False) # Make the mouse invisible
        self.player = Player(50, -50, 20, 20,(255,255,0), 'rect')
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.gameEntities = [self.player] #blocks and other objects that collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses
        self.camera = Camera(900, 600, self.player)
        test = game_object.StaticObject(100, -50, 50, 10,(0,225,0), 'rect')
        self.gameEntities.append(test)
        for i in range(10):
            test = game_object.StaticObject(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), random.randint(0, 100),(0,225,0), 'rect')
            self.gameEntities.append(test)
    def eventHandler(self, event):
        '''
        Handles keyboard events
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
        
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        #send key inputs to player
        self.player.input(self.keys)
        for entity in self.backGroundEntities:
            entity.update(dt)
        for entity in self.gameEntities:
            if (entity.dynamic):
                entity.update(dt, self.gameEntities)
            else:
                entity.update(dt)
        for entity in self.foreGroundEntities:
            entity.update(dt)
        self.camera.update()
    def draw(self, draw, screen):
        '''
        loop through objects and draw them
        '''
        screen.fill(pygame.Color(0, 0, 0))
        for entity in self.backGroundEntities:
            entity.draw(screen, self.camera)
        for entity in self.gameEntities:
            entity.draw(screen, self.camera)
        for entity in self.foreGroundEntities:
            entity.draw(screen, self.camera)