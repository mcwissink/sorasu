''' CS 108
Created Fall 2016
contains editor logic for creating levels
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math
import random
import game_object
import button
import utilities
from camera import Camera
from player import Player

class EditorState():
    def __init__(self):
        '''
        initiate the game
        '''
        pygame.mouse.set_visible(True) # Make the mouse invisible
        self.buttons = [] #containter for buttons
        self.backGroundEntities = [] #scenery and other things that don't collide
        self.gameEntities = [] #blocks and other objects that collide
        self.foreGroundEntities = [] #scenery and other things that don't collide
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False, 'ctrl': False, 'shift': False} #dictionary for key presses
        self.camera = Camera(900, 600, 0)
        #variables for all the editing
        self.variables = {'Parallax: ': 1, 'Scale: ': 1}
        self.snap_to = (0, 0)
        self.line_to = [(0, 0), (0, 0)]
        self.init_pos = (0, 0)
        self.origin = (0, 0)
        self.current_draw = None
        self.continue_draw = False
        self.draw_type = 0
        self.tool = 0 #tool includes 0=pen, 1=eraser, and 2=selector
        self.selector_rect = pygame.Rect(0,0,0,0) #used for selecting objects
        self.selected = [] #list for selected objects
        self.drag = False #used for selector
    def update(self, dt):
        '''
        loop through objects and run logic
        '''      
        #update the current snap function visuals
        position = self.camera.apply_inverse(pygame.mouse.get_pos())
        if self.keys['ctrl']:
            self.snap_to = self.snap_to_corner(position, self.gameEntities)
        else:
            self.snap_to = (0, 0)
        if self.keys['shift']:
            self.line_to = self.snap_to_plane(position, self.gameEntities)
        else:
            self.line_to = [(0, 0), (0, 0)]
        #if drawing something
        if self.continue_draw:
            #snap to corner
            if self.keys['ctrl']:
                position = self.snap_to
            #snap to plane
            elif self.keys['shift']:
                position = self.line_to[1]
            self.current_draw.rect.size = (position[0] - self.origin[0], position[1] - self.origin[1])
            self.current_draw.offsets = self.calculate_offset(self.init_pos, position, self.current_draw.rect)
        #for deleting
        if self.tool == 1:
            if pygame.mouse.get_pressed()[0]:
                self.delete_object(position, self.gameEntities)
        #for draggin
        if self.tool == 2:
            if not self.drag:
                #resize the selection box
                self.selector_rect.size = (position[0] - self.init_pos[0], position[1] - self.init_pos[1])
            else:
                #drag objects around
                for entity in self.selected:
                    entity.rect.x = position[0] + entity.select_offset[0]
                    entity.rect.y = position[1] + entity.select_offset[1]
        self.camera.update(self.keys, dt)
        
    def draw(self, draw, screen):
        '''
        loop through objects and draw them
        '''
        screen.fill(pygame.Color(255, 255, 255))
        for entity in self.backGroundEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1:
                entity.debug_draw(screen, self.camera)
        for entity in self.gameEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1:
                entity.debug_draw(screen, self.camera)
            elif self.tool == 2 and entity in self.selected:
                entity.debug_draw(screen, self.camera)
        for entity in self.foreGroundEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1:
                entity.debug_draw(screen, self.camera)
            elif self.tool == 2 and entity in self.selected:
                entity.debug_draw(screen, self.camera)
        #draw debug visuals
        # entity.debug_draw(screen, self.camera)
        if self.keys['ctrl']:
            pygame.draw.circle(screen, (255,0,0), self.camera.apply_single(self.snap_to), 7, 2)
        if self.keys['shift']:
            pygame.draw.line(screen, (255,0,0), self.camera.apply_single(self.line_to[0]), self.camera.apply_single(self.line_to[1]), 2)
        if pygame.mouse.get_pressed()[0] and self.tool == 2 and not self.drag:
            position = self.camera.apply_single((self.selector_rect.x, self.selector_rect.y))
            pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.selector_rect.width, self.selector_rect.height), 2)

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
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.keys['ctrl'] = True
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.keys['shift'] = True
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
            if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.keys['ctrl'] = False
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.keys['shift'] = False
            if event.key == pygame.K_1:
                self.tool = 0 #pen
                self.selected = []
            if event.key == pygame.K_2:
                self.tool = 1 #eraser
                self.selected = []
            if event.key == pygame.K_3:
                self.tool = 2 #selector
            if event.key == pygame.K_7:
                self.draw_type = 1
            if event.key == pygame.K_8:
                self.draw_type = 0
        #check if mouse downs
        if event.type == pygame.MOUSEBUTTONDOWN:
            #creates things 
            if pygame.mouse.get_pressed()[0]:
                self.init_pos = self.camera.apply_inverse(pygame.mouse.get_pos())
                if self.tool == 0:
                    if self.keys['ctrl']:
                        self.init_pos = self.snap_to_corner(self.camera.apply_inverse(pygame.mouse.get_pos()), self.gameEntities)
                    elif self.keys['shift']:
                        self.init_pos = self.snap_to_plane(self.camera.apply_inverse(pygame.mouse.get_pos()), self.gameEntities)[1] 
                    pygame.mouse.last_click = self.checkButtons(pygame.mouse.get_pos())
                    if not self.continue_draw:
                        #setup a new draw
                        self.origin = self.init_pos
                        draw_entity = game_object.StaticObject(self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)], (0,0,0))
                        self.current_draw = draw_entity
                        self.gameEntities.append(draw_entity)
                        self.continue_draw = True
                    else:
                        #finish draw
                        #snap to corner
                        if self.keys['ctrl']:
                            position = self.snap_to
                        #snap to plane
                        elif self.keys['shift']:
                            position = self.line_to[1]
                        else:
                            position = self.camera.apply_inverse(pygame.mouse.get_pos())
                        self.current_draw.rect.normalize()
                        self.current_draw.offsets = self.calculate_offset(self.origin, position, self.current_draw.rect)
                        #delete object if it is too small
                        if self.current_draw.rect.width < 0.1 or self.current_draw.rect.height < 0.1:
                            self.gameEntities.remove(self.current_draw)
                        self.current_draw = None
                        self.continue_draw = False
                if self.tool == 2:
                    for entity in self.selected:
                        if entity.rect.collidepoint(self.init_pos):
                            self.drag = True
                    if not self.drag:
                        self.selector_rect.x = self.init_pos[0]
                        self.selector_rect.y = self.init_pos[1]
                    else:
                        for entity in self.selected:
                            entity.select_offset = (entity.rect.x - self.init_pos[0], entity.rect.y - self.init_pos[1])
            #change layer
            elif event.button == 4:
                self.parallax = min(self.parallax + 1, 10)
                print(self.parallax)
            elif event.button == 5:
                self.parallax = max(self.parallax - 1, 0)
                print(self.parallax)               
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            pygame.mouse.current_button = self.checkButtons(pygame.mouse.get_pos())
            #left mouse button
            if self.tool == 2:
                if not self.drag:
                    self.selector_rect.normalize()
                    for entity in self.backGroundEntities:
                        if self.selector_rect.colliderect(entity):
                            self.selected.append(entity)
                    for entity in self.gameEntities:
                        if self.selector_rect.colliderect(entity):
                            self.selected.append(entity)
                    for entity in self.foreGroundEntities:
                        if self.selector_rect.colliderect(entity):
                            self.selected.append(entity)
                else:
                    self.drag = False
                    self.selected = []
                    
    #function for initializing the menu
    def initialize_menu(self):
        '''
        initializes the menu and the variables needed for it
        '''
        self.save = Button(-150, 100, self.button_font, (0,0,0), 100, 'Game')
        def onGameClick():
            return GameState()
        self.gameButton.onClick = onGameClick
    def draw_menu(self, screen, ):
        '''
        draws the menu
        '''
        #draw background of the side bar
        screen_size = screen.get_size()
        pygame.draw.rect(screen, (0,0,0), (0, 0, 200, screen_size[1]))
        for entity in self.buttons:
            entity.draw(screen)
    def checkButtons(self, mouse):
        '''
        loop throgh all the buttons and check if clicked
        '''
        for button in self.buttons:
            if button.rect.collidepoint(mouse):
                return button
    def calculate_offset(self, origin, position, rect):
        '''
        calculates the necessary offsets for a shape
        '''
        #corrects offsets for negative rectangle values
        h = 1
        v = 1
        if origin[0] == rect.topright[0]:
            h = -1
        if origin[1] == rect.bottomleft[1]:
            v = -1
        point_list = [(0,0), (0, v*(position[1]-origin[1])), (h*(position[0]-origin[0]), v*(position[1]-origin[1])), (h*(position[0]-origin[0]), 0)]
        if self.draw_type == 0:
            return point_list
        elif self.draw_type == 1:
            if origin == rect.topleft:
                point_list.pop(1)
            elif origin == rect.topright:
                point_list.pop(2)
            elif origin == rect.bottomleft:
                point_list.pop(0)
            else:
                point_list.pop(3)
            return point_list
    def snap_to_corner(self, position, entity_list):
        '''
        snaps position to the nearest corner
        '''
        min_dist = math.inf
        closest_pos = position
        for entity in entity_list:
            if entity != self.current_draw:
                for point in entity.get_corners():
                    dist = math.hypot(position[0] - point[0], position[1] - point[1]) 
                    if dist < min_dist:
                        min_dist = dist
                        closest_pos = point
        return closest_pos
    def snap_to_plane(self, position, entity_list):
        '''
        snaps position to the nearest corner
        '''
        closest_pos = self.snap_to_corner(position, entity_list)
        if abs(closest_pos[0] - position[0]) > abs(closest_pos[1] - position[1]):
            return [closest_pos, (position[0], closest_pos[1])]
        else:
            return [closest_pos, (closest_pos[0], position[1])]
    
    def delete_object(self, position, entity_list):
        '''
        destroys object in list
        '''
        for i in reversed(range(len(entity_list))):
            if entity_list[i].rect.collidepoint(position):
                entity_list.pop(i)
                
    def get_layer(self, z):
        if z == 1:
            return self.gameEntities
        elif z < 0:
            return self.backGroundEntities
        else:
            return self.foreGroundEntities