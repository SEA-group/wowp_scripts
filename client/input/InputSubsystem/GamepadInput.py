# Embedded file name: scripts/client/input/InputSubsystem/GamepadInput.py
__author__ = 'm_kobets'
import Keys
import BWPersonality
from CameraStates import CameraState
from EntityHelpers import EntityStates
import GameEnvironment
from ICMultiUpdate import ICMultiUpdate
import InputMapping
import math
from MathExt import *
from consts import ROLL_AXIS, VERTICAL_AXIS, HORIZONTAL_AXIS, FORCE_AXIS, FREE_HORIZONTAL_CAM, FREE_VERTICAL_CAM
from input.InputSubsystem.InputSubsystemBase import InputSubsystemBase
from clientConsts import NOT_CONTROLLED_MOD

class JoyEvent():

    def __init__(self):
        self.deviceId = None
        self.axis = None
        self.value = None
        return


class GamepadInput(InputSubsystemBase, ICMultiUpdate):

    def __init__(self, profile):
        self.__profile = profile
        self.__isExtraMode = False
        self.__axisValue = {VERTICAL_AXIS: 0,
         HORIZONTAL_AXIS: 0,
         FREE_HORIZONTAL_CAM: 0,
         FREE_VERTICAL_CAM: 0}
        self.__rAxisValue = {VERTICAL_AXIS: 0,
         HORIZONTAL_AXIS: 0}
        self.__cameraStrategy = GameEnvironment.getCamera().getDefualtStrategies['CameraStrategyGamepad']
        self.__lastCorrectMaxAngle = None
        self.__correctMaxAngle = None
        self.__lastDataDir = None
        self.__lastUp = None
        self.__notControlledByUser = False
        self.__lastDirection = Math.Vector3(0, 0, 1)
        self.__lockCursor = False
        self.__triggerRight = 0.0
        self.__triggerLeft = 0.0
        joyEvent = JoyEvent()
        for deviceId in BWPersonality.axis:
            for axis in BWPersonality.axis[deviceId]:
                joyEvent.deviceId = deviceId
                joyEvent.axis = axis
                joyEvent.value = BWPersonality.axis[deviceId][axis]
                self.processJoystickEvent(joyEvent)

        BigWorld.player().onStateChanged += self.__ePlayerAvatarChangeState
        ICMultiUpdate.__init__(self, (0.05, self.__sendCursor))
        return

    def __backCamera(self, value):
        camera = GameEnvironment.getCamera()
        if value:
            camera.setState(CameraState.Back)
        else:
            camera.leaveState(CameraState.Back)

    def addCommandListeners(self, processor):
        processor.addListeners(InputMapping.CMD_BACK_VIEW, None, None, self.__backCamera)
        return

    def removeCommandListeners(self, processor):
        processor.removeListeners(InputMapping.CMD_BACK_VIEW, None, None, self.__backCamera)
        return

    def notControlledByUser(self, value):
        self.__notControlledByUser = value
        cValue = value & (NOT_CONTROLLED_MOD.AUTOPILOT | NOT_CONTROLLED_MOD.PLAYER_MENU | NOT_CONTROLLED_MOD.MOUSE_INPUT_BLOCKED | NOT_CONTROLLED_MOD.LOST_WINDOW_FOCUS)
        if cValue and not self.__lockCursor:
            self.__cameraStrategy.lockCursor()
        if not cValue and self.__lockCursor:
            self.__cameraStrategy.unlockCursor()
        self.__lockCursor = bool(cValue)

    @property
    def __inGame(self):
        return EntityStates.inState(BigWorld.player(), EntityStates.GAME)

    @property
    def __inCameraState(self):
        return GameEnvironment.getCamera().getState() == CameraState.GamepadCombat

    @property
    def __isRunning(self):
        return self.__inGame and self.__inCameraState and not self.__notControlledByUser

    def __ePlayerAvatarChangeState(self, oldState, newState):
        pass

    def restart(self):
        ICMultiUpdate.restart(self)
        self.__isExtraMode = False
        self.__lastDataDir = None
        self.__lastUp = None
        self.__cameraStrategy.reset()
        return

    def dispose(self):
        ICMultiUpdate._SuspendUpdates(self)
        if self.__lockCursor:
            self.__cameraStrategy.unlockCursor()
        self.__cameraStrategy = None
        self.__profile = None
        GameEnvironment.getCamera().leaveState(CameraState.Back)
        return

    def __replacement(self, event):
        joyEvent = JoyEvent()
        joyEvent.deviceId = event.deviceId
        joyEvent.axis = event.axis
        joyEvent.value = event.value
        if event.axis == 5:
            self.__triggerRight = event.value
            joyEvent.axis = 2
            joyEvent.value = self.__triggerRight + self.__triggerLeft
        if event.axis == 2:
            self.__triggerLeft = -event.value
            joyEvent.axis = 2
            joyEvent.value = self.__triggerRight + self.__triggerLeft
        return joyEvent

    def processJoystickEvent(self, event):
        event = self.__replacement(event)
        jSet = InputMapping.g_instance.joystickSettings
        if event.axis == jSet.ROLL_AXIS and (event.deviceId == jSet.ROLL_DEVICE or 0 == jSet.ROLL_DEVICE):
            rValue = InputMapping.translateAxisValue(jSet.AXIS_X_CURVE, event.value)
            if abs(rValue) <= jSet.ROLL_DEAD_ZONE:
                rValue = 0.0
            else:
                rValue = math.copysign((abs(rValue) - jSet.ROLL_DEAD_ZONE) / (1.0 - jSet.ROLL_DEAD_ZONE), rValue)
                rValue = -rValue if jSet.INVERT_ROLL else rValue
            self.__profile.sendPrimaryAxis(ROLL_AXIS, clamp(-1.0, -rValue, 1.0))
        elif event.axis == jSet.G_VERTICAL_AXIS and (event.deviceId == jSet.G_VERTICAL_DEVICE or 0 == jSet.G_VERTICAL_DEVICE):
            vValue = -event.value if jSet.INVERT_G_VERTICAL else event.value
            self.__rAxisValue[VERTICAL_AXIS] = vValue
            r = min(math.hypot(vValue, self.__rAxisValue[HORIZONTAL_AXIS]), 1)
            DEAD_ZONE = jSet.G_VERTICAL_DEAD_ZONE
            if r <= DEAD_ZONE:
                self.__axisValue[VERTICAL_AXIS] = 0.0
            else:
                r_DZ = (r - DEAD_ZONE) / (1 - DEAD_ZONE)
                cos = vValue / r
                r_ = math.pow(r_DZ, (1 - jSet.SENSITIVITY) * 3.0 + 1.0)
                x = r_ * cos
                self.__axisValue[VERTICAL_AXIS] = clamp(-1.0, x, 1.0)
            self.__setCursorSpeed()
        elif event.axis == jSet.G_HORIZONTAL_AXIS and (event.deviceId == jSet.G_HORIZONTAL_DEVICE or 0 == jSet.G_HORIZONTAL_DEVICE):
            hValue = event.value
            self.__rAxisValue[HORIZONTAL_AXIS] = hValue
            r = min(math.hypot(self.__rAxisValue[VERTICAL_AXIS], hValue), 1)
            DEAD_ZONE = jSet.G_VERTICAL_DEAD_ZONE
            if r <= DEAD_ZONE:
                self.__axisValue[HORIZONTAL_AXIS] = 0.0
            else:
                r_DZ = (r - DEAD_ZONE) / (1 - DEAD_ZONE)
                sin = hValue / r
                r_ = math.pow(r_DZ, (1 - jSet.SENSITIVITY) * 3.0 + 1.0)
                y = r_ * sin
                cursorDirection = self.__cameraStrategy.cursorDirection
                cameraDirection = self.__cameraStrategy.cameraDirection
                angle = cursorDirection.angle(cameraDirection)
                if angle > 0.75 * math.pi:
                    y *= -1
                self.__axisValue[HORIZONTAL_AXIS] = clamp(-1.0, y, 1.0)
            self.__setCursorSpeed()
        elif event.axis == jSet.FORCE_AXIS and (event.deviceId == jSet.FORCE_DEVICE or 0 == jSet.FORCE_DEVICE):
            fValue = event.value
            if abs(fValue) < jSet.FORCE_DEAD_ZONE:
                fValue = 0.0
            else:
                fValue = -fValue if jSet.INVERT_FORCE else fValue
            self.__profile.sendPrimaryAxis(FORCE_AXIS, fValue)
        elif event.axis == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_AXIS and (event.deviceId == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEVICE or 0 == jSet.FREE_HORIZONTAL_CAM_GAMEPAD_DEVICE):
            hValue = event.value
            if abs(hValue) <= jSet.G_VERTICAL_DEAD_ZONE:
                self.__axisValue[FREE_HORIZONTAL_CAM] = 0.0
            else:
                hValue = math.copysign((abs(hValue) - jSet.G_VERTICAL_DEAD_ZONE) / (1 - jSet.G_VERTICAL_DEAD_ZONE), hValue)
                self.__axisValue[FREE_HORIZONTAL_CAM] = clamp(-1.0, hValue, 1.0)
        elif event.axis == jSet.FREE_VERTICAL_CAM_GAMEPAD_AXIS and (event.deviceId == jSet.FREE_VERTICAL_CAM_GAMEPAD_DEVICE or 0 == jSet.FREE_VERTICAL_CAM_GAMEPAD_DEVICE):
            vValue = event.value
            if abs(vValue) <= jSet.G_VERTICAL_DEAD_ZONE:
                self.__axisValue[FREE_VERTICAL_CAM] = 0.0
            else:
                vValue = math.copysign((abs(vValue) - jSet.G_VERTICAL_DEAD_ZONE) / (1 - jSet.G_VERTICAL_DEAD_ZONE), vValue)
                vValue = vValue if jSet.INVERT_G_VERTICAL else -vValue
                self.__axisValue[FREE_VERTICAL_CAM] = clamp(-1.0, vValue, 1.0)

    def __setCursorSpeed(self):
        xV = self.__axisValue[HORIZONTAL_AXIS]
        yV = self.__axisValue[VERTICAL_AXIS]
        if GameEnvironment.getCamera().getState() != CameraState.Target and self.__inGame:
            self.__cameraStrategy.rotateCursorSpeed(yV, xV)

    @property
    def _inCameraState(self):
        return GameEnvironment.getCamera().getState() == CameraState.GamepadCombat

    def __sendCursor(self):
        import BattleReplay
        if BattleReplay.isPlaying():
            return
        if EntityStates.inState(BigWorld.player(), EntityStates.GAME):
            self.__updateCurrentRadius()
            direction = self.__cameraStrategy.cursorDirection if not self.__isExtraMode else self.__lastDirection
            self.__profile.setCamDirection(direction)
            dataDir, up = self.__prepareMousePackage(direction)
            self.__lastDirection = direction
            if dataDir != self.__lastDataDir:
                self._lastDataDir = dataDir
                timeSend = GameEnvironment.getInput().inputAxis.serverTime
                BigWorld.player().cell.sendMouseDirData(timeSend, dataDir)
            if up != self.__lastUp:
                self.__lastUp = up
                BigWorld.player().cell.sendMouseUp(up)

    def __prepareMousePackage(self, direct):
        direction = Math.Vector3(direct)
        direction.normalise()
        planeDir = BigWorld.player().getRotation().rotateVec(Math.Vector3(0.0, 0.0, 1.0))
        planeDir.normalise()
        angle = math.acos(clamp(-1.0, direction.dot(planeDir), 1.0))
        direction *= self.__profile.getMouseIntensity(angle, self.__correctMaxAngle)
        tDir = FloatArrayToTupleOfCInt16(direction)
        up = self.__cameraStrategy.cursorUp if not self.__isExtraMode else Math.Vector3(0, 1, 0)
        up = FloatArrayToTupleOfCInt16(up)
        return (tDir, up)

    def __getLimitCoeff(self):
        angle = BigWorld.player().asymptoteVMaxPitch / BigWorld.player().maxPitchRotationSpeed
        return angle

    def __updateCurrentRadius(self):
        angle = 0.5 * BigWorld.projection().fov * (0.3 + 0.7 * InputMapping.g_instance.mouseSettings.RADIUS_OF_CONDUCTING)
        self.__correctMaxAngle = max(BigWorld.projection().fov * 0.5 * 0.3, self.__getLimitCoeff() * angle)
        if self.__correctMaxAngle != self.__lastCorrectMaxAngle:
            self.__lastCorrectMaxAngle = self.__correctMaxAngle

    def __renormalization(self, x):
        return x


class GamePadExpertInput(InputSubsystemBase):

    def __init__(self, profile):
        self.__profile = profile
        self.__isRawForceAxis = True
        self.__rAxisValue = {VERTICAL_AXIS: 0,
         HORIZONTAL_AXIS: 0}

    def setRawForceAxis(self, value):
        self.__isRawForceAxis = value

    def restart(self):
        pass

    def dispose(self):
        self.__profile = None
        return

    def processJoystickEvent(self, event):
        jSet = InputMapping.g_instance.joystickSettings
        if event.axis == jSet.ROLL_AXIS and (event.deviceId == jSet.ROLL_DEVICE or 0 == jSet.ROLL_DEVICE):
            rValue = -event.value if jSet.INVERT_ROLL else event.value
            rawValue = rValue
            if abs(rValue) <= jSet.ROLL_DEAD_ZONE:
                self.__profile.sendPrimaryAxis(ROLL_AXIS, 0.0, rawValue)
            else:
                rValue = math.copysign((abs(rValue) - jSet.ROLL_DEAD_ZONE) / (1.0 - jSet.ROLL_DEAD_ZONE), rValue)
                rValue = InputMapping.translateAxisValue(jSet.AXIS_X_CURVE, rValue)
                self.__profile.sendPrimaryAxis(ROLL_AXIS, clamp(-1.0, rValue, 1.0), rawValue)
        elif event.axis == jSet.G_VERTICAL_AXIS and (event.deviceId == jSet.G_VERTICAL_DEVICE or 0 == jSet.G_VERTICAL_DEVICE):
            vValue = event.value if jSet.INVERT_G_VERTICAL else -event.value
            rawValue = vValue
            self.__rAxisValue[VERTICAL_AXIS] = vValue
            r = min(math.hypot(vValue, self.__rAxisValue[HORIZONTAL_AXIS]), 1)
            DEAD_ZONE = jSet.G_VERTICAL_DEAD_ZONE
            if r <= DEAD_ZONE:
                self.__profile.sendPrimaryAxis(VERTICAL_AXIS, 0.0, rawValue)
            else:
                r_DZ = (r - DEAD_ZONE) / (1 - DEAD_ZONE)
                cos = vValue / r
                r_ = InputMapping.translateAxisValue(jSet.AXIS_Y_CURVE, r_DZ)
                x = r_ * cos
                self.__profile.sendPrimaryAxis(VERTICAL_AXIS, clamp(-1.0, x, 1.0), rawValue)
        elif event.axis == jSet.G_HORIZONTAL_AXIS and (event.deviceId == jSet.G_HORIZONTAL_DEVICE or 0 == jSet.G_HORIZONTAL_DEVICE):
            hValue = event.value if jSet.INVERT_HORIZONTAL else -event.value
            rawValue = hValue
            self.__rAxisValue[HORIZONTAL_AXIS] = hValue
            r = min(math.hypot(self.__rAxisValue[VERTICAL_AXIS], hValue), 1)
            DEAD_ZONE = jSet.G_VERTICAL_DEAD_ZONE
            if r <= DEAD_ZONE:
                self.__profile.sendPrimaryAxis(HORIZONTAL_AXIS, 0.0, rawValue)
            else:
                r_DZ = (r - DEAD_ZONE) / (1 - DEAD_ZONE)
                sin = hValue / r
                r_ = InputMapping.translateAxisValue(jSet.AXIS_Y_CURVE, r_DZ)
                y = r_ * sin
                self.__profile.sendPrimaryAxis(HORIZONTAL_AXIS, clamp(-1.0, y, 1.0), rawValue)
        elif event.axis == jSet.FORCE_AXIS and (event.deviceId == jSet.FORCE_DEVICE or 0 == jSet.FORCE_DEVICE):
            fValue = -event.value if jSet.INVERT_FORCE else event.value
            rawValue = fValue
            if self.__isRawForceAxis:
                fValue = self.__renormalization(fValue)
            self.__profile.sendPrimaryAxis(FORCE_AXIS, fValue, rawValue)

    def __renormalization(self, x):
        return x