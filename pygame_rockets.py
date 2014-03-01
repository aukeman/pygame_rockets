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

from rocket import Rocket

from vector2d import Vector2D

def main():

    import sys

    pygame.mixer.pre_init(buffer=1024)

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

    rockets=[goodguy, badguy]

#    asteroids=[]
    planets=[]

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
            
            draw_bounding_box( asteroid.bounding_box )
		

        for rocket in rockets:
            rocket.update(clock)
            collisions(rocket, targets)

            reposition(viewport, rocket.position)

            glClear(GL_DEPTH_BUFFER_BIT)
            rocket.draw()

            draw_bounding_box( rocket.bounding_box )


        for blaster_list in goodguy_blasters, badguy_blasters:
            for blaster in list(blaster_list):
                blaster.update(clock, targets)

                blaster.draw()

                reposition(viewport, blaster.position)

                if blaster.state is Blaster.OFF:
                    blaster_list.remove(blaster)

        pygame.display.flip()

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

@gl_utilities.debug_configuration(color=(1.0, 1.0, 1.0), line_width=2.0)
def draw_bounding_box( bounding_polygon ):
    xfrmed_vertices=bounding_polygon.transformed_vertices
    glBegin(GL_LINE_STRIP)
    for v in xfrmed_vertices:
        glVertex(-v.x, -v.y, 0.0)
    
    glVertex(-xfrmed_vertices[0].x, -xfrmed_vertices[0].y)
    glEnd()


if __name__ == "__main__":
    main() 

