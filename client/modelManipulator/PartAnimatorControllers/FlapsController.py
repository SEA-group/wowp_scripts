# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/FlapsController.py
import math
from consts import FLAPS_AXIS
from consts import FORCE_AXIS
from ._base import MixedBaseController
from clientConsts import FLAPS_SWITCHING_BY_FORCE

class FlapsController(MixedBaseController):

    def __init__(self, playerId, settings):
        MixedBaseController.__init__(self, playerId, settings)
        if FLAPS_SWITCHING_BY_FORCE:
            self.axis = [FLAPS_AXIS, FORCE_AXIS]
        else:
            self.axis = [FLAPS_AXIS]
        for axis in self.axis:
            self.axisValues[axis] = 0.0

        self.matrixProvider.speed = math.radians(settings.visualSettings.flapperSpeed)
        self.reversed = True

    def animateValues(self):
        self.matrixProvider.pitch = 0
        if self.axisValues[FLAPS_AXIS] != 0 or self.axisValues.get(FORCE_AXIS, 0) == -1:
            self.matrixProvider.pitch = self.settings.visualSettings.flapperMaxAngle
            if self.reversed:
                self.matrixProvider.pitch = -self.matrixProvider.pitch


class FlapsControllerL(FlapsController):

    def __init__(self, playerId, settings):
        FlapsController.__init__(self, playerId, settings)


class FlapsControllerR(FlapsController):
    pass


class UpperFlapsController(FlapsController):

    def __init__(self, playerId, settings):
        FlapsController.__init__(self, playerId, settings)
        self.reversed = False


class LowerFlapsController(FlapsController):

    def __init__(self, playerId, settings):
        FlapsController.__init__(self, playerId, settings)
        self.reversed = True