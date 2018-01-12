# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/PilotHeadController.py
import math
import BigWorld
from random import choice
from consts import HORIZONTAL_AXIS, VERTICAL_AXIS, IS_EDITOR
from ._base import AileronBaseController
from EntityHelpers import EntityStates, isAvatar

class PilotHeadController(AileronBaseController):
    PASSIVE_TIME = 3
    CALLBACK_TIME = 0.1

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [HORIZONTAL_AXIS, VERTICAL_AXIS]
        self.axisValues = {HORIZONTAL_AXIS: 0.0,
         VERTICAL_AXIS: 0.0}
        self.maxAngle = self.settings.visualSettings.rudderMaxAngle
        self.__callback = BigWorld.callback(PilotHeadController.CALLBACK_TIME, self.__idleAnimate)
        self.__passiveTime = PilotHeadController.PASSIVE_TIME
        self.matrixProvider.speed = math.radians(settings.visualSettings.rudderSpeed)

    def setValue(self, value, axis):
        if abs(value) > 0.1 and self.axisValues[axis] != value:
            self.axisValues[axis] = value
            self.animateValues()

    def animateValues(self):
        rudder_h = self.axisValues[HORIZONTAL_AXIS] if not self.reversed else -self.axisValues[HORIZONTAL_AXIS]
        rudder = max(0, self.axisValues[VERTICAL_AXIS])
        rudder_v = -rudder if not self.reversed else rudder
        self.matrixProvider.yaw = self.maxAngle * rudder_h
        self.matrixProvider.pitch = self.maxAngle * rudder_v
        self.__passiveTime = PilotHeadController.PASSIVE_TIME

    def __idleAnimate(self):
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        if not IS_EDITOR and isAvatar(BigWorld.player()) and EntityStates.inState(BigWorld.player(), EntityStates.GAME):
            if self.__passiveTime > 0:
                self.__passiveTime -= PilotHeadController.CALLBACK_TIME
            else:
                rudderY = choice([-1, 0, 1])
                self.matrixProvider.yaw = self.maxAngle * rudderY
                rudderP = choice([0, -1]) * (1 if not self.reversed else -1)
                self.matrixProvider.pitch = self.maxAngle * rudderP
                self.__passiveTime = PilotHeadController.PASSIVE_TIME
        self.__callback = BigWorld.callback(PilotHeadController.CALLBACK_TIME, self.__idleAnimate)
        return

    def destroy(self):
        AileronBaseController.destroy(self)
        if self.__callback is not None:
            BigWorld.cancelCallback(self.__callback)
        return


class PilotHeadControllerIdle(PilotHeadController):

    def __init__(self, playerId, settings):
        PilotHeadController.__init__(self, playerId, settings)
        self.reversed = True

    def setValue(self, value, axis):
        pass