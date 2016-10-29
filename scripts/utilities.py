''' CS 108
Created Fall 2016
contains utilities used for uncommon functions
@author: Mark Wissink (mcw33)
'''

import pygame, sys

def load(image_location, alpha=True):
    ''' CS 108
    Created Fall 2014
    @author: Kristofer Brink (kpb23)
    Loads an image from a location and auto does alpha unless if specified otherwise
    (string, bool) -> pygame surface
    '''
    try:
        surface = pygame.image.load('../images/' + image_location)
        if alpha: # http://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert
            surface = surface.convert_alpha()
        else:
            surface = surface.convert()
        return surface
    except:
        # If image cannot load instead make it a surf that shows the user what image was not able to load
        print('Cannot Load image from path:', image_location)
        
        myfont = pygame.font.SysFont("monospace", 16)
        return myfont.render("Couldn't load " + image_location, 1, (0,0,0))

def merge_dicts(x, y):
    '''
    merges two dictionaries
    '''
    #http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
    z = x.copy()
    z.update(y)
    return z