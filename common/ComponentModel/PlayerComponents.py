# Embedded file name: scripts/common/ComponentModel/PlayerComponents.py
import sys
import inspect
import BigWorld
from Component import Component, OutputSlot

class PlayerMaxRotationSpeed(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [OutputSlot('pitch', Component.SLOT_ANGLE, PlayerMaxRotationSpeed._pitch), OutputSlot('roll', Component.SLOT_ANGLE, PlayerMaxRotationSpeed._roll), OutputSlot('yaw', Component.SLOT_ANGLE, PlayerMaxRotationSpeed._yaw)]

    def _pitch(self):
        return getattr(BigWorld.player(), 'maxPitchRotationSpeed', 1.0)

    def _roll(self):
        return getattr(BigWorld.player(), 'maxRollRotationSpeed', 1.0)

    def _yaw(self):
        return getattr(BigWorld.player(), 'maxYawRotationSpeed', 1.0)


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))