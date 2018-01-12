# Embedded file name: scripts/client/GameEnvironment.py
import GlobalEvents
import consts
import gui.hud
from Camera import Camera
from ClientArena import ClientArena
from ClientStatsCollector import ClientStatsCollector
from CrewSkills.debug import ENABLED as SkillsDebugEnabled
from Event import Event, EventManager, LazyEvent
import gui.hud
import GlobalEvents
from clientEconomics.ClientEconomic import ClientEconomic
from TimerService import TimerService
from input.InputController import *
from battleHints.messenger import Messenger
from GamePlayHints import GamePlayHints
g_instance = None
import BattleReplay
import BigWorld
from functools import partial
from audio import GameSound
from gui.HudElements.IngameChat import Chat
from PlayerAvatarProxy import PlayerAvatarProxy
TIMER_SERVICE = 'TimerService'

class GameEnvironment():

    def __init__(self):
        self.__playerAvatar = None
        self.__playerAvatarProxy = None
        self.__isStarted = False
        self.__services = {}
        self.__preWorldEvents = []
        self.__events = []
        self.__em = EventManager()
        self.eAvatarAdded = Event(self.__em)
        self.eAvatarRemoved = Event(self.__em)
        self.eAvatarInfo = Event(self.__em)
        self.eLoadingProgress = Event(self.__em)
        self.eToggleDebugHUD = Event(self.__em)
        self.eChangeLanguage = Event(self.__em)
        self.eUpdateHUDSettings = Event(self.__em)
        self.eMarkersSettingsUpdate = Event(self.__em)
        self.eAimsSettingsUpdate = Event(self.__em)
        self.eUpdateUIComponents = Event(self.__em)
        self.eOnDenyCursorHideChanged = Event(self.__em)
        self.eAvatarHealthChange = Event(self.__em)
        self.eAvatarChangeLastDamagerID = Event(self.__em)
        self.eTOPartChanged = Event(self.__em)
        self.eVictimInformAboutCrit = Event(self.__em)
        self.eUpdateAvatarPartStates = Event(self.__em)
        self.eFireStateChange = Event(self.__em)
        self.eOnTargetEntity = Event(self.__em)
        self.eOnSetTargetLock = Event(self.__em)
        self.eOnFlapsMessage = Event(self.__em)
        self.eOnMinimapSetMarker = Event(self.__em)
        self.eSetTargetEntity = Event(self.__em)
        self.ePartStateChanging = Event(self.__em)
        self.eOnCrossSizeChanged = Event(self.__em)
        self.eSetBombMarkerPos = Event(self.__em)
        self.eSetBombRolled = Event(self.__em)
        self.eSkipLoading = Event(self.__em)
        self.eGetHudPlaneData = Event(self.__em)
        self.eLoadingFinished = Event(self.__em)
        self.eIntroFinished = Event(self.__em)
        self.ePreBattleFinished = Event(self.__em)
        self.eLoadingDeathFinished = Event(self.__em)
        self.eTemporaryVisibleObjectsUpdate = Event(self.__em)
        self.eGetPlanesCharacteristics = Event(self.__em)
        self.eSetUsersChatStatus = Event(self.__em)
        self.eSetChatMute = Event(self.__em)
        self.eGetTargetsFromFlash = Event(self.__em)
        self.eAllIntreClosed = Event(self.__em)
        self.eTogglePromoHUD = Event(self.__em)
        self.ePlayerGunnerChangedTurret = Event(self.__em)
        self.eTurretEndCritTimeChange = Event(self.__em)
        self.eShowHint = Event(self.__em)
        self.eDisableStartHint = Event(self.__em)
        return

    def __del__(self):
        self.__em.clear()

    def start(self, playerAvatar):
        self.__playerAvatar = playerAvatar
        self.__playerAvatarProxy = PlayerAvatarProxy(playerAvatar)
        self.__isStarted = True
        self.__createServices()
        self.__initServices()
        self.__linkPreWorldEvents()

    def end(self):
        self.__destroyServices()
        self.__playerAvatarProxy.dispose()
        self.__playerAvatarProxy = None
        self.__playerAvatar = None
        self.__isStarted = False
        return

    def __linkPreWorldEvent(self, event, func):
        event += func
        self.__preWorldEvents.append((event, func))

    def __linkPreWorldEvents(self):
        audio = GameSound()
        clientArena = self.__services['ClientArena']
        input = self.__services['Input']
        cam = self.__services['Camera']
        economics = self.__services['ClientEconomics']
        hints = self.__services['BattleHints']
        replay = BattleReplay.g_replay
        self.__linkPreWorldEvent(clientArena.onEconomicEvents, economics.onEconomicEvents)
        self.__linkPreWorldEvent(clientArena.onNewAvatarsInfo, self.eAvatarInfo)
        self.__linkPreWorldEvent(clientArena.onReceiveMarkerMessage, audio.ui.onReceiveMarkerMessage)
        self.__linkPreWorldEvent(clientArena.onTeamObjectDestruction, self.__playerAvatar.reportTeamObjectDestruction)
        self.__linkPreWorldEvent(clientArena.onReportBattleResult, self.__playerAvatar.onReportBattleResult)
        self.__linkPreWorldEvent(clientArena.onReceiveVOIPChannelCredentials, self.__playerAvatar.onReceiveVOIPChannelCredentials)
        self.__linkPreWorldEvent(self.__playerAvatar.eEnterWorldEvent, self.__onEnterWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.eEnterWorldEvent, clientArena.initArenaData)
        self.__linkPreWorldEvent(self.__playerAvatar.eEnterWorldEvent, clientArena.createGameMode)
        self.__linkPreWorldEvent(self.__playerAvatar.eEnterWorldEvent, audio.onPlayerEnterWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.eEnterWorldEvent, replay.onEnterWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.eLeaveWorldEvent, audio.onPlayerLeaveWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.eLeaveWorldEvent, self.__onLeaveWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.eLeaveWorldEvent, replay.onLeaveWorld)
        self.__linkPreWorldEvent(self.__playerAvatar.onStateChanged, cam.onPlayerAvatarStateChanged)
        self.__linkPreWorldEvent(self.__playerAvatar.eReportDestruction, cam.onReportPlayerDestruction)
        self.__linkPreWorldEvent(clientArena.onGameModeCreate, hints.onGameModeCreate)
        self.__linkPreWorldEvent(input.eAddProcessorListeners, cam.addInputListeners)
        self.__linkPreWorldEvent(input.eAddProcessorListeners, self.__playerAvatarProxy.addInputListeners)
        self.__linkPreworldHudEvents(clientArena, input, cam)

    def __linkPreworldHudEvents(self, clientArena, input, cam):
        hud = self.__services['HUD']
        chat = self.__services['Chat']
        hints = self.__services['BattleHints']
        input = self.__services['Input']
        self.__linkPreWorldEvent(self.eSetTargetEntity, cam.setTargetEntity)
        self.__linkPreWorldEvent(clientArena.onReceiveTextMessage, chat.showTextMessage)
        self.__linkPreWorldEvent(clientArena.onBattleMessageReactionResult, chat.showBattleMessageReactionResult)
        self.__linkPreWorldEvent(clientArena.onGainAward, hud.reportGainAward)
        self.__linkPreWorldEvent(clientArena.onRecreateAvatar, hud.restartHUD_QA)
        self.__linkPreWorldEvent(self.eOnDenyCursorHideChanged, hud.onDenyCursorHideChanged)
        self.__linkPreWorldEvent(self.eOnDenyCursorHideChanged, input.onDenyCursorHideChanged)
        self.__linkPreWorldEvent(input.eAddProcessorListeners, hud.addInputListeners)
        self.__linkPreWorldEvent(input.eAddProcessorListeners, chat.addInputListeners)
        self.__linkPreWorldEvent(input.eAddProcessorListeners, hints.addInputListeners)
        self.__linkPreWorldEvent(clientArena.onApplyArenaData, hints.applyArenaData)

    def __unlinkPreWorldEvents(self):
        self.__preWorldEvents.reverse()
        for ev, fn in self.__preWorldEvents:
            ev -= fn

        self.__preWorldEvents = []

    def __linkEvent(self, event, func):
        event += func
        self.__events.append((event, func))

    def __linkEvents(self):
        clientArena = self.__services['ClientArena']
        input = self.__services['Input']
        cam = self.__services['Camera']
        stats = self.__services['ClientStatsCollector']
        replay = BattleReplay.g_replay
        timerService = self.getTimer()
        audio = GameSound()
        DebugHUD = self.__services.get('DebugHUD')
        self.__linkEvent(GlobalEvents.onHideModalScreen, input.onHideModalScreen)
        self.__linkEvent(self.__playerAvatar.onUpdateArena, clientArena.doUpdateArena)
        self.__linkEvent(self.__playerAvatar.eArenaLoaded, replay.onArenaLoaded)
        self.__linkEvent(self.__playerAvatar.eArenaLoaded, audio.onArenaLoaded)
        self.__linkEvent(self.__playerAvatar.eFlyKeyBoardInputAllowed, input.onFlyKeyBoardInputAllowed)
        self.__linkEvent(self.__playerAvatar.onReceiveServerData, cam.update)
        self.__linkEvent(self.__playerAvatar.eUpdateSpectator, cam.updateSpectator)
        self.__linkEvent(self.__playerAvatar.eFlyKeyBoardInputAllowed, cam.onFlyKeyBoardInputAllowed)
        self.__linkEvent(self.__playerAvatar.eFlyKeyBoardInputAllowed, replay.onFlyKeyBoardInputAllowed)
        self.__linkEvent(self.__playerAvatar.eStartCollectClientStats, stats.startCollectClientStats)
        self.__linkEvent(self.__playerAvatar.eStopCollectClientStats, stats.stopCollectClientStats)
        self.__linkEvent(self.__playerAvatar.onStateChanged, input.onPlayerAvatarStateChanged)
        self.__linkEvent(GlobalEvents.onKeyEvent, input.handleKeyEvent)
        self.__linkEvent(GlobalEvents.onMouseEvent, input.processMouseEvent)
        self.__linkEvent(GlobalEvents.onAxisEvent, input.processJoystickEvent)
        self.__linkEvent(GlobalEvents.onSetFocus, input.onSetFocus)
        if not BattleReplay.isPlaying():
            self.__linkEvent(Settings.g_instance.eSetSniperMode, replay.notifySniperModeType)
            self.__linkEvent(Settings.g_instance.eSetSniperMode, cam.setSniperModeType)
        self.__linkEvent(Settings.g_instance.eCameraEffectsSetEnabled, cam.setEffectsEnabled)
        self.__linkEvent(Settings.g_instance.eMaxMouseCombatFovChanged, cam.setMaxMouseCombatFov)
        self.__linkEvent(input.eSideViewPressed, cam.onEnterSideView)
        self.__linkEvent(input.eSideViewReleased, cam.onLeaveSideView)
        self.__linkEvent(input.eInputProfileChange, cam.onInputProfileChange)
        self.__linkEvent(input.eBattleModeChange, cam.onBattleModeChange)
        self.__linkEvent(input.eBattleModeChange, audio.camera.onBattleModeChange)
        self.__linkEvent(clientArena.onReportBattleResult, replay.onBattleResultsReceived)
        self.__linkEvent(self.__playerAvatar.onStateChanged, audio.onPlayerStateChanged)
        self.__linkEvent(self.__playerAvatar.eVictimInformAboutCrit, audio.ui.onVictimInformAboutCrit)
        self.__linkEvent(self.__playerAvatar.ePartStateChanged, audio.ui.onPartStateChanging)
        if DebugHUD and SkillsDebugEnabled:
            self.__linkEvent(self.__playerAvatar.eUniqueSkillStateChanged, DebugHUD.updateAvaibleSkills)
            self.__linkEvent(self.__playerAvatar.eRestartInput, DebugHUD.clearSkills)
        self.__linkHudEvents(clientArena, input)

    def __linkHudEvents(self, clientArena, input):
        hud = self.__services['HUD']
        chat = self.__services['Chat']
        hints = self.__services['BattleHints']
        self.__linkEvent(input.eVisibilityChat, chat.switchChat)
        self.__linkEvent(self.eAllIntreClosed, chat.onAllIntreClosed)
        self.__linkEvent(GlobalEvents.onScreenshot, chat.screenShotNotification)
        self.__linkEvent(clientArena.onReceiveMarkerMessage, chat.onReceiveMarkerMessage)
        self.__linkEvent(self.__playerAvatarProxy.ePartFlagSwitchedNotification, hints.onPartFlagSwitchedNotification)
        self.__linkEvent(self.__playerAvatarProxy.ePartStateChanged, hints.onPartStateChanging)
        self.__linkEvent(self.__playerAvatar.eEngineOverheat, hints.reportEngineOverheat)
        self.__linkEvent(self.__playerAvatar.eReportNoShell, hints.reportNoShell)
        self.__linkEvent(self.__playerAvatar.onAutopilotEvent, hints.autopilot)
        self.__linkEvent(self.__playerAvatarProxy.eOnGunGroupFire, hints.onGunGroupFire)

    def __unlinkEvents(self):
        self.__events.reverse()
        for ev, fn in self.__events:
            ev -= fn

        self.__events = []

    def getTimer(self):
        """
        :return: client.TimerService.TimerService
        """
        return self.service(TIMER_SERVICE)

    def service(self, serviceName):
        if self.__isStarted:
            return self.__services[serviceName]
        else:
            return None
            return None

    def __createServices(self):
        self.__services[TIMER_SERVICE] = TimerService()
        self.__services['ClientArena'] = ClientArena()
        self.__services['HUD'] = gui.hud.HUD()
        self.__services['Input'] = InputController()
        self.__services['Camera'] = Camera()
        self.__services['ClientStatsCollector'] = ClientStatsCollector()
        self.__services['ClientEconomics'] = ClientEconomic()
        self.__services['Chat'] = Chat()
        self.__services['BattleHints'] = Messenger(self)
        self.__services['GamePlayHints'] = GamePlayHints()
        if consts.IS_DEBUG_IMPORTED:
            from debug.AvatarDebug import AvatarDebugService
            self.__services['DebugHUD'] = AvatarDebugService()

    def __initServices(self):
        for s in self.__services.values():
            s.init(self)

    def __onEnterWorld(self):
        self.__linkEvents()
        for s in self.__services.values():
            s.afterLinking()

    def __onLeaveWorld(self):
        self.__unlinkEvents()
        for s in self.__services.values():
            s.doLeaveWorld()

    def __destroyServices(self):
        self.__unlinkPreWorldEvents()
        for s in self.__services.values():
            s.destroy()
            del s

        self.__services.clear()

    def getGlobalID(self):
        clientArena = getClientArena()
        if clientArena is None:
            return 0
        else:
            avatarInfo = clientArena.avatarInfos.get(self.__playerAvatar.id, None)
            if avatarInfo:
                airplaneInfo = avatarInfo.get('airplaneInfo', None)
                if airplaneInfo:
                    return airplaneInfo['globalID']
            return 0

    def isPlayerStarted(self):
        return self.__isStarted

    @property
    def playerAvatarProxy(self):
        return self.__playerAvatarProxy


def getGlobalID():
    global g_instance
    return g_instance.getGlobalID()


def getCamera():
    return g_instance.service('Camera')


def getInput():
    return g_instance.service('Input')


def getHUD():
    """
    :return: gui.hud.Hud
    """
    return g_instance.service('HUD')


def getChat():
    return g_instance.service('Chat')


def getDebugHUD():
    return g_instance.service('DebugHUD')


def getClientArena():
    return g_instance.service('ClientArena')


def getClientEconomics():
    return g_instance.service('ClientEconomics')


def getBattleHintMessenger():
    return g_instance.service('BattleHints')


def CreateGameEnvironment():
    global g_instance
    if g_instance is None:
        g_instance = GameEnvironment()
    return


CreateGameEnvironment()