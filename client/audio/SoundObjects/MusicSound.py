# Embedded file name: scripts/client/audio/SoundObjects/MusicSound.py
from WwiseGameObject import WwiseGameObject, GS
import BigWorld
import db.DBLogic
from WWISE_ import postGlobalEvent
from audio.InteractiveMix.GamePhases import GamePhases, SOUND_PHASES
from audio.AKConsts import SOUND_CASES, MUSIC_SOUND, GLOBAL_EVENTS
import audio.debug
from adapters.IHangarSpacesAdapter import getHangarSpaceByID
import random

class HangarMusic:

    def __init__(self, spaceID, wwiseSoundObject):
        self.__hangarSpaceID = spaceID
        self.__hangarSettings = db.DBLogic.g_instance.getHangarSettings()
        self.__wwiseSoundObject = wwiseSoundObject
        self.__hangarMusicCallback = None
        self.__hangarMusicEvent = None
        return

    def start(self):
        postGlobalEvent(GLOBAL_EVENTS.LOAD_HANGAR)
        if self.__hangarSpaceID not in self.__hangarSettings.hangarSet:
            audio.debug.LOG_INFO('%s %s' % (audio.debug.DEBUG_AUDIO_TAG, "Hangar {0} doesn't found in sound_settings.xml".format(str(self.__hangarSpaceID))))
            return
        spaceSoundEvents = self.__hangarSettings.hangarSet[self.__hangarSpaceID]
        hangarAmbient = spaceSoundEvents[MUSIC_SOUND.HANGAR_ID_TAG[MUSIC_SOUND.AMBIENT]]
        self.__wwiseSoundObject.postEvent(hangarAmbient)
        self.__hangarMusicEvent = spaceSoundEvents[MUSIC_SOUND.HANGAR_ID_TAG[MUSIC_SOUND.MUSIC]]
        self.__playHangarMusic()

    def stop(self):
        if self.__hangarMusicCallback:
            BigWorld.cancelCallback(self.__hangarMusicCallback)

    def clear(self):
        self.__wwiseSoundObject = None
        return

    def __playHangarMusic(self):
        self.__wwiseSoundObject.postEvent(self.__hangarMusicEvent)
        musicLoopInterval = self.__hangarSettings.musicLoopInterval
        time = random.randint(musicLoopInterval.min, musicLoopInterval.max)
        self.__hangarMusicCallback = BigWorld.callback(time, self.__playHangarMusic)


class ArenaMusic:

    def __init__(self, wwiseSoundObject, stingerCooldownTime):
        self.__wwiseSoundObject = wwiseSoundObject
        self.__stingerCooldownCB = None
        self.__stingerCooldownTime = stingerCooldownTime
        self.__endBattleMusicPlayed = False
        return

    def start(self):
        musicPrefix = db.DBLogic.g_instance.getArenaData(BigWorld.player().arenaType).musicPrefix
        mapSoundSettings = db.DBLogic.g_instance.getMapSoundSettings()
        currentMap = {}
        if musicPrefix in mapSoundSettings:
            currentMap = mapSoundSettings[musicPrefix]
        else:
            currentMap = mapSoundSettings['default']
            audio.debug.LOG_INFO('%s %s' % (audio.debug.DEBUG_AUDIO_TAG, "Map {0} doesn't found in sound_settings.xml".format(musicPrefix)))
        for soundTag in MUSIC_SOUND.MAP_ID_TAG.values():
            event = currentMap[soundTag]
            self.__wwiseSoundObject.postEvent(event)

    def stop(self):
        pass

    def clear(self):
        self.__clearStingerCooldownCB()
        self.__wwiseSoundObject = None
        return

    def __isStingerCanBePlayed(self):
        if GamePhases.instance().curretnSoundPhase in (SOUND_PHASES.PILOTING, SOUND_PHASES.DOGFIGHT) and not self.__endBattleMusicPlayed:
            return True
        return False

    def playStinger(self, stingerEvent):
        if not self.__stingerCooldownCB and self.__isStingerCanBePlayed():
            self.__wwiseSoundObject.postEvent(stingerEvent)
            self.__stingerCooldownCB = BigWorld.callback(self.__stingerCooldownTime, self.__clearStingerCooldownCB)

    def __clearStingerCooldownCB(self):
        if self.__stingerCooldownCB:
            BigWorld.cancelCallback(self.__stingerCooldownCB)
            self.__stingerCooldownCB = None
        return

    def playBattleMusic(self):
        if not self.__endBattleMusicPlayed:
            self.__endBattleMusicPlayed = True
            self.__wwiseSoundObject.postEvent(MUSIC_SOUND.EVENT.BATTLE_MUSIC)


g_musicSound = None

class MusicSound(WwiseGameObject):

    def __init__(self):
        WwiseGameObject.__init__(self, 'MusicSound')
        self.__hangar = None
        self.__music = None
        return

    @staticmethod
    def instance():
        global g_musicSound
        if not g_musicSound:
            g_musicSound = MusicSound()
        return g_musicSound

    def convPlay2StopEvent(self, playEvent):
        return playEvent.replace('Play_', 'Stop_')

    def playHangar(self, _, space):
        self.__hangar = HangarMusic(getHangarSpaceByID(space)['spaceID'], self)
        self.__hangar.start()

    def stopHangar(self):
        self.__hangar.stop()
        self.__hangar.clear()
        self.__hangar = None
        return

    def playArena(self):
        self.__music = ArenaMusic(self, MUSIC_SOUND.STINGER_COOLDOWN_TIME)
        self.__music.start()

    def stopArena(self):
        self.__music.stop()
        self.__music.clear()
        self.__music = None
        return

    def playStinger(self, stingerEvent):
        self.__music.playStinger(stingerEvent)

    def playBattleMusic(self):
        self.__music.playBattleMusic()