# Embedded file name: scripts/client/audio/SoundModes.py
import BigWorld
from audio.AKConsts import SOUND_MODES
from EntityHelpers import EntityStates

class SoundModeHandler:

    def __init__(self, avatarID, soundObject, soundStrategies, soundModeID, autoStart = True):
        self._avatar = None
        self._avatarID = avatarID
        self._soundObject = soundObject
        self._soundStrategies = soundStrategies
        self._soundModeID = soundModeID
        self._isPlayer = BigWorld.player().id == self._avatarID
        self.__strategy = None
        if autoStart:
            self.start()
        return

    def start(self):
        self.__setStrategy(self._soundModeID)
        self.__registerEvents()

    def clear(self):
        self.__clearEvents()
        self.__setStrategy(None)
        self._soundObject = None
        self._soundStrategies = None
        return

    def __registerAvatarEvents(self):
        self._avatar = BigWorld.entities.get(self._avatarID)
        self._avatar.eOnEntityStateChanged += self.__onAvatarStateChanged

    def __clearAvatarEvents(self):
        if self._avatar:
            self._avatar.eOnEntityStateChanged -= self.__onAvatarStateChanged
            self._avatar = None
        return

    def __registerEvents(self):
        player = BigWorld.player()
        player.eRespawn += self.__onRespawn
        player.eUpdateSpectator += self.__onSpectator
        player.onAvatarEnterWorldEvent += self.__onAvatarEnterWorld
        player.onAvatarLeaveWorldEvent += self.__onAvatarLeaveWorld
        player.onStateChanged += self.__playerStateChanged
        self.__registerAvatarEvents()

    def __clearEvents(self):
        player = BigWorld.player()
        player.eRespawn -= self.__onRespawn
        player.eUpdateSpectator -= self.__onSpectator
        player.onAvatarEnterWorldEvent -= self.__onAvatarEnterWorld
        player.onAvatarLeaveWorldEvent -= self.__onAvatarLeaveWorld
        player.onStateChanged -= self.__playerStateChanged
        self.__clearAvatarEvents()

    def _createSoundStrategy(self, soundModeID):
        return self._soundStrategies[soundModeID](self._avatarID, self._soundObject)

    def __onRespawn(self):
        if BigWorld.player().state != EntityStates.WAIT_START:
            return
        if self._isPlayer:
            self.__setStrategy(self._soundModeID)
        elif self.__strategy and self.__strategy.soundModeID == SOUND_MODES.SPECTATOR:
            self.__setStrategy(SOUND_MODES.AVATAR)

    def __onSpectator(self, avatarID):
        if not self.__strategy:
            return
        else:
            if self._isPlayer:
                self.__setStrategy(None)
            elif self.__strategy.soundModeID == SOUND_MODES.SPECTATOR and not self._isPlayer:
                self.__setStrategy(SOUND_MODES.AVATAR)
            elif self.__strategy.soundModeID == SOUND_MODES.AVATAR and self._avatarID == avatarID:
                self.__setStrategy(SOUND_MODES.SPECTATOR)
            return

    def __onAvatarEnterWorld(self, avatarID):
        if self._avatarID == avatarID and not self.__strategy:
            self.__registerAvatarEvents()
            self.__setStrategy(SOUND_MODES.AVATAR)

    def __onAvatarLeaveWorld(self, playerAvatar, avatarID, avatar):
        if avatarID == self._avatarID:
            self.__clearAvatarEvents()
            self.__onAvatarDestroy()

    def __onAvatarStateChanged(self, avatarID, oldState, newState):
        if self._isPlayer or self._avatarID != avatarID:
            return
        if oldState != newState and newState == EntityStates.DESTROYED:
            self.__onAvatarDestroy()
        elif oldState != newState and newState == EntityStates.CREATED and not self.__strategy:
            self.__setStrategy(SOUND_MODES.AVATAR)

    def __playerStateChanged(self, oldState, newState):
        if self._isPlayer and oldState != newState and newState == EntityStates.DESTROYED:
            self.__onAvatarDestroy()

    def __setStrategy(self, soundModeID):
        if self.__strategy:
            self.__strategy.finish()
        if soundModeID is None:
            self.__strategy = None
        elif not EntityStates.inState(BigWorld.entities.get(self._avatarID), EntityStates.DESTROYED):
            self.__strategy = self._createSoundStrategy(soundModeID)
        return

    def __onAvatarDestroy(self):
        self.__setStrategy(None)
        return

    def destroyAvatar(self):
        self.__onAvatarDestroy()


class SoundModeStrategyBase:

    def __init__(self, avatarID, soundObject):
        self._avatarID = avatarID
        self._soundObject = soundObject
        self._cid = soundObject.context.cidProxy.handle
        self._node = soundObject.node.id
        self._createSoundObject()
        self._registerEventsBase()

    def _destroySoundObject(self):
        if self._soundObject.wwiseGameObject:
            self._soundObject.wwiseGameObject.stopAll(0, True)
            self._onDestroySoundObject()
            self._soundObject.wwiseGameObject = None
        return

    def _onDestroySoundObject(self):
        pass

    def __clear(self):
        self._soundObject = None
        self._cid = None
        self._node = None
        return

    def finish(self):
        self._clearEventsBase()
        self._clearCBBase()
        if self._soundObject:
            self._destroySoundObject()
        self._finishBase()
        self.__clear()

    def _finishBase(self):
        pass

    def _registerEventsBase(self):
        pass

    def _clearEventsBase(self):
        pass

    def _createSoundObject(self):
        pass

    def _clearCBBase(self):
        pass

    @property
    def soundModeID(self):
        return None