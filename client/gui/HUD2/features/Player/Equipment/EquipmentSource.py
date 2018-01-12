# Embedded file name: scripts/client/gui/HUD2/features/Player/Equipment/EquipmentSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.core.FeatureBroker import Require

class EquipmentSource(DataSource):
    db = Require('db')
    playerAvatar = Require('PlayerAvatar')

    def __init__(self, model):
        """
        :type model: EquipmentModel.EquipmentModel
        """
        self._model = model
        self._subscribe()

    def _subscribe(self):
        self.playerAvatar.eUpdateConsumables += self._onUpdateConsumables

    def _onUpdateConsumables(self, consumablesData):
        """
        :param consumablesData: CONSUMABLE_RECORD in alias.xml
        """
        for consumableRecord in consumablesData:
            consumablesID = consumableRecord['key']
            consumableStructure = self._model.Consumables.first(lambda e: e.ID.get() == consumablesID)
            if consumableStructure is None:
                self._appendConsumable(self._model.Consumables, consumableRecord)
            else:
                self._updateConsumable(consumableRecord, consumableStructure)

        return

    def _appendConsumable(self, consumablesModelList, consumableRecord):
        consumableID = consumableRecord['key']
        consumableDB = self.db.getConsumableByID(consumableID)
        consumablesModelList.append(ID=consumableID, IcoPath=consumableDB.icoPath, IcoPathBig=consumableDB.icoPathBig, Description=consumableDB.localizeTag, ChargesCount=consumableRecord['chargesCount'], CoolDownTill=consumableRecord['coolDownTill'], CoolDownTillMax=consumableDB.coolDownTime, ActiveTill=consumableRecord['activeTill'], ActiveTillMax=consumableDB.effectTime)

    def _updateConsumable(self, consumableRecord, consumableStructure):
        consumableStructure.ChargesCount = consumableRecord['chargesCount']
        consumableStructure.CoolDownTill = consumableRecord['coolDownTill']
        consumableStructure.ActiveTill = consumableRecord['activeTill']