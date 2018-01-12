# Embedded file name: scripts/client/audio/SoundObjects/AircraftReverseEngineSound.py
from AircraftEngineSound import *

class AircraftReverseEngineSound(AircraftEngineSound):

    def __init__(self, name, cid, node, entityID = 0):
        AircraftEngineSound.__init__(self, name, cid, node, entityID=entityID)
        self.setReverseOrientation(True)


class AircraftReverseEngineStrategyPlayer(AircraftEngineStrategyPlayerBase):

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategyPlayerBase.__init__(self, avatarID, soundObject)

    def _createSoundObject(self):
        if not self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject = AircraftReverseEngineSound('ReverseEngineSoundPlayer-{0}'.format(self._avatarID), self._cid, self._node, self._avatarID)
            if BigWorld.player().clientIsReady:
                self.play()

    def _getTag(self, state):
        return '{0}{1}'.format('PlayerReverseEngine', state)


class AircraftReverseEngineStrategyAvatar(AircraftEngineStrategyAvatar):

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategyAvatar.__init__(self, avatarID, soundObject)


class AircraftReverseEngineStrategySpectator(AircraftEngineStrategySpectator):

    def __init__(self, avatarID, soundObject):
        AircraftEngineStrategySpectator.__init__(self, avatarID, soundObject)


g_factory = None

class AircraftReverseEngineSoundFactory(WwiseGameObjectFactory):

    def __init__(self):
        self.__soundStrategies = {SOUND_MODES.PLAYER: AircraftReverseEngineStrategyPlayer,
         SOUND_MODES.AVATAR: AircraftReverseEngineStrategyAvatar,
         SOUND_MODES.SPECTATOR: AircraftReverseEngineStrategySpectator}
        self.__soundBanksManager = SoundBanksManager.instance()

    def createPlayer(self, so):
        player = BigWorld.player()
        soundController = player.controllers.get('soundController', None)

        def onBankLoaded():
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.REVERSE_ENGINE].start()

        if soundController and SOUND_OBJECT_TYPES.REVERSE_ENGINE not in soundController.soundModeHandlers:
            bank = so.soundSet['SoundBankReverse']
            soundController.soundModeHandlers[SOUND_OBJECT_TYPES.REVERSE_ENGINE] = SoundModeHandler(player.id, so, self.__soundStrategies, CURRENT_PLAYER_MODE, autoStart=False)
            self.__soundBanksManager.loadBankAndAttachToCase(BigWorld.player().id, bank, onBankLoaded, self.__soundBanksManager.REFS_COUNTING_ENABLE)
        return

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = AircraftReverseEngineSoundFactory()
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
         'SoundBankReverse'])
        so.factory = AircraftReverseEngineSoundFactory.instance()
        so.context = context
        soundObjects[SOUND_OBJECT_TYPES.REVERSE_ENGINE] = so