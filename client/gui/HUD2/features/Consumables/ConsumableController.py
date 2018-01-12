# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableController.py
import functools
import InputMapping
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.features.Consumables.ConsumableManager import ConsumableManager
from gui.HUD2.hudFeatures import Feature

class ConsumableController(DataController):

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        inputProcessor = features.require(Feature.INPUT).commandProcessor
        self._processor = inputProcessor
        self._consumableManager = ConsumableManager(features)
        self._consumableManager.initConsumables(self._playerAvatar.consumables, None)
        for command in InputMapping.EQUIPMENT_COMMANDS:
            self._processor.addListeners(command, functools.partial(self._useConsumbale, command))

        return

    def _useConsumbale(self, command):
        equipmentCommands = InputMapping.EQUIPMENT_COMMANDS
        if command in equipmentCommands:
            slotID = equipmentCommands.index(command)
            consumable = self._playerAvatar.consumables[slotID]
            if consumable['key'] != -1 and int(consumable['chargesCount']) != 0:
                if self._consumableManager.getStatusForConsumable(consumable['key']) != -1:
                    self._playerAvatar.cell.useConsumable(slotID, -1)

    def dispose(self):
        for command in InputMapping.EQUIPMENT_COMMANDS:
            self._processor.removeListeners(command, functools.partial(self._useConsumbale, command))

        self._processor = None
        self._playerAvatar = None
        self._consumableManager = None
        return