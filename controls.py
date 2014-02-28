import pygame
import gl_utilities
import math

from pygame.constants import *

def process_control_events():
    for e in pygame.event.get( (JOYAXISMOTION,
                                JOYBALLMOTION,
                                JOYHATMOTION,
                                JOYBUTTONUP,
                                JOYBUTTONDOWN,
                                KEYDOWN,
                                KEYUP) ):
        pass

class JoystickControl:

    def __init__(self, id=0):
        pygame.joystick.init()
        self._joystick=pygame.joystick.Joystick(id)
        self._joystick.init()

        self._deadzone=0.1

    def get_throttle(self):
        value=self._joystick.get_axis(1)
        if self._deadzone < math.fabs(value):
            return -value
        else:
            return 0.0

    def get_rotate(self):
        value=self._joystick.get_axis(0)
        if self._deadzone < math.fabs(value):
            return -value
        else:
            return 0.0

    def get_beam_angle(self):

        if self.get_beam_activated():
            axes=(self._joystick.get_axis(2),self._joystick.get_axis(3))
            return math.atan2( *axes )
        else:
            return 0.0

    def get_beam_activated(self):
        axes=(self._joystick.get_axis(2),self._joystick.get_axis(3))
        return (self._deadzone < math.fabs(axes[0]) or
                self._deadzone < math.fabs(axes[1]))

    def fire(self):
        return self._joystick.get_button(0)

ARROWS=0
WADS=1

class KeyboardControl:

    def __init__(self, type=ARROWS):

        if type is ARROWS:
            self._up=K_UP
            self._left=K_LEFT
            self._right=K_RIGHT
            self._down=K_DOWN
            self._fire=K_SPACE
        else:
            self._up=K_w
            self._left=K_a
            self._right=K_d
            self._down=K_s
            self._fire=K_LCTRL

    def get_throttle(self):
        if pygame.key.get_pressed()[self._up]:
            return 1.0
        else:
            return 0.0

    def get_rotate(self):
        if pygame.key.get_pressed()[self._left]:
            return 1.0
        elif pygame.key.get_pressed()[self._right]:
            return -1.0
        else:
            return 0.0

    def get_beam_angle(self):
        return 0.0

    def get_beam_activated(self):
        return pygame.key.get_pressed()[self._down]

    def fire(self):
        return pygame.key.get_pressed()[self._fire]

if __name__ == "__main__":

    pygame.init()

    clock=pygame.time.Clock()

    c=Controls()

    while True:

        clock.tick(2)
        Controls.process_events()
        
        print "throttle: %f  rotate: %f  beam activated %d  beam angle: %f\r" % (c.get_throttle(),
                                                              c.get_rotate(),
                                                              c.get_beam_activated(),
                                                              c.get_beam_angle(),)
