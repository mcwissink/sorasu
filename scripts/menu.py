''' CS 108
Created Fall 2016
menu for the game, can launch game or editor
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import utilities
from camera import Camera
from button import Button
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
        self.button_hover = None #used for highlighting buttons
        self.last_click = None #used for remembering buttons
        self.current_button = None #used to store current button
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
        self.gameButton = Button(-150, 100, self.button_font, (0,0,0), 100, 'Game')
        def onGameClick():
            return GameState()
        self.gameButton.onClick = onGameClick
        self.editorButton = Button(150, 100, self.button_font, (0,0,0), 100, 'Editor')
        def onEditorClick():
            return EditorState()
        self.editorButton.onClick = onEditorClick
        self.buttons = [self.gameButton, self.editorButton] #containter for buttons
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        if not self.last_click:
            current_hover = self.checkButtons(self.camera.apply_inverse(pygame.mouse.get_pos()))
            if current_hover:
                current_hover.label = current_hover.font.render(current_hover.text, 1, (255,0,0))
                self.button_hover = self.checkButtons(self.camera.apply_inverse(pygame.mouse.get_pos()))
            elif self.button_hover:
                self.button_hover.label = self.button_hover.font.render(self.button_hover.text, 1, self.button_hover.color)
                self.button_hover = None
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
            if not self.last_click:
                self.last_click = self.checkButtons(self.camera.apply_inverse(pygame.mouse.get_pos()))
                if self.last_click:
                    self.last_click.font.set_bold(True)
                    self.last_click.label = self.last_click.font.render(self.last_click.text, 1, (255,0,0))
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            if self.last_click:
                self.current_button = self.checkButtons(self.camera.apply_inverse(pygame.mouse.get_pos()))
                if self.last_click == self.current_button and self.current_button != None:
                    return self.current_button.onClick()
                else:
                    self.last_click.font.set_bold(False)
                    self.last_click.label = self.last_click.font.render(self.last_click.text, 1, self.last_click.color)
                    self.last_click = None
    def checkButtons(self, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in self.buttons:
            if button.rect.collidepoint(mouse):
                return button
    def draw_logo(self, screen, camera):
        '''
        draws the logo
        '''
        width, height = self.title_font.size('Sorasu')
        pygame.draw.circle(screen, (255,0,0), camera.apply_single((0,0)), int(width/4))
        screen.blit(self.logo_text, camera.apply_single((self.logo_x-width/2, self.logo_y-height/2)))
        