# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/RudderController.py
import math
import consts
from consts import HORIZONTAL_AXIS
from ._base import AileronBaseController, MixedRudderElevatorBaseController

class RudderController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [HORIZONTAL_AXIS]
        self.maxAngle = self.settings.visualSettings.rudderMaxAngle
        self.matrixProvider.speed = math.radians(settings.visualSettings.rudderSpeed)
        self._shakableAxis = consts.ROTATION_AXIS.YAW

    def setValue(self, value, axis):
        self.matrixProvider.yaw = -self.maxAngle * value


class RightMixedRudderElevatorController(MixedRudderElevatorBaseController):

    def __init__(self, playerId, settings):
        MixedRudderElevatorBaseController.__init__(self, playerId, settings)
        self.reversed = True


class LeftMixedRudderElevatorController(MixedRudderElevatorBaseController):

    def __init__(self, playerId, settings):
        MixedRudderElevatorBaseController.__init__(self, playerId, settings)
        self.reversed = False