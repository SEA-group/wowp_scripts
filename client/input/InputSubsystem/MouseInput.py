# Embedded file name: scripts/client/input/InputSubsystem/MouseInput.py
import EffectManager
import GlobalEvents
__author__ = 'm_kobets'
import BigWorld
from Camera import CameraState
from EntityHelpers import EntityStates, getReductionPointVector, isAvatar
from gui.HUDconsts import HUD_REDUCTION_POINT_SCALE
import GameEnvironment
from ICMultiUpdate import ICMultiUpdate
import InputMapping
import math
import Math
from MathExt import sign, clamp, FloatToCInt16, FloatArrayToTupleOfCInt16
from consts import BATTLE_MODE, WORLD_SCALING, PLANE_TYPE, FORCE_AXIS
from input.InputSubsystem.InputSubsystemBase import InputSubsystemBase
from clientConsts import NOT_CONTROLLED_MOD, SENSITIVITY_SNIPER_MODE_MULTIPLIER, SENSITIVITY_OVERVIEW_MODE_MULTIPLIER, FAKE_ROTATION_LOCKS
from CommonSettings import FORCE_RUDDER_BOMBER_SETTINGS
import Settings
from Event import Event, EventManager

class MouseInput(ICMultiUpdate, InputSubsystemBase):

    def __init__(self, profile):
        self._profile = profile
        self._holdDirection = None
        self._isExtraMode = False
        self._lastCorrectMaxAngle = 0.0
        self._additionalMouseSensitivity = 1.0
        self._sensitivityCfc = 0.1
        self._mousePosition = Math.Vector2(0.0, 0.0)
        self._Q = Math.Quaternion()
        self.__smoothStack = {'x': [0],
         'y': [0]}
        self.__lastMoved = False
        self.__isMoved = False
        self._notControlledByUser = self._profile._notControlledByUser
        self._lastUp = None
        self._lastExSpeed = None
        self._lastDataDir = None
        self.__window = 1
        self._backRevert = 1
        self._cameraStrategy = GameEnvironment.getCamera().getDefualtStrategies['CameraStrategyMouse']
        self._lockCursor = False
        self.__onSetFocus = Event()
        GlobalEvents.onSetFocus += self.__onSetFocus
        self.__mouseLock = None
        ICMultiUpdate.__init__(self, (0.01, self._update), (0.05, self._sendMouseData))
        return

    def dispose(self):
        ICMultiUpdate.dispose(self)
        if self._lockCursor:
            self._cameraStrategy.unlockCursor()
        self._profile = None
        self._cameraStrategy = None
        GameEnvironment.getCamera().leaveState(CameraState.Back)
        GlobalEvents.onSetFocus -= self.__onSetFocus
        return

    def restart(self):
        ICMultiUpdate.restart(self)
        self._isExtraMode = False
        self._lastUp = None
        self._lastExSpeed = None
        self._lastDataDir = None
        return

    def __onSetFocus(self, value):
        if self._cameraStrategy:
            self._cameraStrategy.rotateCursor(0, 0)

    def notControlledByUser(self, value):
        self._cameraStrategy.rotateCursor(0, 0)
        cValue = value & (NOT_CONTROLLED_MOD.AUTOPILOT | NOT_CONTROLLED_MOD.PLAYER_MENU | NOT_CONTROLLED_MOD.MOUSE_INPUT_BLOCKED | NOT_CONTROLLED_MOD.LOST_WINDOW_FOCUS)
        self._notControlledByUser = cValue
        if cValue and not self._lockCursor:
            self._cameraStrategy.lockCursor()
        if not cValue and self._lockCursor:
            self._cameraStrategy.unlockCursor()
        self._lockCursor = bool(cValue)

    def _backCamera(self, value):
        GameEnvironment.getCamera().turnOverLook(value)

    def addCommandListeners(self, processor):
        processor.addListeners(InputMapping.CMD_EXTRA_INPUT_MODE, None, None, self._setExtraMode)
        processor.addListeners(InputMapping.CMD_BACK_VIEW, None, None, self._backCamera)
        return

    def removeCommandListeners(self, processor):
        processor.removeListeners(InputMapping.CMD_EXTRA_INPUT_MODE, None, None, self._setExtraMode)
        processor.removeListeners(InputMapping.CMD_BACK_VIEW, None, None, self._backCamera)
        return

    @staticmethod
    def modYSensOnLowAlt(dy):
        from CommonSettings import SensitivityScale_PillowSettings as settings
        cfc = 1.0
        if dy < 0:
            h = BigWorld.player().getAltitudeAboveObstacle() * WORLD_SCALING
            cfc = clamp(settings.min_sens, (h - settings.h1) / (settings.h2 - settings.h1), 1)
        return dy * cfc

    def processMouseEvent(self, event):
        X = event.dx
        Y = event.dy
        if math.hypot(event.dx, event.dy):
            X = self.__signalSmoothing('x', event.dx)
            Y = self.__signalSmoothing('y', event.dy)
        else:
            self.__smoothStack = {'x': [0],
             'y': [0]}
        signY = 1.0 if self._profile.settings.MOUSE_INVERT_VERT else -1.0
        sensitivityX = (0.1 + 0.9 * self._profile.mouseSensitivity(event)) * self._sensitivityCfc * self._additionalMouseSensitivity
        sensitivityY = signY * sensitivityX
        BigWorld.setSpectatorMouseSensitivity(sensitivityX * SENSITIVITY_OVERVIEW_MODE_MULTIPLIER, sensitivityY * SENSITIVITY_OVERVIEW_MODE_MULTIPLIER)
        dx = self._backRevert * X * sensitivityX
        dy = self.modYSensOnLowAlt(Y * sensitivityY)
        if GameEnvironment.getCamera().isSniperMode:
            dx *= SENSITIVITY_SNIPER_MODE_MULTIPLIER
            dy *= SENSITIVITY_SNIPER_MODE_MULTIPLIER
        elif self._isExtraMode:
            dx *= SENSITIVITY_OVERVIEW_MODE_MULTIPLIER
            dy *= SENSITIVITY_OVERVIEW_MODE_MULTIPLIER
        if GameEnvironment.getCamera().getState() != CameraState.Target:
            self._cameraStrategy.rotateCursor(math.radians(dy), math.radians(dx))
            self.__isMoved = True
        else:
            self._cameraStrategy.rotateCursor(0, 0)

    @property
    def window(self):
        return self.__window

    @window.setter
    def window(self, value):
        self.__window = value

    def __signalSmoothing(self, axis, value):
        self.__smoothStack.setdefault(axis, []).append(value)
        if len(self.__smoothStack[axis]) > self.__window:
            self.__smoothStack[axis].pop(0)
        val = sum(self.__smoothStack[axis]) / len(self.__smoothStack[axis])
        return val

    def _setExtraMode(self, value):
        camera = GameEnvironment.getCamera()
        self._isExtraMode = value
        EffectManager.g_instance.onFreeCameraStateChange(value)
        if value:
            camera.resetToZoomMin()
            camera.getDefualtStrategies['CameraStrategyMouse'].overviewModeEnable()
            BigWorld.player().setLockCursorMtx(FAKE_ROTATION_LOCKS.FREE_CAMERA, True)
        else:
            camera.resetToBackZoom()
            camera.getDefualtStrategies['CameraStrategyMouse'].overviewModeDisable()
            BigWorld.player().setLockCursorMtx(FAKE_ROTATION_LOCKS.FREE_CAMERA, False)
            lastDataDir = self._lastDataDir if self._lastDataDir is not None else BigWorld.player().getRotation().getAxisZ()
            up = Math.Vector3(0, 1, 0)
            from MathExt import TupleOfCInt16ToFloatArray
            direction = TupleOfCInt16ToFloatArray(lastDataDir, Math.Vector3)
            angle = direction.angle(up)
            if 0 < angle < math.pi:
                q = Math.Quaternion()
                q.fromAngleAxis(0.5 * math.pi, direction.cross(up))
                currUp = q.rotateVec(direction)
                mtx = Math.Matrix()
                mtx.lookAt(Math.Vector3(0, 0, 0), direction, currUp)
                self._cameraStrategy.setCameraOrientation(mtx)
                mtx.invert()
                self._cameraStrategy.setCursorOrientation(mtx)
                BigWorld.player()._crossHairMatrix.reset()
        return

    @property
    def _inGame(self):
        return EntityStates.inState(BigWorld.player(), EntityStates.GAME)

    @property
    def _inCameraState(self):
        state = GameEnvironment.getCamera().getState()
        return state in (CameraState.MouseCombat,
         CameraState.MouseAssault,
         CameraState.Bomber,
         CameraState.Gunner,
         CameraState.Sniper)

    @property
    def _isRunning(self):
        return self._inGame and self._inCameraState and not self._notControlledByUser

    @property
    def _correctMaxAngle(self):
        angle = 0.5 * BigWorld.projection().fov * (0.3 + 0.7 * self._profile.radiusOfConducting)
        getLimitCfc = BigWorld.player().asymptoteVMaxPitch / BigWorld.player().maxPitchRotationSpeed
        return max(BigWorld.projection().fov * 0.5 * 0.3, getLimitCfc * angle)

    def _updateCurrentRadius(self):
        correctMaxAngle = self._correctMaxAngle
        if correctMaxAngle != self._lastCorrectMaxAngle:
            self._lastCorrectMaxAngle = correctMaxAngle

    def _prepareMousePackage(self, direct):
        direction = Math.Vector3(direct)
        direction.normalise()
        planeDir = BigWorld.player().getRotation().getAxisZ()
        angle = math.acos(clamp(-1.0, direction.dot(planeDir), 1.0))
        correctMaxAngle = self._correctMaxAngle
        cfc = self._profile.getMouseIntensity(angle, correctMaxAngle)
        direction *= cfc
        exAxis = planeDir.cross(direct)
        exAxis.normalise()
        maxAngle = self._lastCorrectMaxAngle if self._lastCorrectMaxAngle else self._correctMaxAngle
        angle = planeDir.angle(direct)
        n = clamp(0, angle / maxAngle, 1) * BigWorld.player().maxPitchRotationSpeed * (1.0 - cfc)
        exAxis *= n
        try:
            return (FloatArrayToTupleOfCInt16(direction), FloatArrayToTupleOfCInt16(exAxis))
        except:
            print 'trap', direction, exAxis, cfc, angle, correctMaxAngle, n
            raise

    def mousePosition(self):
        player = BigWorld.player()
        fmRotation = player.getRotation()
        rotation = Math.Quaternion(fmRotation)
        rotation.invert()
        direction = self._cameraStrategy.cursorDirection
        planeDir = BigWorld.player().getRotation().getAxisZ()
        angle = self._lastCorrectMaxAngle if self._lastCorrectMaxAngle else self._correctMaxAngle
        self._Q.fromAngleAxis(angle, BigWorld.player().getRotation().getAxisX())
        limitDir = self._Q.rotateVec(planeDir)
        limitDir = rotation.rotateVec(limitDir)
        limitDir.z = 0.0
        limitDir = limitDir.length
        cursorDir = rotation.rotateVec(direction)
        cursorDir.z = 0.0
        self._mousePosition.x = cursorDir.x / limitDir
        self._mousePosition.y = cursorDir.y / limitDir

    def __updateCursorAxis(self):
        if BigWorld.player().planeType == PLANE_TYPE.BOMBER and self._isRunning:
            if self._profile.battleMode == BATTLE_MODE.ASSAULT_MODE:
                cursor = self._cameraStrategy.cursorDirection
                hCursor = Math.Vector3(cursor)
                hCursor.y = 0
                pitch = cursor.angle(hCursor)
                if pitch > FORCE_RUDDER_BOMBER_SETTINGS.get(sign(cursor.y), 100000):
                    self._profile.sendExtraAxis(FORCE_AXIS, sign(cursor.y))
                else:
                    self._profile.sendExtraAxis(FORCE_AXIS, 0)
            else:
                self._profile.sendExtraAxis(FORCE_AXIS, 0)

    def _update(self):
        """ Main update for specific methods, like update HUD. Has update every 0.01 sec. """
        self.__updateCursorAxis()

    def _sendMouseData(self):
        """ Update which send data mouse to cell. Has two update on one server tick. """
        import BattleReplay
        if BattleReplay.isPlaying():
            return
        lastValue = not self._inCameraState
        if self.__mouseLock != lastValue:
            self.__mouseLock = lastValue
            BigWorld.player().cell.sendMouseLock(lastValue)
            if not lastValue and self.__class__.__name__ == 'MouseCursorDirection':
                self._cameraStrategy.reset()
        if self.__lastMoved != self.__isMoved:
            BigWorld.player().cell.sendMouseMoved(self.__isMoved)
            self.__lastMoved = self.__isMoved
        self.__isMoved = False


class MousePlaneDirection(MouseInput):
    __name__ = 'MousePlaneDirection'

    def __init__(self, profile):
        self.__laseCameraState = None
        self.__lastDirection = Math.Vector3()
        MouseInput.__init__(self, profile)
        self._sensitivityCfc = 0.05
        return

    def notControlledByUser(self, value):
        self._cameraStrategy.rotateCursor(0, 0)
        self._notControlledByUser = value
        if value and not self._lockCursor:
            self._cameraStrategy.lockCursor()
        if not value and self._lockCursor:
            self._cameraStrategy.unlockCursor()
        self._lockCursor = bool(value)
        if value & NOT_CONTROLLED_MOD.AUTOPILOT:
            GameEnvironment.getCamera().getDefualtStrategies['CameraStrategyMouse'].autopilot = True
        if value & NOT_CONTROLLED_MOD.PLANE_ALIGN:
            self._mousePosition.x = 0
            self._mousePosition.y = 0

    @property
    def currentRadius(self):
        player = BigWorld.player()
        planeDir = BigWorld.player().getRotation().getAxisZ()
        self._Q.fromAngleAxis(self._lastCorrectMaxAngle, BigWorld.player().getRotation().getAxisX())
        Dir = self._Q.rotateVec(planeDir)
        reductionPointVector = getReductionPointVector(player.weaponsSettings)
        worldPos = Dir * reductionPointVector.length * HUD_REDUCTION_POINT_SCALE + player.position
        screenPoint = BigWorld.worldToScreen(worldPos)
        screenPoint = Math.Vector3(clamp(0.0, screenPoint.x, BigWorld.screenWidth()), clamp(0.0, screenPoint.y, BigWorld.screenHeight()), 1.0)
        x = screenPoint.x - 0.5 * BigWorld.screenWidth()
        y = -screenPoint.y + 0.5 * BigWorld.screenHeight()
        return math.hypot(x, y)

    def __updateAdditionalMouseSensitivity(self):
        radiusSensitivity = 0.3 + 0.7 * self._profile.radiusOfConducting
        if self._profile.battleMode in (BATTLE_MODE.COMBAT_MODE, BATTLE_MODE.ASSAULT_MODE):
            self._additionalMouseSensitivity = radiusSensitivity * BigWorld.projection().fov / math.radians(Settings.g_instance.maxMouseCombatFov)
        else:
            self._additionalMouseSensitivity = 1.0

    def __updateCursorPosition(self):
        player = BigWorld.player()
        reductionPointVector = getReductionPointVector(player.weaponsSettings)
        direction = self._cameraStrategy.cursorDirection
        if self._backRevert < 0:
            p = player.getRotation().getAxisZ()
            angle = p.angle(direction)
            p *= -1
            axis = p.cross(direction)
            self._Q.fromAngleAxis(angle, axis)
            direction = self._Q.rotateVec(p)
        worldPos = direction * reductionPointVector.length * HUD_REDUCTION_POINT_SCALE + player.position
        screenPoint = BigWorld.worldToScreen(worldPos)
        screenPoint = Math.Vector3(clamp(0.0, screenPoint.x, BigWorld.screenWidth()), clamp(0.0, screenPoint.y, BigWorld.screenHeight()), 1.0)
        self.mousePosition()

    def __checkCameraState(self):
        currentCameraState = GameEnvironment.getCamera().getState()
        if self.__laseCameraState != currentCameraState:
            self.__laseCameraState = currentCameraState

    def _setExtraMode(self, value):
        MouseInput._setExtraMode(self, value)
        self._cameraStrategy.behaviorHorizon = value
        if value:
            self._cameraStrategy.reset()
            self._sensitivityCfc = 0.1
        else:
            self._sensitivityCfc = 0.05

    def _backCamera(self, value):
        self._backRevert = -1 if value else 1
        MouseInput._backCamera(self, value)

    def _update(self):
        if not BigWorld.player().isFlyMouseInputAllowed:
            self._cameraStrategy.rotateCursor(0, 0)
        self.__checkCameraState()
        if not self._inGame:
            return
        self.__updateAdditionalMouseSensitivity()
        self.__updateCursorPosition()
        MouseInput._update(self)

    def _sendMouseData(self):
        import BattleReplay
        if BattleReplay.isPlaying():
            if self._inGame and not self._isExtraMode:
                self._updateCurrentRadius()
            return
        MouseInput._sendMouseData(self)
        if self._inGame and not self._isExtraMode:
            self._updateCurrentRadius()
            direction = self._cameraStrategy.cursorDirection
            dataDir, exAxis = self._prepareMousePackage(direction)
            self._profile.setCamDirection(direction)
            if dataDir != self._lastDataDir:
                self._lastDataDir = dataDir
                timeSend = GameEnvironment.getInput().inputAxis.serverTime
                BigWorld.player().cell.sendMouseDirData(timeSend, dataDir)
            if exAxis != self._lastExSpeed:
                self._lastExSpeed = exAxis
                BigWorld.player().cell.sendMouseExtRSpeed(exAxis)


def isValid(vector):
    if vector.length == 0 or math.isnan(vector.length):
        return False
    else:
        return True


class MouseCursorDirection(MouseInput):
    __name__ = 'MouseCursorDirection'

    def __init__(self, profile):
        self.__automaticFlaps = None
        self.__lastDirection = Math.Vector3()
        MouseInput.__init__(self, profile)
        return

    def _sendMouseData(self):
        import BattleReplay
        if BattleReplay.isPlaying():
            if self._inGame and not self._isExtraMode:
                self._updateCurrentRadius()
            return
        MouseInput._sendMouseData(self)
        if self._inGame and not self._isExtraMode:
            self._updateCurrentRadius()
            direction = self._cameraStrategy.cursorDirection
            direction = direction if not self._isExtraMode else self.__lastDirection
            self._profile.setCamDirection(direction)
            if not isValid(direction):
                print 'trap', direction, BigWorld.player().getRotation().getAxisZ()
                return
            dataDir, exAxis = self._prepareMousePackage(direction)
            up = self._cameraStrategy.cursorUp if not self._isExtraMode else Math.Vector3(0, 1, 0)
            up = FloatArrayToTupleOfCInt16(up)
            self.__lastDirection = direction
            if dataDir != self._lastDataDir:
                self._profile.setBattleDirection(Math.Vector3(direction))
                self._lastDataDir = dataDir
                timeSend = GameEnvironment.getInput().inputAxis.serverTime
                BigWorld.player().cell.sendMouseDirData(timeSend, dataDir)
            if up != self._lastUp:
                self._lastUp = up
                BigWorld.player().cell.sendMouseUp(up)
            if exAxis != self._lastExSpeed:
                self._lastExSpeed = exAxis
                BigWorld.player().cell.sendMouseExtRSpeed(exAxis)

    def _update(self):
        if not BigWorld.player().isFlyMouseInputAllowed() or not self._inCameraState:
            self._cameraStrategy.rotateCursor(0, 0)
        self.mousePosition()
        MouseInput._update(self)