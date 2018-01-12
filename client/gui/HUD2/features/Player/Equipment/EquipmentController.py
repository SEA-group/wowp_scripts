# Embedded file name: scripts/client/gui/HUD2/features/Player/Equipment/EquipmentController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.core.FeatureBroker import Require

class EquipmentController(DataController):
    playerAvatar = Require('PlayerAvatar')
    uiSound = Require('uiSound')

    def __init__(self, model):
        """
        :type model: EquipmentModel.EquipmentModel
        """
        self._model = model

    @message
    def useConsumable(self, slotID):
        """
        :type slotID: int
        """
        consumable = self._model.Consumables.get(slotID)
        if consumable is None:
            return
        else:
            if consumable.ChargesCount > 0 and consumable.CoolDownTill <= 0:
                self.playerAvatar.useConsumable(slotID)
            else:
                self.uiSound.play('HUDNoEquipment')
            return