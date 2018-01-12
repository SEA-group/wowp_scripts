# Embedded file name: scripts/client/gui/HUD2/features/HealthRepair/HealthRepairSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from GameModeSettings.ACSettings import LOW_HEALTH_STATE_PER_TYPE

class HealthRepairSource(DataSource):

    def __init__(self, features):
        self._db = features.require(Feature.DB_LOGIC)
        self._model = features.require(Feature.GAME_MODEL).healthRepair
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._setCritPoint()
        self._setRepairZone(False)
        self._setRepair(False)
        self._player.eTacticalSpectator += self._setModel
        self._player.eUnderRepairZoneInfluence += self._setRepairZone
        self._player.eTacticalRespawnEnd += self._setCritPoint
        self._player.eHealthChanged += self._setHealth
        self._player.eRepair += self._setRepair

    def _setModel(self, *args, **kwargs):
        self._setCritPoint()
        self._setRepairZone(False)
        self._setRepair(self._player.repair)

    def _setHealth(self, *args, **kwargs):
        self.__calcUnderRepairZoneInfluence()

    def _setRepairZone(self, *args, **kwargs):
        self.__calcUnderRepairZoneInfluence()

    def __calcUnderRepairZoneInfluence(self):
        isLowHp = self._player.health < self._player.maxHealth
        isZone = self._player.isUnderRepairZoneInfluence > 0
        self._model.isUnderRepairZoneInfluence = isZone and isLowHp

    def _setRepair(self, value):
        self._model.isRepair = value > 0

    def _setCritPoint(self, *args, **kwargs):
        self._model.critPoint = LOW_HEALTH_STATE_PER_TYPE.get(self._player.planeType, 0.0)

    def dispose(self):
        self._player.eTacticalSpectator -= self._setModel
        self._player.eUnderRepairZoneInfluence -= self._setRepairZone
        self._player.eTacticalRespawnEnd -= self._setCritPoint
        self._player.eHealthChanged -= self._setHealth
        self._player.eRepair -= self._setRepair
        self._player = None
        self._model = None
        self._db = None
        return