# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/ElevatorController.py
import math
from consts import VERTICAL_AXIS
from ._base import AileronBaseController, MixedRudderElevatorBaseController

class ElevatorController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [VERTICAL_AXIS]
        self.maxAngle = self.settings.visualSettings.elevatorMaxAngle
        self.matrixProvider.speed = math.radians(settings.visualSettings.elevatorSpeed)


class ElevatorReversedController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [VERTICAL_AXIS]
        self.reversed = True
        self.maxAngle = self.settings.visualSettings.elevatorMaxAngle
        self.matrixProvider.speed = math.radians(settings.visualSettings.elevatorSpeed)