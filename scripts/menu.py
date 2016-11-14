''' CS 108
Created Fall 2016
menu for the game, can launch game or editor
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import utilities
import button
from camera import Camera
from game import GameState
from editor import EditorState

class MenuState():
    def __init__(self):
        '''
        initiate the game
        '''
        self.camera = Camera(900, 600, 1)
        pygame.mouse.set_visible(True) # Make the mouse invisible
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses
        #create buttons and other a e s t h e s t i c s
        button.buttons_init(self)
        #set fonts
        try:
            self.title_font = pygame.font.Font("../images/jbrush.TTF", 150)
            self.button_font = pygame.font.Font("../images/jbrush.TTF", 50)
        except:
            self.title_font = pygame.font.SysFont(None, 150)
            self.button_font = pygame.font.SysFont(None, 50)
        #draw logo
        self.logo_text = self.title_font.render('Sorasu', 1, (0,0,0))
        self.logo_x, self.logo_y = (0,0)
        self.gameButton = button.Button(75, 75, self.button_font, (0,0,0), 100, 'Game',(0.5,0.5), True)
        def onGameClick():
            return GameState('test')
        self.gameButton.onClick = onGameClick
        self.gameButton.realign(self.camera)
        self.buttons.append(self.gameButton)
        self.editorButton = button.Button(-300, 75, self.button_font, (0,0,0), 100, 'Editor', (0.5,0.5), True)
        def onEditorClick():
            return EditorState()
        self.editorButton.onClick = onEditorClick
        self.editorButton.realign(self.camera)
        self.buttons.append(self.editorButton)
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        button.buttons_update(self)
        self.camera.update(self.keys, dt)
        
    def draw(self, draw, screen):
        '''
        loop through objects and draw them
        '''
        screen.fill(pygame.Color(255, 255, 255))
        #draw logo
        self.draw_logo(screen, self.camera)
        for entity in self.buttons:
            entity.draw(screen, self.camera)
            
    def eventHandler(self, event):
        '''
        handles user inputs
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
            button.buttons_mousedown(self)
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            #uses return in this case since we are switching states
            return button.buttons_mouseup(self)
    
    def draw_logo(self, screen, camera):
        '''
        draws the logo
        '''
        width, height = self.title_font.size('Sorasu')
        pygame.draw.circle(screen, (255,0,0), camera.apply_single((0,0)), int(width/4))
        screen.blit(self.logo_text, camera.apply_single((self.logo_x-width/2, self.logo_y-height/2)))
        