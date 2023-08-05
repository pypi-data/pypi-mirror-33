import os
import __main__
from fs.multifs import MultiFS
from fs.errors import *

class Filesystem:
    def __init__(self, gameRef):
        self.game = gameRef
        self.fsm = MultiFS() #fsm - FileSystemMulti

        saveDirPath = os.path.join(os.path.abspath(os.getenv("APPDATA")), self.game.config["filesystem_identity"])
        if not os.path.exists(saveDirPath):
            os.mkdir(saveDirPath)

        self.fsm.add_fs("saveDir", saveDirPath, True)

        gameDirPath = os.path.dirname(os.path.realpath(__main__.__file__))
        self.fsm.add_fs("gameDir", gameDirPath)


    def getAbsPath(self, path):
        return self.fsm.getsyspath(path)


    def getWriteDir(self, path=""):
        return self.fsm.get_fs("saveDir").getsyspath(path)


    def read(self, path, binaryMode=False):
        """
        Read file data

        success, error = read("SomePathToFile.txt")
        """
        try:
            if binaryMode is False:
                fileObject = self.fsm.open(path, "r")
            else:
                fileObject = self.fsm.open(path, "rb")
        except ResourceNotFound as e:
            return False, "Path to file does not exists"
        except:
            return False, "Uncaught Error"

        return fileObject, None


    def write(self, path, data, binaryMode=False):
        """
        Write to file in save directory

        success, error = write("SomePathToFile.txt", "Some Data\nAnd Another Line")
        """
        try:
            if binaryMode is False:
                f = self.fsm.open(path, "w")
            else:
                f = self.fsm.open(path, "wb")
            f.write(data)
            f.close()
        except ResourceNotFound as e:
            return False, "Path to file does not exists"
        except:
            return False, "Uncaught Error"

        return True, None


    def createDirectory(self, path):
        """
        Creates folder in save directory

        success, error = createDirectory("SomeAwsomeFolder")
        """
        try:
            self.fsm.mkdir(path)
        except:
            return False, "Uncaught Error"

        return True, None


    def getDirectoryItems(self, path, namespaces=[]):
        """
        Returns an iterator of all file in the specified path and namespaces

        iter = getDirectoryItems("someAwsomeFolder")
        """
        try:
            return self.fsm.scandir(path, namespaces)
        except ResourceNotFound as e:
            return False, "Path to file does not exists"
        except:
            return False, "Uncaught Error"


    def isDir(self, path):
        """
        Returns True if path is a directory

        dirExists = isDir("SomeAwsomeFolder")
        """
        try:
            return self.fsm.isdir(path)
        except:
            return False, "Uncaught Error"


    def isFile(self, path):
        """
        Returns True if file at path exists

        fileExists = isFile("SomeAwsomeFolder")
        """
        try:
            return self.fsm.isfile(path)
        except:
            return False, "Uncaught Error"


    def getFS(self):
        """
        Returns the MultiFS object from PyFilesystem2

        fsm = getFS()
        """
        return self.fsm
