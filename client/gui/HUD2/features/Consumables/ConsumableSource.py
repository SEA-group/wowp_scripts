# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableSource.py
import BigWorld
import InputMapping
from _equipment_data import ModsTypeEnum
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization
from EntityHelpers import EntityStates
FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP = ['AUTO_RESTARTER',
 'AUTO_FIX_TAIL_AND_WINGS',
 'AUTO_EXTINGUISHER',
 'BLEED-STOPPER']

class ConsumableSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).consumables
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._consumableManager = features.require(Feature.CONSUMABLES_MANAGER)
        from db.DBLogic import g_instance as db
        self._db = db
        self._passiveList = [ModsTypeEnum.ECONOMIC_BONUS_CREDITS,
         ModsTypeEnum.ECONOMIC_BONUS_XP,
         ModsTypeEnum.SPARKLERS,
         ModsTypeEnum.COLOR_PLUMES]
        InputMapping.g_instance.onSaveControls += self.__updateControls
        self._consumableManager.eInitConsumables += self._onInitConsumables
        self._consumableManager.eUpdateConsumables += self._onUpdateConsumables
        self._consumableManager.eUpdateConsumableStatus += self._onUpdateConsumableStatus

    def _addBaseConsumable(self):
        equipmentCommands = InputMapping.EQUIPMENT_COMMANDS
        for index, consumableData in enumerate(self._playerAvatar.consumables):
            key = consumableData.id
            if key != -1:
                keyName = getKeyLocalization(equipmentCommands[index])
                self._appendConsumable(self._model.consumables, consumableData, keyName)

    def _appendConsumable(self, consumablesModelList, consumableRecord, keyName):
        consumableID = consumableRecord.id
        consumableDB = self._db.getConsumableByID(consumableID)
        cooldownTime = self._db.getConsumableByID(consumableID).coolDownTime
        respawnEndTime = int(round(consumableRecord.coolDownTill - BigWorld.serverTime()))
        consumablesModelList.append(id=consumableID, iconPath=consumableDB.icoPathHud, consumableName=consumableDB.name, description=consumableDB.description, amount=consumableRecord.chargesCount, isEmpty=False, isReadyOnRespawn=consumableDB.readyOnRespawn, coolDownTime=consumableDB.coolDownTime, key=keyName, status=0, isAuto=consumableDB.localizeTag in FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP, isPassive=self._checkModsForPassive(consumableDB), respawnEndTime=respawnEndTime, respawnStartTime=int(respawnEndTime - cooldownTime), activeEndTime=int(round(consumableRecord.activeTill - BigWorld.serverTime())))

    def _checkModsForPassive(self, consumableDB):
        isPassive = False
        for mod in consumableDB.mods:
            if mod.type in self._passiveList:
                isPassive = True
                break

        return isPassive

    def __updateControls(self):
        if self._playerAvatar is None:
            return
        else:
            if hasattr(self._playerAvatar, 'consumables'):
                equipmentCommands = InputMapping.EQUIPMENT_COMMANDS
                for index, consumableData in enumerate(self._playerAvatar.consumables):
                    key = consumableData.id
                    if key != -1:
                        keyName = getKeyLocalization(equipmentCommands[index])
                        consumableStructure = self._model.consumables.first(lambda e: e.id.get() == key)
                        consumableStructure.key = keyName

            return

    def _updateConsumable(self, playerConsumable, modelConsumable, status):
        modelConsumable.amount = playerConsumable.chargesCount
        consumableID = modelConsumable.id.get()
        activeEndTime = int(round(playerConsumable.activeTill - BigWorld.player().arenaStartTime))
        if modelConsumable.activeEndTime.get() != activeEndTime:
            modelConsumable.activeEndTime = activeEndTime
        if playerConsumable.chargesCount == 0:
            modelConsumable.isEmpty = True
            modelConsumable.respawnEndTime = 0
        else:
            modelConsumable.isEmpty = False
            respawnEndTime = int(round(playerConsumable.coolDownTill - BigWorld.player().arenaStartTime))
            cooldownTime = self._db.getConsumableByID(consumableID).coolDownTime
            respawnStartTime = int(respawnEndTime - cooldownTime)
            modelConsumable.respawnEndTime = respawnEndTime
            modelConsumable.respawnStartTime = respawnStartTime
        self._updateStatus(modelConsumable, status)
        if EntityStates.inState(self._playerAvatar, EntityStates.END_GAME) and modelConsumable.status.get() == 2:
            modelConsumable.isEmpty = True

    def _updateStatus(self, consumableStructure, status):
        if consumableStructure is None:
            return
        else:
            status = self._getStatusByAmount(consumableStructure, status)
            status = self._getStatusByResp(consumableStructure, status)
            status = self._getStatusByActiveTime(consumableStructure, status)
            if consumableStructure.isAuto.get() and status == 1:
                return
            if consumableStructure.status.get() != status:
                consumableStructure.status = status
            return

    def _getStatusByAmount(self, consumableStructure, status):
        if consumableStructure.amount.get() == 0:
            return -1
        return status

    def _getStatusByActiveTime(self, consumableStructure, status):
        activeEndTime = int(consumableStructure.activeEndTime.get() + BigWorld.player().arenaStartTime)
        serverTime = BigWorld.serverTime()
        if activeEndTime > serverTime:
            return 0
        return status

    def _getStatusByResp(self, consumableStructure, status):
        respawnEndTime = int(consumableStructure.respawnEndTime.get() + BigWorld.player().arenaStartTime)
        serverTime = BigWorld.serverTime()
        if respawnEndTime > serverTime:
            return -1
        return status

    def _onUpdateConsumableStatus(self, consumableId, status):
        consumableStructure = self._model.consumables.first(lambda e: e.id.get() == consumableId)
        self._updateStatus(consumableStructure, status)

    def _onUpdateConsumables(self, consumableStatuses):
        for consumId, status in consumableStatuses.iteritems():
            modelConsumable = self._model.consumables.first(lambda e: e.id.get() == consumId)
            playerConsumable = next((e for e in self._playerAvatar.consumables if e.id == consumId), None)
            if modelConsumable is not None and playerConsumable is not None:
                self._updateConsumable(playerConsumable, modelConsumable, status)

        return

    def _onInitConsumables(self, consumableStatuses, cleanOldModelConsumables = False):
        if cleanOldModelConsumables:
            self._model.consumables.clean()
        self._addBaseConsumable()
        self._onUpdateConsumables(consumableStatuses)

    def dispose(self):
        InputMapping.g_instance.onSaveControls -= self.__updateControls
        self._consumableManager.eInitConsumables -= self._onInitConsumables
        self._consumableManager.eUpdateConsumables -= self._onUpdateConsumables
        self._consumableManager.eUpdateConsumableStatus -= self._onUpdateConsumableStatus
        self._consumableManager.destroy()
        self._consumableManager = None
        self._model = None
        self._playerAvatar = None
        self._passiveList = None
        self._db = None
        return