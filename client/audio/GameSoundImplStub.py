# Embedded file name: scripts/client/audio/GameSoundImplStub.py
from SoundObjects import MusicSound, UI, VoiceoversSoundObject, TurretSoundObjectsFactories, AircraftSoundObjectsFactories

class GameSoundImpl:

    def __init__(self):
        self.__voice = VoiceoversSoundObject()
        self.__music = MusicSound()
        self.__ui = UI()

    def cache(self, objDBData, objectBuilder, context, isPlayer, soundObjects, weaponSoundID, turretSoundIDByTurretID):
        pass

    def initPlayer(self):
        pass

    def initAvatar(self, avatarID):
        pass

    def createTurret(self):
        pass

    def loadArena(self):
        pass

    def unloadArena(self):
        pass

    def getSoundObjects(self, entityId):
        pass

    def findLoadSet(self, eventSet, isPlayer, isAA = False, isTL = False, justCopyList = None):
        pass

    def replayMute(self, mute):
        pass

    def onBattleStart(self):
        pass

    def onBurning(self, burning):
        pass

    def onConnected(self):
        pass

    def onDisconnect(self):
        pass

    def onPlayerEnterWorld(self, *args, **kwargs):
        pass

    def onGameModeReady(self, *args, **kwargs):
        pass

    @property
    def isDisconnected(self):
        return False

    @property
    def isBurning(self):
        return self.__burning

    @property
    def voice(self):
        return self.__voice

    @property
    def music(self):
        return self.__music

    @property
    def ui(self):
        return self.__ui


g_sound_impl = GameSoundImpl()

def GameSound():
    return g_sound_impl