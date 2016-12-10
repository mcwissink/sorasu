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
from door import Door

class GameState():
    def __init__(self, states): 
        '''initiate the game'''
        self.states = states
        self.gameEntities = [] #blocks and other objects that collide
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        button.buttons_init(self) #initialize the button class
        #setup game stuff
        self.camera = Camera(900, 600, 0)
        self.camera.resize(pygame.display.get_surface())
        self.pause = True
        self.player = None
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses

        self.initialize_menu()#initialize the menu
                
    def update(self, dt):
        '''loop through objects and run logic'''
        #update the buttons
        button.buttons_update(self, self.buttons)
        #send key inputs to player
        if not self.pause:
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
        self.draw_menu(screen)
        
    def eventHandler(self, event):
        '''handles input events'''
        #check for key down
        if self.pause:
            if self.textbox.active:
                self.textbox.key_in(event)
        else:
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

        if event.type == pygame.MOUSEBUTTONDOWN:
            button.buttons_mousedown(self, self.buttons)
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            #text box check
            if self.pause:
                if self.textbox.rect.collidepoint(pygame.mouse.get_pos()):
                    self.textbox.active = True
                else:
                    self.textbox.active = False
            return button.buttons_mouseup(self, self.buttons)
            
    
    #function for initializing the menu
    def initialize_menu(self):
        '''initializes the menu and the variables needed for it'''
        #create the textbox for naming
        self.menu_back = pygame.Rect(0, 0, 400, 400) # x and y will get set in the draw method
        self.button_font_big = pygame.font.SysFont(None, 40)
        self.button_font_small = pygame.font.SysFont(None, 20)
        self.textbox = textbox.TextBox(0, 0, 180, 0, self.button_font_big, (0.5,0.5)) # height will be set in the init
        self.textbox.realign(self.camera)
        #saves the game
        self.playButton = button.Button(-100, 100, self.button_font_big, (255,255,255), 100, 'Play', (0.5,0.5))
        def onPlayClick():
            if len(self.textbox.text) > 0:
                try:
                    self.start_game(self.textbox.text)
                    self.camera.viewport.x = self.player.rect.centerx 
                    self.camera.viewport.y = self.player.rect.centery
                    self.switch_menu()
                except Exception:
                    pass
        self.playButton.onClick = onPlayClick
        self.playButton.realign(self.camera)
        self.buttons.append(self.playButton)
        #goes back to menu
        self.backButton = button.Button(100, 100, self.button_font_big, (255,255,255), 100,'Back', (0.5,0.5), True)
        def onBackClick():
            return self.states[0](self.states)
        self.backButton.onClick = onBackClick
        self.backButton.realign(self.camera)
        self.buttons.append(self.backButton)
        
    def draw_menu(self, screen):
        '''draws the menu'''
        if self.pause: #draw only if paused
            self.menu_back.centerx = screen.get_size()[0]/2
            self.menu_back.centery = screen.get_size()[1]/2
            pygame.draw.rect(screen, (0,0,0), self.menu_back)
            self.textbox.draw(screen)
        button.buttons_draw(self, screen, self.buttons)

    def create_pause(self):
        '''pause button for the game'''
        self.pauseButton = button.Button(-100, 0, self.button_font_big, (0,0,0), 100, 'Pause', (1,0))
        def onPauseClick():
            self.switch_menu()
        self.pauseButton.onClick = onPauseClick
        self.pauseButton.realign(self.camera)
        self.buttons.append(self.pauseButton) 
          
    def switch_menu(self):
        '''switches the menu state'''
        self.pause = not self.pause
        if not self.pause:
            #switch to game play
            self.buttons[:] = []
            self.create_pause()
        else:
            self.buttons[:] = []
            self.initialize_menu()
    #for saving and loading the game
    def to_dictionary(self):
        ''' changes the game into a dictionary for saving'''
        return {
                'player' : self.player.to_dictionary(),
                'enemies' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'enemy'],
                'doors' : [entity.to_dictionary() for entity in self.backGroundEntities if entity.type == 'door'],
                'dynamicEntities' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'dynamic'],
                'staticEntities' : [entity.to_dictionary() for entity in self.gameEntities if entity.type == 'static'],
                'backGroundEntities' : [scenery.to_dictionary() for scenery in self.backGroundEntities if scenery.type == 'scenery'],
                'foreGroundEntities' : [scenery.to_dictionary() for scenery in self.foreGroundEntities]
                }
    def from_dictionary(self, dictionary):
        '''load level from a dictionary'''
        self.player = Player(**{key: value for (key, value) in dictionary['player'].items()})
        enemies = [Enemy(**{key: value for (key, value) in i.items()}) for i in dictionary['enemies']]
        doors = [Door(**{key: value for (key, value) in i.items()}) for i in dictionary['doors']]
        for enemy in enemies: #no other way to reference player
            enemy.player = self.player
        for door in doors: #no other way to reference player and game
            door.player = self.player
            door.gameRef = self
        dynamic = [game_object.DynamicObject(**{key: value for (key, value) in i.items()}) for i in dictionary['dynamicEntities']]
        static = [game_object.StaticObject(**{key: value for (key, value) in i.items()}) for i in dictionary['staticEntities']]
        self.gameEntities = dynamic + static + enemies
        self.gameEntities.append(self.player)
        backGround = [game_object.SceneryObject(**{key: value for (key, value) in i.items()}) for i in dictionary['backGroundEntities']]
        self.foreGroundEntities = [game_object.SceneryObject(**{key: value for (key, value) in i.items()}) for i in dictionary['foreGroundEntities']]
        self.backGroundEntities = backGround + doors
    
    def load_game(self, file_name):
        '''loads game from text file'''
        if file_name is not None:
            with open('../levels/' + file_name +'.txt') as file:
                self.from_dictionary(json.loads(file.read()))
                
    def start_game(self, file_name):
        '''start the game'''
        if file_name is not None:
            self.load_game(file_name)
            self.camera = Camera(900, 600, self.player)
            self.camera.resize(pygame.display.get_surface())