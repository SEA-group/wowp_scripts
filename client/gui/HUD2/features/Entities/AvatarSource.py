# Embedded file name: scripts/client/gui/HUD2/features/Entities/AvatarSource.py
from EntitySource import EntitySource

class AvatarSource(EntitySource):

    def __init__(self, model, entity, playerIndex):
        EntitySource.__init__(self, model, entity, playerIndex)
        entity.eRepair += self._eRepair

    def update(self):
        EntitySource.update(self)
        self._model.isRepair = self._entity.repair > 0 and self._entity.isUnderRepairZoneInfluence > 0

    def _eRepair(self, value):
        self._model.isRepair = value > 0 and self._entity.isUnderRepairZoneInfluence > 0

    def dispose(self):
        self._entity.eRepair -= self._eRepair
        EntitySource.dispose(self)