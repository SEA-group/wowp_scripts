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
        self._owner.planeConfigurationChanged += self._onPlaneConfigurationChanged

    def _destroy(self):
        self.__cppObj = None
        self._owner.planeConfigurationChanged -= self._onPlaneConfigurationChanged
        return

    def _onPlaneConfigurationChanged(self):
        obj = self.__cppObj()
        if obj is None:
            return
        else:
            obj.onPlaneConfigurationChanged()
            return