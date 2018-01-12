# Embedded file name: scripts/client/AvatarVSEComponent.py
import weakref
from AvatarControllerBase import AvatarControllerBase

class AvatarVSEComponent(AvatarControllerBase):

    def __init__(self, owner):
        AvatarControllerBase.__init__(self, owner)
        self.__cppObj = None
        return

    @property
    def _cppObj(self):
        return self.__cppObj()

    def _init(self, cppObj):
        self.__cppObj = weakref.ref(cppObj)

    def _destroy(self):
        self.__cppObj = None
        return