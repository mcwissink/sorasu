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
import textbox
from camera import Camera
from player import Player
from enemy import Enemy

class GameState():
    def __init__(self, file_name=None): 
        '''initiate the game'''
        pygame.mouse.set_visible(False) # Make the mouse invisible
        self.gameEntities = [] #blocks and other objects that collide
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        button.buttons_init(self) #initialize the button class
        #load the file
        self.player = None
        self.file_name = file_name
        if file_name is not None:
            self.load_game(file_name)
            self.camera = Camera(900, 600, self.player)
            self.camera.resize(pygame.display.get_surface())
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses

    def update(self, dt):
        '''loop through objects and run logic'''
        #update the buttons
        button.buttons_update(self, self.buttons)
        #send key inputs to player
        self.player.input(self.keys, dt)
        for entity in self.backGroundEntities:
            entity.update(dt)
        for entity in self.gameEntities:
            if entity.dynamic:
                entity.update(dt, self.gameEntities)
            else:
                entity.update(dt)
        for entity in self.foreGroundEntities:
            entity.update(dt)
        #update the camera
        self.camera.update(self.keys, dt)

    def draw(self, draw, screen):
        '''loop through objects and draw them'''
        screen.fill(pygame.Color(255, 255, 255))
        for entity in self.backGroundEntities:
            entity.draw(screen, self.camera)
        for entity in self.gameEntities:
            entity.draw(screen, self.camera)
        for entity in self.foreGroundEntities:
            entity.draw(screen, self.camera)

    def eventHandler(self, event):
        '''handles input events'''
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
            button.buttons_mousedown(self, self.buttons)
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            button.buttons_mouseup(self, self.buttons)
    
    #function for initializing the menu
    def initialize_menu(self):
        '''initializes the menu and the variables needed for it'''
        #create the textbox for naming
        self.button_font_big = pygame.font.SysFont(None, 40)
        self.button_font_small = pygame.font.SysFont(None, 20)
        self.textbox = textbox.TextBox(10, 10, 180, 0, self.button_font_big, (0.5,0.5)) # height will be set in the init
        #saves the game
        self.playButton = button.Button(-100, 100, self.button_font_big, (255,255,255), 100, 'Play', (0.5,0.5))
        def onPlayClick():
            pass
        self.playButton.onClick = onPlayClick
        self.playButton.realign(self.camera)
        self.buttons.append(self.playButton)
        #saves the game
        self.backButton = button.Button(100, 100, self.button_font_big, (255,255,255), 100, 'Back', (0.5,0.5))
        def onBackClick():
            pass
        self.pauseButton.onClick = onBackClick
        self.pauseButton.realign(self.camera)
        self.buttons.append(self.pauseButton)
        
    def draw_menu(self, screen):
        '''draws the menu'''
        #draw background of the side bar
        self.menu_back.height = screen.get_size()[1]
        pygame.draw.rect(screen, (0,0,0), self.menu_back)
        self.textbox.draw(screen)
        button.buttons_draw(self, screen, self.buttons)

    #for saving and loading the game
    def to_dictionary(self):
        ''' changes the game into a dictionary for saving'''
        return {
                'player' : self.player.to_dictionary(),
                'enemies' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'enemy'],
                'dynamicEntities' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'dynamic'],
                'staticEntities' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'static'],
                'backGroundEntities' : [scenery.to_dictionary() for scenery in self.backGroundEntities],
                'foreGroundEntities' : [scenery.to_dictionary() for scenery in self.foreGroundEntities]
                }
    def from_dictionary(self, dictionary):
        '''load level from a dictionary'''
        self.player = Player(**{key: value for (key, value) in dictionary['player'].items()})
        enemies = [Enemy(**{key: value for (key, value) in i.items()}) for i in dictionary['enemies']]
        for enemy in enemies: #no other way to reference player
            enemy.player = self.player
        dynamic = [game_object.DynamicObject(**{key: value for (key, value) in i.items()}) for i in dictionary['dynamicEntities']]
        static = [game_object.StaticObject(**{key: value for (key, value) in i.items()}) for i in dictionary['staticEntities']]
        self.gameEntities = dynamic + static + enemies
        self.gameEntities.append(self.player)
        self.backGroundEntities = [game_object.SceneryObject(**{key: value for (key, value) in i.items()}) for i in dictionary['backGroundEntities']]
        self.foreGroundEntities = [game_object.SceneryObject(**{key: value for (key, value) in i.items()}) for i in dictionary['foreGroundEntities']]
    
    def load_game(self, file_name):
        '''loads game from text file'''
        if file_name is not None:
            with open('../levels/' + file_name +'.txt') as file:
                self.from_dictionary(json.loads(file.read()))