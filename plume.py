import pygame, math
from OpenGL.GL import *

from sprite import Sprite

class Plume:

    def __init__(self):
        self.origin=(0.0, 0.0, 0.0)
        self.angle=0.0
        self.length=4.0
        self.width=1.5

        self.throttle=1.0

        self.min_throttle_opacity=0.25
        self.max_throttle_opacity=1.0

        self.min_throttle_length_percent=0.15
        self.max_throttle_length_percent=0.67

        self.min_throttle_width_percent=0.75
        self.max_throttle_width_percent=1.0

        self.opacity=0.0

        self.color=(0.5, 0.5, 1.0, 1.0)
        self.glow_color=(0.5, 0.5, 1.0)

        self.glow_period=5000
        self.glow_counter=0.0
        self.glow_min_alpha=0.75
        self.glow_max_alpha=0.9
        self.glow_amplitude=self.glow_max_alpha - self.glow_min_alpha

        self.short_time=50
        self.medium_time=50
        self.long_time=50

        self.period = self.short_time + self.medium_time + self.long_time

        self.counter=0.0

        self.fade_time=100.0

        self.flicker = Plume.SHORT
        self.state = Plume.OFF

    def _interp(self, max, min, a):
        return a*(max-min) + min

    def _glow_brightness(self):
        w = self.glow_counter/self.glow_period*2*math.pi
        return math.fabs(math.sin(w))*self.glow_amplitude + self.glow_min_alpha

    def _throttle_opacity(self):
        return self._interp(self.max_throttle_opacity,
                            self.min_throttle_opacity,
                            self.throttle)

    def _throttle_width(self):
        return self._interp(self.max_throttle_width_percent,
                            self.min_throttle_width_percent,
                            self.throttle)

    def _throttle_length(self):
        return self._interp(self.max_throttle_length_percent,
                            self.min_throttle_length_percent,
                            self.throttle)

    def draw(self):


            throttle_opacity=self._throttle_opacity()
            throttle_width=self._throttle_width()
            throttle_length=self._throttle_length()

            if self.flicker is Plume.SHORT:
                percent_length=0.5

            elif self.flicker is Plume.MEDIUM:
                percent_length=0.75

            elif self.flicker is Plume.LONG:
                percent_length=1.0

            scale=(self.length*throttle_length*percent_length,
                   self.width*throttle_width)

            glPushMatrix()

            glRotate(self.angle-90, 0.0, 0.0, 1.0)

            Sprite.plume.draw( position=(1.0, scale[1]/2),
                               scale=scale,
                               color=(self.color[0],
                                      self.color[1],
                                      self.color[2],
                                      self.opacity*throttle_opacity) )

            Sprite.glow.draw( position=(0.0, 1.0),
                              scale=2.0,
                              color=(self.glow_color[0],
                                     self.glow_color[1],
                                     self.glow_color[2],
                                     self._glow_brightness()*self.opacity*throttle_opacity ) )

            Sprite.glow.draw( position=(0.5, 0.5),
                               color=(self.color[0],
                                      self.color[1],
                                      self.color[2],
                                      self.opacity*throttle_opacity*1.1) )

            glPopMatrix()

    def on(self):
        if self.state in (Plume.OFF, Plume.FADE_OUT):
            self.state = Plume.FADE_IN

    def is_on(self):
        return self.state in (Plume.STEADY_STATE, Plume.FADE_IN)

    def off(self):
        if self.state in (Plume.STEADY_STATE, Plume.FADE_IN):
            self.state = Plume.FADE_OUT

    def is_off(self):
        return self.state in (Plume.OFF, Plume.FADE_OUT)

    def update(self,clock):

        if self.state is Plume.OFF:
            return

        self.glow_counter += clock.get_time()
        
        if self.glow_period < self.glow_counter:
            self.glow_counter %= self.glow_period

        self.counter += clock.get_time()

        if self.period < self.counter:
            self.counter %= self.period

        if self.counter < self.short_time:
            self.flicker = Plume.SHORT

        elif self.counter < self.short_time+self.medium_time:
            self.flicker = Plume.MEDIUM

        else:
            self.flicker = Plume.LONG


        if self.state is Plume.FADE_IN:
            self.opacity += (clock.get_time()/self.fade_time)

            if 1.0 <= self.opacity:
                self.opacity = 1.0
                self.state = Plume.STEADY_STATE
            
        if self.state is Plume.FADE_OUT:
            self.opacity -= (clock.get_time()/self.fade_time)

            if self.opacity <= 0.0:
                self.opacity = 0.0
                self.state = Plume.OFF

Plume.SHORT=0
Plume.MEDIUM=1
Plume.LONG=2

Plume.OFF=3
Plume.FADE_IN=4
Plume.STEADY_STATE=5
Plume.FADE_OUT=6


def main():

    import sys
    from OpenGL.GLU import gluPerspective
    from pygame.constants import HWSURFACE, OPENGL, DOUBLEBUF, QUIT, MOUSEBUTTONDOWN, FULLSCREEN, MOUSEMOTION

    pygame.init()
    viewport = (800,600)
    hx = viewport[0]/2
    hy = viewport[1]/2
    srf = pygame.display.set_mode(viewport, HWSURFACE | OPENGL | DOUBLEBUF)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport
    gluPerspective(90.0, width/float(height), 1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_COLOR_MATERIAL)

    glClearColor(0.0, 0.0, 0.0, 0.0)

    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_TEXTURE_2D)

    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glDisable(GL_DEPTH_TEST)

    clock=pygame.time.Clock()

    Sprite.init()

    plume=Plume()

    while 1:

        clock.tick()
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == MOUSEBUTTONDOWN:

                if plume.is_off():
                    plume.on()

                elif plume.is_on():
                    plume.off()
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                plume.throttle += (0.005*j)

                if 1.0 < plume.throttle:
                    plume.throttle=1.0
                elif plume.throttle < 0.33:
                    plume.throttle=0.33

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(-0.0, 0.0, -5.0)

        plume.update(clock)
        plume.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main() 



