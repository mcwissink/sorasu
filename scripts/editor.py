''' CS 108
Created Fall 2016
contains editor logic for creating levels
@author: Mark Wissink (mcw33)
'''

import pygame, sys, os
import math, json
import random
import game_object
import enemy
import utilities
import button
import textbox
import door
from game import GameState
from camera import Camera
from player import Player

class EditorState(GameState):
    def __init__(self, states):
        '''initiate the editor''' 
        super(EditorState, self).__init__(states) #initialize the game, also initializes the menu
        #setup player
        self.player = Player(0, 0, [(0,0),(0,40),(20,40),(20,0)], [10, 0.9])
        self.player.adjust_collision()
        self.gameEntities.append(self.player)
        #center the camera on the player
        self.camera.viewport.x = self.player.rect.centerx 
        self.camera.viewport.y = self.player.rect.centery
        self.camera.target = 0 
        self.editor_keys = {'up': False, 'down': False, 'left': False, 'right': False, 'ctrl': False, 'shift': False} #dictionary for key presses
        #variables for all the editing - used later in the code
        self.parallax = 1
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
        
        #load images for the game objects
        scenery_images = self.load_images('scenery/')
    def update(self, dt):
        '''run logic of the editor - and the game if it is active'''
        if self.draw_type == game_object.SceneryObject: #maybe try to remove this
            self.parallax = self.attr_buttons[0].value#makes handling parallax a little easier
        #update the editor buttons
        button.buttons_update(self, self.buttons)
        #update the current snap function visuals
        #used for snapping to objects
        position = self.camera.apply_inverse(pygame.mouse.get_pos(), self.parallax)
        if self.editor_keys['ctrl']:
            self.snap_to = self.snap_to_corner(position, self.get_layer())
        else:
            self.snap_to = (0, 0)
        if self.editor_keys['shift']:
            self.line_to = self.snap_to_plane(position, self.get_layer())
        else:
            self.line_to = [(0, 0), (0, 0)]
        #if drawing something
        if self.continue_draw: #update the draw
            #snap to corner
            if self.editor_keys['ctrl']:
                position = self.snap_to
            #snap to plane
            elif self.editor_keys['shift']:
                position = self.line_to[1]
            #update the rectangle collider and offsets 
            self.current_draw.rect.size = (position[0] - self.origin[0], position[1] - self.origin[1])
            self.current_draw.offsets = self.calculate_offset(self.init_pos, position)
        #for deleting
        if self.tool == 1:
            if pygame.mouse.get_pressed()[0]:
                self.delete_object(position, self.get_layer())
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
        if not self.pause:
            #run the game
            super(EditorState, self).update(dt)
        else:
            #otherwise run regular camera
            self.camera.update(self.editor_keys, dt)
        
    def draw(self, draw, screen):
        '''loop through objects and draw them'''
        screen.fill(pygame.Color(255, 255, 255))
        for entity in self.backGroundEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1 and self.get_layer() == self.backGroundEntities:
                entity.debug_draw(screen, self.camera)
        for entity in self.gameEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1 and self.get_layer() == self.gameEntities:
                entity.debug_draw(screen, self.camera)
            elif self.tool == 2 and entity in self.selected:
                entity.debug_draw(screen, self.camera)
        for entity in self.foreGroundEntities:
            entity.draw(screen, self.camera)
            if self.tool == 1 and self.get_layer() == self.foreGroundEntities:
                entity.debug_draw(screen, self.camera)
            elif self.tool == 2 and entity in self.selected:
                entity.debug_draw(screen, self.camera)
        #draw what is being drawn
        if self.continue_draw:
            self.current_draw.draw(screen, self.camera)
        #draw debug visuals
        # entity.debug_draw(screen, self.camera)
        if self.editor_keys['ctrl']:
            pygame.draw.circle(screen, (255,0,0), self.camera.apply_single(self.snap_to, self.parallax), 7, 2)
        if self.editor_keys['shift']:
            pygame.draw.line(screen, (255,0,0), self.camera.apply_single(self.line_to[0], self.parallax), self.camera.apply_single(self.line_to[1], self.parallax), 2)
        if pygame.mouse.get_pressed()[0] and self.tool == 2 and not self.drag:
            position = self.camera.apply_single((self.selector_rect.x, self.selector_rect.y), self.parallax)
            pygame.draw.rect(screen, (255,0,0), (position[0], position[1], self.selector_rect.width, self.selector_rect.height), 2)
        #draw the editor over top everything
        self.draw_menu(screen)
    def eventHandler(self, event):
        '''handles user inputs'''
        #special case
        if self.textbox.active:
            self.textbox.key_in(event)
        elif self.door_textbox.active:
            self.door_textbox.key_in(event)
        else:
            if not self.pause:
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
                if event.key == pygame.K_p:
                    self.pause = not self.pause
                    if self.camera.target == self.player:
                        self.camera.target = 0
                    else:
                        self.camera.target = self.player
        #check if mouse downs
        '''This handles all the different tools and editor stuff'''
        if event.type == pygame.MOUSEBUTTONDOWN:
            #creates things 
            if self.menu_back.collidepoint(pygame.mouse.get_pos()):
                button.buttons_mousedown(self, self.buttons)
            else:
                if pygame.mouse.get_pressed()[0]:
                    self.init_pos = self.camera.apply_inverse(pygame.mouse.get_pos(), self.parallax)
                    if self.tool == 0:
                        if self.editor_keys['ctrl']:
                            self.init_pos = self.snap_to_corner(self.camera.apply_inverse(pygame.mouse.get_pos(), self.parallax), self.get_layer())
                        elif self.editor_keys['shift']:
                            self.init_pos = self.snap_to_plane(self.camera.apply_inverse(pygame.mouse.get_pos(), self.parallax), self.get_layer())[1] 
                        if not self.continue_draw:
                            #setup a new draw
                            self.origin = self.init_pos
                            if self.draw_type == door.Door: #special treatment for door
                                self.current_draw = self.draw_type(self, self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)], self.door_textbox.text)
                            elif self.draw_type == enemy.Enemy:
                                self.current_draw = self.draw_type(self.player, self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)], [button.value for button in self.attr_buttons])
                            elif self.draw_type == game_object.SceneryObject:
                                self.current_draw = self.draw_type(self.texture_cache, self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)], [button.value for button in self.attr_buttons])
                            else:   
                                self.current_draw = self.draw_type(self.origin[0], self.origin[1], [(1,1),(-1,1),(-1,-1),(1,-1)], [button.value for button in self.attr_buttons])
                            #append player if necessary
                            if self.draw_type == enemy.Enemy or self.draw_type == door.Door:
                                self.current_draw.player = self.player
                            self.continue_draw = True
                            
                            #if the current draw is scenery with an image, just stamp it
                            if self.draw_type == game_object.SceneryObject and self.current_draw.hasImage:
                                self.current_draw.rect.centerx, self.current_draw.rect.centery = self.origin
                                layer = self.get_layer()
                                layer.append(self.current_draw)
                                #resort list to simulate depth
                                if hasattr(self.current_draw, 'parallax'):
                                    layer.sort(key=lambda x: x.parallax, reverse=False)
                                self.current_draw = None
                                self.continue_draw = False
                        else:
                            #finish draw
                            #snap to corner
                            if self.editor_keys['ctrl']:
                                position = self.snap_to
                            #snap to plane
                            elif self.editor_keys['shift']:
                                position = self.line_to[1]
                            else:
                                position = self.camera.apply_inverse(pygame.mouse.get_pos(), self.parallax)
                            #apply final updates to the shape
                            self.current_draw.rect.size = (position[0] - self.origin[0], position[1] - self.origin[1])
                            self.current_draw.rect.normalize()
                            self.current_draw.offsets = self.calculate_offset(self.origin, position)
                            #adujust collision box for dynamic object, its the only way
                            if self.current_draw.dynamic:
                                self.current_draw.adjust_collision()
                            #delete object if it is too small
                            if not (self.current_draw.rect.width < 0.2 or self.current_draw.rect.height < 0.2):
                                layer = self.get_layer()
                                layer.append(self.current_draw)
                                #resort list to simulate depth
                                if hasattr(self.current_draw, 'parallax'):
                                    layer.sort(key=lambda x: x.parallax, reverse=False)
                            #clear the draw variables   
                            self.current_draw = None
                            self.continue_draw = False
                            
                    if self.tool == 2:
                        for entity in self.selected:
                            #initialize the drag
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
                #change button attributes
                elif event.button == 4:
                    attr_ref = self.draw_type.ATTRIBUTES[self.attr_selected]
                    self.attr_buttons[self.attr_selected].value = round(min(self.attr_buttons[self.attr_selected].value + attr_ref['step'], attr_ref['max']), 3)
                elif event.button == 5:
                    attr_ref = self.draw_type.ATTRIBUTES[self.attr_selected]
                    self.attr_buttons[self.attr_selected].value = round(max(self.attr_buttons[self.attr_selected].value - attr_ref['step'], attr_ref['min']), 3)           
        #check if mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            #clicking in the menu
            if self.menu_back.collidepoint(pygame.mouse.get_pos()):
                if self.textbox.rect.collidepoint(pygame.mouse.get_pos()):
                    self.textbox.active = True
                else:
                    self.textbox.active = False
                if self.door_textbox.rect.collidepoint(pygame.mouse.get_pos()):
                    self.door_textbox.active = True
                else:
                    self.door_textbox.active = False
                return button.buttons_mouseup(self, self.buttons)
            #clicking not in the menu
            else:
                self.door_textbox.active = False
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

    def calculate_offset(self, origin, position):
        '''calculates the necessary offsets for a shape'''
        #corrects offsets for negative rectangle values
        h = 1
        v = 1
        if origin[0] == self.current_draw.rect.topright[0]:
            h = -1
        if origin[1] == self.current_draw.rect.bottomleft[1]:
            v = -1
        point_list = [(0,0), (0, v*(position[1]-origin[1])), (h*(position[0]-origin[0]), v*(position[1]-origin[1])), (h*(position[0]-origin[0]), 0)]
        if self.draw_shape == 0:
            return point_list
        elif self.draw_shape == 1:
            if origin == self.current_draw.rect.topleft:
                point_list.pop(1)
            elif origin == self.current_draw.rect.topright:
                point_list.pop(2)
            elif origin == self.current_draw.rect.bottomleft:
                point_list.pop(0)
            else:
                point_list.pop(3)
            return point_list
    def snap_to_corner(self, position, entity_list):
        '''snaps position to the nearest corner'''
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
        '''snaps position to the nearest corner'''
        closest_pos = self.snap_to_corner(position, entity_list)
        if abs(closest_pos[0] - position[0]) > abs(closest_pos[1] - position[1]):
            return [closest_pos, (position[0], closest_pos[1])]
        else:
            return [closest_pos, (closest_pos[0], position[1])]
    
    def delete_object(self, position, entity_list):
        '''destroys object in list'''
        for i in reversed(range(len(entity_list))):
            if entity_list[i].rect.collidepoint(position):
                entity_list.pop(i)
                
    def get_layer(self):
        '''gets the layer for drawing'''
        if self.draw_type == game_object.SceneryObject:
            if self.attr_buttons[0].value > 1:
                return self.foreGroundEntities
            else:
                return self.backGroundEntities
        elif self.draw_type == door.Door:
            return self.backGroundEntities
        else:
            return self.gameEntities
            
        
    def save_game(self, name, game):
        '''converts the game into a txt file'''
        with open('../levels/' + name +'.txt', 'w') as file:
            # https://docs.python.org/2/library/json.html
            file.write(json.dumps(game.to_dictionary()))
    
    #function for initializing the menu
    def initialize_menu(self):
        '''initializes the menu and the variables needed for it'''
        #set up editor specific values and draws and buttons
        self.attr_buttons = [] #used to store specific buttons
        self.attr_selected = None #used for changing values of objects
        self.menu_back = pygame.Rect(0, 0, 200, 0) # height will get set in the draw method
        self.button_font_big = pygame.font.SysFont(None, 40)
        self.button_font_small = pygame.font.SysFont(None, 20)
        # used for inputing text for the door object
        self.door_textbox = textbox.TextBox(-100, 200, 100, 0, self.button_font_big, (0,0))
        #create the textbox for getting file names
        self.textbox = textbox.TextBox(10, 10, 180, 0, self.button_font_big, (0,0)) # height will be set in the init
        self.saveButton = button.Button(15, self.textbox.rect.bottom+4, self.button_font_big, (255,255,255), 100, 'Save', (0,0))
        #saves the game
        def onSaveClick():
            if len(self.textbox.text) > 0:
                self.save_game(self.textbox.text, super(EditorState, self))
        self.saveButton.onClick = onSaveClick
        self.saveButton.realign(self.camera)
        self.buttons.append(self.saveButton)
        #loads the game
        self.loadButton = button.Button(self.saveButton.rect.right + 10, self.saveButton.rect.y, self.button_font_big, (255,255,255), 100, 'Load', (0,0))
        def onLoadClick():
            if len(self.textbox.text) > 0:
                try:
                    super(EditorState, self).start_game(self.textbox.text)
                    self.pause = True
                    self.camera.viewport.x = self.player.rect.centerx 
                    self.camera.viewport.y = self.player.rect.centery
                    self.camera.target = 0
                except Exception:
                    pass
        self.loadButton.onClick = onLoadClick
        self.loadButton.realign(self.camera)
        self.buttons.append(self.loadButton)
        #resets the game
        self.resetButton = button.Button(15, self.loadButton.rect.bottom+10, self.button_font_big, (255,255,255), 100, 'Reset', (0,0))
        def onResetClick():
            self.reset_game()
            self.pause = True
            #reset the camera to the player
            self.camera.target = 0
            self.camera.viewport.x = self.player.rect.centerx 
            self.camera.viewport.y = self.player.rect.centery
        self.resetButton.onClick = onResetClick
        self.resetButton.realign(self.camera)
        self.buttons.append(self.resetButton)
        #goes back to menu
        self.backButton = button.Button(self.resetButton.rect.right + 10, self.resetButton.rect.y, self.button_font_big, (255,255,255), 100,'Back', (0,0), True)
        def onBackClick():
            return self.states[0](self.states)
        self.backButton.onClick = onBackClick
        self.backButton.realign(self.camera)
        self.buttons.append(self.backButton)
        #tools button
        self.toolsButton = button.Button(15, self.resetButton.rect.bottom+20, self.button_font_big, (255,255,255), 100, 'D  E  S', (0,0))
        def onToolsClick():
            '''selects the tool'''
            if pygame.mouse.get_pos()[0] < self.toolsButton.rect.width/3:
                self.tool = 0
            elif pygame.mouse.get_pos()[0] < self.toolsButton.rect.width*(2/3):
                self.tool = 1
            else:
                self.tool = 2
        self.toolsButton.onClick = onToolsClick
        self.toolsButton.realign(self.camera)
        self.buttons.append(self.toolsButton)
        #sets draw type to static
        self.staticButton = button.Button(15, -100, self.button_font_big, (255,255,255), 100, 'Static', (0,1))
        def onStaticClick():
            self.draw_type = game_object.StaticObject
            self.entity_variables(10, 200, self.draw_type)
            self.parallax = 1
            self.toggle_door_textbox()
        self.staticButton.onClick = onStaticClick
        self.staticButton.realign(self.camera)
        self.buttons.append(self.staticButton)
        #sets draw type to dynamic
        self.dynamicButton = button.Button(15, -150, self.button_font_big, (255,255,255), 100, 'Dynamic', (0,1))
        def onDynamicClick():
            self.draw_type = game_object.DynamicObject
            self.entity_variables(10, 200, self.draw_type)
            self.parallax = 1
            self.toggle_door_textbox()
        self.dynamicButton.onClick = onDynamicClick
        self.dynamicButton.realign(self.camera)
        self.buttons.append(self.dynamicButton)
        #sets draw type to Scenery
        self.sceneryButton = button.Button(15, -200, self.button_font_big, (255,255,255), 100, 'Scenery', (0,1))
        def onSceneryClick():
            self.draw_type = game_object.SceneryObject
            self.entity_variables(10, 200, self.draw_type)
            self.toggle_door_textbox()
        self.sceneryButton.onClick = onSceneryClick
        self.sceneryButton.realign(self.camera)
        self.buttons.append(self.sceneryButton)
        #sets draw type to enemy
        self.enemyButton = button.Button(15, -250, self.button_font_big, (255,255,255), 100, 'Enemy', (0,1))
        def onEnemyClick():
            self.draw_type = enemy.Enemy
            self.entity_variables(10, 200, self.draw_type)
            self.parallax = 1
            self.toggle_door_textbox()
        self.enemyButton.onClick = onEnemyClick
        self.enemyButton.realign(self.camera)
        self.buttons.append(self.enemyButton)
        #sets draw type to door
        self.doorButton = button.Button(15, -300, self.button_font_big, (255,255,255), 100, 'Door', (0,1))
        def onDoorClick():
            self.draw_type = door.Door
            self.entity_variables(10, 200, self.draw_type)
            self.parallax = 1
            self.toggle_door_textbox()
        self.doorButton.onClick = onDoorClick
        self.doorButton.realign(self.camera)
        self.buttons.append(self.doorButton)
        #load the variables that can be edited
        self.entity_variables(10, 200, game_object.StaticObject) #this would normally pass in self.draw_type
     
    def draw_menu(self, screen):
        '''draws the menu'''
        #draw background of the side bar
        self.menu_back.height = screen.get_size()[1]
        pygame.draw.rect(screen, (0,0,0), self.menu_back)
        self.textbox.draw(screen)
        self.door_textbox.draw(screen)
        button.buttons_draw(self, screen, self.buttons)
    
    def toggle_door_textbox(self):
        '''simple fix for togling the textbox'''
        if self.draw_type == door.Door:
            self.door_textbox.rect.x = 10
        else:
            self.door_textbox.rect.x = -100
            self.door_textbox.text = ''

    def entity_variables(self, x, y, entity_type):
        #clear the current buttons in the list
        for attr_button in self.attr_buttons:
            if attr_button in self.buttons:
                self.buttons.remove(attr_button)
        self.attr_buttons[:] = []
        entity_var = entity_type.ATTRIBUTES
        y_offset = 0 #used for vertical spacing
        '''treat this as one big button and get the y of the mouse to find which button is clicked'''
        for var in entity_var:
            varButton = button.Button(x, y + y_offset, self.button_font_small, (255,255,255), 100, var['name']+':', (0,0), False, var['init'], var['name'])
            def onVarClick():
                '''get location of mouse click'''
                for i in range(len(self.attr_buttons)):
                    if y + (varButton.rect.height * (i+1)) > pygame.mouse.get_pos()[1]:
                        self.attr_selected = i
                        break
            varButton.onClick = onVarClick
            y_offset += varButton.rect.height
            self.attr_buttons.append(varButton)
        self.attr_selected = 0
        self.buttons += self.attr_buttons
    
    def load_images(self, path):
        ''' 
        Loads image for the editor to use
        @author: Kristofer Brink (kpb23) 
        '''
        files = sorted(os.listdir('../images/' + path))
        files_png = [i for i in files if i.endswith('.png')]
        images = {}
        for i in files_png:
            new_path = path + i
            images[new_path] = self.texture_cache.load(new_path)
        return images

        