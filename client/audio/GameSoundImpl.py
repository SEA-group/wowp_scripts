# Embedded file name: scripts/client/audio/GameSoundImpl.py
import atexit
import BigWorld
from SoundObjects import MusicSound, UI, VoiceoversSoundObject, CameraSoundObject
from SoundObjects.HitSound import HitSFXFactory
from SoundObjects.ExplosionSound import ExplosionSFXFactory
from WWISE_ import setVolumeAmp, setReplayMute, postGlobalEvent, pyFini
from audio.SoundBanksManager import SoundBanksManager
from Event import Event, EventManager
from consts import GAME_RESULT, ARENA_TYPE
import db.DBLogic
import GameEnvironment
from EntityHelpers import EntityStates
from EntityHelpers import extractGameMode
import BattleReplay
from AKTunes import Arena_Banks, Common_Banks
from AKConsts import INIT_BANK_NAME, SOUND_CASES, AIRCRAFT_SFX, SOUND_OBJECT_TYPES, GLOBAL_EVENTS, SOUND_BANKS
from debug_utils import LOG_INFO
from DopplerEffect import DopplerEffect
from InteractiveMix import InteractiveMixHandler
from audio.SoundEventDispatcher import SoundEventDispatcher
from SoundUpdateManager import SoundUpdateManager

class GameSoundImpl():

    def __init__(self):
        self.__soundBanksManager = SoundBanksManager.instance()
        self.__initPackages()
        self.__soundBanksManager.loadInitBank(INIT_BANK_NAME)
        self.__loadCommonBanks()
        self.__gameModeEventDispatcher = None
        self.__voice = None
        self.__camera = None
        self.__hits = None
        self.__explosions = None
        self.__music = MusicSound.instance()
        self.__ui = UI()
        self.__interactiveMix = InteractiveMixHandler.instance()
        self.__interactiveMix.create()
        self.__prevTarget = None
        self.__burning = {}
        self.__isReplayMute = False
        self.__winner = False
        self.__draw = False
        self.__em = EventManager()
        self.eOnBattleStart = Event(self.__em)
        self.eOnBattleEnd = Event(self.__em)
        self.eLoadingScreenClosed = Event(self.__em)
        atexit.register(nativeFini)
        return

    def __initPackages(self):
        self.__soundBanksManager.loadFilePackage('ambient')
        self.__soundBanksManager.loadFilePackage('common')
        self.__soundBanksManager.loadFilePackage('engines')
        self.__soundBanksManager.loadFilePackage('music')
        self.__soundBanksManager.loadFilePackage('ui')
        self.__soundBanksManager.loadFilePackage('weapons')
        self.__soundBanksManager.loadFilePackage('hangar_1910')
        self.__soundBanksManager.loadFilePackage('hangar_pearl')
        self.__soundBanksManager.loadFilePackage('hangars')

    def __loadCommonBanks(self):
        for bankName in Common_Banks:
            self.__soundBanksManager.loadBank(bankName)

    def initPlayer(self):
        soundController = BigWorld.player().controllers.get('soundController', None)
        if hasattr(soundController, 'soundObjects'):
            for so in soundController.soundObjects.values():
                so.factory.createPlayer(so)

        woosh = db.DBLogic.g_instance.getWoosh()
        BigWorld.initBulletPassbySound(woosh['WooshSphereMain'], int(woosh['MaxHits']), float(woosh['Radius']))
        return

    def initAvatar(self, avatarID):
        avatar = BigWorld.entities.get(avatarID)
        if avatar:
            soundController = avatar.controllers['soundController']
            if hasattr(soundController, 'soundObjects'):
                for so in soundController.soundObjects.values():
                    so.factory.createAvatar(avatar, so)

        else:
            LOG_INFO('[Audio] unable to find an avatar by id: ', avatarID)

    def createTurret(self):
        arena = GameEnvironment.getClientArena()
        for obj in arena.allObjectsData.items():
            val = obj[1]
            if 'turretsLogic' not in val or 'soundController' not in val:
                continue
            if not hasattr(val['soundController'], 'soundObjects'):
                continue
            for so in val['soundController'].soundObjects.values():
                so.factory.createTurret(obj[0], so, val)

    def onPlayerStateChanged(self, oldState, state):
        if state == EntityStates.OUTRO:
            self.onBattleEnd()

    def stopHangar(self):
        postGlobalEvent(GLOBAL_EVENTS.UNLOAD_HANGAR)
        self.music.stopHangar()
        self.ui.setHoverButtonRadius(100.0)

    def loadArenaBanks(self):
        self.__soundBanksManager.unloadSoundCase(SOUND_CASES.HANGAR)
        for bankName in Arena_Banks:
            self.__soundBanksManager.loadBankAndAttachToCase(SOUND_CASES.ARENA, bankName)

        self.__soundBanksManager.loadBankAndAttachToCase(SOUND_CASES.ARENA, SOUND_BANKS.WEAPONS, self.initPlayer)

    def loadArena(self):
        self.__interactiveMix.createArena()
        self.__voice = VoiceoversSoundObject()
        self.__hits = HitSFXFactory()
        self.__explosions = ExplosionSFXFactory()
        self.music.playArena()
        self.__prevTarget = None
        self.__winner = False
        self.__draw = False
        self.__prevTarget = None
        self.__burning = {}
        postGlobalEvent(GLOBAL_EVENTS.LOAD_ARENA)
        GameEnvironment.getClientArena().onGameResultChanged += self.__onGameResultChanged
        SoundUpdateManager.instance().start()
        return

    def unloadArena(self):
        self.__interactiveMix.clearArena()
        if self.__voice:
            self.__voice.unload()
            self.__voice = None
        if self.__camera:
            self.__camera.destroy()
            self.__camera = None
        if self.__hits:
            self.__hits.clear()
            self.__hits = None
        if self.__explosions:
            self.__explosions.clear()
            self.__explosions = None
        postGlobalEvent(GLOBAL_EVENTS.UNLOAD_ARENA)
        self.__soundBanksManager.unloadSoundCase(SOUND_CASES.ARENA)
        SoundUpdateManager.instance().stop()
        BigWorld.finiBulletPassbySound()
        self.__em.clear()
        return

    def findLoadSet(self, eventSet, isPlayer, isAA = False, isTL = False, justCopyList = None):
        loadSet = {}
        for i in eventSet:
            if str(i).find('Player') != -1 and isPlayer or str(i).find('NPC') != -1 or str(i).find('AA') != -1 and isAA or str(i).find('TL') != -1 and isTL or justCopyList and i in justCopyList:
                loadSet[i] = eventSet[i]

        return loadSet

    def replayMute(self, mute):
        self.__isReplayMute = mute
        setReplayMute(mute)

    def setVolumeAmplifier(self, p):
        setVolumeAmp(p)

    def onBattleStart(self):
        self.ui.onBattleStart()
        self.eOnBattleStart()

    def onBattleEnd(self, inGame = True):
        self.eOnBattleEnd()

    def onStateChanged(self, entity, old, new):
        soundController = entity.controllers.get('soundController', None)
        if not soundController or not soundController.soundObjects:
            return
        else:
            for so in soundController.soundObjects.values():
                if not so.wwiseGameObject:
                    continue
                so.wwiseGameObject.onStateChanged(entity, old, new)

            return

    def onBurning(self, entityID, isPlayer, isBurning):
        self.__burning[entityID] = 0 if isBurning else BigWorld.time()
        if isPlayer:
            soundController = BigWorld.player().controllers.get('soundController', None)
            if soundController:
                sfx = soundController.getWwiseGameObject(SOUND_OBJECT_TYPES.SFX)
                if not sfx:
                    return
                if isBurning:
                    sfx.play(AIRCRAFT_SFX.TYPE.FIRE, AIRCRAFT_SFX.CATEGORY.STATE)
                else:
                    sfx.stop(AIRCRAFT_SFX.TYPE.FIRE, AIRCRAFT_SFX.CATEGORY.STATE)
        return

    def onLoadingScreenClosed(self):
        curVehicleID = BigWorld.player().curVehicleID
        DopplerEffect.instance().setListener(BigWorld.player())
        DopplerEffect.instance().activate()
        for k in BigWorld.player().visibleAvatars.keys():
            if not BigWorld.player().visibleAvatars[k].inWorld:
                continue
            self.initAvatar(k)

        if not curVehicleID:
            BigWorld.player().eUpdateSpectator += self.__onSpectator
        self.eLoadingScreenClosed()

    def onArenaLoaded(self):
        self.createTurret()
        gm = extractGameMode(BigWorld.player().gameMode)
        self.onLoadingScreenClosed()

    def __onSpectator(self, target):
        DopplerEffect.instance().setListener(BigWorld.entities.get(target))

    def onPlayerLeaveWorld(self):
        gm = extractGameMode(BigWorld.player().gameMode)
        self.unloadArena()
        BigWorld.player().eUpdateSpectator -= self.__onSpectator
        gameMode = GameEnvironment.getClientArena().gameMode
        gameMode.unsubscribe(self.__gameModeEventDispatcher)
        self.__gameModeEventDispatcher.finish()
        self.__gameModeEventDispatcher = None
        return

    def __onGameResultChanged(self, gameResult, winState):
        winResults = [GAME_RESULT.SUPERIORITY_SUCCESS, GAME_RESULT.ELIMINATION, GAME_RESULT.AREA_CONQUEST_SUCCESS]
        self.__winner = gameResult in winResults and BigWorld.player().teamIndex == winState
        self.__draw = gameResult in [GAME_RESULT.DRAW_ELIMINATION,
         GAME_RESULT.DRAW_ELIMINATION_NO_PLAYERS,
         GAME_RESULT.DRAW_SUPERIORITY,
         GAME_RESULT.DRAW_TIME_IS_RUNNING_OUT]
        battleType = GameEnvironment.getClientArena().battleType
        if battleType == ARENA_TYPE.TRAINING:
            self.onBattleEnd(False)

    def isBurning(self, id, fireAttenuationDelta = 0):
        value = self.__burning.get(id, -1)
        if value < 0:
            return False
        if value > 0:
            return BigWorld.time() < value + fireAttenuationDelta
        return True

    def onPlayerEnterWorld(self, *args, **kwargs):
        """Event handler for PlayerAvatar.eEnterWorldEvent
        """
        gameMode = GameEnvironment.getClientArena().gameMode
        if gameMode.isReady:
            self.onGameModeReady()
        else:
            gameMode.eGameModeReady += self.onGameModeReady
        self.__gameModeEventDispatcher = SoundEventDispatcher(gameMode)
        gameMode.subscribe(self.__gameModeEventDispatcher)
        self.camera.onPlayerEnterWorld()

    def onGameModeReady(self, *args, **kwargs):
        """Event handler for ACGameModeClient.eGameModeReady event
        """
        self.loadArena()

    @property
    def isWinner(self):
        return self.__winner

    @property
    def isDraw(self):
        return self.__draw

    @property
    def isReplayMute(self):
        return self.__isReplayMute or BattleReplay.g_replay and BattleReplay.g_replay.isTimeWarpInProgress

    @property
    def camera(self):
        if not self.__camera:
            self.__camera = CameraSoundObject()
        return self.__camera

    @property
    def hitSFXManager(self):
        return self.__hits

    @property
    def explosionSFXManager(self):
        return self.__explosions

    @property
    def music(self):
        return self.__music

    @property
    def ui(self):
        return self.__ui

    @property
    def interactiveMix(self):
        return self.__interactiveMix


def nativeFini():
    pyFini()


g_sound_impl = None

def GameSound():
    global g_sound_impl
    if g_sound_impl is None:
        g_sound_impl = GameSoundImpl()
    return g_sound_impl


def GS():
    return GameSound()