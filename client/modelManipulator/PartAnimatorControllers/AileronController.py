# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/AileronController.py
import math
from consts import ROLL_AXIS
from ._base import AileronBaseController

class LeftAileronController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [ROLL_AXIS]
        self.matrixProvider.speed = math.radians(settings.visualSettings.aileronSpeed)


class RightAileronController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [ROLL_AXIS]
        self.reversed = True
        self.matrixProvider.speed = math.radians(settings.visualSettings.aileronSpeed)