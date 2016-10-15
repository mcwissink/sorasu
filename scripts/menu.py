''' CS 108
Created Fall 2016
contains game logic and draw calls
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import button

class MenuState():
    def __init__(self):
        '''
        initiate the game
        '''
        self.switch_state = None
        self.buttonTest = button.Button(10, 10, 200, 50, (0, 0, 0), 'Play')
        self.buttonTest.onClick = button.changeState()
        self.buttons = [self.buttonTest] #containter for buttons
        pygame.mouse.set_visible(True) # Make the mouse invisible
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False} #dictionary for key presses
    
    def update(self, dt):
        '''
        loop through objects and run logic
        '''
        #send key inputs to player
    def draw(self, draw, screen):
        '''
        loop through objects and draw them
        '''
        screen.fill(pygame.Color(255, 255, 255))
        for entity in self.buttons:
            entity.draw(screen)
        
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
            pygame.mouse.last_click = self.checkButtons(pygame.mouse.get_pos())
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            pygame.mouse.current_button = self.checkButtons(pygame.mouse.get_pos())
            if pygame.mouse.last_click == pygame.mouse.current_button and pygame.mouse.current_button != None:
                self.switch_state = pygame.mouse.current_button.onClick(self.switch_state, GameState)
    
    def checkButtons(self, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in self.buttons:
            if button.rect.collidepoint(mouse):
                return button