import pygame, math
from OpenGL.GL import *

from sprite import Sprite

class Beam:

    def __init__(self):
        self.origin=(0.0, 0.0, 0.0)
        self.percent_extended=0.0
        self.length=10.0
        self.angle=0.0

        self.beam_color=(0.5, 1.0, 0.5, 1.0)
        self.glow_color=(0.75, 1.0, 0.75, 1.0)

        self.state=Beam.OFF

        self.time_to_extend=250.0
        self.time_to_collapse=100.0
        self.time_to_pulse=1250.0

        self.pulse_spacing=0.5
        self.time_to_pulse_one_space=self.time_to_pulse/self.length*self.pulse_spacing
        self.pulse_offset=0.0

        self.glow_max_alpha=1.0
        self.glow_min_alpha=0.5
        self.glow_period=1000.0
        self.glow_w=0.0
        self.glow_amplitude=\
          (self.glow_max_alpha-self.glow_min_alpha)

        self.extend_w=0.0

    def _glow_brightness(self):
        return math.fabs(math.sin(self.glow_w))*self.glow_amplitude+self.glow_min_alpha
        
    def draw(self):

        if self.state not in (Beam.OFF, Beam.COLLAPSED) :

            glEnable (GL_BLEND)
            glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
            glEnable(GL_TEXTURE_2D)
        
            glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
            
            glDisable(GL_DEPTH_TEST)

            glPushMatrix()

            glRotate( self.angle, 0.0, 0.0, 1.0 ) 

            # the main beam
            Sprite.beam.draw( position=(0.0, 0.125, 0.0),
                              scale=( self.length*self.percent_extended,
                                      0.25 ),
                              color=self.beam_color )

            # draw pulses traveling along the main beam
            glPushMatrix()

            pulse_location=self.pulse_offset
            glTranslate( self.pulse_offset, 0.0, 0.0 )

            while pulse_location <= self.length*self.percent_extended:

                Sprite.glow.draw( position=(-0.25, 0.25, 0.0),
                                  scale=0.5,
                                  color=self.beam_color )

                glTranslate( self.pulse_spacing, 0.0, 0.0 )
                pulse_location += self.pulse_spacing

            glPopMatrix()

            # draw a pulse at the end of the beam, and a
            # half of the pulsating glow centered around the tip
            glPushMatrix()

            glTranslate( self.length*self.percent_extended, 0.0, 0.0 )

            Sprite.glow.draw( position=(-0.25, 0.25, 0.0),
                              scale=0.5,
                              color=self.beam_color )

            pulsating_glow_color=(self.glow_color[0],
                                  self.glow_color[1],
                                  self.glow_color[2],
                                  self._glow_brightness())

            Sprite.glow.draw( position=(-0.0, 0.5, 0.0),
                              src_rect=((0.5,0.0),(1.0,1.0)),
                              scale=(0.5,1.0),
                              color=pulsating_glow_color )

            glPopMatrix()

            # draw the remaining half of the pulsating glow
            # stretched out along the beam
            Sprite.glow.draw( position=(0.0, 0.5, 0.0),
                              src_rect=((0.0,0.0),(0.5,1.0)),
                              scale=(self.length*self.percent_extended,1.0),
                              color=pulsating_glow_color )

            glPopMatrix()

    def on(self):
        if self.state in (Beam.OFF, Beam.COLLAPSED):
            self.state = Beam.EXTENDING

    def is_on(self):
        return self.state in (Beam.STEADY_STATE,
                              Beam.EXTENDING)

    def off(self):
        if self.state in (Beam.STEADY_STATE, Beam.EXTENDING):
            self.state = Beam.COLLAPSING
        elif self.state is Beam.COLLAPSED:
            self.state = Beam.OFF

    def is_off(self):
        return self.state is Beam.OFF

    def is_collapsed(self):
        return self.state is Beam.COLLAPSED

    def is_extending(self):
        return self.state == Beam.EXTENDING

    def is_collapsing(self):
        return self.state == Beam.COLLAPSING

    def update(self,clock):

        if self.state is Beam.OFF:
            return

        # move pulses down the beam 
        percent_pulse_travel = (clock.get_time()/self.time_to_pulse_one_space)

        self.pulse_offset += self.pulse_spacing*percent_pulse_travel

        if self.pulse_spacing < self.pulse_offset:
            self.pulse_offset %= self.pulse_spacing

        # vary the glow alpha
        percent_glow_period = (clock.get_time()/self.glow_period)
        self.glow_w += 2*math.pi*percent_glow_period
        if 2*math.pi < self.glow_w:
            self.glow_w %= 2*math.pi

        if self.state is Beam.EXTENDING:
            self.extend_w += (clock.get_time()/self.time_to_extend)*(math.pi/2)

            previous_percent_extended=self.percent_extended
            self.percent_extended = math.sin(self.extend_w)

            if (1.0 <= self.percent_extended or
                self.percent_extended <= previous_percent_extended):
                self.state = Beam.STEADY_STATE
                self.percent_extended = 1.0
                self.extend_w = math.pi/2

        elif self.state is Beam.STEADY_STATE:
            pass
        
        elif self.state is Beam.COLLAPSING:

            self.extend_w -= (clock.get_time()/self.time_to_extend)*(math.pi/2)
            self.percent_extended = math.sin(self.extend_w)

            if self.percent_extended <= 0.0:
                self.state = Beam.COLLAPSED
                self.percent_extended = 0.0
                self.extend_w = 0.0
                          
Beam.OFF=0
Beam.EXTENDING=1
Beam.STEADY_STATE=2
Beam.COLLAPSING=3
Beam.COLLAPSED=4


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

    beam=Beam()

    while 1:

        clock.tick()
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == MOUSEBUTTONDOWN:

                if beam.is_off():
                    beam.on()

                elif beam.is_on():
                    beam.off()
                    
            elif e.type == MOUSEMOTION and (beam.is_on()):
                i, j = e.rel
                beam.angle += (j*0.75)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(-0.0, 0.0, -5.0)

        glScale(0.5, 0.5,0.0)

        beam.update(clock)
        beam.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main() 



