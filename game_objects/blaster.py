import pygame, math
from OpenGL.GL import *

from utils import gl_utilities
from utils.vector2d import Vector2D
from utils.sprite import Sprite



class Blaster:

    def __init__(self, beam_color, position, direction):

        self.speed=15.0
        self.time_to_live=1.5

        self.beam_color=beam_color

        self.position=Vector2D(position[0], position[1])
        self.velocity=direction*self.speed

        self.state=Blaster.ENROUTE

        self.glow_max_alpha=1.0
        self.glow_min_alpha=0.5
        self.glow_period=1000.0
        self.glow_w=0.0
        self.glow_amplitude=\
          (self.glow_max_alpha-self.glow_min_alpha)

        self.max_explode_size=1.5
        self.explode_size=self.max_explode_size
        self.explode_time=0.25

    def _glow_brightness(self):
        return math.fabs(math.sin(self.glow_w))*self.glow_amplitude+self.glow_min_alpha
        
    @gl_utilities.sprites_configuration
    def draw(self):
        
        glPushMatrix()
        glLoadIdentity()
        glTranslate( -self.position.x, -self.position.y, -10.0 )

        if self.state is Blaster.ENROUTE:

            Sprite.glow.draw( position=(-0.25, 0.25, 0.0),
                              scale=0.5,
                              color=self.beam_color )
        
            pulsating_glow_color=(self.beam_color[0],
                                  self.beam_color[1],
                                  self.beam_color[2],
                                  self._glow_brightness())

            Sprite.glow.draw( position=(-0.5, 0.5, 0.0),
                              color=pulsating_glow_color )

        elif self.state is Blaster.EXPLODE:

            center_size=self.explode_size/2
            half_center_size=center_size

            Sprite.glow.draw(position=(-half_center_size,half_center_size,0.0),
                             scale=center_size,
                             color=self.beam_color )
        
            Sprite.glow.draw( position=(-self.explode_size/2, self.explode_size/2, 0.0),
                              scale=self.explode_size,
                              color=self.beam_color )

        glPopMatrix()

    def update(self,clock,targets):

        seconds_passed=0.001*clock.get_time()

        if self.state is Blaster.ENROUTE:

            # vary the glow alpha
            percent_glow_period = (clock.get_time()/self.glow_period)
            self.glow_w += 2*math.pi*percent_glow_period
            if 2*math.pi < self.glow_w:
                self.glow_w %= 2*math.pi

            motion_vector=(self.velocity*seconds_passed)

            c_point=None
            for target in targets:
                c_point=target.bounding_box.test_collision(self.position,
                                                           motion_vector)

                if c_point is not None:
                    target.collide(self, c_point, self.velocity, 0.01)
                    self.position=c_point
                    self.state = Blaster.EXPLODE

            if c_point is None:
                self.position += motion_vector
                self.time_to_live -= seconds_passed

            if self.time_to_live <= 0.0:
                self.state = Blaster.EXPLODE

        elif self.state is Blaster.EXPLODE:

            self.explode_size -= (seconds_passed/
                                  self.explode_time)*self.max_explode_size

            if self.explode_size <= 0.0:
                self.state = Blaster.OFF


Blaster.ENROUTE=0
Blaster.EXPLODE=1
Blaster.OFF=2

