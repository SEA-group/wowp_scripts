# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/BombHatchesController.py
__author__ = 'm_antipov'
from ._base import PartAnimatorBase
from consts import ANIMATION_TRIGGERS
import math
import BigWorld

class HatchControllerBase(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.matrixProvider = BigWorld.AileronMatrixProvider()
        self.reversed = False


class BombHatchControllerR(HatchControllerBase):

    def __init__(self, playerId, settings):
        HatchControllerBase.__init__(self, playerId, settings)
        self.triggers = [ANIMATION_TRIGGERS.BOMB_HATCH_OPEN]
        vs = self.settings.visualSettings
        self.bombHatchOpenSpeed = math.radians(vs.bombHatchOpenSpeed if hasattr(vs, 'bombHatchOpenSpeed') else 400.0)
        self.bombHatchCloseSpeed = math.radians(vs.bombHatchCloseSpeed if hasattr(vs, 'bombHatchCloseSpeed') else 100.0)
        self.bombHatchMaxAngle = math.radians(vs.bombHatchMaxAngle if hasattr(vs, 'bombHatchMaxAngle') else 90)

    def trigger(self, tigger, value):
        if value > 0.0:
            self.matrixProvider.speed = self.bombHatchOpenSpeed
        else:
            self.matrixProvider.speed = self.bombHatchCloseSpeed
        angle = self.bombHatchMaxAngle * value
        self.matrixProvider.roll = -angle if self.reversed else angle


class BombHatchControllerL(BombHatchControllerR):

    def __init__(self, playerId, settings):
        BombHatchControllerR.__init__(self, playerId, settings)
        self.reversed = True