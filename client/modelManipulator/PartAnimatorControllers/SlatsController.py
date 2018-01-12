# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/SlatsController.py
import math
import BigWorld
import consts
from clientConsts import SLATS_AXIS
from ._base import PartAnimatorBase

class SlatsController(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.axis = [SLATS_AXIS]
        self.reversed = False
        self.matrixProvider = BigWorld.VectorOffsetProvider((0, 0, 0))
        self.maxAngle = self.settings.visualSettings.slateOffset
        self.slateOnAngle = math.radians(self.settings.visualSettings.slateOnAngle)
        self.speed = math.radians(settings.visualSettings.slateSpeed)
        self.__callback = None
        self.__target = None
        self.__currentValue = 0
        self.__slateOn = False
        self.__lastActiveTime = 0
        self.minWorkingTime = 2
        return

    def setValue(self, value, axis):
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        if value >= self.slateOnAngle:
            self.__slateOn = True
            self.__lastActiveTime = BigWorld.time()
        elif self.__slateOn:
            if self.__lastActiveTime + self.minWorkingTime < BigWorld.time():
                self.__slateOn = False
        self.__update((-self.maxAngle if self.reversed else self.maxAngle) if self.__slateOn else 0)
        return

    def __update(self, target = None):
        self.__callback = None
        if target is not None:
            self.__target = target
        if abs(self.__currentValue - self.__target) <= self.speed:
            self.__currentValue = self.__target
        else:
            self.__currentValue += self.speed if self.__target > self.__currentValue else -self.speed
        self.matrixProvider.offset = (0, 0, self.__currentValue)
        if self.__currentValue != self.__target:
            self.__callback = BigWorld.callback(0.05, self.__update)
        return

    def destroy(self):
        PartAnimatorBase.destroy(self)
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        return


class SlatsAileronController(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.axis = [SLATS_AXIS]
        self.matrixProvider = BigWorld.AileronMatrixProvider()
        self.maxAngle = self.settings.visualSettings.slateOffset
        self.slateOnAngle = math.radians(self.settings.visualSettings.slateOnAngle)
        self.speed = math.radians(settings.visualSettings.slateSpeed)

    def setValue(self, value, axis):
        self.matrixProvider.pitch = self.maxAngle if value >= self.slateOnAngle else 0