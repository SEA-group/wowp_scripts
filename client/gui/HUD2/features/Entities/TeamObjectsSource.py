# Embedded file name: scripts/client/gui/HUD2/features/Entities/TeamObjectsSource.py
from math import ceil
import BigWorld
import BWLogging
from EntityHelpers import EntitySupportedClasses
from GameModeSettings.ACSettings import GROUND_OBJECT_TYPE, REPAIR_ZONE
from Helpers import TeamObjectHelper
from Helpers.i18n import localizeObject
from consts import WORLD_SCALING
from gui.HUD2.features.Entities.EntitySource import EntitySource
from gui.HUD2.hudFeatures import Feature
from turrets import TurretsSchemeFactory
from gui.HUD2.features.Entities import getClientTeamIndex
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS

class TeamObjectsSource:

    def __init__(self, model, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._teamObjects = model
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._playerTeamIndex = self._playerAvatar.teamIndex
        self._underRockerAttackScope = {}
        self._sources = dict()
        self._subscribe()

    def _subscribe(self):
        self._gameEnvironment.eTOPartChanged += self._onTOPartChanged
        if self._clientArena.isAllTeamObjectsDataReceived():
            self._onReceiveAllTeamObjectsData()
        else:
            self._clientArena.onReceiveAllTeamObjectsData += self._onReceiveAllTeamObjectsData
        self._clientArena.onReceiveTeamObjectsDataUpdate += self._onReciveUpdatedObjectData
        self._clientArena.gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_TARGET_OBJECT_CHANGED, self._eRocketAttackTarget)
        self._clientArena.gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_HIT_TARGET, self._eRocketAttackEnd)

    def _onTeamObjectAdded(self, teamObject):
        model = self._teamObjects.first(lambda e: e.id.get() == teamObject.id)
        if model is not None:
            self._createTeamObject_EntitySource(teamObject, model)
        return

    def _onTeamObjectRemoved(self, teamObject, isLeaveWorld):
        model = self._teamObjects.first(lambda o: o.id.get() == teamObject.id)
        if model is not None:
            model.inWorld = False
            source = self._sources.get(teamObject.id)
            if source is not None:
                source.dispose()
                del self._sources[teamObject.id]
        return

    def _createTeamObject_EntitySource(self, teamObject, model):
        model.inWorld = True
        isHigh = model.turretName.get() == 't_h'
        if len(model.parts) == 0:
            parts = teamObject.getPartsTypeData(None, True)
            for d in parts:
                model.parts.append(id=d['partId'], partType=TeamObjectHelper.getPartTypeIndex(d['isFiring'], d['isArmored'], isHigh), isDead=d['isDead'])

        source = EntitySource(model, teamObject, self._playerTeamIndex, True)
        if teamObject.id in self._sources:
            self._sources[teamObject.id].dispose()
        self._sources[teamObject.id] = source
        return

    def _updateTeamObject_EntitySource(self, objID, params):
        model = self._teamObjects.first(lambda o: o.id.get() == objID)
        if model:
            self._check_underRockerAttackScope(model, params)
            model.teamIndex = getClientTeamIndex(params['teamIndex'], self._playerTeamIndex)
            model.isAliveOutOfAOI = params['isAlive']

    def _onReceiveAllTeamObjectsData(self):
        for objID, objData in self._clientArena.allObjectsData.iteritems():
            if objData['classID'] == EntitySupportedClasses.TeamObject:
                entity = BigWorld.entities.get(objID)
                inWorld = entity is not None
                objectType, featureRadius = self._getTypeRadius(objData)
                position = self._clientArena.alwaysVisibleObjects.getMapEntry(objID).position
                settings = objData['settings']
                model = self._teamObjects.append(id=objID, position={'x': position.x,
                 'y': position.z}, maxHealth=int(ceil(objData['maxHealth'])), objectType=objectType, featureRadius=float(featureRadius), turretName=settings.turretName, objectName=localizeObject(settings.name), underRocketAttack=self._underRockerAttackScope.get(objID, False))
                if inWorld:
                    self._createTeamObject_EntitySource(entity, model)
                else:
                    model.inWorld = False

        self._gameEnvironment.eAvatarAdded += self._onTeamObjectAdded
        self._gameEnvironment.eAvatarRemoved += self._onTeamObjectRemoved
        return

    def _onReciveUpdatedObjectData(self):
        for objID, params in self._clientArena.updatedObjectsData.iteritems():
            self._updateTeamObject_EntitySource(objID, params)

    def _eRocketAttackTarget(self, sectorId, sectorTeamIndex, targetId):
        if sectorTeamIndex == self._playerTeamIndex:
            self._set_underRocketAttack(targetId, 1)

    def _eRocketAttackEnd(self, sectorId, sectorTeamIndex, targetId):
        if sectorTeamIndex == self._playerTeamIndex:
            self._set_underRocketAttack(targetId, -1)

    def _set_underRocketAttack(self, objID, attack):
        teamObjectModel = self._teamObjects.first(lambda o: o.id.get() == objID)
        if teamObjectModel:
            attackCount = self._underRockerAttackScope.get(objID, 0)
            self._underRockerAttackScope[objID] = max(0, attackCount + attack)
            teamObjectModel.underRocketAttack = self._underRockerAttackScope[objID] > 0

    def _check_underRockerAttackScope(self, model, params):
        if self._playerTeamIndex == params['teamIndex'] and model.id.get() in self._underRockerAttackScope:
            del self._underRockerAttackScope[model.id.get()]
            model.underRocketAttack = False

    def _getTypeRadius(self, objData):
        t = objData['ACType']
        r = 0.0
        if t == GROUND_OBJECT_TYPE.REPAIR:
            r = REPAIR_ZONE.RADIUS * WORLD_SCALING
        else:
            turretName = objData['settings'].turretName
            if turretName:
                isHigh = turretName == 't_h'
                battleLevel = self._playerAvatar.battleLevel
                scheme = TurretsSchemeFactory.getTurretsSchemeByBattleLevel(battleLevel, isHigh)
                if isHigh:
                    r = scheme.HighTargetShootDistanceRadius
                else:
                    r = scheme.TargetLockDistance
        return (t, r)

    def _onTOPartChanged(self, toId, partId, isDead):
        to = self._teamObjects.first(lambda o: o.id.get() == toId)
        if to:
            part = to.parts.first(lambda o: o.id.get() == partId)
            if part:
                if part.isDead.get() != isDead:
                    part.isDead = isDead
        else:
            self._logger.error('onTOPartChanged: TeamObject is None: id = {0}, partID = {1}, isDead = {2}'.format(toId, partId, isDead))

    def dispose(self):
        self._clientArena.gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_TARGET_OBJECT_CHANGED, self._eRocketAttackTarget)
        self._clientArena.gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_HIT_TARGET, self._eRocketAttackEnd)
        self._clientArena.onReceiveTeamObjectsDataUpdate -= self._onReciveUpdatedObjectData
        self._clientArena.onReceiveAllTeamObjectsData -= self._onReceiveAllTeamObjectsData
        self._gameEnvironment.eAvatarAdded -= self._onTeamObjectAdded
        self._gameEnvironment.eAvatarRemoved -= self._onTeamObjectRemoved
        self._gameEnvironment.eTOPartChanged -= self._onTOPartChanged
        for source in self._sources.itervalues():
            source.dispose()

        self._sources = {}