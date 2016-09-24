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
vec*vec is the dot product
'''
def collide(entity1, entity2):
        edges = entity1._edges + entity2._edges
        # The edges to test against for an axis of separation
        _norm = geo.normalize
        _perp = geo.perpendicular
        # I store all the functions I need in local variables so
        # python doesn't have to keep re-evaluating their positions
        # in the for loop.

        entity1_coords = entity1.coordinates
        entity2_coords = entity2.coordinates

        project_entity1 = entity1._project
        project_entity2 = entity2._project

        projections = [] # A list of projections in case there is a collision.
        # We can use the projections to find the minimum translation vector.
        append_projection = projections.append

        for edge in edges:
            edge = _norm(edge)
            # Calculate the axis to project the shapes onto
            axis = _perp(edge)

            # Project the shapes onto the axis
            entity1_projection = project_entity1(axis, entity1_coords)
            entity2_projection = project_entity2(axis, entity2_coords)

            if not (entity1_projection[1] > entity2_projection[0] and \
                    entity1_projection[0] < entity2_projection[1]     ): # Intersection test
                # Break early if an axis has been found.
                return False
            overlap = entity1_projection[1] - entity2_projection[0]
            append_projection((
                axis[0] * overlap,
                axis[1] * overlap
                )) # Append the projection to the list of projections if it occurs
        return projections

def normalize(vector):
    """
    Normalize a given vector.
    """
    # Average time: 9.633639630529273e-07s
    x, y = vector
    magnitude = 1/math.sqrt(x*x + y*y)
    return magnitude*x, magnitude*y

def perpendicular(vector):
    """
    Return the perpendicular vector.
    """
    # Average time: 2.1031882874416398e-07s
    x, y = vector
    return y, -x

def dot_product(v1, v2):
    """
    Calculate the dot product of two vectors.
    """
    # Average time: 2.617608074634745e-07s
    x1, y1 = v1
    x2, y2 = v2
    return x1*x2 + y1*y2