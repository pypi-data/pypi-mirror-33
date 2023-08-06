import struct
from OpenGL import GL, GLU
from PIL import Image as PilImage


def initImage(_drawableStruct):
    global drawableStruct
    drawableStruct = _drawableStruct


class ImageData:
    """
    When making new ImageData there might be a warning about pixels2d being experimental!
    This message only ever shows once per launch
    """

    def __init__(self, game, width=0, height=0, drawable=None, filterMode="linear"):
        self.game = game
        self.width = width
        self.height = height
        self.pixelData = None
        self.fboName = None
        self.filterMode = filterMode
        if drawable is not None:
            GL.glBindTexture(GL.GL_TEXTURE_2D, drawable.texture)
            self.pixelData = GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
            self.width = drawable.width
            self.height = drawable.height
        else:
            self.pixelData = (b"\x00\x00\x00\x00" * self.width) * self.height

        if self.filterMode.lower() == "linear":
            filterModeMag, filterModeMin = GL.GL_LINEAR, GL.GL_LINEAR
        elif self.filterMode.lower() == "nearest":
            filterModeMag, filterModeMin = GL.GL_NEAREST, GL.GL_NEAREST
        elif self.filterMode.lower() == "linear mipmap":
            filterModeMag, filterModeMin = GL.GL_LINEAR, GL.GL_LINEAR_MIPMAP_LINEAR
        elif self.filterMode.lower() == "nearest mipmap":
            filterModeMag, filterModeMin = GL.GL_NEAREST, GL.GL_NEAREST_MIPMAP_NEAREST
        else:
            TypeError("Unknown filterMode '{}'".format(self.filterMode.lower()))

        self.texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self.width, self.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.pixelData)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, filterModeMag)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, filterModeMin)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)


    @property
    def drawable(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.pixelData)
        return drawableStruct(self.texture, self.width, self.height, self.pixelData)


    def getPixel(self, x, y):
        startPos = ((y * self.width) + x) * 4
        v = self.pixelData[startPos:startPos+4]
        r = struct.unpack("B", v[0:1])[0]
        g = struct.unpack("B", v[1:2])[0]
        b = struct.unpack("B", v[2:3])[0]
        a = struct.unpack("B", v[3:4])[0]
        return r, g, b, a


    def setPixel(self, x, y, r=255, g=255, b=255, a=255):
        pixelData = bytes([r, g, b, a])
        startPos = ((y * self.width) + x) * 4
        self.pixelData = self.pixelData[:startPos] + pixelData + self.pixelData[startPos+4:]


    def saveImg(self, filePath, ignoreFsModule=False):
        img = PilImage.frombytes("RGBA", (self.width, self.height), self.pixelData)
        if ignoreFsModule:
            img.save("{}.png".format(filePath))
        else:
            img.save(self.game.filesystem.getWriteDir("{}.png".format(filePath)))


    def setRenderingTarget(self, isRendering=False):
        if isRendering:
            if self.fboName is None:
                self.fboName = GL.glGenFramebuffers(1)

            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fboName)
            GL.glFramebufferTexture(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, self.texture, 0)
            GL.glDrawBuffer(GL.GL_COLOR_ATTACHMENT0)

            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glTexSubImage2D(GL.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, self.pixelData)

            GL.glViewport(0, 0, self.width, self.height)
            GL.glLoadIdentity()
            GLU.gluOrtho2D(0, self.width, 0, self.height)
        else:
            GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            self.pixelData = GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)

            GL.glViewport(0, 0, self.game.config["window_width"], self.game.config["window_height"])
            GL.glLoadIdentity()
            GLU.gluOrtho2D(0, self.game.config["window_width"], self.game.config["window_height"], 0)

