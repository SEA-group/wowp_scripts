# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/SimplePropellorController.py
import BigWorld
from clientConsts import PROPELLOR_TRANSITION_TIME, FORCE_AXIS_DEATH_VALUE, FORCE_AXIS_FALL_VALUE
from consts import FORCE_AXIS
from ._base import PartAnimatorBase, FORCE_VALUE_FOSAGE, FORCE_VALUE_LOW

class SimplePropellorBase(PartAnimatorBase):
    SINGLE = False

    def __init__(self, playerId, settings, direction):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.matrixProvider = BigWorld.PropellorMatrixProvider(1.0 / PROPELLOR_TRANSITION_TIME * 2.0, direction)
        self.axis = [FORCE_AXIS]

    def setValue(self, value, axis):
        settings = self.settings.visualSettings
        if value == FORCE_AXIS_DEATH_VALUE:
            speed = 0.0
        elif value >= FORCE_VALUE_FOSAGE:
            speed = settings.rotorSpeedFosage
        elif value >= FORCE_VALUE_LOW:
            speed = settings.rotorSpeedLow + (settings.rotorSpeedNormal - settings.rotorSpeedLow) * (1 + value)
        elif value == FORCE_AXIS_FALL_VALUE:
            speed = settings.rotorSpeedFalling
        else:
            speed = 0.0
        self.matrixProvider.speed = speed


class SimplePropellorL(SimplePropellorBase):

    def __init__(self, playerId, settings):
        SimplePropellorBase.__init__(self, playerId, settings, 1)


class SimplePropellorR(SimplePropellorBase):

    def __init__(self, playerId, settings):
        SimplePropellorBase.__init__(self, playerId, settings, -1)