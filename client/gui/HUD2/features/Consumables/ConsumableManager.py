# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableManager.py
import BigWorld
from Event import EventManager, Event
from _equipment_data import ModsTypeEnum
from consts import PART_FLAGS
import GameEnvironment
PART_TYPES = {'LeftWing': 0,
 'RightWing': 1,
 'Tail': 2,
 'Engine': 6,
 'Pilot': 8,
 'Gunner1': 9}
PART_CRIT = 3

class EquipmentStatus:
    DISABLED = -1
    NEUTRAL = 0
    ENABLED = 1
    PRIORITY = 2


class ConsumableManager(object):

    def __init__(self):
        self._eventManager = EventManager()
        self.eInitConsumables = Event(self._eventManager)
        self.eUpdateConsumables = Event(self._eventManager)
        self.eUpdateConsumableStatus = Event(self._eventManager)
        self.__update1secCallBack = -1
        self._playerAvatar = GameEnvironment.g_instance.playerAvatarProxy
        self._clientArena = GameEnvironment.getClientArena()
        self._modulesDict = {}
        self._isFire = False
        from db.DBLogic import g_instance as db
        self._db = db
        self._clientArena.onNewAvatarsInfo += self._onSetupManager
        self._isArenaReady = False
        if self._clientArena.isAllServerDataReceived():
            self._onSetupManager(None)
        return

    def _onSetupManager(self, newInfos):
        self._playerAvatar.ePartStateChanged += self._onPartStateChanged
        self._playerAvatar.ePartFlagSwitchedNotification += self._onPartSwitched
        self._playerAvatar.eUpdateConsumables += self._onUpdateConsumables
        self._update1sec()
        self._clientArena.onNewAvatarsInfo -= self._onSetupManager
        self._playerAvatar.eTacticalRespawnEnd += self._onPlayerRespawn
        self._playerAvatar.eTacticalSpectator += self._onPlayerRespawn
        self._playerAvatar.eArenaLoadedAndReady += self._onArenaLoadedAndReady
        if self._isArenaReady:
            consumableStatuses = self._collectConsumablesStatuses()
            self.eInitConsumables(consumableStatuses)

    def _collectConsumablesStatuses(self):
        playerConsumables = dict()
        for consumable in self._playerAvatar.consumables:
            playerConsumables[consumable.id] = self.getStatusForConsumable(consumable.id)

        return playerConsumables

    def _isCrewDamaged(self):
        if self._checkPartOnCrit(PART_TYPES['Gunner1']) or self._checkPartOnCrit(PART_TYPES['Pilot']):
            return EquipmentStatus.ENABLED
        return EquipmentStatus.DISABLED

    def _update1sec(self):
        if BigWorld.player().__class__.__name__ is 'PlayerAvatar':
            self.__update1secCallBack = BigWorld.callback(1.0, self._update1sec)
            self._checkConsumable()

    def _checkConsumable(self):
        for index, consumableData in enumerate(self._playerAvatar.consumables):
            key = consumableData['key']
            if key != -1:
                status = self.getStatusForConsumable(key)
                self.eUpdateConsumableStatus(key, status)

    def getStatusForConsumable(self, key):
        consumable = self._db.getConsumableByID(key)
        if consumable and consumable.mods:
            for mod in consumable.mods:
                return self._isEnabledForUse(mod.type, mod)

        return EquipmentStatus.NEUTRAL

    def _isEnabledForUse(self, equipmentType, mod):
        owner = BigWorld.player()
        if equipmentType == ModsTypeEnum.HP_RESTORE:
            return self._isCrewDamaged()
        if equipmentType == ModsTypeEnum.FIX_TAIL_AND_WINGS:
            return self._isTailOrWingsCrit()
        if equipmentType in [ModsTypeEnum.FIRE_EXTINGUISH_MANUAL, ModsTypeEnum.FIRE_EXTINGUISH_AUTO, ModsTypeEnum.FIRE_CHANCE]:
            if self._isFire:
                return EquipmentStatus.ENABLED
            return EquipmentStatus.DISABLED
        if equipmentType in [ModsTypeEnum.ENGINE_RESTORE, ModsTypeEnum.AUTO_ENGINE_RESTORE]:
            if self._checkPartOnCrit(PART_TYPES['Engine']):
                return EquipmentStatus.ENABLED
            return EquipmentStatus.DISABLED
        if equipmentType == ModsTypeEnum.CLEAR_GUNS_OVERHEAT:
            if owner.controllers['weapons'].isGunsOverHeated(getattr(mod, 'activationValue', 0)):
                return EquipmentStatus.ENABLED
            return EquipmentStatus.DISABLED
        if equipmentType in [ModsTypeEnum.ECONOMIC_BONUS_CREDITS,
         ModsTypeEnum.ECONOMIC_BONUS_XP,
         ModsTypeEnum.SPARKLERS,
         ModsTypeEnum.COLOR_PLUMES]:
            return EquipmentStatus.PRIORITY
        if equipmentType == ModsTypeEnum.CLEAR_ENGINE_OVERHEAT:
            if owner.engineTemperature > getattr(mod, 'activationValue', 0):
                return EquipmentStatus.ENABLED
            return EquipmentStatus.DISABLED
        if equipmentType in [ModsTypeEnum.ROLL_MAX_SPEED_CFG,
         ModsTypeEnum.YAW_MAX_SPEED_CFG,
         ModsTypeEnum.PITCH_MAX_SPEED_CFG,
         ModsTypeEnum.LOCK_ENGINE_POWER,
         ModsTypeEnum.FIRE_WORK]:
            return EquipmentStatus.NEUTRAL
        return EquipmentStatus.DISABLED

    def _isTailOrWingsCrit(self):
        if self._checkPartOnCrit(PART_TYPES['RightWing']) or self._checkPartOnCrit(PART_TYPES['LeftWing']) or self._checkPartOnCrit(PART_TYPES['Tail']):
            return EquipmentStatus.ENABLED
        return EquipmentStatus.DISABLED

    def _checkPartOnCrit(self, hudPartID):
        if hudPartID in self._modulesDict and self._modulesDict[hudPartID] == PART_CRIT:
            return True
        return False

    def _onPartSwitched(self, partID, flagID, flagValue):
        if flagID == PART_FLAGS.FIRE:
            self._isFire = flagValue

    def _onPartStateChanged(self, partData):
        if partData.partTypeData.componentType not in PART_TYPES:
            return
        else:
            partTypeData = partData.partTypeData
            partTypeStr = partTypeData.componentType
            hudPartID = PART_TYPES.get(partTypeStr)
            if hudPartID is not None:
                self._modulesDict[hudPartID] = partData.stateID
            return

    def _onPlayerRespawn(self, *args, **kwargs):
        self._modulesDict = {}
        consumableStatuses = self._collectConsumablesStatuses()
        self.eInitConsumables(consumableStatuses, True)

    def _onArenaLoadedAndReady(self, *args, **kwargs):
        self._isArenaReady = True
        if self._clientArena.isAllServerDataReceived():
            self._modulesDict = {}
            consumableStatuses = self._collectConsumablesStatuses()
            self.eInitConsumables(consumableStatuses)

    def _onUpdateConsumables(self, consumables):
        self._update1sec()
        consumableStatuses = self._collectConsumablesStatuses()
        self.eUpdateConsumables(consumableStatuses)

    def destroy(self):
        BigWorld.cancelCallback(self.__update1secCallBack)
        self._playerAvatar.ePartStateChanged -= self._onPartStateChanged
        self._playerAvatar.ePartFlagSwitchedNotification -= self._onPartSwitched
        self._playerAvatar.eTacticalRespawnEnd -= self._onPlayerRespawn
        self._playerAvatar.eTacticalSpectator -= self._onPlayerRespawn
        self._playerAvatar.eArenaLoadedAndReady -= self._onArenaLoadedAndReady
        self._gameEnvironment = None
        self._playerAvatar = None
        self._clientArena = None
        self._modulesDict = None
        self._db = None
        self._eventManager.clear()
        return