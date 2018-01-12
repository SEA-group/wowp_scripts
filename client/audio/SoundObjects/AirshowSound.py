# Embedded file name: scripts/client/audio/SoundObjects/AirshowSound.py
from WwiseGameObject import WwiseGameObject, WwiseGameObjectFactory
import db.DBLogic
import BigWorld
from audio.AKTunes import RTPC_Airshow_Update_Interval, SOUND_CALLBACKS_PER_TICK
from EntityHelpers import EntityStates
from SoundUtils import AirshowSoundCore
from audio.SoundObjectSettings import SoundObjectSettings
from audio.SoundModes import SoundModeStrategyBase, SoundModeHandler
from audio.AKConsts import SOUND_MODES, CURRENT_PLAYER_MODE, AIRSHOW_SOUND, SOUND_OBJECT_TYPES, SOUND_CALLBACK_QUEUE_TYPES
import audio.debug
from audio.SoundUpdateManager import SoundUpdateManager, SoundUpdateQueue
g_airshowSoundCore = None

class AirshowSound(WwiseGameObject):

    def __init__(self, name, cid, node):
        WwiseGameObject.__init__(self, name, cid, node)


class AirshowSoundStrategy(SoundModeStrategyBase):

    def __init__(self, avatarID, soundObject):
        SoundModeStrategyBase.__init__(self, avatarID, soundObject)

    def _registerEventsBase(self):
        self._registerEvents()

    def _registerEvents(self):
        pass

    def _clearEventsBase(self):
        self._clearEvents()

    def _clearEvents(self):
        pass

    def _createSoundObject(self):
        pass

    def _clearCBBase(self):
        self._clearCB()

    def _clearCB(self):
        pass

    def _finishBase(self):
        self._finish()

    def _finish(self):
        pass


class AirshowSoundStrategyPlayer(AirshowSoundStrategy):
    pass


class AirshowSoundStrategyAvatar(AirshowSoundStrategy):

    def __init__(self, avatarID, soundObject):
        global g_airshowSoundCore
        self.__player = BigWorld.player()
        self.__avatarID = avatarID
        self.__airshowDB = db.DBLogic.g_instance.getAirshowParameters()
        self.__bottomOfExternalSphere = self.__airshowDB.externalSphereRadius * self.__airshowDB.externalSphereRange
        self.__topOfExternalSphere = self.__airshowDB.externalSphereRadius * (2 - self.__airshowDB.externalSphereRange)
        if not g_airshowSoundCore:
            g_airshowSoundCore = AirshowSoundCore(self.__airshowDB.minSpeed, self.__airshowDB.internalShpereRadius, self.__bottomOfExternalSphere, self.__topOfExternalSphere)
        self.__airshowSoundCore = g_airshowSoundCore
        AirshowSoundStrategy.__init__(self, avatarID, soundObject)
        self.__reset(BigWorld.entities.get(self._avatarID))
        self.__start()

    def __del__(self):
        SoundUpdateManager.instance().getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRSHOW_MAIN).remove(self.__airshowMainUpdate)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = AirshowSound('AirshowSound-{0}'.format(self._avatarID), self._cid, self._node)

    def _registerEvents(self):
        self.__player.onStateChanged += self.__onPlayerStateChanged

    def _clearEvents(self):
        self.__player.onStateChanged -= self.__onPlayerStateChanged

    def __reset(self, avatar):
        self.__avatar = avatar
        self.__cooldown = False
        self.__cooldownCB = None
        self.__updateCB = None
        self.__paused = False
        aircraftSound = db.DBLogic.g_instance.getAircraftSound(avatar.settings.airplane.name)
        self.__flybyType = db.DBLogic.g_instance.getAircraftEngineSet(aircraftSound.engineSet)[AIRSHOW_SOUND.FLYBY_TYPE_TAG]
        return

    def __start(self):
        if self.__avatar:
            soundUpdateManager = SoundUpdateManager.instance()
            if not soundUpdateManager.isQueueRegistred(SOUND_CALLBACK_QUEUE_TYPES.AIRSHOW_MAIN):
                queue = SoundUpdateQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRSHOW_MAIN, SOUND_CALLBACKS_PER_TICK.AIRSHOW_MAIN)
                soundUpdateManager.registerQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRSHOW_MAIN, queue)
            soundUpdateManager.getQueue(SOUND_CALLBACK_QUEUE_TYPES.AIRSHOW_MAIN).append(self.__airshowMainUpdate)

    def _clearCB(self):
        if self.__cooldownCB:
            BigWorld.cancelCallback(self.__cooldownCB)
            self.__cooldownCB = None
        return

    def __airshowMainUpdate(self):
        if self.__cooldown or self.__paused:
            return
        flyTime = self.__airshowSoundCore.getFlyTime(self.__player.position, self.__player.getWorldVector(), self.__avatar.position, self.__avatar.getWorldVector())
        if flyTime > 0:
            self.__airshowAction(self.__getClosestTimeInterval(flyTime))
            self.__cooldown = True
            self.__cooldownCB = BigWorld.callback(self.__airshowDB.cooldownTime, self.__onFinishAirshowAction)

    def __getClosestTimeInterval(self, time):
        intervals = self.__airshowDB.timeIntervals.keys()
        matches = [ abs(time - value) for value in intervals ]
        return self.__airshowDB.timeIntervals[intervals[matches.index(min(matches))]]

    def __onPlayerStateChanged(self, oldState, state):
        if state == EntityStates.DESTROYED_FALL or state == EntityStates.DESTROYED:
            self.__paused = True
        else:
            self.__paused = False

    def __airshowAction(self, time):
        flytyType = self.__flybyType if self.__avatar.state != EntityStates.DESTROYED_FALL else AIRSHOW_SOUND.FLYBY_TYPES.DEAD
        self._soundObject.wwiseGameObject.setSwitch(AIRSHOW_SOUND.SWITCH.FLYBY_TYPE, flytyType)
        self._soundObject.wwiseGameObject.setSwitch(AIRSHOW_SOUND.SWITCH.TIME, time)
        self.__play(AIRSHOW_SOUND.EVENT.PLAY)
        if audio.debug.IS_AUDIO_DEBUG:
            if not hasattr(AirshowSoundStrategyAvatar, 'debug_counter'):
                AirshowSoundStrategyAvatar.debug_counter = 1
            audio.debug.SHOW_DEBUG_OBJ('Counter', AirshowSoundStrategyAvatar.debug_counter, group='AirshowSOund')
            audio.debug.SHOW_DEBUG_OBJ('Time', time, group='AirshowSOund')
            audio.debug.SHOW_DEBUG_OBJ('FlybyType', flytyType, group='AirshowSOund')
            AirshowSoundStrategyAvatar.debug_counter += 1

    def __onFinishAirshowAction(self):
        self.__cooldown = False
        self.__cooldownCB = None
        return

    def __play(self, event):
        self._soundObject.wwiseGameObject.postEvent(event)


class AirshowSoundStrategySpectator(AirshowSoundStrategy):
    pass


g_factory = None

class AirshowSoundFactory(WwiseGameObjectFactory):

    def __init__(self):
        self.__soundStrategies = {SOUND_MODES.PLAYER: AirshowSoundStrategyPlayer,
         SOUND_MODES.AVATAR: AirshowSoundStrategyAvatar,
         SOUND_MODES.SPECTATOR: AirshowSoundStrategySpectator}

    def createAvatar(self, avatar, so):
        soundController = avatar.controllers.get('soundController', None)
        if soundController and SOUND_OBJECT_TYPES.AIRSHOW not in soundController.soundModeHandlers and CURRENT_PLAYER_MODE == SOUND_MODES.PLAYER:
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.AIRSHOW] = SoundModeHandler(avatar.id, so, self.__soundStrategies, SOUND_MODES.AVATAR)
        return

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = AirshowSoundFactory()
        return g_factory

    @staticmethod
    def getSoundObjectSettings(data):
        info = data['info']
        soundObjects = data['soundObjects']
        context = data['context']
        so = SoundObjectSettings()
        so.mountPoint = info.mointPoint
        so.factory = AirshowSoundFactory.instance()
        so.context = context
        soundObjects[SOUND_OBJECT_TYPES.AIRSHOW] = so