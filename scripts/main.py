''' CS 108
Created Fall 2016
Runs the game
@author: Mark Wissink (mcw33)
'''

''''
http://www.pygame.org/projects/9/108/
''''
import pygame, os, sys
from game import GameState

def main():
    #http://thepythongamebook.com/en:pygame:step006
    #set up the game and run the main loop
    #os.environ['SDL_VIDEO_CENTERED'] = '1' #center window on the screen
    pygame.init() #initiate pygame
    screen = pygame.display.set_mode((900, 600), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
    clock = pygame.time.Clock() #initiates clock for time usage, such as deltatime and fps
    frameRate = 60
    pygame.display.set_caption('Sorasu') #set the title of the application
    #pygame.display.set_icon(util.load('icon.png')) #set the icon of the application
    currentState = GameState()
    
    #main game loop
    while True:
        deltaTime = clock.tick(frameRate)/100.0 #get time pasted between each frame in seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #if the application is closed - terminate all processes
                pygame.quit()
                sys.exit()
                return
            elif event.type == pygame.VIDEORESIZE: #if screen is resized
                screen = pygame.display.set_mode(event.dict['size'],pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
                currentState.camera.resize(screen)      
            else:
                currentState.eventHandler(event)
        currentState.draw(pygame.draw, screen)
        currentState.update(deltaTime)   
        pygame.display.flip() #updates the screen
        

if __name__ == "__main__":
    main()