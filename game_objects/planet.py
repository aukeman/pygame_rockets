import pygame, math, config

from OpenGL.GL import *
from OpenGL.GLU import *

from utils import gl_utilities
from utils.vector2d import Vector2D
from utils.obj import OBJ

class Planet:

    def __init__(self, obj_file, position, scale, rotate_period=0.0, moons=[]):

        self.model=OBJ(config.basedir+"/assets", obj_file)

        self.position=position
        self.scale=scale

        self.rotate_period=rotate_period
        self.rotate_angle=0.0

        self.moons=moons

    @gl_utilities.shader_configuration(config.basedir+"/shaders/vertex.txt", 
                                       config.basedir+"/shaders/fragment.txt")
    def draw(self):

        glPushMatrix()

        glTranslate(-self.position.x, -self.position.y, -20.0)
        
        glRotate(-90.0, 0.6 , -0.4, 0.5)
        glRotate(self.rotate_angle, 0.0, 0.0, 1.0)

        for moon in self.moons:
            moon.draw()

        glScale(self.scale, self.scale, self.scale)

        glCallList(self.model.gl_list)


        glPopMatrix()


    def update(self,clock):
        
        if self.rotate_period != 0.0:

            seconds_passed = 0.001*clock.get_time()

            self.rotate_angle += 360.0*(seconds_passed/self.rotate_period)
            self.rotate_angle %= 360.0


        for moon in self.moons:
            moon.update(clock)
