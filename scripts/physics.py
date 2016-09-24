''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''
import pygame, sys
import math

'''
physics functions only apply if an entity's collision mask is a rectangle



http://www.metanetsoftware.com/technique/tutorialA.html

http://www.dyn4j.org/2010/01/sat/

http://wiki.roblox.com/index.php?title=2D_Collision_Detection


http://codereview.stackexchange.com/questions/47111/implementation-of-sat-separating-axis-theorem
http://stackoverflow.com/questions/6013333/separating-axis-theorem-and-python
'''
def collide(entity1, entity2):
    '''
    check for collisions between entities and then send resolving vector
    '''
    overlap = math.inf
    #obtain axis from entity2 assuming entity1 is the player and won't change its rotation
    axis_list = get_axis(entity2.get_corners())
    for axis in axis_list:
        # Project the shapes onto the axis
        entity1_projection = project(axis, entity1.get_corners())
        entity2_projection = project(axis, entity2.get_corners())
        #test if the projections overlap
        for projection in [(entity1_projection[1], entity2_projection[0], 1), (entity2_projection[1], entity1_projection[0], -1)]:
            p1, p2, sign = projection
            if not p1 > p2:
                return False
            new_overlap = sign*(p1 - p2)
            if abs(new_overlap) < abs(overlap):
                overlap = new_overlap
                current_axis = axis
    mtv = (current_axis[0]*overlap, current_axis[1]*overlap)
    return mtv
def get_axis(corners):
    '''
    gets all the axis necessary for collision
    '''
    axis = []
    for i in range(len(corners)):
        #create axis and make it perpendicular to face
        vec = (corners[i][0] - corners[i-1][0], corners[i][1] - corners[i-1][1])
        vec = normalize(perpendicular(vec))
        axis.append(vec)
    return axis
def project(axis, corners):
    '''
    project the points on the axis
    '''
    min_point = dot_product(corners[0], axis)
    max_point = min_point
    for i in range(len(corners)):
        p = dot_product(corners[i], axis)
        if (p < min_point):
            min_point = p
        elif (p > max_point):
            max_point = p
    projection = (min_point, max_point)
    return projection

def perpendicular(vec):
    '''
    Return the perpendicular vector.
    '''
    new_vec = (vec[1], -vec[0])
    return new_vec

def dot_product(vec1, vec2):
    '''
    Calculate the dot product of two vectors.
    '''
    x1, y1 = vec1
    x2, y2 = vec2
    return x1*x2 + y1*y2

def normalize(vec):
    '''
    Normalize a given vector.
    '''
    # Average time: 9.633639630529273e-07s
    x, y = vec
    magnitude = 1/math.hypot(x, y)
    return magnitude*x, magnitude*y