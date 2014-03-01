import pygame, math, gl_utilities,random
from OpenGL.GL import *



from vector2d import Vector2D
from sprite import Sprite

class Starfield:

    def __init__(self, viewport, number_of_stars):

        random.seed()
        self.stars=[_create_star(viewport) for i in xrange(0, number_of_stars)]

        self.gl_list=None

    @gl_utilities.sprites_configuration
    def draw(self):

        if self.gl_list is not None:
            glCallList(self.gl_list)
        else:

            self.gl_list = glGenLists(1)
            glNewList(self.gl_list, GL_COMPILE)

            glPushMatrix()

            for star in self.stars:
                star.draw()

            glPopMatrix()

            glEndList()

class Star:

    def __init__(self, position, brightness, size):

        self.position=position
        self.brightness=brightness
        self.size=size

    def draw(self):

        glLoadIdentity()

        glTranslate(-self.position.x, -self.position.y, -10.0)

        Sprite.glow.draw( position=(self.size/2, self.size/2, 0.0),
                          scale=self.size,
                          color=(1.0, 1.0, 1.0, self.brightness) )


def _create_star( viewport ):

        (viewport_left,
         viewport_right,
         viewport_bottom,
         viewport_top)=viewport

        min_brightness, max_brightness = 0.33, 0.66
        min_size,       max_size       = 0.1,  0.25

        return Star( Vector2D(random.uniform(viewport_left, viewport_right),
                              random.uniform(viewport_bottom, viewport_top)),
                     random.uniform(0.33, 0.66),
                     random.uniform(0.1, 0.25) )
                               

        

