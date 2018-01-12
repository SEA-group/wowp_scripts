# Embedded file name: scripts/client/fm/FMPlayerAvatar.py
import functools
import BigWorld
from EntityHelpers import canFireControllEntity, EntityStates
import Settings
from fm.FMAvatarMethods import fmAvatarMethods

def fmPlayerAvatar(objClass):
    FM_FILTER = EntityStates.CREATED | EntityStates.WAIT_START | EntityStates.GAME_CONTROLLED | EntityStates.DESTROYED_FALL | EntityStates.PRE_START_INTRO

    def fm(func):

        @functools.wraps(func)
        def decorated(*args, **kwargs):
            if args[0].filter.__class__ == BigWorld.FMFilter:
                getattr(args[0].filter, func.func_name)(*args[1:], **kwargs)

        return decorated

    @fmAvatarMethods(fm)

    class PlayerAvatar(objClass):

        def __resetFiring(self):
            self.__firing = False
            self.__confirmed = 0
            self.__ready = 255
            self.__fired = 0

        def onBecomePlayer(self):
            objClass.onBecomePlayer(self)
            self.__resetFiring()

        def calcCorrectFireFlags(self, flag):
            flag = objClass.calcCorrectFireFlags(self, flag)
            if canFireControllEntity(self):
                armaments = self.controllers['weapons'].calcArmaments(flag)
                self.__firing = armaments != 0
                if not self.lastArmamentStates:
                    self.lastArmamentStates = armaments
            else:
                self.__firing = False
            return flag

        def __useFMFilter(self):
            return EntityStates.inState(self, FM_FILTER) and Settings.g_instance.getFastFMEnabled()

        def createFilter(self):
            if self.__useFMFilter():
                return BigWorld.FMFilter()
            else:
                return objClass.createFilter(self)

        def movementFilter(self):
            if self.__useFMFilter():
                return self.filter.__class__ == BigWorld.FMFilter
            else:
                return objClass.movementFilter(self)

        def onRespawn(self):
            objClass.onRespawn(self)
            if self.filter.__class__ == BigWorld.FMFilter:
                self._resetAirplaneFilter()
            self.__resetFiring()

        def singleShot(self, groups):
            self.__confirmed |= ~self.__fired & groups
            self.__ready &= ~groups
            self.__fired &= ~groups

        def singleShotReady(self, groups):
            self.__ready |= groups

        def onSingleShot(self, groups):
            pass

        def shootingGroups(self):
            if self.__useFMFilter():
                if self.__firing:
                    return self.lastArmamentStates
                return 0
            return self.armamentStates

        def popSingleShotGroups(self, groups):
            ready = self.__ready & groups
            self.__ready &= ~ready
            self.__fired |= ready
            res = self.__confirmed | ready
            self.__confirmed = 0
            return res

        def set_fmTimeOffset(self, oldValue):
            if self.filter.__class__ == BigWorld.PredictionFilter:
                self.filter.fmTimeOffset = float(self.fmTimeOffset) / 255

    PlayerAvatar.__name__ = objClass.__name__
    return PlayerAvatar