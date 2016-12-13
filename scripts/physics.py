''' CS 108
Created Fall 2016
parent class for all objects used in game
@author: Mark Wissink (mcw33)
'''
import pygame, sys
import math

'''
referenced material for creating library
http://www.metanetsoftware.com/technique/tutorialA.html
http://www.dyn4j.org/2010/01/sat/
http://wiki.roblox.com/index.php?title=2D_Collision_Detection
http://codereview.stackexchange.com/questions/47111/implementation-of-sat-separating-axis-theorem
http://stackoverflow.com/questions/6013333/separating-axis-theorem-and-python
'''
def collide(entity1, entity2):
    '''check for collisions between entities and then send resolving vector'''
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

def collide_test(entity1, entity2):
    '''check for collisions between entities with the dynamics test offsets only for checking'''
    #obtain axis from entity2 assuming entity1 is the player and won't change its rotation
    axis_list = get_axis(entity2.get_corners())
    for axis in axis_list:
        # Project the shapes onto the axis
        entity1_projection = project(axis, entity1.get_corners_test())
        entity2_projection = project(axis, entity2.get_corners())
        #test if the projections overlap
        for projection in [(entity1_projection[1], entity2_projection[0], 1), (entity2_projection[1], entity1_projection[0], -1)]:
            p1, p2, sign = projection
            if not p1 > p2:
                return False
    return True
def get_axis(corners):
    '''gets all the axis necessary for collisio'''
    axis = []
    for i in range(len(corners)):
        #create axis and make it perpendicular to face
        vec = (corners[i][0] - corners[i-1][0], corners[i][1] - corners[i-1][1])
        vec = normalize(perpendicular(vec))
        axis.append(vec)
    return axis
def project(axis, corners):
    '''project the points on the axis'''
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
    '''Return the perpendicular vector.'''
    new_vec = (vec[1], -vec[0])
    return new_vec

def dot_product(vec1, vec2):
    '''Calculate the dot product of two vectors.'''
    x1, y1 = vec1
    x2, y2 = vec2
    return x1*x2 + y1*y2

def normalize(vec):
    '''Normalize a given vector.'''
    # Average time: 9.633639630529273e-07s
    x, y = vec
    try:
        magnitude = 1/math.hypot(x, y)
    except:
        magnitude = 0
    return magnitude*x, magnitude*y

def resolve_collision(entity1, entity2):
    '''resolve collision between two objects'''
    #https://gamedevelopment.tutsplus.com/tutorials/how-to-create-a-custom-2d-physics-engine-the-basics-and-impulse-resolution--gamedev-6331
    res_vec = entity2.vel - entity1.vel
    normal = pygame.math.Vector2(normalize(res_vec))
    #calculate relative velocity in terms of the normal direction
    vel_normal = dot_product(res_vec, normal)
    #do not resolve if velocities are separating
    if normal[1] < -0.8 and normal[1] > -1:
        return False
    #calculate restitution
    e = min(entity1.bounce, entity2.bounce)
    #calculate impulse scalar
    j = -(1 + e) * vel_normal
    j /= entity1.inv_mass + entity2.inv_mass
    #apply impulse
    impulse = j * normal
    entity1.vel -= entity1.inv_mass * impulse
    entity2.vel += entity2.inv_mass * impulse
    return True