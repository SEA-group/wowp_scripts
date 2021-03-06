# Embedded file name: scripts/client/gui/Scaleform/Prebattle.py
import BigWorld
import Settings
import wgPickle
from Helpers.i18n import localizeLobby
from clientConsts import BATTLE_NAME_BY_TYPE_HUD_LOC_ID, BATTLE_DESC_BY_TYPE_HUD_LOC_ID, PLANE_TYPE_BATTLE_RESULT_ICO_PATH, PLANE_TYPES_ORDER, HUD_PLANE_TYPES_LOC_ID, CLASTERS
from consts import EMPTY_IDTYPELIST
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.windows import GUIWindowAccount

class _PrebattleVO:

    def __init__(self):
        self.package_ = 'wowp.prebattle.vo.'
        self.battleType = 0
        self.battleName = ''
        self.battleDescription = ''
        self.planeLevels = []
        self.planeTypes = []
        self.planeTypesIcon = []


class Prebattle(GUIWindowAccount):
    REJOIN_QUEUE_TIME = 30

    def __init__(self):
        GUIWindowAccount.__init__(self, 'loadingPrebattle.swf')
        self.updateCallback = -1
        self.__queueStatistic = None
        self.__lastCallTime = BigWorld.time()
        self.__iGameModesParams = None
        return

    def onGameModesParams(self, params):
        self.__iGameModesParams = params

    def initialized(self):
        LOG_DEBUG('init Prebattle')
        self.updateCallback = -1
        self.movie.backgroundAlpha = 1.0
        self.addExternalCallbacks({'prebattle.forceStart': self.onPrebattleForceStart})
        data = _PrebattleVO()
        data.planeTypesIcon = [ PLANE_TYPE_BATTLE_RESULT_ICO_PATH.icon(planeTypeId) for planeTypeId in PLANE_TYPES_ORDER ]
        data.planeTypes = [ localizeLobby(HUD_PLANE_TYPES_LOC_ID[planeTypeId]) for planeTypeId in PLANE_TYPES_ORDER ]
        player = BigWorld.player()
        from Account import PlayerAccount
        if player != None and player.__class__ == PlayerAccount:
            data.battleType = player.battleType
        else:
            data.battleType = self.__iGameModesParams['curMode']
        try:
            data.battleName = localizeLobby(BATTLE_NAME_BY_TYPE_HUD_LOC_ID[data.battleType])
            data.battleDescription = localizeLobby(BATTLE_DESC_BY_TYPE_HUD_LOC_ID[data.battleType])
        except KeyError:
            data.battleName = 'Battle name for type {} not provided'.format(data.battleType)
            data.battleDescription = 'Battle description for type {} not provided'.format(data.battleType)

        import BWPersonality
        lch = BWPersonality.g_lobbyCarouselHelper
        planeSelected = lch.getCarouselAirplaneSelected()
        if planeSelected:
            data.planeID = planeSelected.planeID
            data.level = planeSelected.level
            data.name = planeSelected.name
            data.longName = planeSelected.longName
            data.planeType = planeSelected.planeType
            data.type = planeSelected.type
            data.previewIconPath = planeSelected.previewIconPath
            data.hudIconPath = planeSelected.hudIconPath
            data.planeIconPath = planeSelected.planeIconPath
            data.isElite = planeSelected.isElite
            data.isPremium = planeSelected.isPremium
            from clientConsts import PLANE_TYPE_ICO_PATH, PLANE_CLASS
            planeStatus = planeSelected.isPremium * PLANE_CLASS.PREMIUM or planeSelected.isElite * PLANE_CLASS.ELITE or PLANE_CLASS.REGULAR
            data.planeTypeIconPath = PLANE_TYPE_ICO_PATH.icon(planeSelected.planeType, planeStatus)
        else:
            LOG_ERROR('Prebattle:initialized - planeSelected is None')
        GUIWindowAccount.initialized(self, data)
        if Settings.g_instance.clusterID == CLASTERS.CN:
            self._startTickerNews()
        return

    def dispossessUI(self):
        GUIWindowAccount.dispossessUI(self)
        if self.updateCallback != -1:
            BigWorld.cancelCallback(self.updateCallback)
            self.updateCallback = -1
        self.removeAllCallbacks()
        import BWPersonality
        BWPersonality.g_lastTimeInQueue = BigWorld.time() - self.__lastCallTime

    def setPrebattleStatistic(self, queueStatisticPacked):
        self.__queueStatistic = wgPickle.loads(wgPickle.FromServerToClient, queueStatisticPacked)

    def hideForceStartButton(self, needToHideButton):
        LOG_DEBUG('UI prebattle, hideForceStartButton', needToHideButton)
        self.call_1('showForceStart', not needToHideButton)

    def onPrebattleForceStart(self):
        print 'onPrebattleForceStart'
        player = BigWorld.player()
        from Account import PlayerAccount
        if player != None and player.__class__ == PlayerAccount:
            player.base.forceStartBalancerBattle()
        return

    def __onGetActiveQuest(self):
        LOG_DEBUG('UI prebattle, __onGetActiveQuest')
        self.viewIFace([[{'IQuestSelectConsist': {}}, EMPTY_IDTYPELIST]])