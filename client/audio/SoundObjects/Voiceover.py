# Embedded file name: scripts/client/audio/SoundObjects/Voiceover.py
from WwiseGameObject import WwiseGameObject, GS
import BigWorld
import db.DBLogic
from consts import TEAM_ID
from audio.AKConsts import VOICEOVERS_BANKS, SOUND_CASES, VOICEOVERS_QUEUE_SIZE, VOICEOVER_NOISE, VOICE, VOICEOVER_DEFAULTS
from audio.SoundBanksManager import SoundBanksManager
import random
import GameEnvironment
import collections
from EntityHelpers import AvatarFlags, EntityStates
from audio import SoundEventDispatcher
from consts import GAME_MODE
import audio.debug

class Voiceover:

    def __init__(self, event, db_dict):
        self.event = event
        self.__probability = self.__initDefaults(VOICEOVER_DEFAULTS.PROBABILITY, db_dict)
        self.__counter = self.__initDefaults(VOICEOVER_DEFAULTS.MAX, db_dict)
        self.__cooldownTime = self.__initDefaults(VOICEOVER_DEFAULTS.COOLDOWN, db_dict)
        self.priority = self.__initDefaults(VOICEOVER_DEFAULTS.PRIORITY, db_dict)
        self.__cooldownCB = None
        return

    def play(self):
        self.__counter -= 1
        if self.__cooldownTime:
            self.__cooldownCB = BigWorld.callback(self.__cooldownTime, self.finishCooldown)

    def finishCooldown(self):
        if self.__cooldownCB:
            BigWorld.cancelCallback(self.__cooldownCB)
            self.__cooldownCB = None
        return

    def isPlayable(self):
        dice = random.randint(0, 100)
        msg = 'Event {0} approved'.format(self.event)
        if not self.__counter:
            msg = 'Event {0} failed: all voices already played'.format(self.event)
        elif self.__cooldownCB:
            msg = 'Event {0} failed: cooldown'.format(self.event)
        elif dice > self.__probability:
            msg = ('Event {0} failed: dice ( ' + str(dice) + ' > ' + str(self.__probability) + ' )').format(self.event)
        audio.debug.LOG_INFO(audio.debug.DEBUG_AUDIO_TAG, 'Voiceover', msg)
        if self.__counter and not self.__cooldownCB and dice <= self.__probability:
            return True
        else:
            return False

    def __initDefaults(self, key, db_dict):
        if key in db_dict:
            return int(db_dict[key])
        return VOICEOVER_DEFAULTS.DEFAULTS[key]


class VoiceoversQueue:

    def __init__(self, max_size):
        self.__size = max_size
        self.__queue = []
        self.__isLock = False

    def push(self, vo):
        if self.__isLock:
            return
        self.__queue.append(vo)
        self.__queue.sort(key=lambda vo: vo.priority)
        self.__queue = self.__queue[:self.__size]

    def pop(self):
        if len(self.__queue):
            vo = self.__queue[0]
            self.__queue = self.__queue[1:]
            return vo
        else:
            return None

    def setLock(self, isLockValue):
        self.__isLock = isLockValue

    def clean(self):
        self.__queue = []


class VoiceoversSoundObject(WwiseGameObject):

    def __init__(self):
        WwiseGameObject.__init__(self, 'Voiceover')
        self.__soundBanksManager = SoundBanksManager.instance()
        self.__playNow = None
        self.__isLock = False
        self.__queue = VoiceoversQueue(VOICEOVERS_QUEUE_SIZE - 1)
        self.__clientArena = GameEnvironment.getClientArena()
        self.__gameModeIndex = self.__clientArena.gameModeEnum - GAME_MODE.AREA_CONQUEST
        self.__player = BigWorld.player()
        self.__initVoiceovers()
        self.load()
        self.__initAdditionalDataForEvents()
        self.__registerEvents()
        self.__ignoreWhenLock = [VOICE.TEAM_WIN, VOICE.TEAM_LOSE]
        return

    def __initVoiceovers(self):
        self.__voiceovers = {}
        for event, db_dict in db.DBLogic.g_instance.getVO(self.__gameModeIndex).voiceovers.items():
            vo = Voiceover(event, db_dict)
            self.__voiceovers[event] = vo

    def load(self):
        self.__soundBanksManager.loadBankAndAttachToCase(SOUND_CASES.ARENA, VOICEOVERS_BANKS.COORDINATOR)

    def play(self, event):
        vo = self.__voiceovers.get(event, None)
        if vo and vo.isPlayable():
            self.__play(vo)
        return

    def __play(self, vo, startLoop = True):
        if self.__isLock and vo.event not in self.__ignoreWhenLock:
            return
        if not self.__playNow:
            self.__playNow = vo
            vo.play()
            if startLoop:
                self.postEvent(VOICEOVER_NOISE.START)
                msg = 'Play event directly ' + vo.event
                audio.debug.LOG_INFO(audio.debug.DEBUG_AUDIO_TAG, 'Voiceover', msg)
            else:
                msg = 'Play event from queue' + vo.event
                audio.debug.LOG_INFO(audio.debug.DEBUG_AUDIO_TAG, 'Voiceover', msg)
            self.postEvent(vo.event, self.__onFinishVO)
        else:
            self.__queue.push(vo)

    def __onFinishVO(self):
        self.__playNow = None
        vo = self.__queue.pop()
        if vo:
            self.__play(vo, False)
        elif getattr(self.__player, 'isArenaLoaded', False):
            self.postEvent(VOICEOVER_NOISE.STOP)
        return

    def unload(self):
        self.__unregisterEvents()
        for vo in self.__voiceovers.values():
            vo.finishCooldown()

        self.__voiceovers = {}

    def __initAdditionalDataForEvents(self):
        self.__playerFlags = {}
        self.__teamSpeechLastPlayer = {}
        self.__curBasesPrc = [0, 0]
        self.__voice_CLOSE_TO_played = False
        self.__sectorsTeamIndexes = {}
        for sector_name, sector_data in self.__clientArena.gameMode.sectors.items():
            self.__sectorsTeamIndexes[sector_name] = sector_data.teamIndex

    def __registerEvents(self):
        GS().eOnBattleStart += self.__onBattleStart
        GS().eOnBattleEnd += self.__onBattleEnd
        self.__player.eArenaLoaded += self.__onArenaLoaded
        SoundEventDispatcher.eVoiceoverRequest += self.play

    def __unregisterEvents(self):
        GS().eOnBattleStart -= self.__onBattleStart
        GS().eOnBattleEnd -= self.__onBattleEnd
        SoundEventDispatcher.eVoiceoverRequest -= self.play

    def __onBattleStart(self):
        if not sum(self.__clientArena.gameMode.scoreGlobal):
            self.play(VOICE.BATTLE_START)

    def __onBattleEnd(self):
        self.__cleanQueue()
        if GS().isWinner:
            self.play(VOICE.TEAM_WIN)
        else:
            self.play(VOICE.TEAM_LOSE)
        self.__lockQueue()

    def __lockQueue(self):
        self.__isLock = True
        self.__queue.setLock(True)

    def __cleanQueue(self):
        self.__queue.clean()

    def __onArenaLoaded(self):
        self.play(VOICE.MAP_LOADED)