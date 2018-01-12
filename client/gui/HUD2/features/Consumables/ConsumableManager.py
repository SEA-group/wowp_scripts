# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableManager.py
import BigWorld
from Event import EventManager, Event
from _equipment_data import ModsTypeEnum
from consts import PART_TYPES_TO_ID, PART_FLAGS
from debug_utils import LOG_DEBUG
from gui.HUD2.hudFeatures import Feature
PART_TYPES = {'Engine': 6,
 'LeftWing': 0,
 'RightWing': 1,
 'Tail': 2,
 'Pilot': 8,
 'Gunner1': 9}
PART_CRIT = 3

class ConsumableManager(object):

    def __init__(self, features):
        self.__LOG_TAG = ' <<< ConsumableManager >>>'
        self._eventManager = EventManager()
        self.onShowHint = Event(self._eventManager)
        self.onUpdateCooldown = Event(self._eventManager)
        self.onGunOverheatedEvent = Event(self._eventManager)
        self._enableConsumableDict = {}
        self.__update1secCallBack = -1
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._modulesDict = {}
        self._isFire = False
        from db.DBLogic import g_instance as db
        self._db = db
        LOG_DEBUG(self.__LOG_TAG, ' __init__ ')

    def initConsumables(self, consumables, showHint):
        LOG_DEBUG(self.__LOG_TAG, ' __initConsumables__ ')
        self._consumables = consumables
        self._playerAvatar.ePartStateChanged += self._updatePart
        self._playerAvatar.ePartFlagSwitchedNotification += self._flagSwitchedNotification
        self._playerAvatar.eUpdateConsumables += self._onUpdateConsumables
        self._showHint = showHint
        self._update1sec()

    def updateConsumable(self, consumables):
        LOG_DEBUG(self.__LOG_TAG, ' __ updateConsumable __ ')
        self._modulesDict = {}
        self._enableConsumableDict = {}
        self._consumables = consumables

    def _onUpdateConsumables(self, consumables):
        self._consumables = consumables
        self._update1sec()

    def _updatePart(self, partData):
        if partData.partTypeData.componentType not in PART_TYPES:
            return
        else:
            partTypeData = partData.partTypeData
            partTypeStr = partTypeData.componentType
            hudPartID = PART_TYPES.get(partTypeStr)
            if hudPartID is not None:
                hudPartID = PART_TYPES.get(partTypeStr)
                self._modulesDict[hudPartID] = partData.stateID
            return

    def _update1sec(self):
        if BigWorld.player().__class__.__name__ is 'PlayerAvatar':
            self.__update1secCallBack = BigWorld.callback(1.0, self._update1sec)
            self._checkConsumable()

    def _checkConsumable(self):
        for index, consumableData in enumerate(self._consumables):
            key = consumableData['key']
            if key != -1:
                status = self.__checkStatus(key)
                if key in self._enableConsumableDict:
                    pass
                else:
                    self._enableConsumableDict[key] = -1
                if self._showHint:
                    self._showHint(key, status)
                self._enableConsumableDict[key] = status

    def getStatusForConsumable(self, key):
        status = self.__checkStatus(key)
        if key in self._enableConsumableDict:
            pass
        else:
            self._enableConsumableDict[key] = -1
        return status

    def __checkStatus(self, key):
        consumable = self._db.getConsumableByID(key)
        if consumable.mods:
            for mod in consumable.mods:
                return self._isEnabledForUse(mod.type, mod)

        return 0

    def _isEnabledForUse(self, equipmentType, mod):
        owner = BigWorld.player()
        if equipmentType == ModsTypeEnum.HP_RESTORE:
            return self.isCrewDamaged()
        if equipmentType in [ModsTypeEnum.FIX_TAIL_AND_WINGS]:
            return self._isTailOrWingsCrit()
        if equipmentType in [ModsTypeEnum.FIRE_EXTINGUISH_MANUAL, ModsTypeEnum.FIRE_EXTINGUISH_AUTO, ModsTypeEnum.FIRE_CHANCE]:
            return self.isFire()
        if equipmentType in (ModsTypeEnum.ENGINE_RESTORE, ModsTypeEnum.AUTO_ENGINE_RESTORE):
            return self._isEngineDamaged()
        if equipmentType == ModsTypeEnum.CLEAR_GUNS_OVERHEAT:
            if owner.controllers['weapons'].isGunsOverHeated(getattr(mod, 'activationValue', 0)):
                return 1
            return -1
        if equipmentType == ModsTypeEnum.FIRE_WORK:
            return 0
        if equipmentType == ModsTypeEnum.ECONOMIC_BONUS_CREDITS:
            return 2
        if equipmentType == ModsTypeEnum.ECONOMIC_BONUS_XP:
            return 2
        if equipmentType == ModsTypeEnum.SPARKLERS:
            return 2
        if equipmentType == ModsTypeEnum.COLOR_PLUMES:
            return 2
        if equipmentType == ModsTypeEnum.CLEAR_ENGINE_OVERHEAT:
            if owner.engineTemperature > getattr(mod, 'activationValue', 0):
                return 1
            return -1
        if equipmentType in [ModsTypeEnum.ROLL_MAX_SPEED_CFG,
         ModsTypeEnum.YAW_MAX_SPEED_CFG,
         ModsTypeEnum.PITCH_MAX_SPEED_CFG,
         ModsTypeEnum.LOCK_ENGINE_POWER]:
            return 0
        return -1

    def isFire(self):
        if self._isFire:
            return 1
        return -1

    def isCrewDamaged(self):
        if self._checkPartOnCrit(PART_TYPES.get('Gunner1')):
            return 1
        if self._checkPartOnCrit(PART_TYPES.get('Pilot')):
            return 1
        return -1

    def _isEngineDamaged(self):
        if self._checkPartOnCrit(PART_TYPES.get('Engine')):
            return 1
        return -1

    def _isTailOrWingsCrit(self):
        if self._checkPartOnCrit(PART_TYPES.get('RightWing')):
            return 1
        if self._checkPartOnCrit(PART_TYPES.get('LeftWing')):
            return 1
        if self._checkPartOnCrit(PART_TYPES.get('Tail')):
            return 1
        return -1

    def _checkPartOnCrit(self, hudPartID):
        if hudPartID in self._modulesDict:
            if self._modulesDict[hudPartID] == PART_CRIT:
                return True
        return False

    def _flagSwitchedNotification(self, partID, flagID, flagValue):
        if flagID == PART_FLAGS.FIRE:
            self._isFire = flagValue

    def destroy(self):
        self._playerAvatar.ePartStateChanged -= self._updatePart
        self._playerAvatar.ePartFlagSwitchedNotification -= self._flagSwitchedNotification
        BigWorld.cancelCallback(self.__update1secCallBack)
        self._enableConsumableDict = None
        self._gameEnvironment = None
        self._playerAvatar = None
        self._modulesDict = None
        self._consumables = None
        self._showHint = None
        return