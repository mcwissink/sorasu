''' CS 108
Created Fall 2016
Runs the game
@author: Mark Wissink (mcw33)
'''
import pygame, os, sys
import utilities
from game import GameState
from menu import MenuState
from editor import EditorState

def main():
    #http://thepythongamebook.com/en:pygame:step006
    #set up the game and run the main loop`
    #os.environ['SDL_VIDEO_CENTERED'] = '1' #center window on the screen
    pygame.init() #initiate pygame
    screen = pygame.display.set_mode((900, 600), pygame.HWSURFACE|pygame.RESIZABLE)
    #screen overlay for a e s t h e t i c
    overlay = utilities.load('../images/overlay/overlay.png')
    overlay = pygame.transform.scale(overlay, screen.get_size())
    clock = pygame.time.Clock() #initiates clock for time usage, such as deltatime and fps
    frameRate = 0
    pygame.display.set_caption('Sorasu') #set the title of the application
    pygame.display.set_icon(utilities.load('icon.png')) #set image for application
    #pygame.display.set_icon(util.load('icon.png')) #set the icon of the application
    currentState = MenuState()
    #main game loop
    while True:
        deltaTime = clock.tick(frameRate)/1000.0 #get time pasted between each frame in seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if the application is closed - terminate all processes
                pygame.quit()
                sys.exit()
                return
            elif event.type == pygame.VIDEORESIZE: #if screen is resized
                screen = pygame.display.set_mode(event.dict['size'],pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
                #resize the overlay
                overlay = pygame.transform.scale(overlay, screen.get_size())
                if hasattr(currentState, 'camera'):
                    currentState.camera.resize(screen)     
            else:
                currentState = currentState.eventHandler(event) or currentState
        currentState.draw(pygame.draw, screen)
        #screen.blit(overlay, (0,0))
        currentState.update(deltaTime)
        pygame.display.flip() #updates the screen
        

if __name__ == "__main__":
    main()