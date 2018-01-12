# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/PropellorController.py
import BigWorld
import Event
from functools import partial
from clientConsts import PROPELLOR_TRANSITION_TIME, FORCE_AXIS_DEATH_VALUE, FORCE_AXIS_FALL_VALUE
from consts import FORCE_AXIS
from ._base import PartAnimatorBase, PROPELLER_SOLID, FORCE_VALUE_FOSAGE, PROPELLER_FORSAGE, FORCE_VALUE_LOW, PROPELLER_NORMAL

class PropellorControllerBase(PartAnimatorBase):
    SINGLE = False

    def __init__(self, playerId, settings, direction):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.__isBroken = False
        self.__lastValue = -1
        self.__lastState = -1
        self.matrixProvider = BigWorld.PropellorMatrixProvider(1.0 / PROPELLOR_TRANSITION_TIME * 2.0, direction)
        self.axis = [FORCE_AXIS]
        self.fashions = [ BigWorld.PyAlphaTransitionFashion(1.0 / PROPELLOR_TRANSITION_TIME, 1.0 if i == 0 else 0.0) for i in range(3) ]
        self.callback = Event.Event()
        for idFashion, fashion in enumerate(self.fashions):
            fashion.callback = partial(self.callback, idFashion + 1)

        self.setValue(self.matrixProvider.speed, FORCE_AXIS)

    def setAngle(self, angle):
        self.matrixProvider.angle = angle

    def setValue(self, value, axis):
        settings = self.settings.visualSettings
        self.__lastValue = value
        if value == FORCE_AXIS_DEATH_VALUE:
            state, speed = PROPELLER_SOLID, 0.0
        elif self.__isBroken:
            state, speed = PROPELLER_SOLID, settings.rotorSpeedBroken
        elif value >= FORCE_VALUE_FOSAGE:
            state, speed = PROPELLER_FORSAGE, settings.rotorSpeedFosage
        elif value >= FORCE_VALUE_LOW:
            state, speed = PROPELLER_NORMAL, settings.rotorSpeedLow + (settings.rotorSpeedNormal - settings.rotorSpeedLow) * (1 + value)
        elif value == FORCE_AXIS_FALL_VALUE:
            state, speed = PROPELLER_SOLID, settings.rotorSpeedFalling
        else:
            state, speed = PROPELLER_SOLID, 0.0
        self.__setState(state)
        self.matrixProvider.speed = speed

    def __setState(self, newState):
        if self.__lastState != newState:
            for i in range(len(self.fashions)):
                self.fashions[i].start(1.0 if newState == i else 0.0)

            self.__lastState = newState

    def setBroken(self, broken):
        if self.__isBroken != broken:
            self.__isBroken = broken
            self.setValue(self.__lastValue, FORCE_AXIS)


class PropellorControllerL(PropellorControllerBase):

    def __init__(self, playerId, settings):
        PropellorControllerBase.__init__(self, playerId, settings, 1)


class PropellorControllerR(PropellorControllerBase):

    def __init__(self, playerId, settings):
        PropellorControllerBase.__init__(self, playerId, settings, -1)