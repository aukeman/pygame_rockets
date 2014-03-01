import pygame, config
from OpenGL.GL import *

class Sprite:

    def __init__( self, src_file ):

        surf=pygame.image.load(config.basedir+"/"+src_file)
        image=pygame.image.tostring(surf,'RGBA',1)

        ix, iy = surf.get_rect().size
        self.texid = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, self.texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, image)


    def draw( self,
              position=None,
              rotate=None,
              scale=None,
              color=None,
              src_rect=((0.0,0.0),(1.0,1.0)) ):

        glPushMatrix()

        if position is not None:
            if len(position) == 3:
                glTranslate( *position )
            else:
                glTranslate( position[0], position[1], 0.0 )

        if rotate is not None:
            if isinstance( rotate, tuple ):
                glRotate( *rotate )
            else:
                glRotate( rotate, 0.0, 0.0, 1.0 )

        if scale is not None:
            if isinstance( scale, tuple ):
                if len(scale) == 3:
                    glScale( *scale )
                else:
                    glScale( scale[0], scale[1], 1.0 )
            else:
                glScale( scale, scale, 1.0 )

        if color is not None:
            glColor(color)

        glBindTexture(GL_TEXTURE_2D, self.texid)

        glBegin(GL_QUADS)

        glTexCoord(src_rect[0][0], src_rect[0][1])
        glVertex( 0.0, 0.0, 0.0 )

        glTexCoord(src_rect[0][0], src_rect[1][1])
        glVertex( 0.0, -1.0, 0.0 )

        glTexCoord(src_rect[1][0], src_rect[1][1])
        glVertex( 1.0, -1.0, 0.0 )

        glTexCoord(src_rect[1][0], src_rect[0][1])
        glVertex( 1.0, 0.0, 0.0 )

        glEnd()

        glPopMatrix()

    @staticmethod
    def init():
        Sprite.glow=Sprite("assets/glow.png") 
        Sprite.beam=Sprite("assets/beam.png") 
        Sprite.plume=Sprite("assets/plume.png")

def main():

    import sys
    from OpenGL.GLU import gluPerspective
    from pygame.constants import HWSURFACE, OPENGL, DOUBLEBUF, QUIT

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

    while 1:

        clock.tick(30)
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslate(0.0, 0.0, -5.0)

        Sprite.glow.draw( position=(-2.0, -2.5), color=(0.5, 1.0, 0.5) )

        Sprite.beam.draw( position=(-3.0, -3.0), scale=(5.0, 0.25), color=(1.0, 0.5, 0.5) )

        

        pygame.display.flip()

if __name__ == "__main__":
    main() 


