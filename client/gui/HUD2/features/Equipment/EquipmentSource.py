# Embedded file name: scripts/client/gui/HUD2/features/Equipment/EquipmentSource.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class EquipmentSource(DataSource):

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._model = features.require(Feature.GAME_MODEL).equipments
        from db.DBLogic import g_instance as db
        self._db = db
        self.equipments = self._playerAvatar.equipment
        for id in self.equipments:
            if id != -1:
                self._appendEquipment(self._model.equipments, id)

    def _appendEquipment(self, equipmentModelList, equipmentID):
        equipmentDB = self._db.getEquipmentByID(equipmentID)
        eqName = 'LOBBY_EQUIPMENT_NAME_' + equipmentDB.localizeTag
        equipmentModelList.append(id=equipmentID, iconPath=equipmentDB.icoPathHud, description=equipmentDB.description, equipmentName=eqName)

    def dispose(self):
        self._playerAvatar = None
        self._model = None
        self._db = None
        self.equipments = None
        return