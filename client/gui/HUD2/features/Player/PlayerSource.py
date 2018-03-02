# Embedded file name: scripts/client/gui/HUD2/features/Player/PlayerSource.py
from math import ceil
from consts import BATTLE_MODE, PLANE_CLASS
from BWLogging import getLogger
from Helpers.i18n import localizeAirplane
from clientConsts import PREBATTLE_PLANE_TYPE_NAME
from EventHelpers import CompositeSubscription, EventSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Entities import getLogicState
from gui.HUD2.hudFeatures import Feature

class PlayerSource(DataSource):

    def __init__(self, features):
        self._db = features.require(Feature.DB_LOGIC)
        self._model = features.require(Feature.GAME_MODEL).player
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameEnv = features.require(Feature.GAME_ENVIRONMENT)
        self._input = features.require(Feature.INPUT)
        self._playerAvatar.eTacticalSpectator += self._reFillModel
        self._input.eBattleModeChange += self._onSetBattleMod
        self._battleMod = BATTLE_MODE.COMBAT_MODE
        self._log = getLogger(self)
        self._fellModel()

    def _fellModel(self):
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        self._fillPlaneData()
        return

    def _reFillModel(self, *args, **kwargs):
        self._setupModel(None)
        self._fillPlaneData()
        return

    def __subscribe(self):
        self._subscription = CompositeSubscription(EventSubscription(self._playerAvatar.eUpdateHealth, self._onUpdateHealth), EventSubscription(self._playerAvatar.onStateChanged, self._onStateChanged), EventSubscription(self._playerAvatar.eTacticalRespawnEnd, self._fillPlaneData), EventSubscription(self._gameEnv.ePlayerGunnerChangedTurret, self._updateModelShootingDistance))
        self._subscription.subscribe()

    def _onSetBattleMod(self, bState):
        if self._battleMod == BATTLE_MODE.GUNNER_MODE or bState == BATTLE_MODE.GUNNER_MODE:
            self._battleMod = bState
            self._updateModelShootingDistance()

    def _updateModelShootingDistance(self, *args, **kwargs):
        self._model.effectiveShootingDistance = self._getGunnerShootingDistance() if self._battleMod == BATTLE_MODE.GUNNER_MODE else self._getMainArmamentShootingDistance()
        self._model.shootingDistanceMax = self._getGunnerShootingDistance() if self._battleMod == BATTLE_MODE.GUNNER_MODE else self._getMainArmamentShootingDistanceMax()
        self._log.debug('new shooting distance effective: %s, new shooting distance max: %s', self._model.effectiveShootingDistance, self._model.shootingDistanceMax)

    def _getMainArmamentShootingDistance(self):
        playerGlobalID = self._playerAvatar.globalID
        return self._db.getShootingDistanceEffective(playerGlobalID)

    def _getMainArmamentShootingDistanceMax(self):
        playerGlobalID = self._playerAvatar.globalID
        return self._db.getShootingDistanceMax(playerGlobalID)

    def _getGunnerShootingDistance(self):
        gunner = self._playerAvatar.controlledGunner
        return gunner.shootDistance

    def _fillPlaneData(self, *args, **kwargs):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        playerGlobalID = self._playerAvatar.globalID
        settings = avatarInfo['settings']
        self._updateModelShootingDistance()
        self._model.planeName = localizeAirplane(settings.airplane.name)
        self._model.planeLevel = settings.airplane.level
        self._model.planeGlobalID = playerGlobalID
        self._model.planeType = settings.airplane.planeType
        self._model.planeTypeName = PREBATTLE_PLANE_TYPE_NAME[settings.airplane.planeType]
        self._model.planePreviewIcon = settings.airplane.previewIconPath
        self._model.planeId = self._playerAvatar.objTypeID
        self._model.planeStatus = self._getPlaneStatus()
        self._model.teamIndex = self._playerAvatar.teamIndex
        self._model.isReconnected = bool(self._playerAvatar.reconnected)

    def _getPlaneStatus(self):
        planeID = self._playerAvatar.objTypeID
        isPremium = self._db.isPlanePremium(planeID)
        isElite = planeID in self._playerAvatar.elitePlanes
        planeStatus = PLANE_CLASS.PREMIUM if isPremium else isElite * PLANE_CLASS.ELITE or PLANE_CLASS.REGULAR
        return planeStatus

    def _setupModel(self, newInfos):
        self.__subscribe()
        id = self._playerAvatar.id
        avatarInfo = self._clientArena.getAvatarInfo(id)
        self._model.id = id
        self._model.clanName = unicode(avatarInfo.get('clanAbbrev', ''))
        self._model.nickName = unicode(avatarInfo.get('playerName', 'unknown name'))
        self._model.health = int(ceil(self._playerAvatar.health))
        self._model.healthMax = int(ceil(self._playerAvatar.maxHealth))
        self._model.squadIndex = avatarInfo.get('squadID', 0)
        self._model.state = getLogicState(avatarInfo)

    def _onUpdateHealth(self, health, lastDamagerID, oldValue):
        self._model.health = int(ceil(health))

    def _onStateChanged(self, oldState, state):
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        self._model.state = getLogicState(avatarInfo)

    def dispose(self):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eTacticalSpectator -= self._reFillModel
        self._subscription.unsubscribe()
        self._subscription = None
        self._input.eBattleModeChange -= self._onSetBattleMod
        self._gameEnv = None
        self._playerAvatar = None
        self._clientArena = None
        self._model = None
        return