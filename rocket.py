import pygame, math, gl_utilities, random, new
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *
from pygame.constants import *

from pygame.mixer import Sound 

from sprite import Sprite
from controls import process_control_events, JoystickControl, KeyboardControl, ARROWS, WADS
from collisions import BoundingPolygon
from starfield import Starfield
from planet import Planet
from asteroid import Asteroid

from obj import OBJ

from beam import Beam
from plume import Plume
from blaster import Blaster

from vector2d import Vector2D

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

        self.model=OBJ("./obj_files", obj_file)

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

        self.blaster_sound=Sound("obj_files\Laser_Shoot_2.wav")
        self.engine_sound=Sound("obj_files\engine.wav")
        self.engine_sound.set_volume(0.075)

        self.fire_counter=3

    @gl_utilities.sprites_configuration
    def _draw_sprites(self):
        self.beam.draw()
        self.plume.draw()

    @gl_utilities.shader_configuration("./vertex.txt", "./fragment.txt")
    def _draw_shader(self):
        glPushMatrix()

        glRotate(self.angle,0.0,0.0,1.0)
        glRotate(90.0,-1.0,0.0,0.0)

        glCallList(self.model.gl_list)
        glPopMatrix()

    def _draw_bounding_box(self):
        _draw_bounding_box(self.bounding_box)
        
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
            self.beam.angle = math.degrees(self.controls.get_beam_angle())
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

@gl_utilities.debug_configuration(color=(1.0, 1.0, 1.0), line_width=2.0)
def _draw_bounding_box( bounding_polygon ):
    xfrmed_vertices=bounding_polygon.transformed_vertices
    glBegin(GL_LINE_STRIP)
    for v in xfrmed_vertices:
        glVertex(-v.x, -v.y, 0.0)
    
    glVertex(-xfrmed_vertices[0].x, -xfrmed_vertices[0].y)
    glEnd()

    glBegin(GL_LINE_STRIP)
    glVertex(bounding_polygon.lower_left.x, bounding_polygon.lower_left.y) 
    glVertex(bounding_polygon.lower_left.x, bounding_polygon.upper_right.y) 
    glVertex(bounding_polygon.upper_right.x, bounding_polygon.upper_right.y) 
    glVertex(bounding_polygon.upper_right.x, bounding_polygon.lower_left.y) 
    glVertex(bounding_polygon.lower_left.x, bounding_polygon.lower_left.y) 
    glEnd()


def reposition( viewport, position ):
    
    (viewport_left,
     viewport_right,
     viewport_bottom,
     viewport_top)=viewport

    if viewport_right < position.x:
        position.x -= (viewport_right-viewport_left)
    elif position.x < viewport_left:
        position.x += (viewport_right-viewport_left)

    if viewport_top < position.y:
        position.y -= (viewport_top-viewport_bottom)
    elif position.y < viewport_bottom:
        position.y += (viewport_top-viewport_bottom)

def collide(subject, target, position, velocity, target_weight):

    pos_to_coll=position-subject.position

    value=(pos_to_coll.dot(velocity) / (float(pos_to_coll)*float(velocity)))
    if -1.0 < value < 1.0:
        alpha = math.acos(value)
    else:
        alpha=0

    arm=math.sin(alpha)*float(pos_to_coll)

    # TODO assign weights to collisions and scale added velocity by weight
    subject.velocity += (target_weight/subject.weight)*velocity

    if 0.0 < pos_to_coll.cross(velocity):
        subject.angle += 1.0*float(arm)
    else:
        subject.angle -= 1.0*float(arm)

    if isinstance(subject, Asteroid) and isinstance(target, Blaster):
        subject.hit_points -= 1


def collisions(subject, targets):
    for target in targets:
        if subject is not target:

            collision_point=subject.bounding_box.test_bounding_polygon_collision(target.bounding_box)

            if collision_point is not None:
                reaction=(collision_point-subject.position).normalized()
                reaction *= float(subject.velocity) + float(target.velocity)
                reaction *= -0.5
                    
                subject.collide(target, collision_point, reaction, target.weight)

def main():

    import sys

    pygame.mixer.pre_init(buffer=1024)

#     viewport=gl_utilities.init_gl_viewport(viewport=(1920,1200),
#                                            screen_extents=(-20,20,-20,20),
#                                            display_flags=HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN)

    viewport=gl_utilities.init_gl_viewport(viewport=(800,600),
                                           screen_extents=(-20,20,-20,20),
                                           display_flags=HWSURFACE|OPENGL|DOUBLEBUF)


    gl_utilities.setup_light( gl_light_index=GL_LIGHT0,
                              position=(-40,200,100,1.0) )

    maximum_speed=5.0
    maximum_acceleration=2.0
    maximum_roll_rate=180.0

    gravity=Vector2D(0.0,0.0)

#    goodguy_control=JoystickControl()
    goodguy_control=KeyboardControl(WADS)
    badguy_control=KeyboardControl(ARROWS)

    starfield=Starfield(viewport, 100)

    planets=[Planet("planet.obj",
                    Vector2D(random.uniform(-15, 15),
                             random.uniform(-15, 15)), 0.25),
             Planet("cold_planet.obj",
                    Vector2D(random.uniform(-15, 15),
                             random.uniform(-15, 15)), 0.2),
             Planet("earth.obj",
                    Vector2D(random.uniform(-15, 15),
                             random.uniform(-15, 15)), 0.33, 60.0),
             Planet("jupiter.obj",
                    Vector2D(random.uniform(-15, 15),
                             random.uniform(-15, 15)), 0.33, 60.0)]

    asteroids=[Asteroid("asteroid.obj",
                        Vector2D(random.uniform(-15, 15),
                                 random.uniform(-15, 15)),
                        Vector2D(random.uniform(-0.5, 0.5),
                                 random.uniform(-0.5, 0.5)),
                        random.uniform(-15.0, 15.0),
                        random.uniform(-15.0, 15.0),
                        random.uniform(-15.0, 15.0),
                        1.0,
                        10,
                        10.0)]
    
    goodguy_blasters=[]
    badguy_blasters=[]

    goodguy=Rocket("rocket_canopy.obj",
                   gravity,
                   maximum_speed,
                   maximum_acceleration,
                   maximum_roll_rate,
                   goodguy_control,
                   goodguy_blasters,
                   (0.5, 0.5, 1.0))

    badguy=Rocket("rocket_canopy_badguy.obj",
                  gravity,
                  maximum_speed,
                  maximum_acceleration,
                  maximum_roll_rate,
                  badguy_control,
                  badguy_blasters,
                  (1.0, 0.5, 0.5))

    goodguy.position=Vector2D(-2.5, 0.0)
    badguy.position=Vector2D(2.5, 0.0)

#    rockets=[goodguy, badguy]
    rockets=[]

    clock=pygame.time.Clock()

    for target in rockets+asteroids:
        target.collide = new.instancemethod(collide, target, target.__class__)

    while 1:

        clock.tick()

        process_control_events()
        
        for e in pygame.event.get(QUIT):
            sys.exit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(0.0,0.0,-10.0)

        starfield.draw()

        targets=rockets+asteroids

        for planet in planets:
            planet.update(clock)
            planet.draw()

        for asteroid in asteroids:

            if asteroid.hit_points < 1:
                asteroids.remove(asteroid)

                new_asteroids=asteroid.explode()
                asteroids.extend(new_asteroids)

                for new_asteroid in new_asteroids:
                    new_asteroid.collide = new.instancemethod(collide, new_asteroid, new_asteroid.__class__)

            else:
                asteroid.update(clock),
                collisions(asteroid, targets)
                reposition(viewport, asteroid.position)
                
                asteroid.draw()
            

            _draw_bounding_box( asteroid.bounding_box )

            print "%5.1f, %5.1f -> %5.1f, %5.1f" % (asteroid.bounding_box.lower_left.x,
                                                    asteroid.bounding_box.lower_left.y,
                                                    asteroid.bounding_box.upper_right.x,
                                                    asteroid.bounding_box.upper_right.y)

            for v in asteroid.bounding_box.transformed_vertices:
                print " %5.1f, %5.1f" % (v.x, v.y)

            print ""

        for rocket in rockets:
            rocket.update(clock)
            collisions(rocket, targets)

            reposition(viewport, rocket.position)

            glClear(GL_DEPTH_BUFFER_BIT)
            rocket.draw()

        for blaster_list in goodguy_blasters, badguy_blasters:
            for blaster in list(blaster_list):
                blaster.update(clock, targets)

                blaster.draw()

                reposition(viewport, blaster.position)

                if blaster.state is Blaster.OFF:
                    blaster_list.remove(blaster)




        pygame.display.flip()

if __name__ == "__main__":
    main() 



