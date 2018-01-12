# Embedded file name: scripts/client/gui/HUD2/features/Entities/EntitiesSource.py
from math import ceil
from debug_utils import LOG_DEBUG
import BWLogging
import BigWorld
from Helpers.i18n import localizeAirplane
from consts import ACNPCTypes
from EventHelpers import EventSubscription, CompositeSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Entities import getClientTeamIndex, getLogicState, checkLost
from gui.HUD2.features.Entities.AvatarSource import AvatarSource
from gui.HUD2.features.Entities.EntitySource import EntitySource
from gui.HUD2.features.Entities.TeamObjectsSource import TeamObjectsSource
from gui.HUD2.features.Entities.TempVisibleObjectsSource import TempVisibleObjectsSource
from gui.HUD2.hudFeatures import Feature

class EntitiesSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).entities
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._db = features.require(Feature.DB_LOGIC)
        self._planeConfigurationsDB = features.require(Feature.PLANES_CONFIGURATIONS_DB)
        self._playerTeamIndex = self._playerAvatar.teamIndex
        self._playerAvatar.eTacticalSpectator += self._hideAvatarData
        self._teamObjectsSource = TeamObjectsSource(self._model.teamObjects, features)
        self._tempVisibleObjectsSource = TempVisibleObjectsSource(self._model, features)
        self._lastTacticalSpectatorID = self._playerAvatar.id
        self._sources = {}
        self._subscribe()

    def _subscribe(self):
        self._subscription = CompositeSubscription(EventSubscription(self._clientArena.onAvatarPlaneTypeRankChanged, self._updateAvatarPlaneTypeRank), EventSubscription(self._clientArena.onAvatarPlaneTypeRankChanged, self._updatePlaneScoresData), EventSubscription(self._clientArena.onPlayerEconomicExtDataReceived, self._updatePlaneScoresData), EventSubscription(self._clientArena.onAvatarChangedPlane, self._updateAvatarPlaneTypeRank), EventSubscription(self._clientArena.onAvatarEnterWorld, self._onAvatarEnterWorld), EventSubscription(self._clientArena.onAvatarLeaveWorld, self._onAvatarLeaveWorld), EventSubscription(self._clientArena.onEconomicPlayersPoints, self._onPlayersPoints), EventSubscription(self._clientArena.onUpdatePlayerStats, self._onUpdatePlayerStats))
        self._subscription.subscribe()
        if self._clientArena.isAllServerDataReceived():
            self._onNewAvatarsInfo(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._onNewAvatarsInfo
        return

    def _onNewAvatarsInfo(self, avatarInfos):
        self._clientArena.onNewAvatarsInfo -= self._onNewAvatarsInfo
        for avatarInfo in self._clientArena.avatarInfos.values():
            id_ = avatarInfo['avatarID']
            if avatarInfo['isNPC'] and avatarInfo['NPCType'] == ACNPCTypes.Bomber:
                bomberModel = self._onNewBomber(id_, avatarInfo)
                self._checkBombersWithEntity(id_, bomberModel)
            else:
                self._onNewAvatar(id_, avatarInfo)

    def _checkBombersWithEntity(self, bomberID, bomberModel):
        entity = BigWorld.entities.get(bomberID)
        if entity is not None:
            if entity.inWorld:
                self._updateAvatarOnEnterWorld(entity, bomberModel)
        return

    def _hideAvatarData(self, *args, **kwargs):
        model = self._getEntityModel(self._lastTacticalSpectatorID)
        if model is not None:
            entity = BigWorld.entities.get(self._lastTacticalSpectatorID)
            if entity is not None:
                model.inWorld = entity.inWorld
        model = self._getEntityModel(self._playerAvatar.id)
        if model is not None:
            model.inWorld = False
        self._lastTacticalSpectatorID = self._playerAvatar.id
        return

    def _onNewAvatar(self, id, avatarInfo):
        entity = BigWorld.entities.get(id)
        if entity:
            self._addAvatarFromEntity(entity, avatarInfo, id)
        else:
            self._addAvatarFromInfo(avatarInfo, id)
        self._updatePlaneScoresData(id)

    def _onNewBomber(self, id, avatarInfo):
        LOG_DEBUG('EntitySource :: _onNewBomber', id)
        settings = avatarInfo.get('settings')
        return self._model.bombers.append(id=id, planeName=localizeAirplane(settings.airplane.name), playerName=avatarInfo['playerName'], teamIndex=getClientTeamIndex(avatarInfo['teamIndex'], self._playerAvatar.teamIndex), maxHealth=int(ceil(avatarInfo['maxHealth'])), inWorld=False)

    def _addAvatarFromEntity(self, entity, avatarInfo, id):
        if id == self._playerAvatar.id:
            return
        avatarModel = self._addAvatarFromInfo(avatarInfo, id)
        self._updateAvatarOnEnterWorld(entity, avatarModel)

    def _addAvatarFromInfo(self, avatarInfo, id):
        settings = avatarInfo.get('settings')
        if not settings:
            globalID = avatarInfo['airplaneInfo']['globalID']
            import _airplanesConfigurations_db
            planeID = _airplanesConfigurations_db.getAirplaneConfiguration(globalID).planeID
            settings = self._db.getAircraftData(planeID)
        untypedName = avatarInfo.get('playerName', '')
        globalID = avatarInfo['airplaneInfo']['globalID']
        currentPlaneType = settings.airplane.planeType
        currentRankID = avatarInfo['planeTypeRank'][currentPlaneType]
        if type(untypedName) is unicode:
            playerName = untypedName
        else:
            playerName = unicode(untypedName, 'utf-8')
        return self._model.avatars.append(id=id, playerName=playerName, planeGlobalID=globalID, isDefender=bool(avatarInfo.get('defendSector')), isBot=bool(avatarInfo.get('databaseID') == 0), planeType=settings.airplane.planeType, planeName=localizeAirplane(settings.airplane.name), planeLevel=settings.airplane.level, previewIconPath=settings.airplane.previewIconPath, teamIndex=getClientTeamIndex(avatarInfo['teamIndex'], self._playerAvatar.teamIndex), squadIndex=avatarInfo['squadID'], maxHealth=int(ceil(avatarInfo['maxHealth'])), points=avatarInfo['economics']['totalBattlePoints'], inWorld=False, state=getLogicState(avatarInfo), isLost=checkLost(avatarInfo), rankID=currentRankID)

    def _onUpdatePlayerStats(self, avatarInfo):
        self._updateStateAvatarInfo(avatarInfo)

    def _onPlayersPoints(self, data):
        for id, points in data.iteritems():
            avatarModel = self._model.avatars.first(lambda e: e.id.get() == id)
            if avatarModel:
                avatarModel.points = points

    def _updateAvatarOnEnterWorld(self, entity, avatarModel):
        avatarModel.inWorld = True
        from Bomber import Bomber
        if not isinstance(entity, Bomber):
            self._updatePlaneIfChanged(entity, avatarModel)
            source = AvatarSource(avatarModel, entity, self._playerTeamIndex)
        else:
            source = EntitySource(avatarModel, entity, self._playerTeamIndex, isBomber=True)
            LOG_DEBUG('EntitySource :: _updateAvatarOnEnterWorld')
        if entity.id in self._sources:
            self._sources[entity.id].dispose()
        self._sources[entity.id] = source

    def _updatePlaneIfChanged(self, entity, avatarModel):
        settings = entity.settings
        newPlaneName = localizeAirplane(settings.airplane.name)
        if newPlaneName != avatarModel.planeName.get():
            avatarModel.planeName = newPlaneName
            avatarModel.planeType = settings.airplane.planeType
            avatarModel.planeLevel = settings.airplane.level

    def _onAvatarEnterWorld(self, entity):
        if not entity.id not in self._sources:
            raise AssertionError
            avatarModel = self._getEntityModel(entity.id)
            avatarModel is not None and self._updateAvatarOnEnterWorld(entity, avatarModel)
        return

    def _onAvatarLeaveWorld(self, entity):
        avatarModel = self._getEntityModel(entity.id)
        if avatarModel is not None:
            avatarModel.inWorld = False
            source = self._sources.get(entity.id)
            if source:
                source.dispose()
                del self._sources[entity.id]
        return

    def _getEntityModel(self, id):
        avatarModel = self._model.avatars.first(lambda e: e.id.get() == id)
        if avatarModel is None:
            avatarModel = self._model.bombers.first(lambda e: e.id.get() == id)
        return avatarModel

    def _updateStateAvatarInfo(self, avatarInfo):
        if avatarInfo:
            avatarID = avatarInfo['avatarID']
            avatarModel = self._model.avatars.first(lambda e: e.id.get() == avatarID)
            if avatarModel:
                logicState = getLogicState(avatarInfo)
                avatarModel.state = logicState
                isLost = checkLost(avatarInfo)
                if avatarModel.isLost.get() != isLost:
                    avatarModel.isLost = isLost

    def _updateAvatarPlaneTypeRank(self, avatarID, *args, **kwargs):
        """Update rank for avatar in model.
        :param avatarID: Identifier of Avatar to update 
        """
        avatarInfo = self._clientArena.avatarInfos[avatarID]
        settings = avatarInfo.get('settings')
        if not settings:
            globalID = avatarInfo['airplaneInfo']['globalID']
            import _airplanesConfigurations_db
            planeID = _airplanesConfigurations_db.getAirplaneConfiguration(globalID).planeID
            settings = self._db.getAircraftData(planeID)
        currentPlaneType = settings.airplane.planeType
        currentRankID = avatarInfo['planeTypeRank'][currentPlaneType]
        avatarModel = self._model.avatars.first(lambda e: e.id.get() == avatarID)
        if avatarModel:
            avatarModel.rankID = currentRankID

    def _updatePlaneScoresData(self, avatarID, *args, **kwargs):
        """Update score data for all avatar planes.
         Is called when avatar rank is changed and when new battle points received from server
        """
        avatarInfo = self._clientArena.avatarInfos[avatarID]
        economics = avatarInfo['economics']
        planeTypeRanks = avatarInfo['planeTypeRank']
        pointsByPlanes = economics['pointsByPlanes']
        if not pointsByPlanes:
            globalID = avatarInfo['airplaneInfo']['globalID']
            planeID = self._planeConfigurationsDB.getAirplaneConfiguration(globalID).planeID
            pointsByPlanes = [(planeID, 0)]
        avatarItem = self._model.avatars.first(lambda e: e.id.get() == avatarID)
        if not avatarItem:
            return
        for planeID, battlePoints in pointsByPlanes:
            planeData = self._db.getAircraftData(planeID)
            planeType = planeData.airplane.planeType
            scoreItem = avatarItem.planeScoresData.first(lambda e: e.planeID.get() == planeID)
            if scoreItem:
                scoreItem.battlePoints = battlePoints
                scoreItem.rankID = planeTypeRanks[planeType]
            else:
                avatarItem.planeScoresData.append(planeID=planeID, planeType=planeType, planeName=localizeAirplane(planeData.airplane.name), battlePoints=battlePoints, rankID=planeTypeRanks[planeType])

    def dispose(self):
        self._subscription.subscribe()
        self._subscription = None
        self._clientArena.onNewAvatarsInfo -= self._onNewAvatarsInfo
        self._playerAvatar.eTacticalSpectator -= self._hideAvatarData
        self._teamObjectsSource.dispose()
        self._tempVisibleObjectsSource.dispose()
        for source in self._sources.itervalues():
            source.dispose()

        self._sources = {}
        return