from obj import OBJ
import pygame, math, gl_utilities

from OpenGL.GL import *
from OpenGL.GLU import *

from vector2d import Vector2D

from collisions import BoundingPolygon

class Asteroid:

    def __init__(self,
                 obj_file,
                 position,
                 velocity,
                 x_rotational_velocity,
                 y_rotational_velocity,
                 z_rotational_velocity,
                 scale,
                 hit_points,
                 weight):

        if isinstance(obj_file,OBJ):
            self.model=obj_file
        else:
            self.model=OBJ("./assets", obj_file)

        self.position=position

        self.velocity=velocity

        self.x_rotational_velocity=x_rotational_velocity
        self.y_rotational_velocity=y_rotational_velocity
        self.z_rotational_velocity=z_rotational_velocity

        self.x_angle=0
        self.y_angle=0
        self.angle=0

        self.scale=scale

        self.hit_points=hit_points
        self.original_hit_points=hit_points
        
        self.bounding_box=BoundingPolygon( (scale*Vector2D(-1.1, 0.7),
                                            scale*Vector2D(0.0, 1.1),
                                            scale*Vector2D(1.1, 0.7),
                                            scale*Vector2D(1.1, -0.7),
                                            scale*Vector2D(0.0, -1.1),
                                            scale*Vector2D(-1.1, -0.7)) )

        self.weight=weight

    @gl_utilities.shader_configuration("./shaders/vertex.txt", "./shaders/fragment.txt")
    def draw(self):

        glPushMatrix()

        glTranslate(-self.position.x, -self.position.y, -10.0)

        glScale(self.scale, self.scale, self.scale)

        glRotate(self.x_angle, 1.0, 0.0, 0.0)
        glRotate(self.y_angle, 1.0, 0.0, 0.0)
        glRotate(self.angle, 1.0, 0.0, 0.0)

        glCallList(self.model.gl_list)

        glPopMatrix()


    def update(self,clock):

        seconds_passed=clock.get_time()/1000.0

        if 2.0 < self.velocity.length():
            self.velocity = self.velocity.normalized()*2.0
        
        self.position += self.velocity*seconds_passed

        self.x_angle += self.x_rotational_velocity*seconds_passed
        self.y_angle += self.y_rotational_velocity*seconds_passed
        self.angle += self.z_rotational_velocity*seconds_passed

        self.bounding_box.position=self.position
        self.bounding_box.update()

    def explode(self):

        new_hitpoints=int(self.original_hit_points/2)

        if 0 < new_hitpoints:

            new_weight_factor=0.5
            new_scale_factor=2.0/3.0


            return [ Asteroid( self.model,
                               self.position + (1, 1),
                               self.velocity + (1, 1),
                               self.x_rotational_velocity,
                               self.y_rotational_velocity,
                               self.z_rotational_velocity,
                               new_scale_factor*self.scale,
                               new_hitpoints,
                               new_weight_factor*self.weight),
                     Asteroid( self.model,
                               self.position - (1, 1),
                               self.velocity - (1, 1),
                               self.x_rotational_velocity,
                               self.y_rotational_velocity,
                               self.z_rotational_velocity,
                               new_scale_factor*self.scale,
                               new_hitpoints,
                               new_weight_factor*self.weight) ]
        else:
            return [] 
                     

