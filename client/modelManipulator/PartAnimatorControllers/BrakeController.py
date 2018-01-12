# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/BrakeController.py
import math
import BigWorld
from consts import FORCE_AXIS
from ._base import AileronBaseController, PartAnimatorBase

class BrakeController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [FORCE_AXIS]
        self.matrixProvider.speed = math.radians(settings.visualSettings.brakeSpeed)
        self.reversed = True

    def setValue(self, value, axis):
        self.matrixProvider.yaw = self.settings.visualSettings.brakeMaxAngle if value == -1 else 0
        if self.reversed:
            self.matrixProvider.yaw = -self.matrixProvider.yaw


class LeftBrakeController(BrakeController):

    def __init__(self, playerId, settings):
        BrakeController.__init__(self, playerId, settings)
        self.reversed = False


class RightBrakeController(BrakeController):

    def __init__(self, playerId, settings):
        BrakeController.__init__(self, playerId, settings)
        self.reversed = True


class UpBrakeController(BrakeController):

    def __init__(self, playerId, settings):
        BrakeController.__init__(self, playerId, settings)
        self.reversed = False

    def setValue(self, value, axis):
        self.matrixProvider.pitch = self.settings.visualSettings.brakeMaxAngle if value == -1 else 0
        if self.reversed:
            self.matrixProvider.pitch = -self.matrixProvider.pitch


class DownBrakeController(BrakeController):

    def __init__(self, playerId, settings):
        BrakeController.__init__(self, playerId, settings)
        self.reversed = True

    def setValue(self, value, axis):
        self.matrixProvider.pitch = self.settings.visualSettings.brakeMaxAngle if value == -1 else 0
        if self.reversed:
            self.matrixProvider.pitch = -self.matrixProvider.pitch


class OffsetUpBrakeController(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.axis = [FORCE_AXIS]
        self.reversed = False
        self.matrixProvider = BigWorld.VectorOffsetProvider((0, 0, 0))
        self.maxAngle = self.settings.visualSettings.brakeOffset
        self.speed = math.radians(settings.visualSettings.brakeOffsetSpeed)
        self.__callback = None
        self.__target = None
        self.__currentValue = 0
        return

    def setValue(self, value, axis):
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        self.__update((-self.maxAngle if self.reversed else self.maxAngle) if value == -1 else 0)
        return

    def __update(self, target = None):
        self.__callback = None
        if target is not None:
            self.__target = target
        self.__currentValue += self.speed if self.__target > self.__currentValue else -self.speed
        if abs(self.__currentValue - self.__target) <= self.speed:
            self.__currentValue = self.__target
        self.matrixProvider.offset = (0, self.__currentValue, 0)
        if self.__currentValue != self.__target:
            self.__callback = BigWorld.callback(0.05, self.__update)
        return

    def destroy(self):
        PartAnimatorBase.destroy(self)
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        return


class OffsetDownBrakeController(OffsetUpBrakeController):

    def __init__(self, playerId, settings):
        OffsetUpBrakeController.__init__(self, playerId, settings)
        self.reversed = True