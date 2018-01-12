# Embedded file name: scripts/client/audio/SoundObjects/AircraftEngineSound.py
from WwiseGameObject import WwiseGameObject, GS, WwiseGameObjectFactory
import BigWorld
import math
from consts import WEP_ENABLE_TEMPERATURE, ENGINE_WORK_INTERVAL, WEP_DISABLE_TEMPERATURE, PLANE_TYPE, BATTLE_MODE
import GameEnvironment
import Settings
from EntityHelpers import EntityStates
import db.DBLogic
from _preparedBattleData_db import preparedBattleData
from audio.AKTunes import RTPC_Altitude_Update_Interval, RTPC_ListenerAngle_Update_Interval, RTPC_Zoomstate_MAX, RTPC_Aircraft_Camera_Zoomstate_VDT, RTPC_Aircraft_Engine_RPM_VDT, RTPC_Aircraft_Engine_RPM_MAX, RTPC_Aircraft_Engine_Boost_VDT, RTPC_ListenerAngle_VDT, RTPC_AircraftPitch_VDT, RTPC_AircraftRoll_VDT, FREECAM_DIST_STEP, RTPC_Altitude_Update_Freq, SOUND_CALLBACKS_PER_TICK, SOUND_CALLBACKS_VCD
from audio.AKConsts import ENGINE_OVERHEAT, PartState, SOUND_MODES, CURRENT_PLAYER_MODE, ENGINE_POV_STATES, SOUND_OBJECT_TYPES, SOUND_CALLBACK_QUEUE_TYPES, RTPC_AIRCRAFT_HEIGHT, RTPC_AIRCRAFT_SPEED
from audio.DopplerEffect import DopplerEffect
from audio.SoundModes import SoundModeStrategyBase, SoundModeHandler
from audio.SoundObjectSettings import SoundObjectSettings
from audio.SoundBanksManager import SoundBanksManager
from audio.SoundUpdateManager import SoundUpdateManager, SoundUpdateQueue

class AircraftEngineSound(WwiseGameObject):
    NPC_DESTROYED_EVENT = 'Play_NPC_engine_destroyed'
    PLAYER_DESTROYED_EVENT = 'Play_engine_destroyed'
    AIRCRAFT_PLANE_TYPE_SWITCH = 'SWITCH_Aircraft_Plain_Type'
    ENGINE_POV_SWITCH = 'sw_engine_pov'

    def __init__(self, name, cid, node, entityID = 0):
        WwiseGameObject.__init__(self, name, cid, node, entityID=entityID)

    def _onStateChanged(self, avatar, old, new):
        if old == new:
            return
        if new == EntityStates.DESTROYED:
            self.stopAll()
        if avatar.id == BigWorld.player().id:
            return
        if new == EntityStates.DESTROYED_FALL:
            self.postEvent(AircraftEngineSound.NPC_DESTROYED_EVENT)


class AircraftEngineStrategy(SoundModeStrategyBase):

    def __init__(self, avatarID, soundObject):
        self._soundSet = soundObject.soundSet
        self._isPlayer = BigWorld.player().id == avatarID
        self._alive = self._isPlayer
        self._playingState = None
        self._avatarID = avatarID
        SoundModeStrategyBase.__init__(self, avatarID, soundObject)
        soundUpdateManager = SoundUpdateManager.instance()
        if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE):
            queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE, SOUND_CALLBACKS_PER_TICK.AIRCRAFT_SPEED_AND_ALTITUDE)
            soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE, queue)
        soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).append(self.__aircraftEngineSpeedUpdate)
        return

    def __del__(self):
        soundUpdateManager = SoundUpdateManager.instance()
        if soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE):
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).remove(self.__aircraftEngineSpeedUpdate)

    def __aircraftEngineSpeedUpdate(self):
        entity = BigWorld.entities.get(self._avatarID)
        entityGID = entity.globalID
        battleData = preparedBattleData.get(entityGID, None)
        if battleData:
            speedometer = battleData.speedometer
            if speedometer:
                maxSpeedPercentRatio = 100.0 / speedometer.diveSpeed
                speed = maxSpeedPercentRatio * entity.getSpeed()
                self._soundObject.wwiseGameObject.setRTPC(RTPC_AIRCRAFT_SPEED, speed, SOUND_CALLBACKS_VCD.AIRCRAFT_SPEED_AND_ALTITUDE)
        return

    def _registerEventsBase(self):
        GS().eOnBattleEnd += self.stop
        self._registerEvents()

    def _registerEvents(self):
        pass

    def _clearEventsBase(self):
        GS().eOnBattleEnd -= self.stop
        self._clearEvents()

    def _clearEvents(self):
        pass

    def _onAvatarLeaveWorld(self):
        pass

    def stop(self):
        self._soundObject.wwiseGameObject.stopAll(500)
        self._playingState = None
        self._stop()
        return

    def _stop(self):
        pass

    def play(self, state = 'Main'):
        if not self._alive:
            return
        if self._playingState == state:
            return
        tag = self._getTag(state)
        if state == 'Main':
            self._soundObject.wwiseGameObject.setSwitch(AircraftEngineSound.ENGINE_POV_SWITCH, self._getSwitch())
        if tag in self._soundSet:
            self._soundObject.wwiseGameObject.postEvent(self._soundSet[tag])
            self._playingState = state

    def _getTag(self, state):
        raise False or AssertionError('override getTag')

    def _getSwitch(self):
        raise False or AssertionError('override getSwitch')

    def onAvatarEnterWorld(self, avatarID):
        if self._avatarID == avatarID:
            self._alive = True
            self.play()


class Overheat:

    def __init__(self, event, wwiseGameObject, startTemperature):
        self.__event = event
        self.__wwiseGameObject = wwiseGameObject
        self.__startTemperature = startTemperature
        self.__state = ENGINE_OVERHEAT.READY
        self.__oneshotCB = None
        return

    def __start(self):
        if self.__state == ENGINE_OVERHEAT.READY:
            self.__wwiseGameObject.postEvent(self.__event)
            self.__state = ENGINE_OVERHEAT.PROCESS

    def end(self):
        self.stop()
        self.oneshot()
        self.__wwiseGameObject.setRTPC(ENGINE_OVERHEAT.RTPC_ENGINE_TEMPERATURE, 0)
        self.__state = ENGINE_OVERHEAT.END

    def reset(self):
        self.stop()
        self.__state = ENGINE_OVERHEAT.READY

    def stop(self):
        if self.__state == ENGINE_OVERHEAT.PROCESS:
            self.__wwiseGameObject.postEvent(str(self.__event).replace('_start', '_end'))

    def updateTemperature(self, currentTemperature, isForsage):
        if currentTemperature < self.__startTemperature:
            if self.__state != ENGINE_OVERHEAT.READY:
                self.reset()
        elif self.__state == ENGINE_OVERHEAT.PROCESS:
            rtpc_value = (currentTemperature - self.__startTemperature) / (WEP_DISABLE_TEMPERATURE - self.__startTemperature) * 100
            self.__wwiseGameObject.setRTPC(ENGINE_OVERHEAT.RTPC_ENGINE_TEMPERATURE, rtpc_value)
        elif self.__state == ENGINE_OVERHEAT.READY:
            self.__start()
        elif self.__state == ENGINE_OVERHEAT.END:
            if isForsage:
                self.oneshot()

    def oneshot(self):
        if not self.__oneshotCB:
            self.__oneshotCB = BigWorld.callback(ENGINE_OVERHEAT.COOLDOWN_TIME, self.clearCB)
            self.__wwiseGameObject.postEvent(str(self.__event).replace('_start', '_oneshot'))

    def clearCB(self):
        if self.__oneshotCB:
            BigWorld.cancelCallback(self.__oneshotCB)
            self.__oneshotCB = None
        return


class AircraftEngineStrategyPlayerBase(AircraftEngineStrategy):
    """
    Base class for main and reverse engine player sound
    """

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategy.__init__(self, avatarID, soundObject)
        self._boost = 0.0
        self._damaged = False
        self.__RTPC_init()
        soundUpdateManager = SoundUpdateManager.instance()
        if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, SOUND_CALLBACKS_PER_TICK.PLAYER_GENERAL)
            soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, queue)
        soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL).append(self.__aircraftEngineUpdateAngles)
        soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).append(self.__aircraftEngineAltitudeUpdate)

    def __del__(self):
        AircraftEngineStrategy.__del__(self)
        soundUpdateManager = SoundUpdateManager.instance()
        if soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL).remove(self.__aircraftEngineUpdateAngles)
        if soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE):
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).remove(self.__aircraftEngineAltitudeUpdate)

    @property
    def soundModeID(self):
        return SOUND_MODES.PLAYER

    def _registerEvents(self):
        BigWorld.player().eUpdateForce += self.__onForce
        BigWorld.player().onStateChanged += self.__onPlayerStateChanged
        BigWorld.player().eUpdateSpectator += self.__onSpectator
        BigWorld.player().eArenaLoaded += self.__onArenaLoaded
        cam = GameEnvironment.getCamera()
        cam.eZoomStateChanged += self.__onZoomStateChanged
        cam.eDistanceChanged += self.__onDistanceChanged
        GS().eLoadingScreenClosed += self.play

    def _clearEvents(self):
        BigWorld.player().eUpdateForce -= self.__onForce
        BigWorld.player().onStateChanged -= self.__onPlayerStateChanged
        BigWorld.player().eUpdateSpectator -= self.__onSpectator
        BigWorld.player().eArenaLoaded -= self.__onArenaLoaded
        cam = GameEnvironment.getCamera()
        cam.eZoomStateChanged -= self.__onZoomStateChanged
        cam.eDistanceChanged -= self.__onDistanceChanged
        GS().eLoadingScreenClosed -= self.play

    def _stop(self):
        self._stopOverheat()
        self._stopDamageFX()

    def _stopOverheat(self):
        pass

    def _getTag(self, state):
        return '{0}{1}'.format('PlayerEngine', state)

    def _getSwitch(self):
        return ENGINE_POV_STATES.MAIN

    def __aircraftEngineUpdateAngles(self):
        if not self._alive:
            return
        entity = BigWorld.player()
        if hasattr(entity.filter, 'velocity'):
            player = entity.filter.velocity.getNormalized()
            camera = BigWorld.camera().direction.getNormalized()
            self._soundObject.wwiseGameObject.setRTPC('RTPC_Aircraft_Listener_Angle', 90 * (1 - camera.dot(player)), SOUND_CALLBACKS_VCD.PLAYER_GENERAL)
            self._soundObject.wwiseGameObject.setRtpcWithGlobal('RTPC_Aircraft_Nosedive_Angle', -math.degrees(entity.pitch), SOUND_CALLBACKS_VCD.PLAYER_GENERAL)
            self._soundObject.wwiseGameObject.setRtpcWithGlobal('RTPC_Aircraft_Body_Roll', math.fabs(math.degrees(entity.roll)), SOUND_CALLBACKS_VCD.PLAYER_GENERAL)

    def __aircraftEngineAltitudeUpdate(self):
        entity = BigWorld.entities.get(self._avatarID)
        height = entity.altitudeAboveObstacle
        self._soundObject.wwiseGameObject.setRTPC(RTPC_AIRCRAFT_HEIGHT, height, SOUND_CALLBACKS_VCD.AIRCRAFT_SPEED_AND_ALTITUDE)

    def __RTPC_init(self):
        self._RTPC_Engine_RPM(0, 0)
        self._RTPC_Engine_Boost_Fixed(False)
        cam = GameEnvironment.getCamera()
        self.__onZoomStateChanged(RTPC_Zoomstate_MAX if cam.isSniperMode else Settings.g_instance.camZoomIndex)

    def _RTPC_Engine_RPM(self, force, vdt = RTPC_Aircraft_Engine_RPM_VDT):
        if self._damaged:
            return
        lowBoundF = 4.0 if force < 0 else 2.0
        rpm = (1.0 + force) * (RTPC_Aircraft_Engine_RPM_MAX / 4.0) + RTPC_Aircraft_Engine_RPM_MAX / lowBoundF
        self._soundObject.wwiseGameObject.setRTPC('RTPC_Aircraft_Engine_RPM', rpm, vdt)

    def _RTPC_Engine_Boost_Fixed(self, forsage):
        if self._boost > 0.0 and forsage:
            return
        boost = 1.0 if forsage else 0.0
        tag = 'RtpcEngineBoost{0}'.format('Attack' if forsage else 'Release')
        fdt = float(self._soundSet.get(tag, -1.0))
        idt = int(1000.0 * fdt)
        self._soundObject.wwiseGameObject.setRtpcWithGlobal('RTPC_Aircraft_Engine_Boost', boost, idt if idt > 0 else RTPC_Aircraft_Engine_Boost_VDT)
        self._boost = boost

    def __onZoomStateChanged(self, val):
        self.__RTPC_Zoomstate(RTPC_Zoomstate_MAX - val)

    def __RTPC_Zoomstate(self, val):
        self._soundObject.wwiseGameObject.setRtpcWithGlobal('RTPC_Aircraft_Camera_Zoomstate', min(max(0, val), RTPC_Zoomstate_MAX), RTPC_Aircraft_Camera_Zoomstate_VDT)

    def __onForce(self, F):
        if BigWorld.player().autopilot:
            return
        self._RTPC_Engine_RPM(F)

    def _onPlayerDestroyedFall(self):
        pass

    def __onPlayerStateChanged(self, oldState, state):
        if state & EntityStates.DESTROYED_FALL:
            self._onPlayerDestroyedFall()
        elif state & EntityStates.DESTROYED:
            self._onDestroySoundObject()

    def _onDestroySoundObject(self):
        if self._soundObject and self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject.postEvent('Stop_avatar_destroy')
        self._stopDamageFX()
        self._alive = False

    def __onSpectator(self, target):
        if not self._alive:
            return
        self._stopDamageFX()
        self._alive = False

    def _stopDamageFX(self):
        pass

    def __onDistanceChanged(self, d):
        self.__RTPC_Zoomstate(math.floor(d / FREECAM_DIST_STEP))

    def __onArenaLoaded(self):
        self.play()


class AircraftEngineStrategyPlayer(AircraftEngineStrategyPlayerBase):
    """
    This class contains some addition functions, which is not actual in reverse engine
    """

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategyPlayerBase.__init__(self, avatarID, soundObject)
        self.__overheat = Overheat(self._soundSet.get('PlayerEngineOverheated'), self._soundObject.wwiseGameObject, WEP_ENABLE_TEMPERATURE + ENGINE_WORK_INTERVAL * float(self._soundSet['OverheatRelativeStart']))
        self.__currentEngineSMSwitch = None
        return

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = AircraftEngineSound('EngineSoundPlayer-{0}'.format(self._avatarID), self._cid, self._node, self._avatarID)
            if BigWorld.player().clientIsReady:
                self.play()

    def _registerEvents(self):
        AircraftEngineStrategyPlayerBase._registerEvents(self)
        BigWorld.player().eUpdateEngineTemperature += self.__updateEngineTemperature
        BigWorld.player().eEngineOverheat += self.__onEngineOverheat
        GameEnvironment.g_instance.ePartStateChanging += self.__onPartState
        GameEnvironment.getInput().eBattleModeChange += self.__onBattleModeChange

    def _clearEvents(self):
        AircraftEngineStrategyPlayerBase._clearEvents(self)
        BigWorld.player().eUpdateEngineTemperature -= self.__updateEngineTemperature
        BigWorld.player().eEngineOverheat -= self.__onEngineOverheat
        GameEnvironment.g_instance.ePartStateChanging -= self.__onPartState
        GameEnvironment.getInput().eBattleModeChange -= self.__onBattleModeChange

    def _onPlayerDestroyedFall(self):
        planeType = self._soundSet['PlainType']
        self._soundObject.wwiseGameObject.setSwitch(AircraftEngineSound.AIRCRAFT_PLANE_TYPE_SWITCH, planeType)
        event = self._soundSet[self._getTag('Main')].replace('_start', '_stop')
        self._soundObject.wwiseGameObject.postEvent(event)
        self._stopDamageFX()

    def __updateEngineTemperature(self, engineTemperature, wepWorkTime, isWarEmergencyPower):
        if BigWorld.player().autopilot:
            self._stopOverheat()
        elif self.__overheat:
            self.__overheat.updateTemperature(engineTemperature, isWarEmergencyPower)
        self._RTPC_Engine_Boost_Fixed(isWarEmergencyPower)

    def _stopOverheat(self):
        self.__overheat.stop()

    def __onEngineOverheat(self):
        self._boost = 0
        self._soundObject.wwiseGameObject.setRtpcWithGlobal('RTPC_Aircraft_Engine_Boost', self._boost, RTPC_Aircraft_Engine_Boost_VDT)
        if BigWorld.player().autopilot:
            return
        if self.__overheat:
            self.__overheat.end()

    def __onPartState(self, name, stateID, position, entityID):
        if not self._alive:
            return
        if self._avatarID != entityID:
            return
        if name == 'Engine':
            if not self._damaged and stateID in [PartState.Destructed]:
                self.play('Damaged')
                self._damaged = True
                self._soundObject.wwiseGameObject.setRTPC('RTPC_Aircraft_Engine_RPM', 0.0, RTPC_Aircraft_Engine_RPM_VDT)
            elif self._damaged and stateID in [PartState.Repaired,
             PartState.Normal,
             PartState.RepairedPartly,
             PartState.Damaged]:
                self._stopDamageFX()

    def _stopDamageFX(self):
        if not self._damaged:
            return
        else:
            ev = self._soundSet['PlayerEngineDamaged']
            self._soundObject.wwiseGameObject.postEvent(str(ev).replace('_start', '_stop'))
            if self._playingState == 'Damaged':
                self._playingState = None
            self._damaged = False
            self._RTPC_Engine_RPM(0.0)
            return

    def _stop(self):
        AircraftEngineStrategyPlayerBase._stop(self)
        self._clearCB()

    def _clearCB(self):
        self.__overheat.clearCB()

    def __onBattleModeChange(self, battleMode):
        if battleMode == BATTLE_MODE.ASSAULT_MODE:
            self.__setSniperModeSwitch(ENGINE_POV_STATES.BOMBING_MODE)
        elif battleMode == BATTLE_MODE.GUNNER_MODE:
            self.__setSniperModeSwitch(ENGINE_POV_STATES.GUNNER_MODE)
        elif battleMode == BATTLE_MODE.SNIPER_MODE:
            if BigWorld.player().planeType == PLANE_TYPE.BOMBER:
                self.__setSniperModeSwitch(ENGINE_POV_STATES.MAIN)
            else:
                self.__setSniperModeSwitch(ENGINE_POV_STATES.SNIPER_MODE)
        else:
            self.__setSniperModeSwitch(ENGINE_POV_STATES.MAIN)

    def __setSniperModeSwitch(self, state):
        if self.__currentEngineSMSwitch != state:
            self.__currentEngineSMSwitch = state
            self._soundObject.wwiseGameObject.setSwitch(AircraftEngineSound.ENGINE_POV_SWITCH, state)


class AircraftEngineStrategyAvatar(AircraftEngineStrategy):

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategy.__init__(self, avatarID, soundObject)
        self.onAvatarEnterWorld(avatarID)
        soundUpdateManager = SoundUpdateManager.instance()
        if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, SOUND_CALLBACKS_PER_TICK.PLAYER_GENERAL)
            soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, queue)
        soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).append(self.__aircraftEngineAltitudeUpdate)

    def __del__(self):
        AircraftEngineStrategy.__del__(self)
        soundUpdateManager = SoundUpdateManager.instance()
        if soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE):
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRCRAFT_SPEED_AND_ALTITUDE).remove(self.__aircraftEngineAltitudeUpdate)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = AircraftEngineSound('EngineSoundNPC-{0}'.format(self._avatarID), self._cid, self._node)
            if not self._avatarID == BigWorld.player().id:
                DopplerEffect.instance().add(self._avatarID, self._soundObject.wwiseGameObject)

    @property
    def soundModeID(self):
        return SOUND_MODES.AVATAR

    def _getTag(self, state):
        return '{0}{1}'.format('NPCEngine', state)

    def _getSwitch(self):
        return ENGINE_POV_STATES.NPC

    def _onDestroySoundObject(self):
        DopplerEffect.instance().discard(self._avatarID, self._soundObject.wwiseGameObject)

    def __aircraftEngineAltitudeUpdate(self):
        entity = BigWorld.entities.get(self._avatarID)
        height = entity.getAltitudeAboveWaterLevel()
        self._soundObject.wwiseGameObject.setRTPC(RTPC_AIRCRAFT_HEIGHT, height, SOUND_CALLBACKS_VCD.AIRCRAFT_SPEED_AND_ALTITUDE)


class AircraftEngineStrategySpectator(AircraftEngineStrategy):

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategy.__init__(self, avatarID, soundObject)
        self.onAvatarEnterWorld(avatarID)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = AircraftEngineSound('EngineSoundSpectator-{0}'.format(self._avatarID), self._cid, self._node)
            self._soundObject.wwiseGameObject.setSwitch(SOUND_MODES.SWITCH, SOUND_MODES.WWISE[SOUND_MODES.SPECTATOR])

    @property
    def soundModeID(self):
        return SOUND_MODES.SPECTATOR

    def _getTag(self, state):
        return '{0}{1}'.format('NPCEngine', state)

    def _getSwitch(self):
        return ENGINE_POV_STATES.NPC


g_factory = None

class AircraftEngineSoundFactory(WwiseGameObjectFactory):

    def __init__(self):
        self.__soundStrategies = {SOUND_MODES.PLAYER: AircraftEngineStrategyPlayer,
         SOUND_MODES.AVATAR: AircraftEngineStrategyAvatar,
         SOUND_MODES.SPECTATOR: AircraftEngineStrategySpectator}
        self.__soundBanksManager = SoundBanksManager.instance()

    def createPlayer(self, so):
        player = BigWorld.player()
        soundController = player.controllers.get('soundController', None)

        def onBankLoaded():
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.ENGINE].start()

        if soundController and SOUND_OBJECT_TYPES.ENGINE not in soundController.soundModeHandlers:
            bank = so.soundSet['SoundBank']
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.ENGINE] = SoundModeHandler(player.id, so, self.__soundStrategies, CURRENT_PLAYER_MODE, autoStart=False)
            self.__soundBanksManager.loadBankAndAttachToCase(BigWorld.player().id, bank, onBankLoaded, self.__soundBanksManager.REFS_COUNTING_ENABLE)
        return

    def createAvatar(self, avatar, so):
        soundController = avatar.controllers.get('soundController', None)

        def onBankLoaded():
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.ENGINE].start()

        if soundController and SOUND_OBJECT_TYPES.ENGINE not in soundController.soundModeHandlers:
            bank = so.soundSet['SoundBankNPC']
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.ENGINE] = SoundModeHandler(avatar.id, so, self.__soundStrategies, SOUND_MODES.AVATAR, autoStart=False)
            self.__soundBanksManager.loadBankAndAttachToCase(avatar.id, bank, onBankLoaded, self.__soundBanksManager.REFS_COUNTING_ENABLE)
        return

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = AircraftEngineSoundFactory()
        return g_factory

    @staticmethod
    def getSoundObjectSettings(data):
        isPlayer = data['isPlayer']
        soundObjects = data['soundObjects']
        context = data['context']
        info = data['info']
        so = SoundObjectSettings()
        so.mountPoint = info.mointPoint
        engineSet = db.DBLogic.g_instance.getAircraftEngineSet('Default')
        engineSet.update(db.DBLogic.g_instance.getAircraftEngineSet(info.engineSet))
        so.soundSet = GS().findLoadSet(engineSet, isPlayer, False, False, ['OverheatRelativeStart',
         'RtpcEngineBoostAttack',
         'RtpcEngineBoostRelease',
         'PlainType',
         'SoundBank',
         'SoundBankNPC'])
        so.factory = AircraftEngineSoundFactory.instance()
        so.context = context
        soundObjects[SOUND_OBJECT_TYPES.ENGINE] = so