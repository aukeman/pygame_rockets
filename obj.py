import pygame
from OpenGL.GL import *

from OpenGL.GL.shaders import *


 
def MTL(filename):
    contents = {}
    mtl = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            mtl = contents[values[1]] = {}
        elif mtl is None:
            raise ValueError, "mtl file doesn't start with newmtl stmt"
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            mtl[values[0]] = values[1]
            surf = pygame.image.load(mtl['map_Kd'])
            image = pygame.image.tostring(surf, 'RGBA', 1)
            ix, iy = surf.get_rect().size
            texid = mtl['texture_Kd'] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA,
                GL_UNSIGNED_BYTE, image)
        else:
            mtl[values[0]] = map(float, values[1:])
    return contents
 
class OBJ:
    def __init__(self, dirname, filename):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []
 
        material = None
        for line in open(dirname+"/"+filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
#                 if swapyz:
#                     v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
#                 if swapyz:
#                     v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                self.mtl = MTL(dirname + "/" + values[1])
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))
 
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        glFrontFace(GL_CCW)
        glEnable(GL_CULL_FACE)
        glPolygonMode( GL_FRONT, GL_FILL )
        glPolygonMode( GL_BACK, GL_LINE )
        glEnable( GL_LINE_SMOOTH )

        glDisable(GL_TEXTURE_2D)
#        glCullFace(GL_FRONT)
#        glColor(0.25, 0.25, 0.25, 1.0)
#        glLineWidth(2.0)

#       for face in self.faces:
#           vertices, normals, texture_coords, material = face

#            glBegin(GL_POLYGON)
#            for i in range(len(vertices)):
#                if normals[i] > 0:
#                    glNormal3fv(self.normals[normals[i] - 1])
#                if texture_coords[i] > 0:
#                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
#                glVertex3fv(self.vertices[vertices[i] - 1])
#            glEnd()

        
        glEnable(GL_TEXTURE_2D)
        glCullFace(GL_BACK)
        glColor(1.0, 1.0, 1.0, 1.0)
        glLineWidth(1.0)

        for face in self.faces:
            vertices, normals, texture_coords, material = face
 
            mtl = self.mtl[material]
            if 'texture_Kd' in mtl:
                # use diffuse texmap
                glBindTexture(GL_TEXTURE_2D, mtl['texture_Kd'])
            else:
                # just use diffuse colour
                glColor(*mtl['Kd'])
  
            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                if normals[i] > 0:
                    glNormal3fv(self.normals[normals[i] - 1])
                if texture_coords[i] > 0:
                    glTexCoord2fv(self.texcoords[texture_coords[i] - 1])
                glVertex3fv(self.vertices[vertices[i] - 1])
            glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

# # Sample usage of this code (saving the above as the module "objloader.py"
# # and passing the filename of the obj file to display on the command-line.

# # Basic OBJ file viewer. needs objloader from:
# #  http://www.pygame.org/wiki/OBJFileLoader
# # LMB + move: rotate
# # RMB + move: pan
# # Scroll wheel: zoom in/out
# import sys, pygame
# from pygame.locals import *
# from pygame.constants import *
# from OpenGL.GL import *
# from OpenGL.GLU import *
 
# # IMPORT OBJECT LOADER
# from objloader_cel import *
 
# pygame.init()
# viewport = (800,600)
# hx = viewport[0]/2
# hy = viewport[1]/2
# srf = pygame.display.set_mode(viewport, HWSURFACE | OPENGL | DOUBLEBUF)
 
# glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
# glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
# glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
# glEnable(GL_LIGHT0)
# glEnable(GL_LIGHTING)
# glEnable(GL_COLOR_MATERIAL)
# glEnable(GL_DEPTH_TEST)
# glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded
# glClearColor(0.0, 0.0, 0.0, 0.0)

# glEnable (GL_BLEND)
# glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
 
# # LOAD OBJECT AFTER PYGAME INIT
# obj = OBJ(sys.argv[1], swapyz=True)

# glow = Glow( (0.0, -3.0, 0.0), 1.0, (0.5, 1.0, 0.5, 1.0) )
# beam = Beam( (-10.0, -3.0, 0.0), (10.0, -3.0, 0.0), 0.25, (0.5, 1.0, 0.5, 1.0) )
 
# clock = pygame.time.Clock()
 
# glMatrixMode(GL_PROJECTION)
# glLoadIdentity()
# width, height = viewport
# gluPerspective(90.0, width/float(height), 1, 100.0)
# glEnable(GL_DEPTH_TEST)
# glMatrixMode(GL_MODELVIEW)

# toon_shader = compileProgram(

#     compileShader("""
# varying vec3 normal;
# void main() {
#   normal = gl_NormalMatrix * gl_Normal;
#   gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
# }
# """, GL_VERTEX_SHADER ),
    
#     compileShader("""
# varying vec3 normal;
# void main(){

#   vec3 n = normalize(normal);
#   vec3 l = normalize(gl_LightSource[0].position).xyz;

#   float d = ceil(dot(l,n));

#   float intensity = 1.0;

#   if ( d <  0.25 )
#   {
#     intensity = 0.5;
#   }

#   gl_FragColor = vec4(gl_FrontMaterial.ambient[0]*intensity,
#                       gl_FrontMaterial.ambient[1]*intensity,
#                       gl_FrontMaterial.ambient[2]*intensity,
#                       1.0);
# }
# """, GL_FRAGMENT_SHADER ))

# rx, ry = (0,0)
# tx, ty = (0,0)
# zpos = 5
# rotate = move = False

# glow_pos=-10.0

# while 1:
#     clock.tick(60)
#     for e in pygame.event.get():
#         if e.type == QUIT:
#             sys.exit()
#         elif e.type == KEYDOWN and e.key == K_ESCAPE:
#             sys.exit()
#         elif e.type == MOUSEBUTTONDOWN:
#             if e.button == 4: zpos = max(1, zpos-1)
#             elif e.button == 5: zpos += 1
#             elif e.button == 1: rotate = True
#             elif e.button == 3: move = True
#         elif e.type == MOUSEBUTTONUP:
#             if e.button == 1: rotate = False
#             elif e.button == 3: move = False
#         elif e.type == MOUSEMOTION:
#             i, j = e.rel
#             if rotate:
#                 rx += i
#                 ry += j
#             if move:
#                 tx += i
#                 ty -= j
 
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
 
#     # RENDER OBJECT
#     glTranslate(tx/20., ty/20., - zpos)

#     glDisable(GL_DEPTH_TEST)

#     glUseProgram(0)
#     glCallList(beam.gl_list)

#     glPushMatrix()
#     glTranslate(-glow_pos, 0.0, 0.0)
#     glCallList(glow.gl_list)
#     glPopMatrix()

#     glow_pos += 0.5

#     if ( 10.0 < glow_pos ):
#         glow_pos = -10.0

#     glRotate(ry, 1, 0, 0)
#     glRotate(rx, 0, 1, 0)

#     glEnable(GL_DEPTH_TEST)

#     glUseProgram(toon_shader)
#     glCallList(obj.gl_list)
 
#     pygame.display.flip()
