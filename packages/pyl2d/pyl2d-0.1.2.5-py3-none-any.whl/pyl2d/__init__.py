import os
import threading
import time
from OpenGL import GL, GLU
from collections import namedtuple

os.environ['PYSDL2_DLL_PATH'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dependencies")

from sdl2 import *
from sdl2.sdlttf import *
from sdl2.sdlimage import *
from sdl2.ext import get_events

from .Filesystem import Filesystem
from .Graphics import Graphics, initGraphics
from .Physics import Physics
from .Image import ImageData, initImage

drawableStruct = namedtuple("drawableStruct", "texture width height pixelData")
initGraphics(drawableStruct)
initImage(drawableStruct)


def RGBAToFloatRGBA(r, g, b, a):
    return r / 255, g / 255, b / 255, a / 255


class Pyl2d:
    def __init__(self):
        self.hasInit = False
        self.config = {
            "window_width":1280,
            "window_height":720,
            "window_title":"Python Love2d (Recorration)",
            "window_fullscreen":False,
            "window_fullscreen_mode":"window_fullscreen", # fullscreen, window_fullscreen
            "window_resizable":False,
            "window_vsync":True,
            "filesystem_identity":"NOID",
            "getFps_interval":1,
            "draw_doClearOnDraw":True,
            "draw_clearColor":(0, 0, 0, 0)
        }
        self.window = None
        self.context = None
        self.vbo = None
        self.programRunning = None
        self.events = None
        self.updateThread = None
        self.updateThreadRunning = False
        self.programReload = False
        self.makeError = None
        self.drawFrameCountFPSGet = 0
        self.fps_lasttime = 0
        self.drawFPS = 0
        self.lastMousePos = (0, 0)
        self._fonts = {}

        self.graphics = None
        self.physics = None
        self.filesystem = None

        self.event = None
        self._updateThread = None


    def __processEvents(self):
        for event in get_events():
            if SDL_QUIT == event.type:
                self.programRunning = False
            elif SDL_TEXTINPUT == event.type:
                self.textinput(event.text.text.decode())
            elif SDL_KEYDOWN == event.type:
                self.keypressed(SDL_GetKeyName(event.key.keysym.sym).decode().lower())
            elif SDL_KEYUP == event.type:
                self.keyreleased(SDL_GetKeyName(event.key.keysym.sym).decode().lower())
            elif SDL_MOUSEMOTION == event.type:
                self.lastMousePos = (event.motion.x, event.motion.y)
                self.mousemoved(event.motion.x, event.motion.y, event.motion.xrel, event.motion.yrel)
            elif SDL_MOUSEBUTTONDOWN == event.type:
                self.mousepressed(event.button.button)
            elif SDL_MOUSEBUTTONUP == event.type:
                self.mousereleased(event.button.button)
            elif SDL_MOUSEWHEEL == event.type:
                self.wheelmoved(event.wheel.x, event.wheel.y)
            elif SDL_WINDOWEVENT == event.type:
                if SDL_WINDOWEVENT_MOVED == event.type:
                    self.windowmoved(event.window.data1, event.window.data2)
                elif SDL_WINDOWEVENT_RESIZED == event.window.event:
                    self.windowresized(event.window.data1, event.window.data2)
                elif SDL_WINDOWEVENT_MINIMIZED == event.window.event:
                    self.windowminimized()
                elif SDL_WINDOWEVENT_MAXIMIZED == event.window.event:
                    self.windowmaximized()
                elif SDL_WINDOWEVENT_FOCUS_GAINED == event.window.event:
                    self.windowfocus(True)
                elif SDL_WINDOWEVENT_FOCUS_LOST == event.window.event:
                    self.windowfocus(False)
                elif SDL_WINDOWEVENT_ENTER == event.window.event:
                    self.windowenter(True)
                elif SDL_WINDOWEVENT_LEAVE == event.window.event:
                    self.windowenter(False)
                else:
                    #print("Uncaught Window Event: ", self.event.window.event)
                    pass
            else:
                #print("Uncaught Event: ", self.event.type)
                pass


    def __updateThread(self):
        self._updateThreadRunning = True
        dtToUse = 0
        while self.programRunning:
            startTime = time.perf_counter()
            try:
                self.update(dtToUse)
            except Exception as e:
                self.makeError = e
                break
            time.sleep(0.0001)
            dtToUse = time.perf_counter() - startTime

        self._updateThreadRunning = False


    def init(self):
        """
        Init everything
        This is here so you can change the config otherwise some configs will not work
        """

        if self.config["filesystem_identity"] is "NOID":
            self.config["filesystem_identity"] = self.config["window_title"]

        self.graphics = Graphics(self)
        self.physics = Physics(self)
        self.filesystem = Filesystem(self)

        #Init SDL
        if SDL_Init(SDL_INIT_EVERYTHING) < 0:
            raise("SLD could not initialize")

        TTF_Init()
        IMG_Init(IMG_INIT_JPG | IMG_INIT_PNG | IMG_INIT_TIF | IMG_INIT_WEBP)

        self._fonts["NimbusRomNo9L-Med"] = TTF_OpenFont(os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts", "NimbusRomNo9L-Med.ttf").encode(), 18)
        self._fonts["default"] = self._fonts["NimbusRomNo9L-Med"]
        self._fonts["active"] = self._fonts["default"]

        self.hasInit = True


    def constructWindowArgs(self):
        default = SDL_WINDOW_OPENGL | SDL_RENDERER_ACCELERATED | SDL_WINDOW_ALLOW_HIGHDPI
        if self.config["window_resizable"]:
            default = default | SDL_WINDOW_RESIZABLE

        return default


    def run(self):
        """
        Run's the game
        """
        if not self.hasInit:
            self.init()

        # Init window
        if self.programReload is not True:
            self.window = SDL_CreateWindow(
                str.encode(self.config["window_title"]),
                SDL_WINDOWPOS_CENTERED,
                SDL_WINDOWPOS_CENTERED,
                self.config["window_width"],
                self.config["window_height"],
                self.constructWindowArgs()
            )
            if not self.window:
                ValueError("Error creating window!")

        self.programReload = False

        self.setFullscreen(self.config["window_fullscreen"], self.config["window_fullscreen_mode"])

        self.context = SDL_GL_CreateContext(self.window)

        # WARNING: this is ment to be before the window is created the wiki says, i spent a long time and this needs to be after the context is made!
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE)
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)  # 3.x
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3)  # x.3
        SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)

        if not self.context:
            ValueError("Error creating openGL context!")

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluOrtho2D(0, self.config["window_width"], self.config["window_height"], 0)
        GL.glClearColor(0, 0, 0, 1)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        try:
            self.load()
        except Exception as e:
            print("Error in load()")
            raise e

        self.programRunning = True
        self.event = SDL_Event()

        self._updateThread = threading.Thread(target=self.__updateThread, name="_updateThread", daemon=True)
        self._updateThread.start()

        try:
            while self.programRunning:
                self.__processEvents()

                # Clear glContext
                if self.config["draw_doClearOnDraw"]:
                    GL.glClearColor(*self.config["draw_clearColor"])
                    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

                # Run draw function
                try:
                    self.graphics.push()
                    self.graphics.setColor(255, 255, 255, 255)
                    self.draw()
                    self.graphics.pop()
                except Exception as e:
                    print("Error in draw()")
                    raise e

                # Show Back Buffer
                SDL_GL_SetSwapInterval(int(self.config["window_vsync"]))
                SDL_GL_SwapWindow(self.window)

                self.drawFrameCountFPSGet += 1
                if self.fps_lasttime < SDL_GetTicks() - self.config["getFps_interval"]*1000:
                    self.fps_lasttime = SDL_GetTicks()
                    self.drawFPS = int(self.drawFrameCountFPSGet / self.config["getFps_interval"])
                    self.drawFrameCountFPSGet = 0

                if self.makeError is not None:
                    raise self.makeError
        except KeyboardInterrupt:
            self.programRunning = False
            print("KeyboardInterrupt: Stopping...")

        print("Waiting For Update Thread To Close")
        while self._updateThreadRunning:
            time.sleep(0.1)
        print("Update Thread Closed")

        SDL_GL_DeleteContext(self.context)

        if self.programReload is True:
            self.run()
        else:
            SDL_DestroyWindow(self.window)

        try:
            self.onQuit()
        except Exception as e:
            print("Error in onQuit()")
            raise e


    def quit(self, restart=False):
        self.programRunning = False
        self.programReload = restart


    def setFullscreen(self, fullscreen=False, fsType="window_fullscreen"):
        """
        Sets the fullscreen type and state

        setFullscreen(self, True, "window_fullscreen")
        """
        if fullscreen is True:
            SDL_SetWindowFullscreen(self.window, SDL_WINDOW_FULLSCREEN if fsType == "fullscreen" else SDL_WINDOW_FULLSCREEN_DESKTOP)
        else:
            SDL_SetWindowFullscreen(self.window, 0)


    def keyIsDown(self, key):
        """
        Check if the given key is currently down (MIGHT not work well in update() due to threading)

        isKeyPDown = keyIsDown("p")
        """
        if SDL_GetKeyboardState(None)[SDL_GetScancodeFromName(key.encode())]:
            return True
        else:
            return False


    def mouseIsDown(self, button, useSDLbuttonNumbers=False):
        """
        Check if the given key is currently down (MIGHT not work well in update() due to threading)

        isMouseOneDown = keyIsDown(1)
        isMouseOneDown = keyIsDown((1, 2))

        1 = Left Button
        2 = Right Button
        3 = Middle Button
        4 = Bottom Side Button (This might very)
        5 = Top Side Button (This might very)
        """
        if type(button) == int:
            mState = SDL_GetMouseState(None, None)

            if useSDLbuttonNumbers is False:
                if button == 1:
                    mState -= 1
                elif button == 3:
                    mState -= 2
                elif button == 2:
                    mState -= 4
                elif button == 4:
                    mState -= 8
                elif button == 5:
                    mState -= 16
            else:
                mState - button

            return mState == 0
        else:
            mState = SDL_GetMouseState(None, None)

            for b in button:
                if useSDLbuttonNumbers is False:
                    if b == 1:
                        mState -= 1
                    elif b == 2:
                        mState -= 2
                    elif b == 3:
                        mState -= 4
                    elif b == 4:
                        mState -= 8
                    elif b == 5:
                        mState -= 16
                else:
                    mState - b

            return mState == 0


    def getMousePosition(self):
        """
        Returns the x,y of the mouse on the window

        MousePosTuple = getMousePosition()
        """
        return self.lastMousePos


    def reload(self):
        """
        Basic reload function to only reload the game and renderer but not the window

        reload()
        """
        self.programRunning = False
        self.programReload = True


    def load(self):
        """
        Callback Function
        This runs when the game loads (including reload)

        def load(self):
            pass
        """
        pass


    def draw(self):
        """
        Callback Function
        This runs every draw update

        def draw(self):
            pass
        """
        pass


    def update(self, dt):
        """
        Callback Function
        This runs every update in the update THREAD
        you can just use an alteritive of your own

        def keypressed(self, dt):
            pass
        """
        pass


    def keypressed(self, key):
        """
        Callback Function
        This runs when a key on the keyboard is pressed

        def keypressed(self, key):
            pass
        """
        pass


    def keyreleased(self, key):
        """
        Callback Function
        This runs when a key on the keyboard is released

        def keyreleased(self, key):
            pass
        """
        pass


    def textinput(self, text):
        """
        Callback Function
        This runs when there is a textinput event
        On windows this is just same as keypressed but takes into account the shift key ect, but ignores keys like pause|break

        def textinput(self, text):
            pass
        """
        pass


    def mousemoved(self, x, y, mx, my):
        """
        Callback Function
        This runs when the mouse is moved

        def mousemoved(self, x, y, mx, my):
            pass
        """
        pass


    def wheelmoved(self, x, y):
        """
        Callback Function
        This runs when the mouse scroll wheel is moved

        def wheelmoved(self, x, y):
            pass
        """
        pass


    def mousepressed(self, button):
        """
        Callback Function
        This runs when the mouse is pressed

        def mousereleased(self, button):
            pass
        """
        pass


    def mousereleased(self, button):
        """
        Callback Function
        This runs when the mouse is released

        def mousereleased(self, button):
            pass
        """
        pass


    def onQuit(self):
        """
        Callback Function
        This runs when the window gets closed OR when it gets reloaded

        def onQuit(self):
            pass
        """
        pass


    def windowmoved(self, x, y):
        pass


    def windowresized(self, x, y):
        pass


    def windowminimized(self):
        pass


    def windowmaximized(self):
        pass


    def windowfocus(self, state):
        pass


    def windowenter(self, state):
        pass
