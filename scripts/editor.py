''' CS 108
Created Fall 2016
contains editor logic for creating levels
@author: Mark Wissink (mcw33)
'''

import pygame, sys
import math, json
import random
import game_object
import utilities
import button
import textbox
from game import GameState
from camera import Camera
from player import Player

class EditorState(GameState):
    def __init__(self, file_name=None):
        '''
        initiate the editor
        '''  
        super(EditorState, self).__init__(file_name)
        if file_name is None:
            self.player = Player(0, 0, [(0,0),(0,40),(20,40),(20,0)], 10)
            self.gameEntities.append(self.player)
            self.camera = Camera(900, 600, 0)
            self.camera.resize(pygame.display.get_surface())
        #center the camera on the player
        self.camera.viewport.centerx = self.player.rect.centerx 
        self.camera.viewport.centery = self.player.rect.centery
        self.camera.target = 0
        pygame.mouse.set_visible(True) # Make the mouse invisible
        #set up editor specific values and draws and buttons
        button.buttons_init(self)
        self.attr_selected = None
        self.editor_keys = {'up': False, 'down': False, 'left': False, 'right': False, 'ctrl': False, 'shift': False} #dictionary for key presses
        self.test_level = False
        #create the menu
        self.initialize_menu()
        #variables for all the editing
        self.snap_to = (0, 0)
        self.line_to = [(0, 0), (0, 0)]
        self.init_pos = (0, 0)
        self.origin = (0, 0)
        self.current_draw = None
        self.continue_draw = False
        self.draw_type = game_object.StaticObject
        self.draw_shape = 0
        self.tool = 0 #tool includes 0=pen, 1=eraser, and 2=selector
        self.selector_rect = pygame.Rect(0,0,0,0) #used for selecting objects
        self.selected = [] #list for selected objects
        self.drag = False #used for selector
        
    def update(self, dt):
        '''
        loop through objects and run logic
        '''      
        #update the editor buttons
        button.buttons_update(self, self.buttons)
        #update the current snap function visuals
        position = self.camera.apply_inverse(pygame.mouse.get_pos())
        if self.editor_keys['ctrl']:
            self.snap_to = self.snap_to_corner(position, self.gameEntities)
        else:
            self.snap_to = (0, 0)
        if self.editor_keys['shift']:
            self.line_to = self.snap_to_plane(position, self.gameEntities)
        else:
            self.line_to = [(0, 0), (0, 0)]
        #if drawing something
        if self.continue_draw:
            #snap to corner
            if self.editor_keys['ctrl']:
                position = self.snap_to
            #snap to plane
            elif self.editor_keys['shift']:
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
                    #since the variable pos and spawn plays into dynamic objects positioning
                    if entity.dynamic:
                        entity.pos[0] = entity.rect.x
                        entity.pos[1] = entity.rect.y 
                        entity.spawn = (entity.rect.x, entity.rect.y)
        #perform game logic if game is running
        if self.test_level:
            super(EditorState, self).update(dt)   
        else:
            #otherwise run regular camera
            self.camera.update(self.editor_keys, dt)
        
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
        #draw what is being drawn
        if self.continue_draw:
            self.current_draw.draw(screen, self.camera)
        #draw debug visuals
        # entity.debug_draw(screen, self.camera)
        if self.editor_keys['ctrl']:
            pygame.draw.circle(screen, (255,0,0), self.camera.apply_single(self.snap_to), 7, 2)
        if self.editor_keys['shift']:
            pygame.draw.line(screen, (255,0,0), self.camera.apply_single(self.line_to[0]), self.camera.apply_single(self.line_to[1]), 2)
        if pygame.mouse.get_pressed()[0] and self.tool == 2 and not self.drag:
            position = self.camera.apply_single((self.selector_rect.x, self.selector_rect.y))
            pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.selector_rect.width, self.selector_rect.height), 2)
        #draw the editor over top everything
        self.draw_menu(screen)
    def eventHandler(self, event):
        '''
        handles user inputs
        '''
        #special case
        if self.textbox.active:
            self.textbox.key_in(event)
        else:
            if self.test_level:
                super(EditorState, self).eventHandler(event)
            #check for key down
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.editor_keys['up'] = True
                if event.key == pygame.K_s:
                    self.editor_keys['down'] = True
                if event.key == pygame.K_a:
                    self.editor_keys['left'] = True
                if event.key == pygame.K_d:
                    self.editor_keys['right'] = True
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.editor_keys['ctrl'] = True
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.editor_keys['shift'] = True
            #check if for key up
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.editor_keys['up'] = False
                if event.key == pygame.K_s:
                    self.editor_keys['down'] = False
                if event.key == pygame.K_a:
                    self.editor_keys['left'] = False
                if event.key == pygame.K_d:
                    self.editor_keys['right'] = False
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    self.editor_keys['ctrl'] = False
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.editor_keys['shift'] = False
                if event.key == pygame.K_1:
                    self.tool = 0 #pen
                    self.selected = []
                if event.key == pygame.K_2:
                    self.tool = 1 #eraser
                    self.selected = []
                if event.key == pygame.K_3:
                    self.tool = 2 #selector
                if event.key == pygame.K_7:
                    self.draw_shape = 1
                if event.key == pygame.K_8:
                    self.draw_shape = 0
                if event.key == pygame.K_9:
                    self.self.attr_selected += 0.1
                if event.key == pygame.K_0:
                    self.self.attr_selected += 0.1
                if event.key == pygame.K_p:
                    self.test_level ^= True
                    if self.camera.target == self.player:
                        self.camera.target = 0
                    else:
                        self.camera.target = self.player
        #check if mouse downs
        if event.type == pygame.MOUSEBUTTONDOWN:
            #creates things 
            if self.menu_back.collidepoint(pygame.mouse.get_pos()):
                button.buttons_mousedown(self, self.buttons)
            else:
                if pygame.mouse.get_pressed()[0]:
                    self.init_pos = self.camera.apply_inverse(pygame.mouse.get_pos())
                    if self.tool == 0:
                        if self.editor_keys['ctrl']:
                            self.init_pos = self.snap_to_corner(self.camera.apply_inverse(pygame.mouse.get_pos()), self.gameEntities)
                        elif self.editor_keys['shift']:
                            self.init_pos = self.snap_to_plane(self.camera.apply_inverse(pygame.mouse.get_pos()), self.gameEntities)[1] 
                        if not self.continue_draw:
                            #setup a new draw
                            self.origin = self.init_pos
                            self.current_draw = self.draw_type(self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)])
                            self.continue_draw = True
                        else:
                            #finish draw
                            #snap to corner
                            if self.editor_keys['ctrl']:
                                position = self.snap_to
                            #snap to plane
                            elif self.editor_keys['shift']:
                                position = self.line_to[1]
                            else:
                                position = self.camera.apply_inverse(pygame.mouse.get_pos())
                            self.current_draw.rect.normalize()
                            self.current_draw.offsets = self.calculate_offset(self.origin, position, self.current_draw.rect)
                            #delete object if it is too small
                            
                            if not (self.current_draw.rect.width < 0.1 or self.current_draw.rect.height < 0.1):
                                self.gameEntities.append(self.current_draw)
                            self.current_draw = None
                            self.continue_draw = False
                    if self.tool == 2:
                        for entity in self.selected:
                            #initilaze the drage
                            if entity.rect.collidepoint(self.init_pos):
                                self.drag = True
                        if not self.drag:
                            #resize the selecting rectangle
                            self.selector_rect.x = self.init_pos[0]
                            self.selector_rect.y = self.init_pos[1]
                        else:
                            #set the select offset
                            for entity in self.selected:
                                entity.select_offset = (entity.rect.x - self.init_pos[0], entity.rect.y - self.init_pos[1])
                #change layer
                elif event.button == 4:
                    self.attr_selected.value = min(self.attr_selected.value + 0.1, 10)
                elif event.button == 5:
                    self.attr_selected.value = max(self.attr_selected.value - 0.1, 0)              
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            #clicking in the menu
            if self.menu_back.collidepoint(pygame.mouse.get_pos()):
                if self.textbox.rect.collidepoint(pygame.mouse.get_pos()):
                    self.textbox.active = True
                else:
                    self.textbox.active = False
                button.buttons_mouseup(self, self.buttons)
            #clicking not in the menu
            else:
                self.textbox.active = False 
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
        if self.draw_shape == 0:
            return point_list
        elif self.draw_shape == 1:
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
        
    def save_game(self, name, game):
        '''
        converts the game into a txt file
        '''
        with open('../levels/' + name +'.txt', 'w') as file:
            # https://docs.python.org/2/library/json.html
            file.write(json.dumps(game.to_dictionary(), indent = 2))
    
    #function for initializing the menu
    def initialize_menu(self):
        '''
        initializes the menu and the variables needed for it
        '''
        self.menu_back = pygame.Rect(0, 0, 200, 0) # height will get set in the draw method
        #create the textbox for naming
        self.textbox = textbox.TextBox(10, 10, 180, 0) # height will be set in the init
        self.button_font_big = pygame.font.SysFont(None, 40)
        self.button_font_small = pygame.font.SysFont(None, 20)
        self.saveButton = button.Button(15, self.textbox.rect.bottom+4, self.button_font_big, (255,255,255), 100, 'Save', (0,0))
        #saves the game
        def onSaveClick():
            if len(self.textbox.text) > 0:
                self.save_game(self.textbox.text, super(EditorState, self))
        self.saveButton.onClick = onSaveClick
        self.saveButton.realign(self.camera)
        self.buttons.append(self.saveButton)
        #loads the game
        self.loadButton = button.Button(105, self.textbox.rect.bottom+4, self.button_font_big, (255,255,255), 100, 'Load', (0,0))
        def onLoadClick():
            if len(self.textbox.text) > 0:
                try:
                    super(EditorState, self).load_game(self.textbox.text)
                    self.test_level = False
                    self.camera.viewport.centerx = self.player.rect.centerx 
                    self.camera.viewport.centery = self.player.rect.centery
                    self.camera.target = 0
                except:
                    pass
        self.loadButton.onClick = onLoadClick
        self.loadButton.realign(self.camera)
        self.buttons.append(self.loadButton)
        #resets the game
        self.resetButton = button.Button(15, self.loadButton.rect.bottom+10, self.button_font_big, (255,255,255), 100, 'Reset', (0,0))
        def onResetClick():
            for entity in self.gameEntities:
                if entity.dynamic:
                    entity.reset()
            self.test_level = False
            #reset the camera to the player
            self.camera.target = 0
            self.camera.viewport.centerx = self.player.rect.centerx 
            self.camera.viewport.centery = self.player.rect.centery
        self.resetButton.onClick = onResetClick
        self.resetButton.realign(self.camera)
        self.buttons.append(self.resetButton)
        #sets draw type to static
        self.staticButton = button.Button(15, -100, self.button_font_big, (255,255,255), 100, 'Static', (0,1))
        def onStaticClick():
            self.draw_type = game_object.StaticObject
        self.staticButton.onClick = onStaticClick
        self.staticButton.realign(self.camera)
        self.buttons.append(self.staticButton)
        #sets draw type to dynamic
        self.dynamicButton = button.Button(15, -200, self.button_font_big, (255,255,255), 100, 'Dynamic', (0,1))
        def onDynamicClick():
            self.draw_type = game_object.DynamicObject
        self.dynamicButton.onClick = onDynamicClick
        self.dynamicButton.realign(self.camera)
        self.buttons.append(self.dynamicButton)
        #load the variables that can be edited
        self.entity_variables(game_object.StaticObject)
        
    def entity_variables(self, entity_type):
        entity_var = entity_type.ATTRIBUTES
        y_offset = 20
        for var in entity_var:
            varButton = button.Button(100, 300+y_offset, self.button_font_small, (255,255,255), 100, var+':', (0,0), False, entity_var[var])
            def onVarClick():
                self.attr_selected = varButton
            varButton.onClick = onVarClick
            self.buttons.append(varButton)
            y_offset += 20
    
    def draw_menu(self, screen):
        '''
        draws the menu
        '''
        #draw background of the side bar
        self.menu_back.height = screen.get_size()[1]
        pygame.draw.rect(screen, (0,0,0), self.menu_back)
        self.textbox.draw(screen)
        button.buttons_draw(self, screen, self.buttons)
        