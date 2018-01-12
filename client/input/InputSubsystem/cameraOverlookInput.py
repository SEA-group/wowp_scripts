# Embedded file name: scripts/client/input/InputSubsystem/cameraOverlookInput.py
import math
import Math
import BigWorld
import InputMapping
import GameEnvironment
from CameraStates import CameraState
from MathExt import clamp
from ICMultiUpdate import ICMultiUpdate
from consts import FREE_HORIZONTAL_CAM, FREE_VERTICAL_CAM
from collections import namedtuple
cmdInfo = namedtuple('cmdInfo', ('axis', 'value'))

class SIDE:
    FRONT = Math.Vector3(1, 0, 0)
    BACK = Math.Vector3(-1, 0, 0)
    RIGHT = Math.Vector3(0, 1, 0)
    LEFT = Math.Vector3(0, -1, 0)
    UP = Math.Vector3(0, 0, 1)
    DOWN = Math.Vector3(0, 0, -1)


_SENSITIVITY_CFC = 0.1
_BASE_SMOOTH_WINDOW = 10
_HUD_MANAGER_UPDATE_TIME = 0.1

class cameraOverlookInput(ICMultiUpdate):

    def __init__(self):
        self.__keyMainDirect = Math.Vector3(0, 0, 0)
        self.__keyStaticDirect = Math.Vector3(0, 0, 0)
        self.__axisValue = {FREE_HORIZONTAL_CAM: 0,
         FREE_VERTICAL_CAM: 0}
        self.__mouseExtraValue = {'x': 0,
         'y': 0}
        self.__mapping_function = {}
        self.__mouseMode = False
        self.__turnSpeed = 100
        self.__staticVision = False
        self.__lastSmoothWin = {}
        self.__smoothStack = {}
        self.__enemyTarget = None
        self.__linkEvents()
        self.__last_hud_switch = False
        self.__cmdDict = {}
        self.__currCmdState = {}
        ICMultiUpdate.__init__(self, (_HUD_MANAGER_UPDATE_TIME, self.__hudManager))
        return

    def __linkEvents(self):
        GameEnvironment.g_instance.eSetTargetEntity += self.__setEnemyTarget

    def __unlinkEvents(self):
        GameEnvironment.g_instance.eSetTargetEntity -= self.__setEnemyTarget

    @property
    def __cameraStrategy(self):
        return GameEnvironment.getCamera().getDefualtStrategies['CameraStrategyGamepad']

    def __hudManager(self):
        active = True
        if active != self.__last_hud_switch:
            self.__last_hud_switch = active

    def __setEnemyTarget(self, enemy):
        if self.__enemyTarget != enemy and enemy is not None:
            self.__enemyTarget = enemy
        return

    def restart(self):
        self.__lastSmoothWin = {}
        self.__smoothStack = {}
        self.__last_hud_activity = False
        ICMultiUpdate.restart(self)

    def dispose(self):
        self.__freeOutAllButtonsOnDestroy()
        ICMultiUpdate.dispose(self)
        self.__mapping_function = {}
        self.__enemyTarget = None
        self.__unlinkEvents()
        return

    def setTurnSpeed(self, value):
        self.__turnSpeed = value

    def __enableTargetLook(self, fired):
        on_of = fired and self.__enemyTarget is not None
        return

    def __cmdKeyTurn(self, fired, turnDir):
        self.__keyMainDirect += turnDir if fired else -1 * turnDir
        if fired:
            self.__keyStaticDirect = turnDir

    def processJoystickEvent(self, event):
        jSet = InputMapping.g_instance.joystickSettings
        if event.axis == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_AXIS and (event.deviceId == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEVICE or 0 == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEVICE):
            hValue = event.value
            if abs(hValue) <= jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEAD_ZONE:
                hValue = 0.0
            else:
                hValue = math.copysign((abs(hValue) - jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEAD_ZONE) / (1 - jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEAD_ZONE), hValue)
            hValue = self.__signalSmoothing(jSet.FREE_HORIZONTAL_CAM_GAMEPAD_AXIS, hValue, jSet.FREE_HORIZONTAL_CAM_GAMEPAD_SMOOTH_WINDOW)
            hValue = self.__signalDiscrete(jSet.FREE_HORIZONTAL_CAM_GAMEPAD_SENSITIVITY, hValue, event.deviceId, event.axis)
            self.__axisValue[FREE_HORIZONTAL_CAM] = clamp(-1.0, hValue, 1.0)
            self.__setAxisMove()
        elif event.axis == jSet.FREE_VERTICAL_CAM_GAMEPAD_AXIS and (event.deviceId == jSet.FREE_VERTICAL_CAM_GAMEPAD_DEVICE or 0 == jSet.FREE_VERTICAL_CAM_GAMEPAD_DEVICE):
            vValue = event.value
            if abs(vValue) <= jSet.FREE_VERTICAL_CAM_GAMEPAD_DEAD_ZONE:
                vValue = 0.0
            else:
                vValue = math.copysign((abs(vValue) - jSet.FREE_VERTICAL_CAM_GAMEPAD_DEAD_ZONE) / (1 - jSet.FREE_VERTICAL_CAM_GAMEPAD_DEAD_ZONE), vValue)
            vValue = self.__signalSmoothing(jSet.FREE_VERTICAL_CAM_GAMEPAD_AXIS, vValue, jSet.FREE_VERTICAL_CAM_GAMEPAD_SMOOTH_WINDOW)
            vValue = self.__signalDiscrete(jSet.FREE_VERTICAL_CAM_GAMEPAD_SENSITIVITY, vValue, event.deviceId, event.axis)
            vValue = vValue if jSet.INVERT_FREE_VERTICAL_CAM_GAMEPAD else -vValue
            self.__axisValue[FREE_VERTICAL_CAM] = clamp(-1.0, vValue, 1.0)
            self.__setAxisMove()

    def __signalDiscrete(self, discrete, value, deviceId, axis):
        SENSITIVITY = 14 * discrete
        joyDPI = BigWorld.getJoystickResolution(deviceId, axis) / pow(2.0, math.floor(SENSITIVITY))
        halfSingleSignal = 0.5 / joyDPI
        if abs(value) < 0.25 * halfSingleSignal or abs(value) > 1.0 - 0.25 * halfSingleSignal:
            return value
        absValue = math.floor(abs(value) * joyDPI) / joyDPI + halfSingleSignal
        return math.copysign(absValue, value)

    def __signalSmoothing(self, axis, value, win, e = 0.99):
        if self.__lastSmoothWin.get(axis, None) != win:
            self.__lastSmoothWin[axis] = win
            if self.__smoothStack.get(axis, None):
                self.__smoothStack[axis] = []
        if value != 0:
            window = max(int(_BASE_SMOOTH_WINDOW * win), 1)
            self.__smoothStack.setdefault(axis, []).append(value)
            if len(self.__smoothStack[axis]) > window:
                self.__smoothStack[axis].pop(0)
            if abs(value) >= e:
                return math.copysign(1.0, value)
            return sum(self.__smoothStack[axis]) / len(self.__smoothStack[axis])
        else:
            self.__smoothStack[axis] = [0]
            return 0
            return

    def __setAxisMove(self):
        x = self.__axisValue[FREE_HORIZONTAL_CAM]
        y = self.__axisValue[FREE_VERTICAL_CAM]

    def processMouseEvent(self, event):
        """ main mouse event """
        y = math.radians(_SENSITIVITY_CFC * event.dy)
        x = math.radians(_SENSITIVITY_CFC * event.dx)

    def __activateMouse(self, value):
        self.__mouseMode = bool(value)

    def __setStaticVision(self, value):
        self.__staticVision = value
        if not self.__keyMainDirect.length:
            self.__keyStaticDirect = Math.Vector3(0, 0, 0)

    def __applyInput(self, pressed, cmd):
        value = self.__cmdDict[cmd].value
        axis = self.__cmdDict[cmd].axis
        axisValue = 0.0
        if pressed:
            axisValue = value
        self.__currCmdState[axis] = axisValue
        BigWorld.player().applyInputAxis(axis, axisValue)

    def __normalize(self, value):
        if value > 1.0:
            return value - 2.0
        if value < -1.0:
            return 2.0 + value
        return value

    def __addCMD(self, processor, cmd):
        func = lambda value: self.__applyInput(value, cmd)
        processor.addPredicate(cmd, self.__overviewPredicate)
        processor.addListeners(cmd, None, None, func)
        self.__mapping_function[cmd] = func
        return

    @staticmethod
    def __overviewPredicate():
        camState = GameEnvironment.getCamera().getState()
        return not GameEnvironment.getCamera().isSniperMode and camState not in (CameraState.Bomber, CameraState.Gunner)

    def addCommandListeners(self, processor):
        self.__cmdDict = {InputMapping.CMD_SIDE_VIEW_LEFT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=0.5),
         InputMapping.CMD_SIDE_VIEW_RIGHT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=-0.5),
         InputMapping.CMD_FRONT_VIEW: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=0.0),
         InputMapping.CMD_BACK_VIEW: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=1.0),
         InputMapping.CMD_SIDE_VIEW_UP: cmdInfo(axis=FREE_VERTICAL_CAM, value=0.5),
         InputMapping.CMD_SIDE_VIEW_DOWN: cmdInfo(axis=FREE_VERTICAL_CAM, value=-0.5),
         InputMapping.CMD_SIDE_VIEW_UP_LEFT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=0.25),
         InputMapping.CMD_SIDE_VIEW_UP_RIGHT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=-0.25),
         InputMapping.CMD_SIDE_VIEW_DOWN_LEFT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=0.75),
         InputMapping.CMD_SIDE_VIEW_DOWN_RIGHT: cmdInfo(axis=FREE_HORIZONTAL_CAM, value=-0.75)}
        for cmd in self.__cmdDict.iterkeys():
            self.__addCMD(processor, cmd)

    def removeCommandListeners(self, processor):
        for cmd in self.__cmdDict.iterkeys():
            processor.removeListeners(cmd, None, None, self.__mapping_function[cmd])

        return

    def __freeOutAllButtonsOnDestroy(self):
        """
            some chit. Need on switch InputSystem.
        """
        buttons_cmd_list = [InputMapping.CMD_OVERLOOK_MOD, InputMapping.CMD_STATIC_MOD, InputMapping.CMD_TARGET_CAMERA] + self.__cmdDict.keys()
        commandProcessor = GameEnvironment.getInput().commandProcessor
        for cmd in buttons_cmd_list:
            commandProcessor.getCommand(cmd).isFired = False

    def __resetCurrCmdState(self):
        self.__currCmdState.clear()