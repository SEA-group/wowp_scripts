# Embedded file name: scripts/client/Camera.py
from functools import partial
import CameraZoomStatsCollector
import GUI
import InputMapping
import Settings
import db.DBLogic
from CameraStates import CameraState, BattleCameraStateMachine
from CameraStrategyLegacyProxy import *
from EntityHelpers import EntityStates
from Event import Event, EventManager, LazyEvent
from GameServiceBase import GameServiceBase
from MathExt import toVec4
from clientConsts import CAMERA_MOVING_SPEED, CAMERA_DEFAULT_BOMBING_IDX, CAMERA_MAX_TARGET_SPEED, SWITCH_STYLES_BUTTONS, OUTRO_FADEIN_DURATION, CAMERA_START_ALIGN_TIME, CAMERA_STOP_ALIGN_TIME, CAMERA_ALIGN_FLEXIBILITY, CAMERA_ZOOM_PRESET
from consts import BATTLE_MODE, INPUT_SYSTEM_STATE
from debug_utils import LOG_ERROR, LOG_TRACE
inputToCamState = {INPUT_SYSTEM_STATE.MOUSE: {BATTLE_MODE.COMBAT_MODE: CameraState.MouseCombat,
                            BATTLE_MODE.ASSAULT_MODE: CameraState.MouseCombat,
                            BATTLE_MODE.GUNNER_MODE: CameraState.Gunner,
                            BATTLE_MODE.SNIPER_MODE: CameraState.Sniper},
 INPUT_SYSTEM_STATE.KEYBOARD: {BATTLE_MODE.COMBAT_MODE: CameraState.NormalCombat,
                               BATTLE_MODE.ASSAULT_MODE: CameraState.NormalCombat,
                               BATTLE_MODE.GUNNER_MODE: CameraState.Gunner,
                               BATTLE_MODE.SNIPER_MODE: CameraState.Sniper},
 INPUT_SYSTEM_STATE.JOYSTICK: {BATTLE_MODE.COMBAT_MODE: CameraState.JoystickCombat,
                               BATTLE_MODE.ASSAULT_MODE: CameraState.JoystickCombat,
                               BATTLE_MODE.GUNNER_MODE: CameraState.Gunner,
                               BATTLE_MODE.SNIPER_MODE: CameraState.JoystickSniper},
 INPUT_SYSTEM_STATE.GAMEPAD_DIRECT_CONTROL: {BATTLE_MODE.COMBAT_MODE: CameraState.GamepadCombat,
                                             BATTLE_MODE.ASSAULT_MODE: CameraState.GamepadCombat,
                                             BATTLE_MODE.GUNNER_MODE: CameraState.GamepadCombat,
                                             BATTLE_MODE.SNIPER_MODE: CameraState.Sniper}}
cameraStatesWithZoom = [CameraState.MouseCombat,
 CameraState.GamepadCombat,
 CameraState.MouseAssault,
 CameraState.NormalCombat,
 CameraState.NormalAssault,
 CameraState.JoystickCombat,
 CameraState.JoystickAssault,
 CameraState.Bomber,
 CameraState.Gunner,
 CameraState.Sniper,
 CameraState.JoystickSniper]

class ZoomStates:
    Normal = 1
    Sniper = 2


class CameraContext:

    def __init__(self, entity):
        self.entity = entity
        self.entityMatrix = entity.realMatrix
        self.targetMatrix = entity.resMatrix.b
        self.cameraSettings = db.DBLogic.g_instance.getAirplaneCameraPreset(entity.settings.airplane.visualSettings.camera)
        self.cameraOffset = entity.settings.airplane.visualSettings.cameraOffset
        self.normalFov = math.radians(self.cameraSettings.defaultFov)


def toggleDebug():
    GameEnvironment.getCamera().debugMode = not GameEnvironment.getCamera().debugMode


def toggleDebugCameraEffect():
    GameEnvironment.getCamera().getAircraftCam().effectController.isDebugEnabled = not GameEnvironment.getCamera().getAircraftCam().effectController.isDebugEnabled


class Camera(GameServiceBase):
    PRE_INTRO_ZOOM_STATE = ZoomStates.Normal
    PRE_INTRO_ZOOM_START_TIME = 7
    PRE_INTRO_CINEMATIC_START_TIME = 30

    def __init__(self):
        LOG_DEBUG('Camera constructor')
        super(Camera, self).__init__()
        self.__createEvents()
        self.__createMatrices()
        self.__cameraStateMachine = BattleCameraStateMachine()
        self.__zoomDataPosition = Math.Vector3(0, 0, 0)
        self.__inputState = None
        self.__inputBattleMode = BATTLE_MODE.COMBAT_MODE
        self.__updateZoomCallback = None
        self.__modelVisible = True
        self.__backToCurrentZoomDataIdx = None
        self.__isZoomEnable = True
        self.__isSniperModeEnable = True
        self.__bombingPrevZoomDataIdx = CAMERA_DEFAULT_BOMBING_IDX + 1
        self.__altMode = False
        self.__effectFOV = 1.0
        self.__context = None
        self.__targetEntity = None
        self.__curZoomState = ZoomStates.Normal
        self.setEffectsEnabled(Settings.g_instance.cameraEffectsEnabled)
        self.__sniperOnZoomDataIdx = None
        self.__inputToCamState = inputToCamState
        self.__curZoomPreset = CAMERA_ZOOM_PRESET.DEFAULT
        self.setMaxMouseCombatFov(Settings.g_instance.maxMouseCombatFov)
        self.__cbOutro = None
        self.__cinematicStarted = False
        self.__cursorLocked = False
        self.__preintroStopped = False
        self.__preintroFinished = False
        self.__cinematicPlayed = False
        self.__isInOverview = False
        return

    @property
    def curZoomData(self):
        preset = self.__context.cameraSettings.zoomPresets[self.__curZoomPreset]
        if self.__curZoomState == ZoomStates.Sniper:
            return preset.sniper
        else:
            return preset.normal

    def reload(self):
        if self.__context:
            self.__context.cameraSettings = db.DBLogic.g_instance.getAirplaneCameraPreset(self.__context.entity.settings.airplane.visualSettings.camera)
        self.reset()

    def setMaxMouseCombatFov(self, value):
        self.__maxDistanceFOV = value
        if self.__context and self.__context.cameraSettings:
            self.__applyZoomStateFov(self.zoomInterpolationTime)

    def getMaxMouseCombatFov(self):
        return self.__maxDistanceFOV

    @property
    def context(self):
        return self.__context

    @property
    def zoomInterpolationTime(self):
        return self.__compositeOffset.duration

    @zoomInterpolationTime.setter
    def zoomInterpolationTime(self, value):
        if self.__compositeOffset:
            self.__compositeOffset.duration = value

    @property
    def zoomPreset(self):
        return self.__context.cameraSettings.zoomPresets[self.__curZoomPreset]

    @property
    def isSniperMode(self):
        return self.getState() in CameraState.SniperStates

    def __unlockCursor(self, flexibility = -1):
        if self.__defaultStrategies['CameraStrategyMouse']:
            if flexibility > 0.0:
                self.__defaultStrategies['CameraStrategyMouse'].flexibility = flexibility
            self.__defaultStrategies['CameraStrategyMouse'].unlockCursor()
            self.__defaultStrategies['CameraStrategyMouse'].rotateCursor(0, 0)

    def __checkBattleCount(self):
        arenaStartTime = BigWorld.player().arenaStartTime
        serverTime = BigWorld.serverTime()
        curTime = int(round(arenaStartTime - serverTime))
        if arenaStartTime > 0 and CAMERA_STOP_ALIGN_TIME < curTime <= CAMERA_START_ALIGN_TIME:
            GameEnvironment.g_instance.getTimer().eUpdate -= self.__checkBattleCount
            if self.__defaultStrategies['CameraStrategyMouse']:
                flexibility = self.__defaultStrategies['CameraStrategyMouse'].flexibility
                self.__defaultStrategies['CameraStrategyMouse'].flexibility = CAMERA_ALIGN_FLEXIBILITY
                self.__defaultStrategies['CameraStrategyMouse'].lockCursor()
                self.__defaultStrategies['CameraStrategyMouse'].rotateCursor(0, 0)
                BigWorld.callback(CAMERA_STOP_ALIGN_TIME, partial(self.__unlockCursor, flexibility))

    def __updateHUDProgress(self):
        arenaStartTime = BigWorld.player().arenaStartTime
        serverTime = BigWorld.serverTime()
        curTime = int(round(arenaStartTime - serverTime))
        if arenaStartTime > 0:
            if curTime <= self.__class__.PRE_INTRO_CINEMATIC_START_TIME:
                if curTime > self.__class__.PRE_INTRO_ZOOM_START_TIME:
                    if not self.__cinematicStarted:
                        player = BigWorld.player()
                        if EntityStates.inState(player, EntityStates.PRE_START_INTRO):
                            if 'scenarioCameraController' in player.controllers:
                                import BWPersonality
                                player.controllers['scenarioCameraController'].onEvent(BWPersonality.getNextIntroTimeline(), BigWorld.serverTime())
                                cinematicStartTime = self.__class__.PRE_INTRO_CINEMATIC_START_TIME - curTime
                                if cinematicStartTime < self.__class__.PRE_INTRO_CINEMATIC_START_TIME:
                                    self.getStateObject().setCinematicTime(cinematicStartTime)
                            self.__cinematicStarted = True
                elif not self.__preintroFinished:
                    curTime = clamp(0.0, curTime, self.__class__.PRE_INTRO_ZOOM_START_TIME)
                    self.stopPreIntro(curTime)

    def __startPreIntro(self):
        if not self.__cinematicPlayed:
            self.__setZoom(self.PRE_INTRO_ZOOM_STATE)
            GameEnvironment.g_instance.getTimer().eUpdate += self.__updateHUDProgress
            self.setZoomEnable(False)
            self.__cinematicPlayed = True

    def __finishPreIntro(self, interpTime = 0.0):
        if not self.__preintroFinished:
            self.__preintroFinished = True
            self.zoomInterpolationTime = interpTime
            GameEnvironment.g_instance.getTimer().eUpdate -= self.__updateHUDProgress
        self.__setZoom(ZoomStates.Normal)

    def __returnToNormalFov(self):
        if self.__context is not None and self.__context.cameraSettings:
            self.__applyZoomStateFov(CAMERA_MOVING_SPEED)
        return

    def stopPreIntro(self, interpTime = 0.0):
        self.__finishPreIntro(interpTime)
        if self.getState() == CameraState.SpectatorSide:
            self.getStateObject().setReturnToNormalTime(0.0)
            self.leaveState(CameraState.SpectatorSide)
        self.zoomInterpolationTime = CAMERA_MOVING_SPEED
        self.__preintroStopped = True
        self.setZoomEnable(True)
        BigWorld.callback(0.01, self.__returnToNormalFov)

    def __startOutro(self):
        self.__cbOutro = None
        player = BigWorld.player()
        arenaData = db.DBLogic.g_instance.getArenaData(player.arenaType)
        timelineID = arenaData.outroTimeline
        if self.getState() == CameraState.ReplayFree:
            self.leaveState(CameraState.ReplayFree)
        player.controllers['scenarioCameraController'].onEvent(timelineID, BigWorld.serverTime())
        return

    def setSniperModeType(self, type):
        self.__isLastZoomModeAirplane = type
        self.__lastZoomDataIndecesShift = 1 if self.__isLastZoomModeAirplane else 2
        if self.isSniperMode:
            self.__setZoom(ZoomStates.Sniper)

    def __createEvents(self):
        self.__eventManager = EventManager()
        em = self.__eventManager
        self.eSetCameraRingVisible = Event(em)
        self.eStateChanged = Event(em)
        self.eZoomStateChanged = Event(em)
        self.eDistanceChanged = Event(em)
        self.eSniperMode = Event(em)
        self.eSetViewpoint = Event(em)
        self.eSetCrosshairVisible = Event(em)
        self.leSetCenterPointMatrix = LazyEvent(em)
        self.leSetMovingTargetMatrix = LazyEvent(em)

    def addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_CURSOR_CAMERA, lambda : self.setState(CameraState.Free), lambda : self.leaveState(CameraState.Free))
        processor.addPredicate(InputMapping.CMD_CURSOR_CAMERA, lambda : self.getState() not in (CameraState.Bomber,
         CameraState.Gunner,
         CameraState.Sniper,
         CameraState.JoystickSniper,
         CameraState.Target))
        processor.addListeners(InputMapping.CMD_TARGET_CAMERA, None, None, self.setTargetCamera)
        processor.addListeners(InputMapping.CMD_SWITCH_TACTICAL_MODE, None, None, lambda fired: self.switchTacticalMode())
        return

    def switchTacticalMode(self):
        if self.getState() == CameraState.DynamicSpectator:
            self.getStateObject().switchTacticalMode()

    def __createMatrices(self):
        self.__mainMatrixProvider = Math.MatrixProduct()
        self.__mainMatrixProvider.a = Math.Matrix()
        self.__mainMatrixProvider.a.setIdentity()
        self.__mainMatrixProvider.b = Math.MatrixProduct()
        self.__vibrationMatrix = BigWorld.VibroMatrixProvider()
        self.__mainMatrixProvider.b.a = self.__vibrationMatrix
        self.__mainMatrixProvider.b.a.isEnable = True
        self.__cam = BigWorld.AircraftCamera()
        self.__cam.parentMatrix = self.__mainMatrixProvider
        self.__compositeOffset = Math.Vector4Morph()
        self.__compositeOffset.duration = CAMERA_MOVING_SPEED
        self.__target = Math.Vector4Morph()
        self.__target.target = Math.Vector4(0.0, 0.0, 0.0, 0.0)
        self.__target.duration = CAMERA_MOVING_SPEED
        self.__rotationX = GUI.RotationXMatrixMorph()
        self.__rotationX.target = 0
        self.__rotationX.duration = CAMERA_MOVING_SPEED
        mtx = Math.MatrixProduct()
        mtx.a = GameEnvironment.getHUD().offsetMtx.reduction
        mtx.b = self.__rotationX
        self.__offsetTarget = Math.Vector4Product()
        self.__offsetTarget.a = self.__target
        self.__offsetTarget.b = Math.Vector4Translation(mtx)
        self.__defaultStrategies = {'CameraStrategyMouse': BigWorld.CameraStrategyScript(CameraStrategyMouse(self.__compositeOffset, self.__offsetTarget, Math.Matrix())),
         'CameraStrategyNormal': BigWorld.CameraStrategyScript(CameraStrategyJoystick(self.__compositeOffset, self.__offsetTarget, Math.Matrix())),
         'CameraStrategyGamepad': BigWorld.CameraStrategyScript(CameraStrategyGamepad(self.__compositeOffset, self.__offsetTarget, Math.Matrix())),
         'CameraStrategyGunner': BigWorld.CameraStrategyScript(CameraStrategyGunner(self.__compositeOffset, self.__offsetTarget, Math.Matrix())),
         'CameraStrategyDebug': BigWorld.CameraStrategyScript(CameraStrategyDebug(self.__compositeOffset, self.__offsetTarget, Math.Matrix(), None))}
        return

    def onSpeedStateMachineInitialized(self, minSpeed, maxSpeed):
        self.__defaultStrategies['CameraStrategyMouse'].onSpeedStateMachineInitialized(minSpeed, maxSpeed)
        self.__defaultStrategies['CameraStrategyGunner'].onSpeedStateMachineInitialized(minSpeed, maxSpeed)
        self.__defaultStrategies['CameraStrategyNormal'].onSpeedStateMachineInitialized(minSpeed, maxSpeed)
        self.__defaultStrategies['CameraStrategyGamepad'].onSpeedStateMachineInitialized(minSpeed, maxSpeed)

    def __calcTargetSpeed(self, targetCamSpeed):
        sensitivity = (1 - Settings.g_instance.camTargetSensitivity) ** 4.0
        return targetCamSpeed * (1.0 - sensitivity) + CAMERA_MAX_TARGET_SPEED * sensitivity

    def getCursorDirection(self):
        return self.getStateStrategy().cursorDirection

    def setCameraOffset(self, cameraOffset):
        if not self.__context.entity.isDestroyed and self.__context.entity.inWorld:
            self.__context.mainMatrixProvider = self.__mainMatrixProvider
            self.__context.cameraOffset = self.__compositeOffset

    def __setContext(self, context):
        self.__context = context
        self.__context.mainMatrixProvider = self.__mainMatrixProvider
        self.__context.defaultStrategies = self.__defaultStrategies
        self.__context.cameraInstance = self.__cam
        self.__context.cameraManager = self
        self.__context.isAltMode = self.isAltMode
        self.__context.applyZoomStateFov = self.__applyZoomStateFov
        self.__context.getCurZoomlessOffset = self.__getCurZoomlessOffset
        self.__context.setZoom = self.__setZoom
        self.__context.getDestZoomDataIdx = lambda : self.__curZoomState
        self.setCameraOffset(Math.Vector3(0.0, 0.0, 0.0))
        self.__vibrationMatrix.offsetAmplitude = self.__context.cameraSettings.vibrationAmplitudes
        self.__vibrationMatrix.offsetFreqs = self.__context.cameraSettings.vibrationFrequencies
        self.__target.target = Math.Vector4(1.0, 1.0, 1.0, 1.0)
        self.__rotationX.target = 0
        CameraState.setInitParams(self.__context)
        self.__cameraStateMachine.reEnterState()
        self.__mainMatrixProvider.a = self.__context.entityMatrix
        strategy = self.__defaultStrategies['CameraStrategyNormal']
        strategy.sourceMatrix = self.__mainMatrixProvider
        strategy = self.__defaultStrategies['CameraStrategyDebug']
        strategy.sourceMatrix = self.__mainMatrixProvider
        strategy = self.__defaultStrategies['CameraStrategyMouse']
        strategy.sourceMatrix = self.__mainMatrixProvider
        strategy = self.__defaultStrategies['CameraStrategyGamepad']
        strategy.sourceMatrix = self.__mainMatrixProvider
        strategy = self.__defaultStrategies['CameraStrategyGunner']
        gunnerMtx = Math.MatrixProduct()
        tMtx = Math.Matrix()
        tMtx.setRotateY(math.pi)
        gunnerMtx.a = tMtx
        gunnerMtx.b = self.__mainMatrixProvider
        strategy.sourceMatrix = gunnerMtx
        CameraState.setInitParams(self.__context)
        self.__cameraStateMachine.reEnterState()

    def __getCurZoomlessOffset(self):
        if self.isSniperMode:
            return self.__context.cameraSettings.zoomPresets[self.__curZoomPreset].sniper.position
        else:
            return self.__context.cameraSettings.zoomPresets[self.__curZoomPreset].normal.position

    def afterLinking(self):
        super(self.__class__, self).afterLinking()
        BigWorld.camera(self.__cam)
        import BattleReplay
        if not BattleReplay.isPlaying():
            self.setSniperModeType(Settings.g_instance.getGameUI()['isSniperMode'])
            BattleReplay.g_replay.notifySniperModeType(Settings.g_instance.getGameUI()['isSniperMode'])
        if BigWorld.player().state == EntityStates.PRE_START_INTRO:
            self.eSetViewpoint(BigWorld.player().mapMatrix)
        else:
            self.eSetViewpoint(BigWorld.camera().invViewMatrix)

    def doLeaveWorld(self):
        CameraZoomStatsCollector.g_cameraZoomStatsCollector.allowProfiling(False)
        self.__cancelZoomCallback()
        if self.__cameraStateMachine:
            self.__cameraStateMachine.destroy()
            self.__cameraStateMachine = None
        BigWorld.projection().fov = self.__context.normalFov
        self.__cam.parentMatrix = Math.Matrix()
        self.__cam = None
        self.__context = None
        self.__target = None
        self.__rotationX = None
        self.__offsetTarget = None
        self.__compositeOffset = None
        self.__mainMatrixProvider.b = None
        self.__mainMatrixProvider = None
        self.__vibrationMatrix = None
        self.__defaultStrategies['CameraStrategyNormal'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyNormal'].Deactivate()
        self.__defaultStrategies['CameraStrategyMouse'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyMouse'].Deactivate()
        self.__defaultStrategies['CameraStrategyGamepad'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyGamepad'].Deactivate()
        self.__defaultStrategies['CameraStrategyGunner'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyGunner'].Deactivate()
        self.__defaultStrategies['CameraStrategyDebug'].sourceMatrix = Math.Matrix()
        CameraState.setInitParams(None)
        super(Camera, self).doLeaveWorld()
        if self.__cbOutro:
            BigWorld.cancelCallback(self.__cbOutro)
            self.__cbOutro = None
        return

    def destroy(self):
        self.__defaultStrategies['CameraStrategyNormal'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyMouse'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyGamepad'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyGunner'].sourceMatrix = Math.Matrix()
        self.__defaultStrategies['CameraStrategyDebug'].sourceMatrix = Math.Matrix()
        self.__eventManager.clear()
        super(self.__class__, self).destroy()

    def reset(self):
        if self.__context.entity.id != BigWorld.player().id:
            self.setMainEntity(BigWorld.player())
        self.__cameraStateMachine.reset()
        self.__changeInputState()
        BigWorld.callback(0.2, BigWorld.player().onObserver)

    def setInputToCamState(self, curr):
        self.__inputToCamState = curr

    def __changeInputState(self):
        if EntityStates.inState(BigWorld.player(), EntityStates.OBSERVER | EntityStates.END_GAME | EntityStates.DEAD | EntityStates.OUTRO):
            return
        self.setState(self.__inputToCamState[self.__inputState][self.__inputBattleMode])

    def onInputProfileChange(self, inputState):
        if self.__inputState:
            self.leaveState(self.__inputToCamState[self.__inputState][self.__inputBattleMode])
            if self.__inputState in (INPUT_SYSTEM_STATE.MOUSE, INPUT_SYSTEM_STATE.GAMEPAD_DIRECT_CONTROL, INPUT_SYSTEM_STATE.JOYSTICK):
                self.__cam.removeShadowStrategy(self.__defaultStrategies['CameraStrategyMouse'])
        if inputState in (INPUT_SYSTEM_STATE.MOUSE, INPUT_SYSTEM_STATE.GAMEPAD_DIRECT_CONTROL, INPUT_SYSTEM_STATE.JOYSTICK):
            self.__cam.addShadowStrategy(self.__defaultStrategies['CameraStrategyMouse'])
        self.__isInOverview = False
        self.__inputState = inputState
        self.__changeInputState()

    def onBattleModeChange(self, mode):
        self.__curZoomState = ZoomStates.Normal
        if self.__inputState:
            self.leaveState(self.__inputToCamState[self.__inputState][self.__inputBattleMode])
        self.__inputBattleMode = mode
        self.__changeInputState()

    def setTargetCameraOnMe(self, isOn):
        if isOn:
            self.__context.targetMatrix = self.__context.entityMatrix
            self.setState(CameraState.TargetMe)
        else:
            self.leaveState(CameraState.TargetMe)

    def setTargetCamera(self, targetCamera):
        if targetCamera and self.__targetEntity is not None:
            self.__context.targetMatrix = self.__targetEntity.matrix
            self.__context.targetMatrix.notModel = True
            self.setState(CameraState.Target)
        else:
            self.leaveState(CameraState.Target)
        if self.__inputState == INPUT_SYSTEM_STATE.JOYSTICK:
            if targetCamera:
                self.resetToZoomMin()
            else:
                self.resetToBackZoom(ignoreZoomDataIdxList=[])
        return

    def setTargetEntity(self, entity):
        needRefreshTargetMatrix = entity is not None and entity != self.__targetEntity
        self.__targetEntity = entity
        if self.getState() == CameraState.Target:
            if needRefreshTargetMatrix:
                self.setTargetCamera(True)
            elif entity is None:
                cmd = InputMapping.CMD_TARGET_CAMERA
                if InputMapping.g_instance.getSwitchingStyle(cmd) == SWITCH_STYLES_BUTTONS.SWITCH:
                    GameEnvironment.getInput().commandProcessor.getCommand(cmd).isFired = False
                self.setTargetCamera(False)
        return

    def storeBombingData(self):
        pass

    def setBombingData(self):
        self.__setZoom(self.zoomPreset.normal)

    def restoreBombingData(self):
        self.__setZoom(self.zoomPreset.normal)

    def updateSpectator(self, vehicleID):
        if BigWorld.player().isObserverToBattleTransition:
            return
        else:
            currentTarget = BigWorld.entities.get(vehicleID, None)
            if currentTarget:
                self.setMainEntity(currentTarget)
            if self.getState() != CameraState.DynamicSpectator:
                self.setState(CameraState.DynamicSpectator, 0)
            self.getStateObject().updateTarget(vehicleID)
            return

    def switchToSpectator(self):
        self.onTacticalSpectator(0)

    def onTacticalSpectator(self, spectatorType):
        if self.getState() == CameraState.DynamicSpectator:
            self.getStateObject().onTacticalSpectator(spectatorType)
        else:
            self.setState(CameraState.DynamicSpectator, spectatorType)

    def setMainEntity(self, entity):
        """set main matrix for all camera states from entity"""
        LOG_TRACE('Camera.setMainEntity', entity.id)
        self.__setContext(CameraContext(entity))
        self.__cancelZoomCallback()
        self.__context.entity.setModelVisible(not (self.curZoomData.hideModel if self.curZoomData else False))

    def onPlayerAvatarStateChanged(self, oldState, state):
        if state == EntityStates.PRE_START_INTRO:
            GameEnvironment.g_instance.getTimer().eUpdate += self.__checkBattleCount
        if oldState == EntityStates.PRE_START_INTRO:
            self.eSetViewpoint(BigWorld.camera().invViewMatrix)
            self.stopPreIntro()
            self.zoomInterpolationTime = CAMERA_MOVING_SPEED
        if state & EntityStates.GAME:
            CameraZoomStatsCollector.g_cameraZoomStatsCollector.allowProfiling(True)
            CameraZoomStatsCollector.g_cameraZoomStatsCollector.onChangeZoom(self.__curZoomState)
        if state & (EntityStates.DEAD | EntityStates.OUTRO):
            CameraZoomStatsCollector.g_cameraZoomStatsCollector.allowProfiling(False)
        if state == EntityStates.DESTROYED and oldState != EntityStates.DESTROYED_FALL:
            self.onReportPlayerDestruction({'killerID': BigWorld.player().id,
             'victimID': BigWorld.player().id})
            if CameraEffect.g_instance:
                CameraEffect.g_instance.onCameraEffect('DESTRUCTION')
        elif state == EntityStates.PRE_START_INTRO:
            import BattleReplay
            if Settings.g_instance.preIntroEnabled and not BattleReplay.isPlaying():
                self.__startPreIntro()
        elif state == EntityStates.OUTRO:
            self.__cbOutro = BigWorld.callback(OUTRO_FADEIN_DURATION, self.__startOutro)
        if state == EntityStates.OBSERVER:
            self.setEffectsEnabled(Settings.g_instance.cameraEffectsEnabled)
            if self.getState() != CameraState.DynamicSpectator:
                self.switchToSpectator()

    def onReportPlayerDestruction(self, killingInfo):
        victimId = killingInfo['victimID']
        if victimId == BigWorld.player().id:
            self.__curZoomPreset = CAMERA_ZOOM_PRESET.DEFAULT
            if self.__cameraStateMachine:
                self.__cameraStateMachine.reset()
            self.setState(CameraState.DestroyedFall, killingInfo['killerID'])

    def setEffectsEnabled(self, isEnabled):
        if self.__cam:
            self.__cam.effectController.setEnabled(isEnabled or EntityStates.inState(BigWorld.player(), EntityStates.OBSERVER))
        else:
            LOG_ERROR("Cannot change camera effects state, bacause AircraftCamera isn't created yet.")

    def setSniperModeEnabled(self, isEnabled):
        if self.__isInOverview:
            return
        if not isEnabled and self.isSniperMode:
            self.__switchSniperMode()
        self.__isSniperModeEnable = isEnabled

    def __onSniperModeKeyPressed(self, keyState):
        if self.__isInOverview:
            return
        if InputMapping.g_instance.getSwitchingStyle(InputMapping.CMD_SNIPER_CAMERA) == SWITCH_STYLES_BUTTONS.HOLD and self.isSniperMode and keyState:
            return
        if not self.isSniperMode and not keyState:
            return
        self.__switchSniperMode()

    def __switchSniperMode(self):
        prevStateObject = None
        prevState = self.__cameraStateMachine.getPrevState()
        if prevState and self.__isSniperModeEnable and self.isSniperMode:
            prevStateObject = self.__cameraStateMachine.getStateObject(prevState)
        if self.__isSniperModeEnable and (self.getStateObject().zoomPresent() or prevStateObject and prevStateObject.zoomPresent()):
            isSniper = not self.isSniperMode
            curZoomDataState = ZoomStates.Sniper if isSniper else ZoomStates.Normal
            self.__setZoom(curZoomDataState)
        return

    def isModelVisible(self):
        return self.__modelVisible

    def setZoomEnable(self, isEnable):
        """Tutorial/Pre-Intro"""
        self.__isZoomEnable = isEnable

    def isMouseHandled(self):
        state = self.getState()
        return state in (CameraState.Free,
         CameraState.Spectator,
         CameraState.DestroyedFall,
         CameraState.SuperFree,
         CameraState.ReplayFree)

    def processMouseEvent(self, event):
        if EntityStates.inState(BigWorld.player(), EntityStates.WAIT_START | EntityStates.CREATED):
            return
        if getattr(self.getStateObject(), 'isInOverview', False):
            self.__cameraStateMachine.updateStateAttr(self.getState(), 'onOverlookScroll', event.dz)
        elif not self.__cameraStateMachine.updateStateAttr(self.getState(), 'onMouseScroll', event.dz):
            stateInstance = self.getStateObject()
            if stateInstance and stateInstance.zoomPresent() and self.__isZoomEnable:
                if event.dz > 0 and self.__curZoomState != ZoomStates.Sniper:
                    self.__setZoom(ZoomStates.Sniper)
                elif event.dz < 0 and self.__curZoomState != ZoomStates.Normal:
                    self.__setZoom(ZoomStates.Normal)
        else:
            camStateStrategy = self.getStateStrategy()
            if hasattr(camStateStrategy, 'distance'):
                dist = self.getStateStrategy().distance
                self.eDistanceChanged(dist)

    def __applyZoomState(self):
        CameraZoomStatsCollector.g_cameraZoomStatsCollector.onChangeZoom(self.__curZoomState)
        self.__applyZoomStateFov(self.zoomInterpolationTime)
        self.__target.duration = self.zoomInterpolationTime
        self.__modelVisible = self.__context.entity.model and not self.curZoomData.hideModel
        self.__context.entity.setModelVisible(self.isModelVisible())
        if self.getState() in [CameraState.MouseCombat, CameraState.NormalCombat, CameraState.JoystickCombat]:
            zoomPosClose = self.__context.cameraSettings.zoomPresets[self.__curZoomPreset][0].position
            offset = self.__compositeOffset.target
            scale = min(1.0, abs(offset.z / zoomPosClose.z))
            self.__updateZoomCallback = BigWorld.callback(self.zoomInterpolationTime * 0.5 * scale, self.__onUpdateZoomCallback)
        elif self.getState() in [CameraState.MouseAssault,
         CameraState.NormalAssault,
         CameraState.JoystickAssault,
         CameraState.Bomber,
         CameraState.Gunner] + CameraState.SniperStates:
            self.__updateZoomCallback = BigWorld.callback(self.zoomInterpolationTime * 0.5, self.__onUpdateZoomCallback)
        self.__updateZoomDataPosition()
        self.__target.target = Math.Vector4(1.0, 1.0, 1.0, 1.0)
        self.__rotationX.target = math.radians(self.curZoomData.angle)
        if self.__cameraStateMachine.getState() is not None:
            self.getStateObject().onZoomIndexChanged(self.__curZoomState, self.curZoomData)
        self.eZoomStateChanged(self.__curZoomState)
        return

    def __onUpdateZoomCallback(self):
        if self.curZoomData:
            self.__modelVisible = not self.__context.entity.isDestroyed and self.__context.entity.inWorld and self.__context.entity.model and not self.curZoomData.hideModel
        if not self.__context.entity.isDestroyed and self.__context.entity.inWorld:
            self.__context.entity.setModelVisible(self.isModelVisible())

    def __cancelZoomCallback(self):
        if self.__updateZoomCallback is not None:
            BigWorld.cancelCallback(self.__updateZoomCallback)
            self.__updateZoomCallback = None
        return

    def __updateZoomDataPosition(self):
        if self.getState() is not None:
            stateObject = self.getStateObject()
            self.__zoomDataPosition = stateObject.getZoomDataPosition(self.curZoomData)
            destOffset = toVec4(self.__zoomDataPosition)
            self.__compositeOffset.target = destOffset
        return

    def __setZoom(self, zoomState = None, zoomPreset = None):
        if self.__context and (zoomState != ZoomStates.Sniper or not self.__isInOverview):
            import BattleReplay
            BattleReplay.g_replay.notifyZoomChange(zoomState, zoomPreset)
            if zoomState is None:
                zoomState = self.__curZoomState
            self.__lastZoomDataIdx = self.__curZoomState
            self.__curZoomState = zoomState
            if zoomPreset is not None:
                self.__curZoomPreset = zoomPreset
            if self.zoomPresent():
                self.__applyZoomState()
        return

    def resetToMinZoom(self):
        """TO REMOVE"""
        self.__setZoom(ZoomStates.Normal)

    def resetToZoomMin(self):
        zoomDataIdx = 0
        self.__backToCurrentZoomDataIdx = self.__curZoomState
        self.__setZoom(zoomDataIdx)

    def resetToBackZoom(self, ignoreZoomDataIdxList = []):
        if self.__backToCurrentZoomDataIdx is not None:
            if self.__backToCurrentZoomDataIdx not in ignoreZoomDataIdxList:
                self.__setZoom(self.__backToCurrentZoomDataIdx)
            cmd = InputMapping.CMD_SNIPER_CAMERA
            if InputMapping.g_instance.getSwitchingStyle(cmd) == SWITCH_STYLES_BUTTONS.SWITCH:
                if self.__backToCurrentZoomDataIdx == ZoomStates.Sniper and self.__curZoomState != ZoomStates.Sniper:
                    GameEnvironment.getInput().commandProcessor.getCommand(cmd).isFired = False
            self.__backToCurrentZoomDataIdx = None
        return

    def zoomPresent(self):
        if self.__cameraStateMachine is not None:
            return self.getStateObject().zoomPresent()
        else:
            return False

    def update(self):
        if self.getState() is not None and self.curZoomData is not None and EntityStates.inState(BigWorld.player(), EntityStates.GAME):
            self.__updateZoomDataPosition()
            self.getStateObject().onZoomIndexChanged(self.__curZoomState, self.curZoomData)
        return

    def __setAltMode(self, value):
        if value != self.__altMode:
            self.__altMode = value
            self.__cameraStateMachine.reEnterState()

    def isAltMode(self):
        return self.__altMode

    def updateStateAttr(self, stateName, attrName, attrValue):
        return self.__cameraStateMachine.updateStateAttr(stateName, attrName, attrValue)

    def onEnterSideView(self, stateData, cameraFreezed):
        if cameraFreezed:
            if self.getState() != CameraState.FreeFixable:
                self.setState(CameraState.FreeFixable)
            self.__cameraStateMachine.updateStateAttr(CameraState.FreeFixable, 'rotationPower', stateData[1])
        else:
            state = stateData[0]
            self.setState(state)

    def onLeaveSideView(self, stateData, cameraFreezed):
        if cameraFreezed:
            self.__cameraStateMachine.updateStateAttr(CameraState.FreeFixable, 'rotationPower', (0, 0))
        else:
            state = stateData[0]
            self.leaveState(state)

    def getFOV(self):
        return BigWorld.projection().fov

    def convertToVerticalFOV(self, horizontalFOV):
        return math.degrees(2.0 * math.atan(math.tan(math.radians(horizontalFOV) * 0.5) / BigWorld.projection().aspect))

    def __applyZoomStateFov(self, speed, forceCombatMode = False):
        defaultFov = math.radians(self.__context.cameraSettings.defaultFov) * self.curZoomData.fovPercent
        fov = defaultFov
        state = self.getState()
        if (forceCombatMode or state in [CameraState.MouseCombat, CameraState.NormalCombat, CameraState.JoystickCombat]) and self.__curZoomState != ZoomStates.Sniper:
            if speed == 0:
                self.setFov(fov)
            else:
                arenaStartTime = BigWorld.player().arenaStartTime
                serverTime = BigWorld.serverTime()
                curTime = int(round(arenaStartTime - serverTime))
                if not self.__preintroStopped and self.__class__.PRE_INTRO_CINEMATIC_START_TIME > curTime > self.__class__.PRE_INTRO_ZOOM_START_TIME:
                    speed = curTime * 0.5
                self.setFov(fov * self.__effectFOV)
        else:
            fov = defaultFov * self.__effectFOV
        self.setFov(fov, speed, self.__context.cameraSettings.fovRampCurvature)

    def setState(self, newState, params = None, replayMode = False):
        """
        @param newState: stateID
        """
        import EffectManager
        if newState not in cameraStatesWithZoom:
            CameraZoomStatsCollector.g_cameraZoomStatsCollector.onChangeZoom(None)
        import BattleReplay
        BattleReplay.g_replay.notifyCameraState(newState, True)
        if BattleReplay.isPlaying() and not replayMode:
            return
        else:
            prevState = self.getState()
            if prevState != CameraState.SuperFree and self.__cameraStateMachine:
                self.__cameraStateMachine.setState(newState, params)
                if newState == CameraState.Free:
                    EffectManager.g_instance.onFreeCameraStateChange(True)
                if newState in [CameraState.MouseCombat, CameraState.NormalCombat, CameraState.JoystickCombat]:
                    self.__applyZoomStateFov(self.zoomInterpolationTime)
                newStateObj = self.getStateObject()
                self.eStateChanged(newStateObj)
                self.eSetCrosshairVisible(newStateObj.crossHairVisible and not self.__isInOverview)
            return

    def setPrevState(self, newState):
        self.__cameraStateMachine.setPrevState(newState)

    def onHideBackendGraphics(self):
        """
        @return:
        """
        self.__checkSideCameraOnSwitchingInput()

    def leaveState(self, state = None):
        """
        @param state:
        @return:
        """
        import EffectManager
        if self.__cameraStateMachine:
            import BattleReplay
            BattleReplay.g_replay.notifyCameraState(state if state is not None else self.getState(), False)
            self.__cameraStateMachine.leaveState(state)
            if state == CameraState.Free:
                EffectManager.g_instance.onFreeCameraStateChange(False)
            if self.getState() in [CameraState.MouseCombat, CameraState.NormalCombat, CameraState.JoystickCombat]:
                self.__applyZoomStateFov(self.zoomInterpolationTime)
            newStateObj = self.getStateObject()
            self.eStateChanged(newStateObj)
            self.eSetCrosshairVisible(newStateObj.crossHairVisible and not self.__isInOverview)
        return

    def stateObject(self, state):
        """
        @param state: camera state object with  stateID==state
        @return:
        """
        if self.__cameraStateMachine:
            return self.__cameraStateMachine.getStateObject(state)

    def getStateObject(self):
        """
        @return: current camera object
        """
        return self.__cameraStateMachine.getCurStateObject()

    def getState(self):
        """
        @return: current camera stateID
        """
        if self.__cameraStateMachine:
            return self.__cameraStateMachine.getState()

    def getStateStrategy(self):
        """
        @return: current camera state strategy
        """
        stateObj = self.getStateObject()
        if stateObj:
            return stateObj.strategy

    @property
    def getDefualtStrategies(self):
        return self.__defaultStrategies

    def __checkSideCameraOnSwitchingInput(self):
        if self.getState() not in [CameraState.DestroyedFall,
         CameraState.Spectator,
         CameraState.SuperFree,
         CameraState.NormalCombat,
         CameraState.NormalAssault]:
            self.reset()

    def onFlyKeyBoardInputAllowed(self, flag, playerAvatar):
        if not flag and EntityStates.inState(playerAvatar, EntityStates.GAME):
            if self.getState() not in [CameraState.DebugCamera,
             CameraState.Spectator,
             CameraState.DestroyedFall,
             CameraState.SuperFree,
             CameraState.ReplayFree,
             CameraState.Gunner,
             CameraState.Bomber]:
                self.reset()

    def getAircraftCam(self):
        return self.__cam

    @property
    def debugMode(self):
        return self.__cam.isDebugEnabled

    @debugMode.setter
    def debugMode(self, value):
        self.__cam.isDebugEnabled = value

    @property
    def behaviorHorizon(self):
        return self.__behaviorHorizon

    @behaviorHorizon.setter
    def behaviorHorizon(self, value):
        self.__behaviorHorizon = value

    def getDistanceToSource(self):
        camera_pos = BigWorld.camera().position
        source_pos = Math.Matrix(self.__context.mainMatrixProvider).applyToOrigin()
        return (camera_pos - source_pos).length

    def getCurStateName(self):
        id = self.getState()
        for k, v in CameraState.__dict__.items():
            if v == id:
                return k

        return 'UNKNOWN_STATE'

    def setFov(self, newFov, duration = 0.0, curvature = 1.1):
        curStateObj = self.getStateStrategy()
        if curStateObj:
            if hasattr(curStateObj, 'setZoomStateFov'):
                curStateObj.setZoomStateFov(self.__curZoomState == ZoomStates.Sniper)
            else:
                curStateObj.defaultFov = newFov
        else:
            BigWorld.projection().rampFov(newFov, duration, curvature)

    def setPos(self, newPos):
        curState = self.getState()
        curStateObj = self.__cameraStateMachine.getStateObject(self.__cameraStateMachine.getState())
        if curState == CameraState.Left:
            self.__context.cameraSettings.leftCamPos = newPos
            curStateObj._setTransformation(self.__context.cameraSettings.leftCamPos, self.__context.cameraSettings.leftCamDir, Math.Vector3(0.0, 1.0, 0.0))
            curStateObj.reEnter()
        elif curState == CameraState.Right:
            self.__context.cameraSettings.rightCamPos = newPos
            curStateObj._setTransformation(self.__context.cameraSettings.rightCamPos, self.__context.cameraSettings.rightCamDir, Math.Vector3(0.0, 1.0, 0.0))
            curStateObj.reEnter()
        elif curState == CameraState.Top:
            self.__context.cameraSettings.topCamPos = newPos
            curStateObj._setTransformation(self.__context.cameraSettings.topCamPos, self.__context.cameraSettings.topCamDir, Math.Vector3(0.0, 0.0, -1.0))
            curStateObj.reEnter()
        elif curState == CameraState.Bottom:
            self.__context.cameraSettings.bottomCamPos = newPos
            curStateObj._setTransformation(self.__context.cameraSettings.bottomCamPos, self.__context.cameraSettings.bottomCamDir, Math.Vector3(0.0, 0.0, 1.0))
            curStateObj.reEnter()
        elif curState in (CameraState.Free, CameraState.ReplayFree):
            pass
        elif curState == CameraState.SuperFree:
            pass
        else:
            self.curZoomData.position = newPos

    def getPos(self):
        curState = self.getState()
        if curState == CameraState.Left:
            return self.__context.cameraSettings.leftCamPos
        if curState == CameraState.Right:
            return self.__context.cameraSettings.rightCamPos
        if curState == CameraState.Top:
            return self.__context.cameraSettings.topCamPos
        if curState == CameraState.Bottom:
            return self.__context.cameraSettings.bottomCamPos
        if curState in (CameraState.Free, CameraState.ReplayFree):
            return self.__getCurZoomlessOffset().length
        if curState == CameraState.SuperFree:
            return BigWorld.dcursor().matrix
        return self.__zoomDataPosition

    def setCameraPosQA(self, x, y, z):
        m = Math.Matrix(BigWorld.player().matrix)
        y = -y if z > 0 else y
        x = -x
        v = Math.Vector3(x, y, z)
        m1 = Math.Matrix()
        m1.setIdentity()
        m1.lookAt((0, 0, 0), v, (0, 1, 0))
        m.setRotateYPR(Math.Vector3(m.yaw + m1.yaw, m.pitch + m1.pitch, m.roll))
        self.__context.mainMatrixProvider = m
        self.setState(CameraState.SuperFree)
        strategy = self.getStateStrategy()
        strategy.distance = v.length

    def resetCameraPosQA(self):
        self.leaveState(CameraState.SuperFree)
        self.__context.mainMatrixProvider = self.__mainMatrixProvider

    @property
    def isInOverlook(self):
        return self.__isInOverview

    def turnOverLook(self, value):
        """
        @param value:  boot
        triggering OverLook (BackView) camera
        """
        if self.__isInOverview != value:
            if value:
                self.resetToZoomMin()
                self.applyInputAxis(FREE_HORIZONTAL_CAM, 1.0)
            else:
                self.resetToBackZoom()
                self.applyInputAxis(FREE_HORIZONTAL_CAM, 0.0)
            self.eSetCrosshairVisible(not value)

    def applyInputAxis(self, axis, value):
        validStrategy = (self.__defaultStrategies['CameraStrategyMouse'], self.__defaultStrategies['CameraStrategyNormal'])
        for strategy in validStrategy:
            strategy.handleAxisInput(axis, value)
            if axis in (FREE_VERTICAL_CAM, FREE_HORIZONTAL_CAM):
                self.__isInOverview = value != 0.0
                newStateObj = self.getStateObject()
                self.eSetCrosshairVisible(newStateObj.crossHairVisible and not self.__isInOverview)