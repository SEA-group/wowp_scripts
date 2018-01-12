# Embedded file name: scripts/client/gui/HUD2/features/Entities/EntitySource.py
from math import ceil
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Entities import getClientTeamIndex
from debug_utils import LOG_DEBUG

class EntitySource(DataSource):

    def __init__(self, model, entity, playerIndex, isTeamObject = False, isBomber = False):
        self._model = model
        self._entity = entity
        self._playerIndex = playerIndex
        self._isTeamObject = isTeamObject
        self._isBomber = isBomber
        entity.eHealthChanged += self._eAvatarHealthChanged
        entity.eTeamIndexChanged += self._eTeamIndexChanged
        entity.eOnEntityStateChanged += self._eStateChanged
        if self._isTeamObject or isBomber:
            self._model.state = entity.state
        self.updateModelByEntityData()

    def updateModelByEntityData(self):
        if self._isBomber:
            LOG_DEBUG(' EntitySource :: updateModelByEntityData ', self._entity.id)
        self._model.health = int(ceil(self._entity.health))
        self._model.maxHealth = int(ceil(self._entity.maxHealth))
        self._model.teamIndex = getClientTeamIndex(self._entity.teamIndex, self._playerIndex)
        self._updateState(self._entity.state)
        if self._isTeamObject:
            self._model.isAliveOutOfAOI = self._entity.health > 0

    def _eAvatarHealthChanged(self, id, health, lastDamager, oldHealth, maxHealth):
        self._model.health = int(ceil(health))

    def _eTeamIndexChanged(self, teamIndex):
        self._model.teamIndex = getClientTeamIndex(teamIndex, self._playerIndex)

    @property
    def model(self):
        return self._model

    def _eStateChanged(self, id, oldState, state):
        self._updateState(state)

    def _updateState(self, state):
        if self._isTeamObject or self._isBomber:
            if self._isBomber:
                LOG_DEBUG(' EntitySource :: _updateState ', self._entity.id, state)
            self._model.state = state

    def dispose(self):
        self._model = None
        self._entity.eHealthChanged -= self._eAvatarHealthChanged
        self._entity.eTeamIndexChanged -= self._eTeamIndexChanged
        self._entity.eOnEntityStateChanged -= self._eStateChanged
        self._entity = None
        return