# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys
from pygame.constants import *
from OpenGL.GLU import *

# IMPORT OBJECT LOADER
#from objloader2 import *
#from objloader2axis import *

def plotobj(generateOBJ, filename, title, winwidth, winheight, plotaxis, factor):
    """

    This function generates a .OBJ 3D model from an input .bds file (digital shape kernel)

    :param generateOBJ: example: "dskexp -dsk inputfilename.bds -text outputfilename.obj
                        -format obj -prec 10"
    :type generateOBJ: str
    :param filename: outputfilaname.obj
    :type filename: str
    :param title: title to be displayed in the visualization window
    :type title: str
    :param winwidth: width of the visualization window. Example: 1200
    :type winwidth: int
    :param winheight: height of the visualization window. Example: 900
    :type winheight: int
    :param plotaxis: if set equal to 1, it displays a reference frame in the visualization window
    :type plotaxis: int
    :param factor: factor to size the dimensions of the displayed reference frame.
                   If not known set it to 1
    :type factor: int

    :return:
    """
    command = (generateOBJ)
    os.system(command)

    pygame.init()
    viewport = (winwidth, winheight)
    hx = viewport[0] / 2
    hy = viewport[1] / 2
    pygame.display.set_mode((winwidth, winheight), pygame.DOUBLEBUF | pygame.OPENGL)
    pygame.display.set_caption(title)

    # Function checker
    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glEnable(GL_CULL_FACE)
    #
    glMatrixMode(GL_PROJECTION)
    gluPerspective(90.0, float(800) / 600, 1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # LOAD OBJECT AFTER PYGAME INIT
    obj = OBJ(filename)

    if plotaxis == 1:
        xaxis = OBJax('xaxis.obj', 1.0, 0.0, 0.0, -1, -2, 2, factor)
        yaxis = OBJax('yaxis.obj', 0.0, 1.0, 0.0, -1, -2, 2, factor)
        zaxis = OBJax('zaxis.obj', 0.0, 0.0, 1.0, -1, -2, 2, factor)

    clock = pygame.time.Clock()

    rx, ry = (0, 0)
    tx, ty = (0, 0)
    zpos = 3  # like distance from camera to object
    rotate = move = False
    while 1:
        clock.tick(30)
        print(tx, ty, rx, ry, zpos)
        for e in pygame.event.get():
            if e.type == QUIT:
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                sys.exit()
            elif e.type == MOUSEBUTTONDOWN:
                if e.button == 4:
                    zpos = max(1, zpos - 1)
                elif e.button == 5:
                    zpos += 1
                elif e.button == 1:
                    rotate = True
                elif e.button == 3:
                    move = True
            elif e.type == MOUSEBUTTONUP:
                if e.button == 1:
                    rotate = False
                elif e.button == 3:
                    move = False
            elif e.type == MOUSEMOTION:
                i, j = e.rel
                if rotate:
                    rx += i
                    ry += j
                if move:
                    tx += i
                    ty -= j

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.902, 0.902, 1, 0.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # RENDER OBJECT
        glTranslate(tx / 20., ty / 20., - zpos)
        glRotate(ry, 1, 0, 0)
        glRotate(rx, 0, 1, 0)
        glCallList(obj.gl_list)
        if plotaxis == 1:
            glCallList(xaxis.gl_list)
            glCallList(yaxis.gl_list)
            glCallList(zaxis.gl_list)

        pygame.display.flip()

    return

class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.faces = []

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'f':
                face = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                self.faces.append(face)

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glDisable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for f in face:
                vertexDraw = self.vertices[int(f) - 1]
                if int(f) % 3 == 1:
                    glColor4f(0.282, 0.239, 0.545, 0.35)
                elif int(f) % 3 == 2:
                    glColor4f(0.329, 0.333, 0.827, 0.35)
                else:
                    glColor4f(0.345, 0.300, 0.145, 0.35)
                glVertex3fv(vertexDraw)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()

class OBJax:
    def __init__(self, filename, R, G, B, X0, Y0, Z0, factor, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.faces = []

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                values[1] = str(X0 + factor*float(values[1]))
                values[2] = str(Z0 + factor* float(values[2]))
                values[3] = str(Y0 + factor* float(values[3]))
                v = list(map(float, values[1:4]))
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'f':
                face = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                self.faces.append(face)

        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glDisable(GL_TEXTURE_2D)
        glFrontFace(GL_CCW)

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for f in face:
                vertexDraw = self.vertices[int(f) - 1]
                if int(f) % 3 == 1:
                    glColor4f(R, G, B, 0.35)
                elif int(f) % 3 == 2:
                    glColor4f(R, G, B, 0.35)
                else:
                    glColor4f(R, G, B, 0.35)
                glVertex3fv(vertexDraw)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEndList()
