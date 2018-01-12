# Embedded file name: scripts/client/BWPersonality.py
import BigWorld
import CompoundSystem
from gui.Scaleform.WaitingInfoHelper import WaitingInfoHelper
import time
from consts import WAITING_INFO_TYPE
_bwPersonalityStarted = time.time()
BigWorld.gameLoadingScreenSetProgress(0.242)
import GUI, Keys
from InitPlayerInfo import InitPlayerInfo, ClanExtendedInfo, CommandsFiredCounter
import Settings
import ResMgr
import config_consts
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_INFO, dump_mem_leaks_all, LOG_ERROR, LOG_WARNING
from messenger import g_xmppChatHandler
from gui.WindowsManager import g_windowsManager
import ClientLog
import VOIP
import GlobalEvents
from HelperFunctions import generateID, createIMessage
import consts
from clientConsts import NONBATTLE_MUSIC_THEME, INTRO_CAMERA_TIMELINE_POOL, COMPOUND_ALPHA_ANIM_SPEED
from gui.Scaleform.utils import RSSDownloader
BigWorld.gameLoadingScreenSetProgress(0.254)
import sys
from Helpers.i18n import localizeMessages
from ConnectionManager import connectionManager
from Helpers.cleaner import deleteOldFiles
from audio import GameSound
from CrewHelpers import DEFAULT_BOT_AVATAR_BODY_TYPE
from gui.Scaleform import main_interfaces
import fm
try:
    import debug
    BigWorld.gameLoadingScreenSetProgress(0.364)
except:
    if config_consts.IS_DEVELOPMENT:
        LOG_CURRENT_EXCEPTION()
    LOG_INFO('DEBUG LAYERS IS NOT LOADED')

import locale
try:
    locale.setlocale(locale.LC_TIME, '')
except locale.Error:
    LOG_CURRENT_EXCEPTION()

g_repeatKeyHandlers = set()
g_waitingInfoHelper = WaitingInfoHelper()
IGNORE_CACHE_TAG = 'ignoreDBCache'

def init(scriptConfig, engineConfig, userPreferences, customGraphicPrefs, loadingScreenGUI = None):
    global g_settings
    if not config_consts.SEND_CONSTS_TO_CLIENT:
        import db.DBLogic
        db.DBLogic.initDB(False, IGNORE_CACHE_TAG not in sys.argv)
    BigWorld.gameLoadingScreenSetProgress(0.965)
    import gc
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE | gc.DEBUG_INSTANCES | gc.DEBUG_SAVEALL)
    if consts.IS_DEBUG_IMPORTED:
        debug.init()
    Settings.g_instance = Settings.Settings(scriptConfig, engineConfig, userPreferences, customGraphicPrefs)
    g_settings = Settings.g_instance
    BigWorld.gameLoadingScreenSetProgress(0.992)
    ClientLog.g_instance.init(Settings.g_instance.userPrefs[Settings.KEY_CLIENT_LOGGING])
    ClientLog.g_instance.general('Client start.')
    for x in GUI.roots():
        GUI.delRoot(x)

    BigWorld.worldDrawEnabled(False)
    BigWorld.setRedefineKeysMode(True)
    CompoundSystem.setCompoundAlphaAnimSpeed(COMPOUND_ALPHA_ANIM_SPEED)
    g_windowsManager.start()
    if loadingScreenGUI:
        loadingScreenGUI.script.removeAllCallbacks()
        loadingScreenGUI.script.active(False)
    BigWorld.setScreenshotNotifyCallback(screenshotNotifyCallback)
    from account_helpers import ClanEmblemsCache
    ClanEmblemsCache.ClanEmblemsCache()
    import CameraZoomStatsCollector
    CameraZoomStatsCollector.CameraZoomStatsCollector()
    days = engineConfig.readInt('debug/logDayLimit', -1)
    if days >= 0:
        deleteOldFiles(BigWorld.getAppLogsDirectory(), days, '.log')
        deleteOldFiles(BigWorld.getAppLogsDirectory(), days, '.dmp')
    import BattleReplay
    BattleReplay.g_replay = BattleReplay.BattleReplay()
    BattleReplay.g_replay.deleteOldReplays()
    RSSDownloader.init()
    connectionManager.onConnected += onConnected
    connectionManager.onDisconnected += onDisconnected
    g_waitingInfoHelper.addWaitingInfo(WAITING_INFO_TYPE.BOOTSTRAP, time.time() - _bwPersonalityStarted)


def start():
    if consts.IS_DEBUG_IMPORTED:
        debug.start()


def fini():
    if consts.IS_DEBUG_IMPORTED:
        debug.fini()
    BigWorld.clearEntitiesAndSpaces()
    clearAccount()
    RSSDownloader.fini()
    Settings.g_instance.fini()
    g_windowsManager.destroy()
    BigWorld.setScreenshotNotifyCallback(None)
    from account_helpers import ClanEmblemsCache
    ClanEmblemsCache.g_clanEmblemsCache.close()
    import BattleReplay
    BattleReplay.g_replay.destroy()
    BattleReplay.g_replay = None
    g_xmppChatHandler.fini()
    dump_mem_leaks_all()
    return


def clearAccount():
    global g_AOGASNotifier
    global g_questSelected
    global g_connectedAccountID
    global g_lobbyCarouselHelper
    g_connectedAccountID = None
    g_initPlayerInfo.clanAbbrev = 0
    g_initPlayerInfo.clanDBID = 0
    g_initPlayerInfo.clanAttrs = 0
    g_initPlayerInfo.requestStats = 0
    g_clanExtendedInfo.resetAttrs()
    g_questSelected = None
    g_waitingInfoHelper.clearWaitingStats()
    if g_lobbyCarouselHelper:
        g_lobbyCarouselHelper.destroy()
        g_lobbyCarouselHelper = None
    if g_AOGASNotifier:
        g_AOGASNotifier.destroy()
        g_AOGASNotifier = None
    VOIP.shutdown()
    return


def onStreamComplete(id, desc, data):
    player = BigWorld.player()
    if player is None:
        LOG_ERROR('onStreamComplete: no player entity available for process stream (%d, %s) data' % (id, desc))
    else:
        player.onStreamComplete(id, data)
    return


def screenshotNotifyCallback(path):
    GlobalEvents.onScreenshot(path)
    if g_windowsManager.activeMovie.className == main_interfaces.GUI_SCREEN_INTERVIEW:
        return
    else:
        player = BigWorld.player()
        from Account import PlayerAccount
        if player != None and player.__class__ == PlayerAccount:
            msgid, ob = createIMessage(consts.MESSAGE_TYPE.SCREENSHOT, localizeMessages('LOBBY_MSG_SCREENSHOT').format(adress=path), msgHeader=localizeMessages('LOBBY_HEADER_SCREENSHOT'))
            player.responseSender([[msgid, 'message']], 'IMessage', ob)
        return


def onRecreateDevice():
    GlobalEvents.onRecreateDevice()


def handleSetFocus(state):
    GlobalEvents.onSetFocus(state)


def onMemoryCritical():
    dump_mem_leaks_all()
    BigWorld.dumpTextureManager()


def refreshScreenResolutionList():
    GlobalEvents.onRefreshResolutions()


def afterChangeVideoMode():
    Settings.g_instance.updateBlockSystemKeys()


def handleInputLangChangeEvent():
    GlobalEvents.onChangeLocale()
    return False


def onChangeEnvironments(inside):
    pass


def addChatMsg(someInt, msg):
    LOG_INFO('addChatMsg:', msg)


def handleKeyEvent(event):
    if event.key == 0:
        return False
    result = GlobalEvents.onKeyEvent(event)
    result = result and not event.isKeyDown() and event.key != Keys.KEY_SYSRQ
    return result


def handleMouseEvent(event):
    return GlobalEvents.onMouseEvent(event)


axis = {}

def handleAxisEvent(event):
    global axis
    if event.deviceId not in axis.keys():
        axis[event.deviceId] = {}
    axis[event.deviceId][event.axis] = event.value
    return GlobalEvents.onAxisEvent(event)


def onConnected():
    LOG_INFO('Client::onConnected')


def onDisconnected():
    LOG_INFO('Client::disconnected')
    clearAccount()
    g_lastBattleType = consts.ARENA_TYPE.NORMAL
    from Helpers import cache
    cache.destroy()
    from gui.Scaleform.Waiting import Waiting
    Waiting.hideAll()


qaCommands = {}

def holdCommand(commandID, flag):
    global qaCommands
    if flag:
        qaCommands[commandID] = 1
    else:
        qaCommands.pop(commandID, None)
    import InputMapping
    keyCodes = InputMapping.g_instance.keyboardSettings.getCommandKeys(commandID)
    if keyCodes:
        if len(keyCodes) > 0:
            from input.InputController import UserKeyEvent
            keyInfo = keyCodes[0]
            handleKeyEvent(UserKeyEvent(keyInfo['code'], keyInfo['device']))
        else:
            LOG_WARNING('!!!there is not one key mapped to command', commandID)
    else:
        LOG_ERROR('!!!invalid command', commandID, 'to hold')
    return


def pressCommand(commandID):
    qaCommands[commandID] = 1
    import InputMapping
    keyCodes = InputMapping.g_instance.keyboardSettings.getCommandKeys(commandID)
    if keyCodes:
        if len(keyCodes) > 0:
            from input.InputController import UserKeyEvent
            keyInfo = keyCodes[0]
            handleKeyEvent(UserKeyEvent(keyInfo['code'], keyInfo['device']))
        else:
            LOG_WARNING('!!!there is not one key mapped to command', commandID)
    else:
        LOG_ERROR('!!!invalid command', commandID, 'to press')
    qaCommands.pop(commandID, None)
    return


g_connectedAccountID = None
g_lobbyCarouselHelper = None
g_initGame = False
g_lastBattleType = consts.ARENA_TYPE.NORMAL
g_AOGASNotifier = None
g_initPlayerInfo = InitPlayerInfo({})
g_premiumData = None
g_gamesPlayed = 0
g_loadLoginTime = 0.0
g_loadLobbyTime = 0.0
g_clanExtendedInfo = ClanExtendedInfo()
g_commandsFiredCounter = CommandsFiredCounter()
g_lastTimeInQueue = 0.0
g_lobbyInterview = [None, None]
g_lastMapID = -1
g_lobbyCrewBodyType = DEFAULT_BOT_AVATAR_BODY_TYPE
g_lobbyCrewLastNationID = None
g_fromOutro = False
g_settings = None

def getNextIntroTimeline():
    if not INTRO_CAMERA_TIMELINE_POOL:
        return None
    else:
        from itertools import cycle
        self = getNextIntroTimeline
        if not hasattr(self, 'gen'):
            self.gen = (timeline for timeline in cycle(INTRO_CAMERA_TIMELINE_POOL))
        return next(self.gen)


_PYTHON_MACROS = {'p': 'BigWorld.player()',
 't': 'BigWorld.target()',
 'B': 'BigWorld',
 'gc': 'import gc; gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS);gc.collect(2)',
 'gcd': 'import gc; gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS);from debug_utils import dump_garbage; dump_garbage()',
 'gcd2': 'from debug_utils import dump_garbage_2; dump_garbage_2'}

def expandMacros(line):
    import re
    patt = '\\$(' + reduce(lambda x, y: x + '|' + y, _PYTHON_MACROS.iterkeys()) + ')(\\W|\\Z)'

    def repl(match):
        return _PYTHON_MACROS[match.group(1)] + match.group(2)

    return re.sub(patt, repl, line)