# Embedded file name: scripts/client/gui/HUD2/features/PlayerInfo/PlayerInfoSource.py
from Helpers.i18n import localizeAirplane
from EventHelpers import CompositeSubscription, EventSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Entities import getLogicState
from gui.HUD2.hudFeatures import Feature

class PlayerInfoSource(DataSource):

    def __init__(self, features):
        self._db = features.require(Feature.DB_LOGIC)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._model = features.require(Feature.GAME_MODEL).currentPlayerInfo
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._planesConfigurationsDB = features.require(Feature.PLANES_CONFIGURATIONS_DB)
        self._subscription = CompositeSubscription(EventSubscription(self._playerAvatar.onStateChanged, self._onStateChanged), EventSubscription(self._playerAvatar.eTacticalRespawnEnd, self._fillPlaneData), EventSubscription(self._clientArena.onAvatarPlaneTypeRankChanged, self._onAvatarPlaneTypeRankChanged), EventSubscription(self._clientArena.onAvatarPlaneTypeRankChanged, self._updatePlaneScoresData), EventSubscription(self._clientArena.onPlayerEconomicExtDataReceived, self._updatePlaneScoresData))
        self._subscription.subscribe()
        self._fellModel()

    def _fellModel(self, *args, **kwargs):
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        self._fillPlaneData()
        return

    def _fillPlaneData(self, *args, **kwargs):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        settings = avatarInfo['settings']
        self._model.planeName = localizeAirplane(settings.airplane.name)
        self._model.planeLevel = settings.airplane.level
        self._model.planeGlobalID = self._playerAvatar.globalID
        self._model.id = self._playerAvatar.id
        self._model.planeType = settings.airplane.planeType
        self._model.teamIndex = self._playerAvatar.teamIndex
        if self._clientArena.isAllServerDataReceived():
            self._updatePlaneTypeRank()

    def _setupModel(self, newInfos):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        self._model.clanName = unicode(avatarInfo.get('clanAbbrev', ''))
        self._model.nickName = unicode(avatarInfo.get('playerName', 'unknown name'))
        self._model.squadIndex = avatarInfo.get('squadID', 0)
        self._model.state = getLogicState(avatarInfo)
        self._updatePlaneTypeRank()
        self._updatePlayerPlaneScoresData()

    def _onStateChanged(self, oldState, state):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        self._model.state = getLogicState(avatarInfo)

    def _onAvatarPlaneTypeRankChanged(self, avatarID, *args, **kwargs):
        if avatarID == self._bigWorld.player().id:
            self._updatePlaneTypeRank()

    def _updatePlaneTypeRank(self):
        id_ = self._bigWorld.player().id
        avatarInfo = self._clientArena.avatarInfos[id_]
        settings = avatarInfo['settings']
        planeType = settings.airplane.planeType
        self._model.rank = avatarInfo['planeTypeRank'][planeType]

    def _updatePlaneScoresData(self, avatarID, *args, **kwargs):
        """Update score data for all avatar planes.
         Is called when avatar rank is changed and when new battle points received from server
        """
        if avatarID == self._bigWorld.player().id:
            self._updatePlayerPlaneScoresData()

    def _updatePlayerPlaneScoresData(self):
        avatarInfo = self._clientArena.avatarInfos[self._bigWorld.player().id]
        economics = avatarInfo['economics']
        planeTypeRanks = avatarInfo['planeTypeRank']
        pointsByPlanes = economics['pointsByPlanes']
        if not pointsByPlanes:
            globalID = avatarInfo['airplaneInfo']['globalID']
            planeID = self._planesConfigurationsDB.getAirplaneConfiguration(globalID).planeID
            pointsByPlanes = [(planeID, 0)]
        for planeID, battlePoints in pointsByPlanes:
            planeData = self._db.getAircraftData(planeID)
            planeType = planeData.airplane.planeType
            scoreItem = self._model.planeScoresData.first(lambda e: e.planeID.get() == planeID)
            if scoreItem:
                scoreItem.battlePoints = battlePoints
                scoreItem.rankID = planeTypeRanks[planeType]
            else:
                self._model.planeScoresData.append(planeID=planeID, planeType=planeType, planeName=localizeAirplane(planeData.airplane.name), battlePoints=battlePoints, rankID=planeTypeRanks[planeType])

    def dispose(self):
        self._subscription.unsubscribe()
        self._subscription = None
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar = None
        self._clientArena = None
        self._model = None
        return