import pygame, math, random, new, config
from OpenGL.GL import *
from OpenGL.GLU import *

from pygame.mixer import Sound 

from utils import gl_utilities
from utils.collisions import BoundingPolygon
from utils.obj import OBJ
from utils.vector2d import Vector2D

from game_objects.beam import Beam
from game_objects.plume import Plume
from game_objects.blaster import Blaster


class Rocket:

    def __init__(self,
                 obj_file,
                 gravity,
                 maximum_speed,
                 maximum_acceleration,
                 maximum_roll_rate,
                 controls,
                 blaster_list,
                 blaster_color):

        self.gravity=gravity
        
        self.maximum_speed=maximum_speed
        self.maximum_acceleration=maximum_acceleration
        self.maximum_roll_rate=maximum_roll_rate
        
        self.controls=controls

        self.blaster_list=blaster_list
        
        self.blaster_color=blaster_color
        
        self.angle=0.0

        self.model=OBJ(config.basedir+"/assets", obj_file)

        self.position=Vector2D(0.0,0.0)
        self.velocity=Vector2D(0.0,0.0)

        self.bounding_box=BoundingPolygon( (Vector2D(-1.0, 1.0),
                                            Vector2D(1.0, 1.0),
                                            Vector2D(1.0, -1.0),
                                            Vector2D(0.0, -2.0),
                                            Vector2D(-1.0, -1.0)) )

        self.weight=1.0

        self.beam=Beam()
        self.plume=Plume()

        self.blaster_sound=Sound(config.basedir+"/assets/Laser_Shoot_2.wav")
        self.engine_sound=Sound(config.basedir+"/assets/engine.wav")
        self.engine_sound.set_volume(0.075)

        self.fire_counter=3

    @gl_utilities.sprites_configuration
    def _draw_sprites(self):
        self.beam.draw()
        self.plume.draw()

    @gl_utilities.shader_configuration(config.basedir+"/shaders/vertex.txt", 
                                       config.basedir+"/shaders/fragment.txt")
    def _draw_shader(self):
        glPushMatrix()

        glRotate(self.angle,0.0,0.0,1.0)
        glRotate(90.0,-1.0,0.0,0.0)

        glCallList(self.model.gl_list)
        glPopMatrix()

    def draw(self):

        glPushMatrix()

        glTranslate(-self.position.x, -self.position.y, 0.0)

        self._draw_sprites()
        self._draw_shader()

        glPopMatrix()

#        _draw_bounding_box(self.bounding_box)

    def _fire(self):
#    angle, position, blaster_color, blaster_list):

        direction=Vector2D(math.sin(math.radians(self.angle)),
                           -math.cos(math.radians(self.angle)))

        self.blaster_list.append(Blaster(self.blaster_color,
                                         self.position+2.001*direction,
                                         direction))

    def update(self,clock):

        seconds_passed=clock.get_time()/1000.0

        self.angle += (self.maximum_roll_rate*
                       self.controls.get_rotate()*
                       seconds_passed)

        if 0 < self.controls.get_throttle():
            if self.plume.is_off():
                self.plume.on()

            self.engine_sound.play()

            self.plume.throttle=self.controls.get_throttle()

            thrust=self.maximum_acceleration*seconds_passed*self.plume.throttle

            accel=Vector2D(math.sin(math.radians(self.angle))*thrust,
                           -math.cos(math.radians(self.angle))*thrust)
            
            self.velocity += accel
            
        elif self.controls.get_throttle() <= 0 and self.plume.is_on():
            self.plume.off()
            self.engine_sound.stop()

        self.velocity += self.gravity*seconds_passed

        speed = self.velocity.length()
 
        if self.maximum_speed < speed:
            self.velocity *= self.maximum_speed/speed

        self.position += self.velocity*seconds_passed

        self.bounding_box.position=self.position
        self.bounding_box.angle=self.angle

        self.bounding_box.update()

        if self.controls.get_beam_activated() and self.beam.is_off():
            tmp_beam_angle = self.controls.get_beam_angle()

            if tmp_beam_angle is None:
                self.beam.angle = self.angle + 90
            else:
                self.beam.angle = math.degrees(tmp_beam_angle)

            self.beam.on()
        elif not self.controls.get_beam_activated():
            self.beam.off()

        if self.controls.fire() or (0 < self.fire_counter < 3) :
            if 0 < self.fire_counter:
                self.blaster_sound.play()
                self._fire()
                self.fire_counter -= 1
        else:
            self.fire_counter=3

        self.beam.update(clock)
        self.plume.update(clock)

        self.plume.angle = self.angle


        if self.beam.is_on() and not self.beam.is_extending():
            self.beam.off()
