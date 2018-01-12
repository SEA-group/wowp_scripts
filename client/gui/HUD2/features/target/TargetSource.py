# Embedded file name: scripts/client/gui/HUD2/features/target/TargetSource.py
import BigWorld
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.HUDconsts import HUD_MODULE_DESTROYED
from debug_utils import LOG_ERROR, LOG_DEBUG

class TargetSource(DataSource):
    DAMAGE_TIMEOUT = 3.5

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).target
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._targetCurrentDamage = 0
        self._lastDamageTime = BigWorld.time()
        self._linkEvents()

    def dispose(self):
        self._gameEnvironment.eOnTargetEntity -= self.__onSelectTarget
        self._unlinkEvents()

    def _linkEvents(self):
        BigWorld.player().onAvatarLeaveWorldEvent += self._onEntityLeaveWorld
        self._gameEnvironment.eAvatarRemoved += self._onAvaratRemovingFromArena
        self._gameEnvironment.eOnTargetEntity += self.__onSelectTarget

    def _unlinkEvents(self):
        self._gameEnvironment.eAvatarRemoved -= self._onAvaratRemovingFromArena
        BigWorld.player().onAvatarLeaveWorldEvent -= self._onEntityLeaveWorld
        self._gameEnvironment.eOnTargetEntity -= self.__onSelectTarget

    def _onAvaratRemovingFromArena(self, entity, isLeaveWorld):
        if isLeaveWorld:
            self.__internalUnsubscribeEntity(entity=entity)

    def _onEntityLeaveWorld(self, player, entityId, entity):
        self.__internalUnsubscribeEntity(entity=entity)

    def __onSelectTarget(self, entityId):
        if self._model.targetId.get():
            self.__internalUnsubscribeEntity(entityID=self._model.targetId.get())
        self._model.targetId = entityId
        self.__internalSubscribeEntity(entityId)

    def __internalSubscribeEntity(self, entityId):
        from Avatar import Avatar
        from PlayerAvatar import PlayerAvatar
        self._targetCurrentDamage = 0
        if not entityId:
            return
        entity = BigWorld.entities.get(entityId)
        if not entity:
            LOG_ERROR('Target entity not found: {0}'.format(entityId))
            return
        entity.eHealthChanged += self._onTargetDamage
        if isinstance(entity, (Avatar, PlayerAvatar)):
            self._model.targetModules = self._getPartsDict(entity.partStates)
            entity.ePartStateChanged += self._onTargetPartChanged
        else:
            entity.eOnTeamObjectLeaveWorld += self._onEntityLeaveWorld

    def __internalUnsubscribeEntity(self, entityID = None, entity = None):
        from Avatar import Avatar
        from PlayerAvatar import PlayerAvatar
        if entityID:
            entity = BigWorld.entities.get(entityID)
        if not entity:
            return
        entity.eHealthChanged -= self._onTargetDamage
        if isinstance(entity, (Avatar, PlayerAvatar)):
            entity.ePartStateChanged -= self._onTargetPartChanged
        else:
            entity.eOnTeamObjectLeaveWorld -= self._onEntityLeaveWorld

    def _onTargetPartChanged(self, part):
        entity = BigWorld.entities.get(self._model.targetId.get())
        if entity:
            self._model.targetModules = self._getPartsDict(entity.partStates)

    def _getPartsDict(self, parts):
        entityID = self._model.targetId.get()
        entity = BigWorld.entities.get(entityID)
        airplane = entity.settings.airplane
        return {airplane.getPartByID(partID).getFirstPartType().componentType:partState for partID, partState in parts if partState == HUD_MODULE_DESTROYED}

    def _onTargetDamage(self, avatarId, health, lastDamagerID, oldHealth, maxHealth):
        damage = oldHealth - health
        if damage > 0:
            targetId = self._model.targetId.get()
            nowTime = BigWorld.time()
            differentAvatars = avatarId != targetId
            if differentAvatars or nowTime - self._lastDamageTime > self.DAMAGE_TIMEOUT:
                self._targetCurrentDamage = 0
                if differentAvatars:
                    LOG_ERROR('TargetSource error: targetId not equal Damaged! ({0} != {1})'.format(targetId, avatarId))
            self._lastDamageTime = nowTime
            self._targetCurrentDamage += damage
            self._model.targetCurrentDamage = self._targetCurrentDamage
            LOG_DEBUG('TargetSource._onTargetDamage: avatadId: {0}, mg_delta: {1}, hl_current: {2}'.format(avatarId, damage, health))