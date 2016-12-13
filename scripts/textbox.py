''' CS 108
Created Fall 2016
Runs the game
@author: Mark Wissink (mcw33)
'''
import pygame, pygame.font, pygame.event, pygame.draw
from pygame.locals import *

'''source for code: http://www.pygame.org/pcr/inputbox/
Author: Timothy Downs
Submission date: January 23, 2002

Had to edit a lot of code to make it work in my game
the main function that I referenced was the key_in function
'''
class TextBox():
    def __init__(self, x, y, width, height, font, align):
        '''initilizes the textbox'''
        #set fonts
        self.font = font
        self.text = ''
        self.offset = (x,y)
        self.align = align # percent value for positioning on screen
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.height = self.font.size(self.text)[1]
        self.text_list = []
        self.active = False
    
    def draw(self, screen):
        "Print a message in a box in the middle of the screen"
        if self.active:
            pygame.draw.rect(screen, (255,0,0), self.rect, 1)
        else:
            pygame.draw.rect(screen, (255,255,255), self.rect, 1)
        if len(self.text) != 0:
            screen.blit(self.font.render(self.text, 1, (255,255,255)), (self.rect.x+2, self.rect.y))
        
    def key_in(self, event):
        '''ask(screen, question) -> answer'''
        if event.type == pygame.KEYDOWN:
            if event.key == K_BACKSPACE:
                self.text_list = self.text_list[0:-1]
            elif event.key == K_RETURN:
                self.active = False
            elif event.key <= 127 and chr(event.key).isalnum() and len(self.text_list) < 8:
                self.text_list.append(chr(event.key))
            if len(self.text_list) != 0:
                self.text = ''.join(self.text_list)
            else:
                self.text = ''
    
    def realign(self, camera):
        '''realigns the button based on the percent given to align'''
        self.rect.x = camera.viewport.width*self.align[0] + self.offset[0]
        self.rect.y = camera.viewport.height*self.align[1] + self.offset[1]