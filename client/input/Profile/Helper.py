# Embedded file name: scripts/client/input/Profile/Helper.py
from ICMultiUpdate import ICMultiUpdate
from CameraStates import CameraState
from consts import ROLL_AXIS, VERTICAL_AXIS, HORIZONTAL_AXIS, BATTLE_MODE
from input.InputSubsystem.MouseInput import MouseCursorDirection
from input.InputSubsystem.GunnerInput import GunnerInput
from CommonSettings import ALTERNATIVE_BATTLE_MODE_INPUT_SETTINGS
import GameEnvironment
import Settings
import BigWorld
import math

class JoyMouseEvent(object):

    def __init__(self):
        self.dx = 0
        self.dy = 0


class KeyMouseEvent(object):
    kmState = True

    def __init__(self):
        self.dx = 0
        self.dy = 0


mouse_event_dt = 0.05

class MouseProfileProxy(object):
    Settings = ALTERNATIVE_BATTLE_MODE_INPUT_SETTINGS
    axisFilter = (VERTICAL_AXIS, ROLL_AXIS, HORIZONTAL_AXIS)

    def __init__(self, profile):
        self._profile = profile
        self._notControlledByUser = 0
        self.__isMouseActivate = False
        self.mouseSpeedAxis = {VERTICAL_AXIS: 0,
         ROLL_AXIS: 0,
         HORIZONTAL_AXIS: 0}
        self.battleMode = BATTLE_MODE.COMBAT_MODE

    def sendExtraAxis(self, axis, value):
        self._profile.sendExtraAxis(axis, value)

    def getSpeedAxis(self, axis):
        return self.mouseSpeedAxis.get(axis, 0)

    def getJoystickToMouseTranslation(self, dt):
        yaw = self.getSpeedAxis(HORIZONTAL_AXIS)
        roll = self.getSpeedAxis(ROLL_AXIS)
        dx = yaw if abs(yaw) > abs(roll) else roll
        dy = self.getSpeedAxis(VERTICAL_AXIS)
        return (dx * dt, dy * dt)

    def setSpeedAxis(self, axis, value):
        if axis in MouseProfileProxy.axisFilter:
            dz = MouseProfileProxy.Settings.DEAD_ZONE
            hValue = math.copysign(max(abs(value) - dz, 0) / (1 - dz), value)
            self.mouseSpeedAxis[axis] = hValue * MouseProfileProxy.Settings.AXIS_MAX_SPEED.get(axis, 0)

    def setBattleDirection(self, v):
        pass

    def setMouseSpeedAxis(self):
        for axis in self.mouseSpeedAxis:
            self._profile.sendExtraAxis(axis, 0)

    @staticmethod
    def setCamDirection(direction):
        pass

    @staticmethod
    def getMouseIntensity(angle, correctMaxAngle):
        return 1

    @property
    def radiusOfConducting(self):
        return 1

    @property
    def settings(self):
        return MouseProfileProxy.Settings

    @staticmethod
    def mouseSensitivity(event):
        return MouseProfileProxy.Settings.mouseSensitivity

    @property
    def isMouseActivate(self):
        return self.__isMouseActivate

    @isMouseActivate.setter
    def isMouseActivate(self, value):
        if BigWorld.player().planeType in MouseProfileProxy.Settings.VALID_PLANE_TYPES:
            self.__isMouseActivate = value in [BATTLE_MODE.ASSAULT_MODE]
            if self.__isMouseActivate:
                self.setMouseSpeedAxis()

    def reset(self):
        self._notControlledByUser = 0
        self.__isMouseActivate = False
        self.mouseSpeedAxis = {VERTICAL_AXIS: 0,
         ROLL_AXIS: 0,
         HORIZONTAL_AXIS: 0}
        self.battleMode = BATTLE_MODE.COMBAT_MODE


class MouseInputProxy(object):

    def __init__(self, profile):
        pass

    def restart(self):
        pass

    def dispose(self):
        pass

    def notControlledByUser(self, v):
        pass

    def processMouseEvent(self, e):
        pass


class GunnerInputProxy(object):

    def __init__(self, profile):
        pass

    def restart(self):
        pass

    def dispose(self):
        pass

    def eBattleModeChange(self, v):
        pass

    def processMouseEvent(self, e):
        pass

    @property
    def isActive(self):
        return False


def getMouseInput(planeType):
    if planeType in ALTERNATIVE_BATTLE_MODE_INPUT_SETTINGS.VALID_PLANE_TYPES:
        return MouseCursorDirection
    return MouseInputProxy


def getGunnerInput(planeType):
    if planeType in ALTERNATIVE_BATTLE_MODE_INPUT_SETTINGS.VALID_PLANE_TYPES:
        return GunnerInput
    return GunnerInputProxy


class KeyEventFilter(object):
    filterAxis = [ROLL_AXIS]
    state_list = [BATTLE_MODE.ASSAULT_MODE, BATTLE_MODE.GUNNER_MODE]

    def __init__(self, ktlm):
        self._ktlm = ktlm
        self._last_mouse_event = {}
        self._last_key_event = {}
        self._last_cam_state = -1

    def clear_last_key_event(self, state):
        if state in KeyEventFilter.state_list or self._last_cam_state in KeyEventFilter.state_list:
            self._ktlm.profile.altMouseEvent(KeyMouseEvent())
            for ax in self._last_mouse_event.iterkeys():
                self._ktlm.set_mouse_event_speed(ax, 0)

            self._last_mouse_event.clear()
            for ax in self._last_key_event.iterkeys():
                if ax in KeyEventFilter.filterAxis:
                    self._ktlm.profile.sendAxis(ax, 0)

            self._last_key_event.clear()
        self._last_cam_state = state

    def dispose(self):
        self._ktlm = None
        return

    def slipCompensationVisualisation(self):
        self._ktlm.profile.slipCompensationVisualisation()

    def sendAxis(self, axis, value):
        if self._ktlm.profile.isKeyEventFilterActive:
            if axis in KeyEventFilter.filterAxis:
                self._last_mouse_event[axis] = value
                self._ktlm.set_mouse_event_speed(axis, value)
            else:
                self._last_key_event[axis] = value
                self._ktlm.profile.sendAxis(axis, value)
        else:
            self._last_key_event[axis] = value
            self._ktlm.profile.sendAxis(axis, value)


class KeysTurnLikeMouse(ICMultiUpdate):
    move_dict = {ROLL_AXIS: 'x'}
    move_speed_cfc = {ROLL_AXIS: 20}

    def __init__(self, profile):
        self.profile = profile
        self._filter = KeyEventFilter(self)
        self._move_speed = dict(((key, 0) for key in KeysTurnLikeMouse.move_dict.itervalues()))
        self._last_mouse_event = True
        self._maxPitchRotationSpeed = math.degrees(BigWorld.player().maxPitchRotationSpeed)
        ICMultiUpdate.__init__(self, (mouse_event_dt, self.__keys_mouse_move))

    def dispose(self):
        ICMultiUpdate.dispose(self)
        self._filter.dispose()
        self.profile = None
        return

    def restart(self):
        ICMultiUpdate.restart(self)
        self._maxPitchRotationSpeed = math.degrees(BigWorld.player().maxPitchRotationSpeed)

    def set_mouse_event_speed(self, axis, value):
        ax_key = KeysTurnLikeMouse.move_dict.get(axis, 'null')
        if self._move_speed.has_key(ax_key):
            self._move_speed[ax_key] = -value * KeysTurnLikeMouse.move_speed_cfc.get(axis, 0) * self._maxPitchRotationSpeed

    def __keys_mouse_move(self):
        dx = self._move_speed['x'] * mouse_event_dt
        dy = 0
        if dx or not self._last_mouse_event:
            event = KeyMouseEvent()
            event.dx = dx
            event.dy = dy
            self._last_mouse_event = not dx
            self.profile.altMouseEvent(event)

    def get_filter(self):
        return self._filter

    @staticmethod
    def checkEvent(event):
        return getattr(event, 'kmState', False)

    @staticmethod
    def mouse_event_router(func):

        def wrapper(self, event):
            if self.isKeyEventFilterActive:
                if KeysTurnLikeMouse.checkEvent(event):
                    self._mouse.processMouseEvent(event)
                else:
                    func(self, event)
            else:
                func(self, event)

        return wrapper