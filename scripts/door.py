''' CS 108
Created Fall 2016
switches level ingame
@author: Mark Wissink (mcw33)
'''
import pygame, sys, math
import utilities
import random
from game_object import GameObject

class Door(GameObject):
    ''' 
    door for switching levels
    '''
    ATTRIBUTES = []
    def __init__(self, x, y, offsets, link=''):
        GameObject.__init__(self, x, y, offsets)
        self.link = link #link to the next room
        self.type = 'door'
        self.color = (0,255,255)

    def update(self, dt):
        #player and gameRef get set elsewhere
        if self.rect.colliderect(self.player) and self.player.past_up:
            try:
                self.gameRef.start_game(self.link)
                self.gameRef.camera.viewport.x = self.player.rect.centerx 
                self.gameRef.camera.viewport.y = self.player.rect.centery
            except Exception:
                pass
    def to_dictionary(self):
        '''creates a dictionary of variables for saving specifically for Dynamic Objects'''
        return utilities.merge_dicts(GameObject.to_dictionary(self),
                {'link' : self.link}) 