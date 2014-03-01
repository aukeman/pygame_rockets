import pygame, config
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import *

from pygame.constants import HWSURFACE, OPENGL, DOUBLEBUF

from sprite import Sprite

_shader_registry=dict()

def init_gl_viewport( viewport=(800,600),
                      display_flags=HWSURFACE | OPENGL | DOUBLEBUF,
                      screen_extents=(-5, 5, -5, 5),
                      clipping_planes=(1,100),
                      clear_color=(0.0,0.0,0.0,0.0)):

    pygame.init()

    srf = pygame.display.set_mode(viewport, display_flags )

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    width, height = viewport

    aspect_ratio=(float(width)/float(height))

    horizontal_midpoint=(screen_extents[0]+screen_extents[1])/2
    vertical_distance=screen_extents[3]-screen_extents[2]

    glOrtho( horizontal_midpoint-(vertical_distance*aspect_ratio)/2,
             horizontal_midpoint+(vertical_distance*aspect_ratio)/2,
             screen_extents[2],
             screen_extents[3],
             clipping_planes[0],
             clipping_planes[1] )

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_COLOR_MATERIAL)

    glEnable(GL_CULL_FACE)
    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glClearColor(0.0, 0.0, 0.0, 0.0)

    Sprite.init()

    if config.enable_shaders:
        for (shader_filenames, shader) in _shader_registry.items():
            if shader is None:
                shader_files=map(load_file, shader_filenames)
                _shader_registry[shader_filenames]=load_shaders(*shader_files)

    return ( horizontal_midpoint-(vertical_distance*aspect_ratio)/2,
             horizontal_midpoint+(vertical_distance*aspect_ratio)/2,
             screen_extents[2],
             screen_extents[3] )


def setup_light( gl_light_index=GL_LIGHT0,
                 ambient=(0.2,0.2,0.2,1.0),
                 diffuse=(1.0,1.0,1.0,1.0),
                 specular=(0.0,0.0,0.0,1.0),
                 position=(0.0,0.0,0.0,0.0) ):
    glLightfv(gl_light_index, GL_POSITION,  position)
    glLightfv(gl_light_index, GL_AMBIENT,   ambient)
    glLightfv(gl_light_index, GL_DIFFUSE,   diffuse)
    glLightfv(gl_light_index, GL_SPECULAR,  specular)
    glEnable(gl_light_index)
    glEnable(GL_LIGHTING)

def load_shaders(vertex_shader, fragment_shader):
    return compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                          compileShader(fragment_shader, GL_FRAGMENT_SHADER))

def setup_for_shader(shader):
    if config.enable_shaders:
        glUseProgram(shader)
    else:
        glUseProgram(0)    


def teardown_for_shader():
    glUseProgram(0)

def setup_for_sprites():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

def teardown_for_sprites():
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

    glEnable (GL_BLEND)
    glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

def setup_for_debug():
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_TEXTURE_2D)
#    glEnable(GL_POINT_SMOOTH)

def teardown_for_debug():
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    

def sprites_configuration( draw_fxn ):
    def _wrapped(*args,**kwargs):
        setup_for_sprites()
        draw_fxn(*args,**kwargs)
        teardown_for_sprites()
    return _wrapped

def shader_configuration(vertex_shader_path, fragment_shader_path):

    _shader_registry[(vertex_shader_path,fragment_shader_path)]=None
    
    def _wrapped_decorator(draw_fxn):
        def _wrapped(*args,**kwargs):

            setup_for_shader(_shader_registry[(vertex_shader_path,
	                                           fragment_shader_path)])
            draw_fxn(*args,**kwargs)
            teardown_for_shader()

        return _wrapped
    return _wrapped_decorator

def debug_configuration(color=(1.0,1.0,1.0), point_size=1.0, line_width=1.0 ):
    def _wrapped_decorator(draw_fxn):
        def _wrapped(*args, **kwargs):
            setup_for_debug()
            glColor(color)
            glPointSize(point_size)
            glLineWidth(line_width)
            draw_fxn(*args,**kwargs)
            teardown_for_debug()
        return _wrapped
    return _wrapped_decorator
        
def load_file(filename):
    f=open(filename)
    lines=f.readlines()
    f.close()
    return "\n".join(lines)
