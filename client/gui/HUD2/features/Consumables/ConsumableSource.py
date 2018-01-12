# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableSource.py
import BigWorld
import InputMapping
from debug_utils import LOG_DEBUG
from _equipment_data import ModsTypeEnum
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.features.Consumables.ConsumableManager import ConsumableManager
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization
from EntityHelpers import EntityStates
FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP = {'ENGINE': 'AUTO_RESTARTER',
 'TAIL_OR_WINGS': 'AUTO_FIX_TAIL_AND_WINGS',
 'FIRE': 'AUTO_EXTINGUISHER',
 'CREW': 'BLEED-STOPPER'}

class ConsumableSource(DataSource):

    def __init__(self, features):
        self._LOG_TAG = '  Consumable : '
        self._model = features.require(Feature.GAME_MODEL).consumables
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._consumableManager = ConsumableManager(features)
        self._isArenaReady = False
        self._passiveList = [ModsTypeEnum.ECONOMIC_BONUS_CREDITS,
         ModsTypeEnum.ECONOMIC_BONUS_XP,
         ModsTypeEnum.SPARKLERS,
         ModsTypeEnum.COLOR_PLUMES]
        from db.DBLogic import g_instance as db
        self._db = db
        self._playerAvatar.eUpdateConsumables += self._onUpdateConsumables
        InputMapping.g_instance.onSaveControls += self.__updateControls
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    def _setupModel(self, newInfos):
        self._consumableManager.initConsumables(self._playerAvatar.consumables, self._showHint)
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eTacticalRespawnEnd += self._onRespawn
        self._playerAvatar.eTacticalSpectator += self._onRespawn
        self._playerAvatar.eArenaLoadedAndReady += self._onArenaLoadedAndReady
        if self._isArenaReady:
            self._initConsumables()

    def _initConsumables(self):
        self._addBaseConsumable()
        self._consumableManager.updateConsumable(self._playerAvatar.consumables)
        self._updateAllConsumable()

    def _onArenaLoadedAndReady(self, *args, **kwargs):
        self._isArenaReady = True
        if self._clientArena.isAllServerDataReceived():
            self._initConsumables()

    def _onRespawn(self, *args, **kwargs):
        self._model.consumables.clean()
        self._consumableManager.updateConsumable(self._playerAvatar.consumables)
        self._addBaseConsumable()
        self._updateAllConsumable()

    def _updateAllConsumable(self):
        consumablesData = self._playerAvatar.consumables
        self._onUpdateConsumables(consumablesData)

    def _onUpdateConsumables(self, consumablesData):
        """
        :param consumablesData: CONSUMABLE_RECORD in alias.xml
        """
        for consumableRecord in consumablesData:
            consumablesID = consumableRecord.id
            consumableStructure = self._model.consumables.first(lambda e: e.id.get() == consumablesID)
            if consumableStructure is not None:
                self._updateConsumable(consumableRecord, consumableStructure)

        return

    def __updateControls(self):
        if self._playerAvatar:
            if hasattr(self._playerAvatar, 'consumables'):
                consumables = self._playerAvatar.consumables
                equipmentCommands = InputMapping.EQUIPMENT_COMMANDS
                for index, consumableData in enumerate(consumables):
                    key = consumableData.id
                    if key != -1:
                        keyName = getKeyLocalization(equipmentCommands[index])
                        consumableStructure = self._model.consumables.first(lambda e: e.id.get() == key)
                        consumableStructure.key = keyName

    def _addBaseConsumable(self):
        consumables = self._playerAvatar.consumables
        equipmentCommands = InputMapping.EQUIPMENT_COMMANDS
        for index, consumableData in enumerate(consumables):
            key = consumableData.id
            if key != -1:
                keyName = getKeyLocalization(equipmentCommands[index])
                self._appendConsumable(self._model.consumables, consumableData, keyName)

    def _appendConsumable(self, consumablesModelList, consumableRecord, keyName):
        consumableID = consumableRecord.id
        consumableDB = self._db.getConsumableByID(consumableID)
        cooldownTime = self._db.getConsumableByID(consumableID).coolDownTime
        respawnEndTime = int(round(consumableRecord.coolDownTill - BigWorld.serverTime()))
        consumablesModelList.append(id=consumableID, iconPath=consumableDB.icoPathHud, consumableName=consumableDB.name, description=consumableDB.description, amount=consumableRecord.chargesCount, isEmpty=False, isReadyOnRespawn=consumableDB.readyOnRespawn, coolDownTime=consumableDB.coolDownTime, key=keyName, status=0, isAuto=self._checkAutoType(consumableDB), isPassive=self._checkModsForPassive(consumableDB), respawnEndTime=respawnEndTime, respawnStartTime=int(respawnEndTime - cooldownTime), activeEndTime=int(round(consumableRecord.activeTill - BigWorld.serverTime())))

    def _checkModsForPassive(self, consumableDB):
        isPassive = False
        for mod in consumableDB.mods:
            if mod.type in self._passiveList:
                isPassive = True

        return isPassive

    def _checkAutoType(self, consumable):
        if consumable.localizeTag in FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP.values():
            return True
        return False

    def _updateConsumable(self, consumableRecord, consumableStructure):
        consumableStructure.amount = consumableRecord.chargesCount
        consumableID = consumableStructure.id.get()
        activeEndTime = int(round(consumableRecord.activeTill - BigWorld.player().arenaStartTime))
        status = self._consumableManager.getStatusForConsumable(consumableRecord.id)
        if consumableStructure.activeEndTime.get() != activeEndTime:
            consumableStructure.activeEndTime = activeEndTime
        if consumableRecord.chargesCount == 0:
            consumableStructure.isEmpty = True
            consumableStructure.respawnEndTime = 0
        else:
            consumableStructure.isEmpty = False
            respawnEndTime = int(round(consumableRecord.coolDownTill - BigWorld.player().arenaStartTime))
            cooldownTime = self._db.getConsumableByID(consumableID).coolDownTime
            respawnStartTime = int(respawnEndTime - cooldownTime)
            consumableStructure.respawnEndTime = respawnEndTime
            consumableStructure.respawnStartTime = respawnStartTime
        self._updateStatus(consumableStructure, status)
        if EntityStates.inState(self._playerAvatar, EntityStates.END_GAME) and consumableStructure.status.get() == 2:
            consumableStructure.isEmpty = True

    def _showHint(self, itemId, status):
        consumableStructure = self._model.consumables.first(lambda e: e.id.get() == itemId)
        self._updateStatus(consumableStructure, status)

    def _updateStatus(self, consumableStructure, status):
        if consumableStructure is not None:
            status = self._getStatusByAmount(consumableStructure, status)
            status = self._getStatusByResp(consumableStructure, status)
            status = self._getStatusByActiveTime(consumableStructure, status)
            if consumableStructure.isAuto.get():
                if status == 1:
                    return
            self._updateStatusStructure(consumableStructure, status)
        return

    def _updateStatusStructure(self, consumableStructure, status):
        if consumableStructure.status.get() != status:
            consumableStructure.status = status

    def _getStatusByAmount(self, consumableStructure, status):
        if consumableStructure.amount.get() == 0:
            status = -1
        return status

    def _getStatusByActiveTime(self, consumableStructure, status):
        activeEndTime = int(consumableStructure.activeEndTime.get() + BigWorld.player().arenaStartTime)
        serverTime = BigWorld.serverTime()
        if activeEndTime > serverTime:
            status = 0
        return status

    def _getStatusByResp(self, consumableStructure, status):
        respawnEndTime = int(consumableStructure.respawnEndTime.get() + BigWorld.player().arenaStartTime)
        serverTime = BigWorld.serverTime()
        if respawnEndTime > serverTime:
            status = -1
        return status

    def dispose(self):
        self._playerAvatar.eTacticalRespawnEnd -= self._onRespawn
        self._playerAvatar.eTacticalSpectator -= self._onRespawn
        InputMapping.g_instance.onSaveControls -= self.__updateControls
        self._playerAvatar.eUpdateConsumables -= self._onUpdateConsumables
        self._playerAvatar.eArenaLoadedAndReady -= self._onArenaLoadedAndReady
        self._consumableManager.destroy()
        self._consumableManager = None
        self._model = None
        self._consumableManager = None
        return