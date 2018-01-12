# Embedded file name: scripts/client/CameraStates.py
import GameEnvironment
from MathExt import *
from consts import *
from StateMachine import *
import Settings
import collections
from debug_utils import *
from gui.HUDconsts import HUD_REDUCTION_POINT_SCALE
from clientConsts import CAMERA_ALT_MODE_SHIFT_VECTOR, CAMERA_ZOOM_PRESET, SPECTATOR_TYPE
from random import randint, uniform
from CommonSettings import BOMBER_CAM_LIMITED_ANGLES, GUNNER_CAM_LIMITED_ANGLES
from EntityHelpers import *
import EffectManager
import BigWorld
import Math
import math
g_useLowAltitudeCorrection = True

class ZSCameraData:

    def __init__(self, cameraToCursor, maxCursorSpeed, minCursorSpeed, cursorMaxSpeedAngle, cursorMinSpeedAngle, cursorUpToAircraft, cursorMaxRollSpeed, cursorMaxRollAcceleration, cursorBackSpeed):
        self.maxCursorSpeed = maxCursorSpeed
        self.minCursorSpeed = minCursorSpeed
        self.__cursorMinSpeedAngle = math.radians(cursorMinSpeedAngle)
        self.__cursorMaxSpeedAngle = math.radians(cursorMaxSpeedAngle)
        self.__cursorBackSpeed = math.radians(cursorBackSpeed)

    @property
    def cursorMinSpeedAngle(self):
        if self.__cursorMinSpeedAngle == 180.0:
            a = 1.0
        else:
            a = max(0.01, BigWorld.player().asymptoteVMaxPitch)
        return self.__cursorMinSpeedAngle * a

    @property
    def cursorMaxSpeedAngle(self):
        if self.__cursorMinSpeedAngle == 180.0:
            a = 1.0
        else:
            a = max(0.01, BigWorld.player().asymptoteVMaxPitch)
        return self.__cursorMaxSpeedAngle * a

    def setToStrategy(self, strategy):
        strategy.maxCursorSpeed = self.maxCursorSpeed
        strategy.minCursorSpeed = self.minCursorSpeed
        strategy.cursorMinSpeedAngle = self.cursorMinSpeedAngle
        strategy.cursorMaxSpeedAngle = self.cursorMaxSpeedAngle
        strategy.cursorBackSpeed = self.__cursorBackSpeed


class CameraState(object):
    NormalCombat = 0
    Free = 1
    Back = 2
    Left = 3
    Right = 4
    Top = 5
    Bottom = 6
    DestroyedFall = 7
    Spectator = 9
    DynamicSpectator = 10
    BottomLeft = 11
    BottomRight = 12
    TopLeft = 13
    TopRight = 14
    Bomb = 15
    Target = 16
    SuperFree = 17
    FreeFixable = 18
    TargetMe = 19
    NormalAssault = 20
    JoystickCombat = 21
    JoystickAssault = 22
    MouseCombat = 23
    GamepadCombat = 24
    MouseAssault = 25
    Empty = 26
    ReplayFree = 27
    SpectatorSide = 28
    DebugCamera = 29
    Bomber = 30
    Gunner = 31
    Sniper = 32
    JoystickSniper = 33
    SniperStates = [Sniper, JoystickSniper]
    StatesWithoutExtraMode = [Bomber,
     Gunner,
     Sniper,
     JoystickSniper]
    _context = None
    _particleEffects = []

    def __init__(self):
        self.returnToNormalTime = -1
        self.strategy = None
        self.crossHairVisible = False
        self.isTargetCameraEnabled = True
        self._particleEffectEnabled = False
        return

    def enter(self, params = None):
        self._triggerEffects(True)

    def exit(self):
        self.strategy = None
        self._triggerEffects(False)
        return

    def _triggerEffects(self, enable):
        if EffectManager.g_instance:
            if self._particleEffectEnabled != enable:
                for effectId in self._particleEffects:
                    if enable:
                        EffectManager.g_instance.showScreenParticle(effectId)
                    else:
                        EffectManager.g_instance.hideScreenParticle(effectId, clearPixie=True)

                self._particleEffectEnabled = enable

    def reEnter(self, params = None):
        pass

    def updateParams(self, params = None):
        pass

    def getReturnToNormalTime(self):
        return -1.0

    def refreshState(self):
        pass

    def trySetCenterHudMatrix(self):
        pass

    @staticmethod
    def setInitParams(stateInitParams):
        CameraState._context = stateInitParams

    def zoomPresent(self):
        return False

    def onZoomIndexChanged(self, zoomIndex, zoomData):
        pass

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def applyInputAxis(self, axis, value):
        pass


class CameraStateMachine(StateMachine):

    def __init__(self):
        StateMachine.__init__(self)
        self.__stateStack = collections.deque()
        self.__cachedStateParams = {}
        self.__modalStates = set([CameraState.SpectatorSide])

    COMPOSITE_STATES = {(CameraState.Top, CameraState.Right): CameraState.TopRight,
     (CameraState.Top, CameraState.Left): CameraState.TopLeft,
     (CameraState.Bottom, CameraState.Right): CameraState.BottomRight,
     (CameraState.Bottom, CameraState.Left): CameraState.BottomLeft}

    def __compositeLastStates(self):
        stackSize = len(self.__stateStack)
        if stackSize > 1:
            if (self.__stateStack[-1], self.__stateStack[-2]) in CameraStateMachine.COMPOSITE_STATES:
                return CameraStateMachine.COMPOSITE_STATES[self.__stateStack[-1], self.__stateStack[-2]]
            if (self.__stateStack[-2], self.__stateStack[-1]) in CameraStateMachine.COMPOSITE_STATES:
                return CameraStateMachine.COMPOSITE_STATES[self.__stateStack[-2], self.__stateStack[-1]]
        if stackSize == 0:
            LOG_WARNING('CameraStateMachine: state stack is empty!')
            return CameraState.NormalCombat
        else:
            return self.__stateStack[-1]

    def setState(self, name, params = None, addToStack = True):
        curState = self.getState()
        if name != curState:
            if addToStack and name not in self.__stateStack:
                self.__stateStack.append(name)
                if params:
                    self.__cachedStateParams[name] = params
            if curState in self.__modalStates and curState in self.__stateStack:
                self.setPrevState(name)
            else:
                newState = self.__compositeLastStates()
                returnToNormalTime = -1
                if self.currentState:
                    returnToNormalTime = self.currentState.getReturnToNormalTime()
                self.getStateObject(newState).returnToNormalTime = returnToNormalTime
                StateMachine.setState(self, newState, params)
        elif curState not in self.__modalStates:
            self.reEnterState(params)

    def setPrevState(self, newState):
        temp = self.__stateStack.pop()
        if temp != newState:
            self.__stateStack.append(newState)
        self.__stateStack.append(temp)

    def leaveState(self, name = None):
        if len(self.__stateStack) > 1:
            newState = None
            if name is None:
                self.__stateStack.pop()
                newState = self.__stateStack[-1]
            elif name in self.__stateStack:
                self.__stateStack.remove(name)
                newState = self.__stateStack[-1]
            if newState is not None:
                params = self.__cachedStateParams[newState] if newState in self.__cachedStateParams else None
                self.setState(newState, params, False)
        return

    def destroy(self):
        self.getCurStateObject().exit()

    def reset(self):
        StateMachine.reset(self)
        self.__stateStack.clear()
        self.__cachedStateParams.clear()

    def getPrevState(self):
        if len(self.__stateStack) >= 2:
            return self.__stateStack[-2]
        else:
            return None
            return None


class BattleCameraStateMachine(CameraStateMachine):

    def __init__(self):
        CameraStateMachine.__init__(self)
        self.addState(CameraState.Empty, CameraStateEmpty())
        self.addState(CameraState.NormalCombat, CameraStateNormalCombat())
        self.addState(CameraState.NormalAssault, CameraStateNormalAssault())
        self.addState(CameraState.MouseCombat, CameraStateMouseCombat())
        self.addState(CameraState.GamepadCombat, CameraStateGamepadCombat())
        self.addState(CameraState.MouseAssault, CameraStateMouseAssault())
        self.addState(CameraState.JoystickCombat, CameraStateJoystickCombat())
        self.addState(CameraState.JoystickAssault, CameraStateJoystickAssault())
        self.addState(CameraState.Bomber, CameraBomberState())
        self.addState(CameraState.Gunner, CameraGunnerState())
        self.addState(CameraState.Sniper, CameraStateSniper())
        self.addState(CameraState.JoystickSniper, CameraStateJoystickSniper())
        self.addState(CameraState.Free, CameraStateFree())
        self.addState(CameraState.Back, CameraStateBack())
        self.addState(CameraState.Left, CameraStateSideLeft())
        self.addState(CameraState.Right, CameraStateSideRight())
        self.addState(CameraState.Top, CameraStateSideTop())
        self.addState(CameraState.Bottom, CameraStateSideBottom())
        self.addState(CameraState.Spectator, CameraStateSpectator())
        self.addState(CameraState.DynamicSpectator, CameraStateDynamicSpectator())
        self.addState(CameraState.BottomLeft, CameraStateSideBottomLeft())
        self.addState(CameraState.BottomRight, CameraStateSideBottomRight())
        self.addState(CameraState.TopLeft, CameraStateSideTopLeft())
        self.addState(CameraState.TopRight, CameraStateSideTopRight())
        self.addState(CameraState.Target, CameraStateTarget())
        self.addState(CameraState.SuperFree, CameraStateSuperFree())
        self.addState(CameraState.FreeFixable, CameraStateFreeFixable())
        self.addState(CameraState.DestroyedFall, CameraStateDestroyedFall())
        self.addState(CameraState.TargetMe, CameraStateTargetOnMe())
        self.addState(CameraState.ReplayFree, CameraStateFree())
        self.addState(CameraState.SpectatorSide, CameraStateSpectatorSide())
        self.addState(CameraState.DebugCamera, CameraStateDebugCamera())
        self.setState(CameraState.Empty)

    def reset(self):
        CameraStateMachine.reset(self)
        self.setState(CameraState.Empty)


def _dCursorToTarget(targetVec3):
    direction = BigWorld.camera().position - targetVec3
    BigWorld.dcursor().pitch = -direction.pitch
    BigWorld.dcursor().yaw = direction.yaw
    BigWorld.dcursor().roll = 0.0


class CameraStateEmpty(CameraState):
    pass


class CameraStateWithZoom(CameraState):

    def __init__(self):
        CameraState.__init__(self)
        self.__timerIn = 0.0
        self.__timerOut = 0.0
        self.__height = 1.0
        self.__centralHudToCam = False
        self.strategy = None
        return

    def _createStrategy(self):
        pass

    def _applyStrategySettings(self):
        pass

    def _setFovSettings(self):
        self.strategy.defaultFov = self._context.normalFov
        preset = self._context.cameraSettings.zoomPresets[self.zoomPreset()]
        self.strategy.setZoomStateInitialData(maxFovMultiplier=preset.sniper.fovPercent, minFovMultiplier=preset.normal.fovPercent, duration=self._context.cameraSettings.sniperStateInterpolationTime)

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DEFAULT

    def zoomPresent(self):
        return True

    def enter(self, params = None):
        CameraState.enter(self, params)
        if self.strategy is None:
            self._createStrategy()
        self._applyStrategySettings()
        self._setFovSettings()
        self._context.setZoom(zoomPreset=self.zoomPreset())
        self._context.cameraInstance.setStrategy(self.strategy, self._getInterpolationTime())
        self._checkCenterHudMatrix()
        self._trySetCrossHeirMatrix()
        import CameraEffect
        if CameraEffect.g_instance:
            CameraEffect.g_instance.startAccelerationEffect()
        return

    def reEnter(self, params = None):
        CameraState.reEnter(self, params)
        self.enter(params)
        self.strategy.reset()

    def onZoomIndexChanged(self, zoomIndex, zoomData):
        self._checkCenterHudMatrix()

    def _checkCenterHudMatrix(self):
        self.__setCenterHudMatrix(True)

    def _getCenterHudMatrix(self):
        return None

    def __setCenterHudMatrix(self, active):
        if active != self.__centralHudToCam:
            self.__centralHudToCam = active
            if active:
                centerHudMatrix = self._getCenterHudMatrix()
                if centerHudMatrix is not None:
                    GameEnvironment.getCamera().leSetCenterPointMatrix(centerHudMatrix)
        return

    def _trySetCrossHeirMatrix(self):
        BigWorld.player().trySetCursorMtx(None)
        return

    def exit(self):
        self.__setCenterHudMatrix(False)
        self._triggerEffects(False)

    def _getInterpolationTime(self):
        interpolationTime = self._context.cameraSettings.normalCamInterpolationTime
        if self.returnToNormalTime != -1:
            interpolationTime = self.returnToNormalTime
        return interpolationTime

    def applyInputAxis(self, axis, value):
        self.strategy.handleAxisInput(axis, value)


class CameraStateNormalBase(CameraStateWithZoom):

    def __init__(self):
        CameraStateWithZoom.__init__(self)
        self.crossHairVisible = True

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyNormal']
        self.strategy.reset()

    def enter(self, params = None):
        CameraStateWithZoom.enter(self, params)
        self._context.cameraManager.eSetCameraRingVisible(False)

    def _getCenterHudMatrix(self):
        return self._context.entity.realMatrix

    def refreshState(self):
        self._context.cameraInstance.setStrategy(self.strategy, 0.0)


class CameraStateDebugCamera(CameraStateNormalBase):

    def __init__(self):
        CameraStateNormalBase.__init__(self)
        self.crossHairVisible = True

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyDebug']

    def enter(self, params = None):
        CameraStateNormalBase.enter(self, params)

    def reEnter(self, params = None):
        self.strategy.reset()

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def _setFovSettings(self):
        pass


class CameraStateNormalCombat(CameraStateNormalBase):

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def enter(self, params = None):
        CameraStateNormalBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime(), True)


class CameraStateNormalAssault(CameraStateNormalBase):

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def enter(self, params = None):
        CameraStateNormalBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime())


class CameraStateJoystickCombat(CameraStateNormalBase):

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def enter(self, params = None):
        CameraStateNormalBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime(), True)
        self.strategy.Activate()

    def exit(self):
        CameraStateNormalBase.exit(self)
        self.strategy.Deactivate()


class CameraStateJoystickAssault(CameraStateNormalBase):

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def enter(self, params = None):
        CameraStateNormalBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime())


class CameraStateMouseBase(CameraStateWithZoom):

    def __init__(self):
        CameraStateWithZoom.__init__(self)
        self.onZoomTableChanged(1.0)
        self.__hudMatrix = None
        self.crossHairVisible = True
        return

    def _applyStrategySettings(self):
        self.strategy.bottomPitchBound = math.radians(0.0)
        self.strategy.topPitchBound = math.radians(10.0)
        self.strategy.isPitchLimited = False

    def enter(self, params = None):
        CameraStateWithZoom.enter(self, params)
        self._context.cameraManager.eSetCameraRingVisible(True)
        self.onZoomIndexChanged(self._context.getDestZoomDataIdx(), None)
        return

    def exit(self):
        CameraStateWithZoom.exit(self)

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyMouse']
        self.strategy.reset()

    def _getCenterHudMatrix(self):
        if self.__hudMatrix is None:
            self.__hudMatrix = self.strategy.cursorMatrixProvider
        return self.__hudMatrix

    def onZoomIndexChanged(self, zoomIndex, zoomData):
        CameraStateWithZoom.onZoomIndexChanged(self, zoomIndex, zoomData)
        self.__zSCameraTable[zoomIndex].setToStrategy(self.strategy)

    def onZoomTableChanged(self, cameraToCursor):
        self.__zSCameraTable = [ZSCameraData(cameraToCursor, 180.0, 180.0, 180.0, 181.0, 0.1, 120.0, 30.0, 0.0),
         ZSCameraData(cameraToCursor, 90.0, 90.0, 180.0, 181.0, 0.15, 120.0, 30.0, 0.0),
         ZSCameraData(cameraToCursor, 70.0, 30.0, 90.0, 180.0, 0.2, 120.0, 30.0, 0.0),
         ZSCameraData(cameraToCursor, 50.0, 5.0, 0.0, 60.0, 0.25, 120.0, 30.0, 100),
         ZSCameraData(cameraToCursor, 25.0, 5.0, 0.0, 30.0, 0.3, 120.0, 30.0, 50)]


class CameraStateMouseCombat(CameraStateMouseBase):

    def enter(self, params = None):
        CameraStateMouseBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime(), True)
        self.strategy.enableCourseComponents()
        self.strategy.Activate()

    @property
    def isInOverview(self):
        return self.strategy.isInOverview

    def onOverlookScroll(self, dz):
        if dz and self.strategy:
            self.strategy.applyOverviewDistance(dz)

    def _trySetCrossHeirMatrix(self):
        BigWorld.player().trySetCursorMtx(self.strategy.cursorMatrixProvider)
        wData = getAirplaneWeaponSettings(BigWorld.player().settings.airplane)
        self.strategy.cursorFlexibilityAngle = wData.gunRotationAngleMax

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def exit(self):
        CameraStateMouseBase.exit(self)
        self.strategy.Deactivate()


class CameraStateGamepadCombat(CameraStateMouseBase):

    def enter(self, params = None):
        CameraStateMouseBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime(), True)
        self.strategy.Activate()

    def _trySetCrossHeirMatrix(self):
        BigWorld.player().trySetCursorMtx(self.strategy.cursorMatrixProvider)
        wData = getAirplaneWeaponSettings(BigWorld.player().settings.airplane)
        self.strategy.cursorFlexibilityAngle = wData.gunRotationAngleMax

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def getZoomDataPosition(self, zoomData):
        return zoomData.position

    def exit(self):
        CameraStateMouseBase.exit(self)
        self.strategy.Deactivate()

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyGamepad']
        self.strategy.reset()


class CameraStateMouseAssault(CameraStateMouseBase):

    def enter(self, params = None):
        CameraStateMouseBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime())

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT


class CameraStateJoystickSniper(CameraStateJoystickCombat):
    _particleEffects = ['aim_sniper']

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_SNIPER

    def enter(self, params = None):
        CameraStateJoystickCombat.enter(self, params)
        if EffectManager.g_instance:
            EffectManager.g_instance.setSniperMode(True)

    def exit(self):
        CameraStateJoystickCombat.exit(self)
        if EffectManager.g_instance:
            EffectManager.g_instance.setSniperMode(False)


class CameraStateSniper(CameraStateMouseCombat):
    _particleEffects = ['aim_sniper']

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_SNIPER

    def onOverlookScroll(self, dz):
        pass

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyMouse']

    def enter(self, params = None):
        CameraStateMouseCombat.enter(self, params)
        if EffectManager.g_instance:
            EffectManager.g_instance.setSniperMode(True)

    def exit(self):
        CameraStateMouseCombat.exit(self)
        if EffectManager.g_instance:
            EffectManager.g_instance.setSniperMode(False)


class CameraBomberState(CameraStateMouseBase):
    _particleEffects = ['aim_bomber']

    def __init__(self):
        CameraStateMouseBase.__init__(self)
        self._pitchAngle = radians(80)
        self._flexibility = 0.5
        self._crossMtx = None
        self.isTargetCameraEnabled = False
        return

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_ASSAULT

    def _swapFlexibility(self):
        flexibility = self.strategy.flexibility
        self.strategy.flexibility = self._flexibility
        self._flexibility = flexibility

    def _applyStrategySettings(self):
        self._swapFlexibility()
        self.strategy.bottomPitchBound = BOMBER_CAM_LIMITED_ANGLES.bottomPitchBound
        self.strategy.topPitchBound = BOMBER_CAM_LIMITED_ANGLES.topPitchBound
        self.strategy.isPitchLimited = True
        self.strategy.yawLimit = BOMBER_CAM_LIMITED_ANGLES.yawBound
        self.strategy.isYawLimited = True
        self.strategy.Activate()
        self.strategy.reset()
        self.strategy.disableCourseComponents()

    def onZoomIndexChanged(self, zoomIndex, zoomData):
        self._pitchAngle = radians(getattr(zoomData, 'angle', self._pitchAngle))
        super(CameraStateMouseBase, self).onZoomIndexChanged(zoomIndex, zoomData)

    def _getCenterHudMatrix(self):
        if self._crossMtx is None:
            offset = Math.Matrix()
            offset.setRotateYPR((0, self._pitchAngle, 0))
            mtx = Math.MatrixProduct()
            mtx.a = offset
            mtx.b = self.strategy.cursorMatrixProvider
            self._crossMtx = mtx
        return self._crossMtx

    def enter(self, params = None):
        CameraStateMouseBase.enter(self, params)
        mtx = Math.Matrix()
        direction = BigWorld.player().getRotation().getAxisZ()
        direction.y = 0
        if direction.length <= 0:
            direction = Math.Vector3(1, 0, 0)
        direction.normalise()
        mtx.lookAt(Math.Vector3(), direction, Math.Vector3(0, 1, 0))
        self.strategy.setCameraOrientation(mtx)
        mtx.invert()
        self.strategy.setCursorOrientation(mtx)
        self.strategy.resetComponents()
        self._context.applyZoomStateFov(self._getInterpolationTime())
        self._context.entity.setModelVisible(False)

    def exit(self):
        self._swapFlexibility()
        self.strategy.isPitchLimited = False
        self.strategy.isYawLimited = False
        self.strategy.Deactivate()
        self.strategy.reset()
        if not EntityStates.inState(self._context.entity, EntityStates.DESTROYED):
            self._context.entity.setModelVisible(True)
        CameraStateMouseBase.exit(self)


class CameraGunnerState(CameraStateMouseBase):
    _particleEffects = ['aim_reargunner']

    def __init__(self):
        CameraStateMouseBase.__init__(self)
        self._flexibility = 0.05
        self.isTargetCameraEnabled = False

    def zoomPreset(self):
        return CAMERA_ZOOM_PRESET.DIRECT_GUNNER

    def _createStrategy(self):
        self.strategy = self._context.defaultStrategies['CameraStrategyGunner']

    @property
    def _altStrategy(self):
        return self._context.defaultStrategies['CameraStrategyMouse']

    def _setGunnerCursorMtx(self):
        gunner = BigWorld.player().controlledGunner
        if gunner is not None:
            gunner.setControlMtx(self.strategy.cursorMatrixProvider)
        return

    def _swapFlexibility(self):
        flexibility = self.strategy.flexibility
        self.strategy.flexibility = self._flexibility
        self._flexibility = flexibility

    def enter(self, params = None):
        CameraStateMouseBase.enter(self, params)
        self._context.applyZoomStateFov(self._getInterpolationTime())
        self.strategy.Activate()
        self.strategy.isPitchLimited = True
        self.strategy.bottomPitchBound = GUNNER_CAM_LIMITED_ANGLES.bottomPitchBound
        self.strategy.topPitchBound = GUNNER_CAM_LIMITED_ANGLES.topPitchBound
        self._altStrategy.yawLimit = GUNNER_CAM_LIMITED_ANGLES.yawBound
        self._altStrategy.isYawLimited = True
        self._swapFlexibility()
        self._setGunnerCursorMtx()
        gunnerSettings = self._context.cameraSettings.gunnerStateSettings
        if gunnerSettings is not None:
            self.strategy.setSectorDistSettings(duration=gunnerSettings.duration, minPosition=gunnerSettings.minDeltaPosition, maxPosition=gunnerSettings.maxDeltaPosition, distanceCurvePoints=gunnerSettings.distanceCurvePoints, heightCurvePoints=gunnerSettings.heightCurvePoints, minHeight=gunnerSettings.minHeight, maxHeight=gunnerSettings.maxHeight)
        GameEnvironment.getHUD().offsetMtx.isEnabled = False
        return

    def exit(self):
        self._swapFlexibility()
        self._altStrategy.isYawLimited = False
        self.strategy.isPitchLimited = False
        self.strategy.Deactivate()
        self.strategy.reset()
        GameEnvironment.getHUD().offsetMtx.isEnabled = True
        CameraStateMouseBase.exit(self)


class CameraStateFree(CameraState):

    def __init__(self):
        CameraState.__init__(self)
        self.__invertVertical = False
        self._pivotDist = None
        return

    def _initPivotDist(self):
        self._pivotDist = (self._context.cameraSettings.pivotDistMin, self._context.cameraSettings.pivotDistMax)

    def onMouseScroll(self, dz):
        if dz and self.strategy:
            newDist = self.strategy.distance - dz * self._context.cameraSettings.freeCamZoomFactor
            self.strategy.distance = newDist
            self.setFovByDistance(newDist, self._context.cameraSettings.freeCamFovInterpolationTime)
            return newDist

    def setFovByDistance(self, distance, rampTime):
        distMin = self._pivotDist[0]
        distMax = self._pivotDist[1]
        distance = clamp(distMin, distance, distMax)
        k = (distance - distMin) / (distMax - distMin)
        newFov = (self._context.cameraManager.getMaxMouseCombatFov() - self._context.cameraSettings.minMouseCombatFov) * k + self._context.cameraSettings.minMouseCombatFov
        BigWorld.projection().rampFov(math.radians(self._context.cameraManager.convertToVerticalFOV(newFov)), rampTime)

    def setInvertVertical(self, value):
        LOG_DEBUG('setInvertVertical %s' % value)
        BigWorld.dcursor().invertVerticalMovement = bool(value)

    def __startInterpolation(self, duration):
        self.__sensitivity = BigWorld.dcursor().mouseSensitivity
        BigWorld.dcursor().mouseSensitivity = self.__sensitivity * 0.2

    def __endInterpolation(self):
        BigWorld.dcursor().mouseSensitivity = self.__sensitivity

    def enter(self, params = None):
        import BattleReplay
        if not self._context.cameraManager.isSniperMode:
            _dCursorToTarget(Math.Matrix(self._context.mainMatrixProvider).translation)
        else:
            direction = -Math.Matrix(self._context.entity.realMatrix).applyToAxis(2)
            BigWorld.dcursor().pitch = -direction.pitch
            BigWorld.dcursor().yaw = direction.yaw
            BigWorld.dcursor().roll = 0.0
        self._initPivotDist()
        self.__invertVertical = BigWorld.dcursor().invertVerticalMovement
        pivotDistMin, pivotDistMax = self._pivotDist[0], self._pivotDist[1]
        distance = self._context.getCurZoomlessOffset().length
        self.strategy = BigWorld.CameraStrategyFree(distance, BigWorld.dcursor().matrix, pivotDistMin, pivotDistMax, self._context.mainMatrixProvider)
        self.strategy.interpolationEndCallback = self.__endInterpolation
        self.strategy.interpolationStartCallback = self.__startInterpolation
        self.strategy.aroundLocalAxes = bool(Settings.g_instance.cinemaCamera)
        self.strategy.invertVertical = bool(self.__invertVertical)
        self.setFovByDistance(distance, self._context.cameraSettings.freeCamInterpolationTime)
        self._context.cameraInstance.setStrategy(self.strategy, self._context.cameraSettings.freeCamInterpolationTime if not BattleReplay.isPlaying() else 0, True)
        self.strategy.distanceHalflife = self._context.cameraSettings.freeCamDistHalflife
        player = BigWorld.player()
        GameEnvironment.getCamera().setCameraOffset(player.settings.airplane.visualSettings.cameraOffset - player.settings.hpmass.mass.position)
        self.strategy.pitchClampingEnabled = True

    def exit(self):
        GameEnvironment.getCamera().setCameraOffset(Math.Vector3(0.0, 0.0, 0.0))
        self.strategy.pitchClampingEnabled = False
        self.setInvertVertical(self.__invertVertical)

    def getReturnToNormalTime(self):
        if not Settings.g_instance.cinemaCamera:
            return 0.0
        else:
            return -1.0


class CameraStateSuperFree(CameraState):

    def onMouseScroll(self, dz):
        if dz and self.strategy:
            self.strategy.distance -= dz * 0.01

    @property
    def distance(self):
        return self.strategy.distance

    def enter(self, params = None):
        _dCursorToTarget(Math.Matrix(self._context.mainMatrixProvider).translation)
        self.strategy = BigWorld.CameraStrategySuperFree(BigWorld.dcursor().matrix)
        self._context.cameraInstance.setStrategy(self.strategy, 0.0)

    def exit(self):
        CameraState.exit(self)


class CameraStateBack(CameraState):

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        reductionPt = self._context.reductionPoint * HUD_REDUCTION_POINT_SCALE
        self.strategy = BigWorld.CameraStrategyFixed(cameraSettings.backCamPos, -reductionPt, Math.Vector3(0.0, 1.0, 0.0), self._context.mainMatrixProvider)
        BigWorld.projection().rampFov(math.radians(cameraSettings.backCamFov), cameraSettings.backCamInterpolationTime)
        self._context.cameraInstance.setStrategy(self.strategy, cameraSettings.backCamInterpolationTime, True)

    def getReturnToNormalTime(self):
        return 0.0


class CameraStateSide(CameraState):

    def __init__(self):
        CameraState.__init__(self)

    def _setTransformation(self, pos, direction, dirUp):
        self.__pos = pos
        self.__dir = direction
        self.__dirUp = dirUp

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        sideShift = CAMERA_ALT_MODE_SHIFT_VECTOR if self._context.isAltMode() else Math.Vector3(0.0, 0.0, 0.0)
        self.strategy = BigWorld.CameraStrategyFixed(self.__pos, self.__dir + sideShift, self.__dirUp, self._context.mainMatrixProvider)
        BigWorld.projection().rampFov(self._context.normalFov, cameraSettings.sideCamInterpolationTime)
        self._context.cameraInstance.setStrategy(self.strategy, cameraSettings.sideCamInterpolationTime, True)

    def reEnter(self, params = None):
        self.enter(params)


class CameraStateSideLeft(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        self._setTransformation(self._context.cameraSettings.leftCamPos, self._context.cameraSettings.leftCamDir, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


class CameraStateSideRight(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        self._setTransformation(self._context.cameraSettings.rightCamPos, self._context.cameraSettings.rightCamDir, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


class CameraStateSideTop(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        self._setTransformation(self._context.cameraSettings.topCamPos, self._context.cameraSettings.topCamDir, Math.Vector3(0.0, 0.0, -1.0))
        CameraStateSide.enter(self, params)


class CameraStateSideBottom(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        self._setTransformation(self._context.cameraSettings.bottomCamPos, self._context.cameraSettings.bottomCamDir, Math.Vector3(0.0, 0.0, 1.0))
        CameraStateSide.enter(self, params)


class CameraStateSideBottomLeft(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        rotMatrix = Math.Matrix()
        rotMatrix.setRotateY(math.radians(-45))
        pos = rotMatrix.applyVector(self._context.cameraSettings.leftCamPos)
        direction = rotMatrix.applyVector(self._context.cameraSettings.leftCamDir)
        self._setTransformation(pos, direction, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


class CameraStateSideBottomRight(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        rotMatrix = Math.Matrix()
        rotMatrix.setRotateY(math.radians(45))
        pos = rotMatrix.applyVector(self._context.cameraSettings.rightCamPos)
        direction = rotMatrix.applyVector(self._context.cameraSettings.rightCamDir)
        self._setTransformation(pos, direction, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


class CameraStateSideTopLeft(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        rotMatrix = Math.Matrix()
        rotMatrix.setRotateY(math.radians(45))
        pos = rotMatrix.applyVector(self._context.cameraSettings.leftCamPos)
        direction = rotMatrix.applyVector(self._context.cameraSettings.leftCamDir)
        self._setTransformation(pos, direction, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


class CameraStateSideTopRight(CameraStateSide):

    def __init__(self):
        CameraStateSide.__init__(self)

    def enter(self, params = None):
        rotMatrix = Math.Matrix()
        rotMatrix.setRotateY(math.radians(-45))
        pos = rotMatrix.applyVector(self._context.cameraSettings.rightCamPos)
        direction = rotMatrix.applyVector(self._context.cameraSettings.rightCamDir)
        self._setTransformation(pos, direction, Math.Vector3(0.0, 1.0, 0.0))
        CameraStateSide.enter(self, params)


from CameraStrategyLegacyProxy import *

class CameraStateDestroyedFall(CameraState):

    def __init__(self):
        CameraState.__init__(self)

    def enter(self, params = None):
        cameraInstance = self._context.cameraInstance
        killerId = params
        normalZoomPreset = self._context.cameraManager.zoomPreset.normal
        cameraOffset = normalZoomPreset.position
        self.strategy = BigWorld.CameraStrategyDestroyedFall(Math.Vector4(cameraOffset.x, cameraOffset.y, cameraOffset.z, 0.0), BigWorld.player().id, killerId)
        self.strategy.defaultFov = self._context.normalFov * normalZoomPreset.fovPercent
        if EntityStates.inState(self._context.entity, EntityStates.DESTROYED_FALL):
            self._context.entity.setModelVisible(True)
        cameraInstance.setStrategy(self.strategy, 0.0)
        if CameraEffect.g_instance is not None:
            CameraEffect.g_instance.onCameraEffect('DESTRUCTION')
        return

    def reEnter(self, params = None):
        pass


class CameraStateSpectator(CameraStateFree):

    def __init__(self):
        CameraStateFree.__init__(self)
        self.__cameraTarget = None
        self.__lastRelDistance = None
        return

    def _initPivotDist(self):
        cameraSettings = self._context.cameraSettings
        zoomData = cameraSettings.zoomPresets[self._getZoomPresetPivotDist()]
        self._pivotDist = (abs(zoomData.normal.minScrollPosition.z), abs(zoomData.normal.maxScrollPosition.z))

    def onMouseScroll(self, dz):
        newDist = CameraStateFree.onMouseScroll(self, dz)
        if newDist is not None:
            self.__calcRelDistance(newDist)
            return newDist
        else:
            return

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        cameraInstance = self._context.cameraInstance
        self._initPivotDist()
        BigWorld.dcursor().pitch = 0
        BigWorld.dcursor().yaw = 0
        if self.__lastRelDistance is None:
            self.__calcRelDistance(self._context.getCurZoomlessOffset().length)
        pivotDistMin, pivotDistMax = self._pivotDist[0], self._pivotDist[1]
        distanceRange = pivotDistMax - pivotDistMin
        absDistance = pivotDistMin + self.__lastRelDistance * distanceRange
        self.strategy = BigWorld.CameraStrategyFree(absDistance, BigWorld.dcursor().matrix, pivotDistMin, pivotDistMax, self._context.mainMatrixProvider)
        self.strategy.aroundLocalAxes = False
        self.strategy.distanceHalflife = self._context.cameraSettings.freeCamDistHalflife
        cameraInstance.setStrategy(self.strategy, cameraSettings.spectatorCamInterpolationTime)
        self.setFovByDistance(absDistance, cameraSettings.spectatorCamInterpolationTime)
        self.strategy.pitchClampingEnabled = True
        return

    def reEnter(self, params = None):
        self.enter(params)

    def __calcRelDistance(self, absDistance):
        pivotDistMin, pivotDistMax = self._pivotDist[0], self._pivotDist[1]
        checkedDist = clamp(pivotDistMin, absDistance, pivotDistMax)
        distanceRange = pivotDistMax - pivotDistMin
        self.__lastRelDistance = (checkedDist - pivotDistMin) / distanceRange

    def getReturnToNormalTime(self):
        return -1.0

    def _getZoomPresetPivotDist(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def updateTarget(self, vehicleID):
        if self.strategy:
            self._initPivotDist()
            self.strategy.distanceMin = self._pivotDist[0]
            self.strategy.distanceMax = self._pivotDist[1]
            self.strategy.distance = self.strategy.distance
            self.strategy.sourceProvider = self._context.mainMatrixProvider
        else:
            LOG_ERROR("Cannot update the target because the strategy isn't exist!")


class CameraStateDynamicSpectator(CameraStateSpectator):
    _particleEffects = ['aim_spectator']

    def __init__(self):
        CameraStateSpectator.__init__(self)
        self.crossHairVisible = True
        self.strategy = BigWorld.CameraStrategyDynamicSpectator()
        self.currentSpectatorType = None
        return

    def onMouseScroll(self, dz):
        pass

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        cameraInstance = self._context.cameraInstance
        self.strategy.defaultFov = self._context.normalFov
        self.strategy.setObservedEntity(BigWorld.player().curVehicleID)
        self.strategy.pySwitchSpectatorMode(params)
        cameraInstance.setStrategy(self.strategy, cameraSettings.spectatorCamInterpolationTime)

    def reEnter(self, params = None):
        pass

    def getReturnToNormalTime(self):
        return -1.0

    def _getZoomPresetPivotDist(self):
        return CAMERA_ZOOM_PRESET.DIRECT_COMBAT

    def updateTarget(self, vehicleID):
        entityID = vehicleID
        if entityID is None:
            entityID = 0
        if self.strategy:
            self.strategy.setObservedEntity(entityID)
        return

    def onTacticalSpectator(self, spectatorType):
        self.strategy.pySwitchSpectatorMode(spectatorType)
        self.currentSpectatorType = spectatorType

    def switchTacticalMode(self):
        self.strategy.switchTacticalMode()

    def exit(self):
        pass

    def cycleSpectatorType(self):
        if self.currentSpectatorType == SPECTATOR_TYPE.CINEMATIC:
            self.onTacticalSpectator(SPECTATOR_TYPE.CONTROLLED_TACTICAL)
        elif self.currentSpectatorType == SPECTATOR_TYPE.CONTROLLED_TACTICAL:
            self.onTacticalSpectator(SPECTATOR_TYPE.AUTO_TACTICAL)
        else:
            self.onTacticalSpectator(SPECTATOR_TYPE.CINEMATIC)


class CameraStateTarget(CameraState):

    def __init__(self):
        CameraState.__init__(self)
        self.crossHairVisible = True

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        cameraInstance = self._context.cameraInstance
        self.strategy = BigWorld.CameraStrategyTarget(self._context.mainMatrixProvider, self._context.getCurZoomlessOffset(), self._context.targetMatrix)
        self.strategy.worldUp = False
        BigWorld.projection().rampFov(self._context.normalFov, cameraSettings.targetCamInterpolationTime)
        cameraInstance.setStrategy(self.strategy, cameraSettings.targetCamInterpolationTime)

    def reEnter(self, params = None):
        self.enter(params)


class CameraStateTargetOnMe(CameraStateTarget):
    pass


class CameraStateFreeFixable(CameraState):
    PITCH_MIN = -math.pi * 0.5 + 0.3
    PITCH_MAX = math.pi * 0.5 - 0.3

    def enter(self, params = None):
        cameraSettings = self._context.cameraSettings
        self.strategy = BigWorld.CameraStrategyFreeFixable(self._context.mainMatrixProvider, self._context.getCurZoomlessOffset(), cameraSettings.freeFixableCamSpeed, CameraStateFreeFixable.PITCH_MIN, CameraStateFreeFixable.PITCH_MAX)
        self._context.cameraInstance.setStrategy(self.strategy, cameraSettings.freeFixableCamInterpolationTime)

    def rotationPower(self, rotationData):
        if self.strategy:
            self.strategy.horRotationPower = rotationData[0]
            self.strategy.vertRotationPower = rotationData[1]


class CameraStateSpectatorSide(CameraState):
    GROUND_NODE_UPDATE_TIME = 1.5

    def __init__(self):
        CameraState.__init__(self)
        self.__hpModel = BigWorld.Model('objects/camera_spectator.model')
        self.__cbExitState = None
        self.__returnToNormal = -1.0
        self.__lagHalfLife = 0.0
        self.__finishTime = 0.0
        self.__isNodeTimeline = False
        return

    def __parseData(self, data):
        if self.__cbExitState:
            BigWorld.cancelCallback(self.__cbExitState)
            self.__cbExitState = None
        if data.finishTime > 0.0:
            self.__finishTime = data.finishTime
            self.__cbExitState = BigWorld.callback(self.__finishTime, self._context.cameraManager.leaveState)
            self.__returnToNormal = data.finishLength
        if hasattr(data, 'lagHalfLife'):
            self.__lagHalfLife = data.lagHalfLife
        strategyData = {}
        self.__parseNodePositions(data, strategyData)
        self.__parseNodeTargets(data, strategyData)
        self.__parseFOVs(data, strategyData)
        self.__parsePositions(data, strategyData)
        self.__parseRotations(data, strategyData)
        self.__parseEffects(data, strategyData)
        if hasattr(data, 'linkingType'):
            strategyData['linkingType'] = data.linkingType
        else:
            LOG_ERROR("Linking type isn't exist!")
        return strategyData

    def __parseNodePositions(self, data, parsedData):
        if hasattr(data, 'nodePositionTimeline'):
            parsedData['nodePositions'] = self.__parseNodeTimeline(data.nodePositionTimeline)

    def __parseNodeTargets(self, data, parsedData):
        if hasattr(data, 'nodeTargetTimeline'):
            parsedData['nodeTargets'] = self.__parseNodeTimeline(data.nodeTargetTimeline)

    def __parseFOVs(self, data, parsedData):
        parsedData['fov'] = self.__parseFOVTimeline(data.fovTimeline)

    def __parsePositions(self, data, parsedData):
        if hasattr(data, 'positionTimeline'):
            parsedData['positions'] = self.__parsePositionTimeline(data.positionTimeline)

    def __parseRotations(self, data, parsedData):
        if hasattr(data, 'rotationTimeline'):
            parsedData['rotations'] = self.__parseRotationTimeline(data.rotationTimeline)

    def __parseEffects(self, data, parsedData):
        if hasattr(data, 'effectTimeline'):
            parsedData['effects'] = self.__parseEffectTimeline(data.effectTimeline)

    def __parsePositionTimeline(self, data):
        positionKeytimes = []
        for keytime in data.keytime:
            try:
                coord = keytime.position
                fadeinTime = keytime.fadeinTime if hasattr(keytime, 'fadeinTime') else 0.0
                fadeoutTime = keytime.fadeoutTime if hasattr(keytime, 'fadeoutTime') else 0.0
                positionKeytimes.append((keytime.time,
                 coord,
                 0,
                 keytime.type,
                 keytime.duration,
                 fadeinTime,
                 fadeoutTime))
            except:
                LOG_CURRENT_EXCEPTION()
                continue

        return positionKeytimes

    def __parseRotationTimeline(self, data):
        rotationKeytimes = []
        for keytime in data.keytime:
            try:
                fadeinTime = keytime.fadeinTime if hasattr(keytime, 'fadeinTime') else 0.0
                fadeoutTime = keytime.fadeoutTime if hasattr(keytime, 'fadeoutTime') else 0.0
                rotationKeytimes.append((keytime.time,
                 keytime.rotation,
                 0,
                 keytime.type,
                 keytime.duration,
                 fadeinTime,
                 fadeoutTime))
            except:
                LOG_CURRENT_EXCEPTION()
                continue

        return rotationKeytimes

    def __parseNodeTimeline(self, data):
        nodeKeytimes = []
        for keytime in data.keytime:
            try:
                from clientConsts import NODE_TIMELINE_NODE_FLAGS
                from clientConsts import NODE_TIMELINE_NEAREST_NODE
                flags = NODE_TIMELINE_NODE_FLAGS.NONE
                try:
                    if keytime.node == 'SP_battle_camera_position':
                        x, y, z, _ = GameEnvironment.getCamera().context.cameraOffset.target
                        coord = Math.Vector3(x, y, z)
                    else:
                        coord = self.__hpModel.node(keytime.node).nodeLocalTransform.applyToOrigin() * WORLD_SCALING
                except:
                    x, y, z, flags = BigWorld.getCameraNode(keytime.node)
                    coord = Math.Vector3(x, y, z)

                fadeinTime = keytime.fadeinTime if hasattr(keytime, 'fadeinTime') else 0.0
                fadeoutTime = keytime.fadeoutTime if hasattr(keytime, 'fadeoutTime') else 0.0
                nodeKeytimes.append((keytime.time,
                 coord,
                 flags,
                 keytime.type,
                 keytime.duration,
                 fadeinTime,
                 fadeoutTime))
            except:
                LOG_CURRENT_EXCEPTION()
                continue

        return nodeKeytimes

    def __parseFOVTimeline(self, data):
        fovKeytimes = []
        for keytime in data.keytime:
            fadeinTime = keytime.fadeinTime if hasattr(keytime, 'fadeinTime') else 0.0
            fadeoutTime = keytime.fadeoutTime if hasattr(keytime, 'fadeoutTime') else 0.0
            fovKeytimes.append((keytime.time,
             keytime.fov,
             keytime.duration,
             fadeinTime,
             fadeoutTime))

        return fovKeytimes

    def __parseEffectTimeline(self, data):
        effectKeytimes = []
        for keytime in data.keytime:
            weight = keytime.weight if hasattr(keytime, 'weight') else 1.0
            effectKeytimes.append((keytime.time,
             keytime.id,
             weight,
             keytime.enable))

        return effectKeytimes

    def enter(self, params = None):
        if params:
            animationData = self.__parseData(params)
            self.__isNodeTimeline = 'nodePositions' in animationData
            if not self.__isNodeTimeline:
                source = Math.Matrix()
                source.translation = Math.Vector3(0.0, 0.0, 0.0)
            else:
                source = self._context.mainMatrixProvider
            self._context.cameraInstance.parentMatrix = source
            self._context.cameraInstance.collisionCheckEnabled = self.__isNodeTimeline
            self.strategy = BigWorld.CameraStrategyCinematic(animationData, Math.Vector3(0.0, 1.0, 0.0), source, self.__cbExitState is None, self._context.cameraInstance.effectController, self.__lagHalfLife)
            self.strategy.staticNodeUpdateTime = self.__class__.GROUND_NODE_UPDATE_TIME
            self._context.cameraInstance.setStrategy(self.strategy, 0.0)
        return

    def exit(self):
        CameraState.exit(self)
        self.__clear()

    def __clear(self):
        if self.__cbExitState:
            BigWorld.cancelCallback(self.__cbExitState)
            self.__cbExitState = None
        self._context.cameraInstance.parentMatrix = self._context.mainMatrixProvider
        self._context.cameraInstance.collisionCheckEnabled = True
        self.__finishTime = 0.0
        return

    def reEnter(self, params = None):
        self.updateParams(params)

    def updateParams(self, params = None):
        self.__clear()
        self.enter(params)

    def getReturnToNormalTime(self):
        return self.__returnToNormal

    def setReturnToNormalTime(self, val):
        self.__returnToNormal = val

    def setCinematicTime(self, value):
        self.strategy.setTime(value)
        if self.__finishTime > 0.0:
            if value < self.__finishTime:
                leaveTime = self.__finishTime - value
                if self.__cbExitState:
                    BigWorld.cancelCallback(self.__cbExitState)
                self.__cbExitState = BigWorld.callback(leaveTime, self._context.cameraManager.leaveState)

    def updateTarget(self, vehicleID):
        if self.strategy:
            if self.__isNodeTimeline:
                newSource = self._context.mainMatrixProvider
                self.strategy.sourceMatrix = newSource
                self._context.cameraInstance.parentMatrix = newSource
        else:
            LOG_ERROR("Cannot update the target because the strategy isn't exist!")