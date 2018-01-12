# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/MixedAileronElevator.py
import math
from consts import ROLL_AXIS, VERTICAL_AXIS
from ._base import MixedBaseController, AileronBaseController

class MixedAileronElevatorBaseController(MixedBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [ROLL_AXIS, VERTICAL_AXIS]
        self.axisValues = {ROLL_AXIS: 0.0,
         VERTICAL_AXIS: 0.0}
        self.matrixProvider.speed = math.radians(settings.visualSettings.aileronSpeed)

    def animateValues(self):
        aileron = self.settings.visualSettings.aileronMaxAngle * self.axisValues[ROLL_AXIS]
        if self.reversed:
            aileron = -aileron
        self.matrixProvider.pitch = (aileron + self.settings.visualSettings.elevatorMaxAngle * self.axisValues[VERTICAL_AXIS]) / 2


class LeftMixedAileronElevatorController(MixedAileronElevatorBaseController):

    def __init__(self, playerId, settings):
        MixedAileronElevatorBaseController.__init__(self, playerId, settings)
        self.reversed = False


class RightMixedAileronElevatorController(MixedAileronElevatorBaseController):

    def __init__(self, playerId, settings):
        MixedAileronElevatorBaseController.__init__(self, playerId, settings)
        self.reversed = True