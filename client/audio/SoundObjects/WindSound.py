# Embedded file name: scripts/client/audio/SoundObjects/WindSound.py
from WwiseGameObject import WwiseGameObject, GS, WwiseGameObjectFactory
import db.DBLogic
import BigWorld
import GameEnvironment
from audio.AKTunes import RTPC_Wind_Update_Interval, SOUND_CALLBACKS_PER_TICK, SOUND_CALLBACKS_VCD
from audio.AKConsts import SOUND_MODES, CURRENT_PLAYER_MODE, WIND_SOUND, SOUND_OBJECT_TYPES, SOUND_CALLBACK_QUEUE_TYPES, SOUND_BANKS, SOUND_CASES
from audio.SoundModes import SoundModeStrategyBase, SoundModeHandler
from MathExt import clamp
import math
from audio.SoundObjectSettings import SoundObjectSettings
from EntityHelpers import EntityStates
from audio.SoundUpdateManager import SoundUpdateManager, SoundUpdateQueue
from audio.SoundBanksManager import SoundBanksManager
import audio.debug

class WindSound(WwiseGameObject):

    def __init__(self, name, cid, node):
        WwiseGameObject.__init__(self, name, cid, node)

    def convPlay2StopEvent(self, playEvent):
        return playEvent.replace('Play_', 'Stop_')


class WindSoundStrategy(SoundModeStrategyBase):

    def __init__(self, avatarID, soundObject):
        self._windDB = db.DBLogic.g_instance.getWindParameters()
        self.__avatar = BigWorld.entities.get(avatarID)
        self.__avatarID = avatarID
        self.__avatarDiveSpeed = self.__avatar.settings.airplane.flightModel.hull[0].diveSpeed
        self.__avatarStallSpeed = self.__avatar.settings.airplane.flightModel.hull[0].stallSpeed
        self.__spectatorMode = False
        self.__currentStopEvent = None
        self._isPlayer = self.__avatar.id == BigWorld.player().id
        self.__finished = None
        SoundModeStrategyBase.__init__(self, avatarID, soundObject)
        if self.__isLoading():
            self._startLogic(WIND_SOUND.EVENT.LOADIND, False)
        else:
            self._generateStartEvent()
        return

    def __del__(self):
        soundUpdateQueue = SoundUpdateManager.instance().getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL)
        if soundUpdateQueue:
            soundUpdateQueue.remove(self.__updateWindSoundListenerAngle)
            soundUpdateQueue.remove(self.__updateWindSoundCriticalLandscape)
            soundUpdateQueue.remove(self.__updateWindSoundCriticalManeuvers)
            soundUpdateQueue.remove(self.__updateWindSoundAircraftSpeed)

    def __isLoading(self):
        return not BigWorld.player().clientIsReady

    def _startLogic(self, event, inProcess = True):
        if self.__currentStopEvent:
            self._soundObject.wwiseGameObject.postEvent(self.__currentStopEvent)
        self._soundObject.wwiseGameObject.postEvent(event)
        self.__currentStopEvent = self._soundObject.wwiseGameObject.convPlay2StopEvent(event)
        self.__inProcess = inProcess
        soundUpdateManager = SoundUpdateManager.instance()
        if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, SOUND_CALLBACKS_PER_TICK.PLAYER_GENERAL)
            soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, queue)
        player_general_queue = soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL)
        player_general_queue.append(self.__updateWindSoundListenerAngle)
        player_general_queue.append(self.__updateWindSoundCriticalLandscape)
        player_general_queue.append(self.__updateWindSoundCriticalManeuvers)

    def _destroySoundObject(self):
        if self._soundObject.wwiseGameObject:
            if self.__currentStopEvent:
                self._soundObject.wwiseGameObject.postEvent(self.__currentStopEvent)
                self.__currentStopEvent = None
            else:
                self._soundObject.wwiseGameObject.stopAll(self._windDB.onDestroyFadeTime, True)
        self.__inProcess = False
        self._soundObject.wwiseGameObject = None
        self._onDestroySoundObject()
        return

    def __updateWindSoundAircraftSpeed(self):
        self.__avatarSpeed = self.__avatar.getSpeed()
        param = (self.__avatarSpeed - self.__avatarStallSpeed) / (self.__avatarDiveSpeed - self.__avatarStallSpeed) * 100
        RTPC_Wind_Aircraft_Speed = clamp(0, param, 100)
        self._soundObject.wwiseGameObject.setRTPC(WIND_SOUND.RTPC.WIND_AIRCRAFT_SPEED, RTPC_Wind_Aircraft_Speed, SOUND_CALLBACKS_VCD.PLAYER_GENERAL)

    def __updatePreparations(self):
        self.__avatar = BigWorld.entities.get(self.__avatarID, None)
        if not self.__inProcess or not self.__avatar or EntityStates.inState(self.__avatar, EntityStates.DESTROYED):
            return False
        else:
            return True

    def __updateWindSoundListenerAngle(self):
        if not self.__updatePreparations():
            return
        avatar = self.__avatar.getWorldVector().getNormalized()
        camera = BigWorld.camera().direction.getNormalized()
        angle = 90 * (1 - camera.dot(avatar))
        self._soundObject.wwiseGameObject.setRTPC(WIND_SOUND.RTPC.AIRCRAFT_LISTENER_ANGLE, angle, SOUND_CALLBACKS_VCD.PLAYER_GENERAL)
        if audio.debug.IS_AUDIO_DEBUG:
            audio.debug.SHOW_DEBUG_OBJ('Aircraft_Listener_Angle', angle, group='WindSound')

    def __updateWindSoundCriticalLandscape(self):
        if not self.__updatePreparations():
            return
        height = self.__avatar.getAltitudeAboveObstacle()
        top = self._windDB.altitudeTop
        bottom = self._windDB.altitudeBottom
        value = (1 - (height - bottom) / (top - bottom)) * 100
        self._soundObject.wwiseGameObject.setRTPC(WIND_SOUND.RTPC.CRITICAL_LANDSCAPE, clamp(0, value, 100), SOUND_CALLBACKS_VCD.PLAYER_GENERAL)

    def __updateWindSoundCriticalManeuvers(self):
        if not self.__updatePreparations():
            return
        avatarWorldVector = self.__avatar.getWorldVector()
        avatarAxisZ = self.__avatar.getRotation().getAxisZ()
        angle = math.degrees(avatarWorldVector.angle(avatarAxisZ))
        top = self._windDB.maneuversAngleTop
        bottom = self._windDB.maneuversAngleBottom
        value = (angle - bottom) / (top - bottom) * 100
        self._soundObject.wwiseGameObject.setRTPC(WIND_SOUND.RTPC.CRITICAL_MANEUVERS, clamp(0, value, 100))

    def _registerEventsBase(self):
        player = BigWorld.player()
        if self.__isLoading():
            player.eArenaLoaded += self._generateStartEvent
        player.onStateChanged += self.__onPlayerStateChanged

    def _clearEventsBase(self):
        player = BigWorld.player()
        player.eArenaLoaded -= self._generateStartEvent
        player.onStateChanged -= self.__onPlayerStateChanged

    def __onPlayerStateChanged(self, oldState, state):
        if state == EntityStates.GAME:
            soundUpdateManager = SoundUpdateManager.instance()
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL).append(self.__updateWindSoundAircraftSpeed)

    def _generateStartEvent(self):
        pass

    def _finishBase(self):
        if not self.__finished:
            self.__finished = True
            self._clearEventsBase()


class WindSoundStrategyPlayer(WindSoundStrategy):

    class CameraInfo:

        def __init__(self):
            self.camera = None
            self.direction = None
            self.ticksDelay = None
            self.ticksCounter = None
            return

    def __init__(self, avatarID, soundObject):
        self.__cameraInfo = WindSoundStrategyPlayer.CameraInfo()
        self.__cameraInfo.camera = BigWorld.camera()
        self.__cameraInfo.direction = self.__cameraInfo.camera.direction
        self.__cameraInfo.ticksDelay = 2
        self.__cameraInfo.ticksCounter = 0
        WindSoundStrategy.__init__(self, avatarID, soundObject)
        soundUpdateManager = SoundUpdateManager.instance()
        if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, SOUND_CALLBACKS_PER_TICK.PLAYER_GENERAL)
            soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL, queue)
        soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL).append(self.__updateCameraSpeed)

    def __del__(self):
        WindSoundStrategy.__del__(self)
        soundUpdateManager = SoundUpdateManager.instance()
        if soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL):
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.PLAYER_GENERAL).remove(self.__updateCameraSpeed)

    def _onDestroySoundObject(self):
        self.__cameraInfo = None
        return

    def _generateStartEvent(self):
        self._startLogic(WIND_SOUND.EVENT.PLAYER)

    def __updateCameraSpeed(self):
        cameraSpeed = 0
        speed = math.degrees(self.__cameraInfo.direction.angle(self.__cameraInfo.camera.direction)) / RTPC_Wind_Update_Interval
        top = self._windDB.cameraSpeedTop
        bottom = self._windDB.cameraSpeedBottom
        if bottom < speed:
            self.__cameraInfo.ticksCounter += 1
        else:
            self.__cameraInfo.ticksCounter = 0
        if self.__cameraInfo.ticksDelay <= self.__cameraInfo.ticksCounter:
            value = (speed - bottom) / (top - bottom) * 100
            cameraSpeed = clamp(0, value, 100)
        self.__cameraInfo.direction = self.__cameraInfo.camera.direction
        self._soundObject.wwiseGameObject.setRTPC(WIND_SOUND.RTPC.CRITICAL_CAMERA_SPEED, cameraSpeed)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = WindSound('WindSoundPlayer', self._cid, self._node)

    @property
    def soundModeID(self):
        return SOUND_MODES.PLAYER


class WindSoundStrategySpectator(WindSoundStrategy):

    def __init__(self, avatarID, soundObject):
        WindSoundStrategy.__init__(self, avatarID, soundObject)

    def _generateStartEvent(self):
        self._startLogic(WIND_SOUND.EVENT.SPECTATOR)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = WindSound('WindSoundSpectator-{0}'.format(self._avatarID), self._cid, self._node)

    @property
    def soundModeID(self):
        return SOUND_MODES.SPECTATOR


class WindSoundStrategyAvatar(SoundModeStrategyBase):

    @property
    def soundModeID(self):
        return SOUND_MODES.AVATAR


g_factory = None

class WindSoundFactory(WwiseGameObjectFactory):

    def __init__(self):
        self.__soundStrategies = {SOUND_MODES.PLAYER: WindSoundStrategyPlayer,
         SOUND_MODES.AVATAR: WindSoundStrategyAvatar,
         SOUND_MODES.SPECTATOR: WindSoundStrategySpectator}

    def createPlayer(self, so):
        player = BigWorld.player()
        soundController = player.controllers.get('soundController', None)

        def onBankLoaded():
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.WIND].start()

        if soundController and SOUND_OBJECT_TYPES.WIND not in soundController.soundModeHandlers:
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.WIND] = SoundModeHandler(player.id, so, self.__soundStrategies, CURRENT_PLAYER_MODE, autoStart=False)
            SoundBanksManager.instance().loadBankAndAttachToCase(SOUND_CASES.ARENA, SOUND_BANKS.WIND, onBankLoaded)
        return

    def createAvatar(self, avatar, so):
        soundController = avatar.controllers.get('soundController', None)
        if soundController and SOUND_OBJECT_TYPES.WIND not in soundController.soundModeHandlers:
            arena = GameEnvironment.getClientArena()
            avatarInfo = arena.avatarInfos.get(avatar.id, {})
            playerTeam = arena.avatarInfos.get(BigWorld.player().id).get('teamIndex', None)
            avatarTeam = avatarInfo.get('teamIndex', None)
            isPlayerTeamate = playerTeam is not None and playerTeam == avatarTeam
            if isPlayerTeamate:
                soundController.soundModeHandlers[SOUND_OBJECT_TYPES.WIND] = SoundModeHandler(avatar.id, so, self.__soundStrategies, SOUND_MODES.AVATAR)
        return

    @staticmethod
    def getSoundObjectSettings(data):
        info = data['info']
        soundObjects = data['soundObjects']
        context = data['context']
        so = SoundObjectSettings()
        so.mountPoint = info.mointPoint
        so.factory = WindSoundFactory.instance()
        so.context = context
        soundObjects[SOUND_OBJECT_TYPES.WIND] = so

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = WindSoundFactory()
        return g_factory