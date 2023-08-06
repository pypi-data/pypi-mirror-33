from OpenGL import GL
from sdl2 import *
from sdl2.sdlttf import *
from sdl2.sdlimage import *
import numpy as np
import ctypes
import math

from .Image import ImageData


def initGraphics(_drawableStruct):
    global drawableStruct
    drawableStruct = _drawableStruct


def mapRange(value, input_min, input_max, output_min, output_max):
    return output_min + ((output_max - output_min) / (input_max - input_min)) * (value - input_min)


class Graphics:
    def __init__(self, gameRef):
        self.game = gameRef
        self.drawTargetWidth = None
        self.drawTargetHeight = None


    def pop(self): # Second
        """
        This is called after push()

        Requiers a corresponding push() operation

        pop()
        """
        GL.glPopMatrix()


    def push(self): # First
        """
        This is called before pop()

        Requiers a corresponding pop() operation

        push()
        """
        GL.glPushMatrix()


    def translate(self, dx, dy):
        """
        Translate the screen in dx, dy
        This works with the transform matrix stack

        translate(100, 0)
        """
        GL.glTranslatef(dx, dy, 0)


    def rotate(self, r, x=0, y=0):
        """
        Rotates around x, y in Degrees, default is origin

        rotate(180)
        """
        GL.glTranslatef(x, y, 0)
        GL.glRotatef(r, 0, 0, 1)
        GL.glTranslatef(-x, -y, 0)


    def scale(self, sx, sy="sx"):
        """
        Adds the sx, sy scale to the current scale
        Scale is on a multiplication factor

        scale(2)
        """
        if sy == "sx":
            sy = sx
        GL.glScale(sx, sy, 0)


    def getFPS(self):
        return self.game.drawFPS


    def addFont(self, path, name, size, ignoreFsModule=False):
        if name in self.game._fonts:
            ValueError("Attempted to override Font: {}".format(name))
        else:
            if ignoreFsModule is True:
                self.game._fonts[name] = TTF_OpenFont(str.encode(path), size)
            else:
                self.game._fonts[name] = TTF_OpenFont(str.encode(self.game.filesystem.fsm.getsyspath(path)), size)


    def setFont(self, name):
        if name in self.game._fonts:
            self.game._fonts["active"] = self.game._fonts[name]
        else:
            IndexError("Attempted to access Font that is not loaded: {}".format(name))


    def print(self, printStr, x=0, y=0, r=0):
        textSurface = TTF_RenderUTF8_Blended(self.game._fonts["active"], str(printStr).encode(), SDL_Color(255, 255, 255, 255))

        width = textSurface[0].w
        height = textSurface[0].h
        pixelData = ctypes.c_void_p(textSurface[0].pixels)

        imageTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, imageTexture)

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 4, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixelData) # IDK what format 4 is but it works magic
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_DECAL)

        SDL_FreeSurface(textSurface)

        textDrawable = drawableStruct(imageTexture, width, height, pixelData)
        self.draw(textDrawable, x, y, r)


    def setColor(self, r, g, b, a):
        """
        Sets the draw color to be r, g, b, a
        This effects almost anything in the graphics module

        setColor(255, 255, 255, 255)
        """
        GL.glColor4f(r/255, g/255, b/255, a/255)


    def newImage(self, path, ignoreFsModule=False, filterMode="linear"):
        """
        Creates a new image of type 'drawableStruct', use with draw()

        DO NOT USE THIS IN UPDATE() OR DRAW()! AS IT IS A HEAVY OPERATION

        Supported Formats:
        JPEG, PNG, TIFF, BMP, And maybe more

        Filter Modes:
            linear
            nearest

        newImage("path/to/my/awsome/image.png")
        """

        image = None

        if ignoreFsModule is True:
            image = IMG_Load(str.encode(path))
        else:
            image = IMG_Load(str.encode(self.game.filesystem.fsm.getsyspath(path)))

        if image is None:
            TypeError("Error Loading Image!")

        if filterMode.lower() == "linear":
            filterModeMag, filterModeMin = GL.GL_LINEAR, GL.GL_LINEAR
        elif filterMode.lower() == "nearest":
            filterModeMag, filterModeMin = GL.GL_NEAREST, GL.GL_NEAREST
        elif filterMode.lower() == "linear mipmap":
            filterModeMag, filterModeMin = GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR
        elif filterMode.lower() == "nearest mipmap":
            filterModeMag, filterModeMin = GL.GL_NEAREST, GL.GL_NEAREST_MIPMAP_NEAREST
        else:
            TypeError("Bad Argument: Unknown filterMode '{}'".format(filterMode.lower()))

        width = image[0].w
        height = image[0].h
        pixelData = ctypes.c_void_p(image[0].pixels)

        imageTexture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, imageTexture)

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, pixelData)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, filterModeMag)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, filterModeMin)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

        return drawableStruct(imageTexture, width, height, pixelData)


    def draw(self, drawable, x=0, y=0, r=0, w=None, h=None):
        """
        Draws a drawable of type 'drawableStruct'
        `r` is in degrees

        This can also accept ImageData as a drawable

        draw(someImage, x, y, 90)
        """
        if isinstance(drawable, ImageData):
            drawable = drawable.drawable

        if w is None:
            w = drawable.width
        if h is None:
            h = drawable.height

        GL.glPushMatrix()

        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, drawable.texture)
        GL.glTexEnvi(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)

        GL.glTranslatef(x+(w/2), y+(h/2), 0)
        GL.glRotatef(r, 0, 0, 1)
        GL.glTranslatef(-(w/2), -(h/2), 0)

        GL.glBegin(GL.GL_QUADS)

        # Top-left vertex
        GL.glTexCoord2f(0, 0)
        GL.glVertex2f(0, 0)

        # Top-right vertex
        GL.glTexCoord2f(1, 0)
        GL.glVertex2f(w, 0)

        # Bottom-right vertex
        GL.glTexCoord2f(1, 1)
        GL.glVertex2f(w, h)

        # Bottom-left vertex
        GL.glTexCoord2f(0, 1)
        GL.glVertex2f(0, h)

        GL.glEnd()

        GL.glDisable(GL.GL_TEXTURE_2D)

        GL.glPopMatrix()


    def setDrawTarget(self, drawable=None, isStillDrawing=False):
        """
        Allows drawing multiple images of the same image a bit more efficient

        setDrawTarget(drawable, True)
        drawTarget(0, 0)
        drawTarget(100, 0)
        setDrawTarget(drawable, False)
        """
        if isStillDrawing and drawable is not None:
            if isinstance(drawable, ImageData):
                drawable = drawable.drawable
            else:
                drawable = drawable

            GL.glPushMatrix()

            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glEnable(GL.GL_BLEND)
            GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
            GL.glBindTexture(GL.GL_TEXTURE_2D, drawable.texture)
            GL.glTexEnvi(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_MODULATE)
            self.drawTargetWidth = drawable.width
            self.drawTargetHeight = drawable.height
        else:
            GL.glDisable(GL.GL_BLEND)
            GL.glDisable(GL.GL_TEXTURE_2D)

            GL.glPopMatrix()
            self.drawTargetWidth = None
            self.drawTargetHeight = None


    def drawTarget(self, x=0, y=0, r=0, w=None, h=None):
        """
        Same as `draw()` but for `setDrawTarget()`

        setDrawTarget(drawable, True)
        drawTarget(0, 0)
        drawTarget(100, 0)
        setDrawTarget(drawable, False)
        """
        if w is None:
            w = self.drawTargetWidth
        if h is None:
            h = self.drawTargetHeight
        GL.glTranslatef(x+(w/2), y+(h/2), 0)
        GL.glRotatef(r, 0, 0, 1)
        GL.glTranslatef(-(w/2), -(h/2), 0)

        GL.glBegin(GL.GL_QUADS)

        # Top-left vertex
        GL.glTexCoord2f(0, 0)
        GL.glVertex2f(0, 0)

        # Top-right vertex
        GL.glTexCoord2f(1, 0)
        GL.glVertex2f(w, 0)

        # Bottom-right vertex
        GL.glTexCoord2f(1, 1)
        GL.glVertex2f(w, h)

        # Bottom-left vertex
        GL.glTexCoord2f(0, 1)
        GL.glVertex2f(0, h)

        GL.glEnd()


    def rectangle(self, x, y, width, height, mode="fill"):
        """
        Draws a rectangle at x, y with width and height
        modes: fill, line

        rectangle(100, 100 50, 50, mode="fill")
        rectangle(125, 120 90, 80, mode="line")
        """
        if mode == "fill":
            GL.glPushMatrix()
            GL.glTranslatef(x, y, 0)
            GL.glBegin(GL.GL_POLYGON)
            GL.glVertex2f(0, 0)
            GL.glVertex2f(width, 0)
            GL.glVertex2f(width, height)
            GL.glVertex2f(0, height)
            GL.glEnd()
            GL.glPopMatrix()
        elif mode == "line":
            GL.glPushMatrix()
            GL.glTranslatef(x, y, 0)
            GL.glBegin(GL.GL_LINE_LOOP)
            GL.glVertex2f(0, 0)
            GL.glVertex2f(width, 0)
            GL.glVertex2f(width, height-1)
            GL.glVertex2f(-1, height)
            GL.glEnd()
            GL.glPopMatrix()


    def lines(self, *args):
        """
        Draws lines to each (x, y) in the list
        Does not connect start line to end line!

        lines((100, 100), (200, 200), (200, 300))
        """
        GL.glPushMatrix()
        GL.glTranslatef(0, 0, 0)
        GL.glBegin(GL.GL_LINES)
        for i in range(0, len(args)-1):
            line = args[i]
            nextLine = args[i+1]
            GL.glVertex2f(line[0], line[1])
            GL.glVertex2f(nextLine[0], nextLine[1])
        GL.glEnd()
        GL.glPopMatrix()


    def line(self, x1, y1, x2, y2):
        """
        Draw a single line from x1, y1 to x2, y2

        line(100, 100, 200, 200)
        """
        GL.glPushMatrix()
        GL.glTranslatef(0, 0, 0)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(x1, y1)
        GL.glVertex2f(x2, y2)
        GL.glEnd()
        GL.glPopMatrix()


    def setLineWidth(self, size):
        GL.glLineWidth(size)


    def point(self, x, y):
        """
        Draws a small rectangle at x, y

        point(100, 100)
        """
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2f(x, y)
        GL.glEnd()


    def points(self, *args):
        """
        Draws a small rectangles at (x, y) in the list

        points((100, 100), (200, 200), (300, 300))
        """
        GL.glBegin(GL.GL_POINTS)
        for point in args:
            GL.glVertex2f(point[0], point[1])
        GL.glEnd()


    def setPointSize(self, size):
        """
        Sets the size of point() and points() in radius

        setPointSize(3)
        """
        GL.glPointSize(size)


    def circle(self, x=0, y=0, r=8, mode="fill", segments=360):
        """
        Draws a simple cirlce at x, y with radius of r
        modes: fill, line

        circle(120, 120, 9)
        """
        self.ellipse(x, y, r, r, mode=mode, segments=segments)


    def ellipse(self, x=0, y=0, w=10, h=15, mode="fill", segments=360):
        if mode == "fill":
            GL.glPushMatrix()
            GL.glTranslatef(x, y, 0)
            GL.glBegin(GL.GL_POLYGON)
            for i in range(0, segments):
                rad = math.radians(mapRange(i, 0, segments, 0, 360))
                GL.glVertex2f(np.cos(rad)*w,np.sin(rad)*h)
            GL.glEnd()
            GL.glPopMatrix()
        elif mode == "line":
            GL.glPushMatrix()
            GL.glTranslatef(x, y, 0)
            GL.glBegin(GL.GL_LINE_LOOP)
            for i in range(0, segments):
                rad = math.radians(mapRange(i, 0, segments, 0, 360))
                GL.glVertex2f(np.cos(rad)*w,np.sin(rad)*h)
            GL.glEnd()
            GL.glPopMatrix()


    def newImageData(self, widthOrDrawable=100, height=100, filterMode="linear"):
        if type(widthOrDrawable) == drawableStruct:
            return ImageData(self.game, drawable=widthOrDrawable, filterMode=filterMode)
        else:
            return ImageData(self.game, width=widthOrDrawable, height=height, filterMode=filterMode)
