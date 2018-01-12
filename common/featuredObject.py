# Embedded file name: scripts/common/featuredObject.py
import BigWorld
from _consumables_data import ModsTypeEnum
import db.DBLogic
from debug_utils import *
from consts import IS_CELLAPP
from _bonusSchemes_data import BonusSchemesDB
from Event import Event
from BWUserTypesCommon.ConsumableRecord import ConsumableRecord
if IS_CELLAPP:
    from ConsumablesAction import ACTION_TABLE, ACTIVATION_TABLE
ModsTypesToName = dict(((v, k) for k, v in ModsTypeEnum.__dict__.items() if not k.startswith('__')))

class IEquipmentFeaturedObject(object):

    def applyObjMods(self, modifiers):
        pass


class CamouflageFeatureObject(IEquipmentFeaturedObject):

    def __init__(self, bonusSchemaName, isCamouflageSpecializedForCurMap):
        self.__mods = BonusSchemesDB[bonusSchemaName] if bonusSchemaName else []
        self.__isCamouflageSpecializedForCurMap = isCamouflageSpecializedForCurMap

    def applyObjMods(self, modifiers):
        for mod in self.__mods:
            if self.__isCamouflageSpecializedForCurMap or mod.isActiveForAllMapTypes:
                modifiers.__dict__[ModsTypesToName[mod.type]] *= mod.value_


class EquipmentFeaturedObject(IEquipmentFeaturedObject):

    def __init__(self, data, skillsID):
        self._crewSkillsID = skillsID
        self._equipmentModifierData = db.DBLogic.g_instance.getSkillWithRelations()
        if data != -1:
            self.__mods = db.DBLogic.g_instance.getEquipmentByID(data).mods
        else:
            self.__mods = []

    def _value(self, mod, modifiers):
        res = mod.value_
        for ID, value in self._equipmentModifierData.iteritems():
            key, relations = value
            if ID in self._crewSkillsID and mod.type in relations:
                res = (res - 1.0) * getattr(modifiers, ModsTypesToName[key], {}).get(ID, 1) + 1.0

        return res

    def applyObjMods(self, modifiers):
        for mod in self.__mods:
            modifiers.__dict__[ModsTypesToName[mod.type]] *= self._value(mod, modifiers)


class ConsumableEquipmentFeaturedObject(IEquipmentFeaturedObject):

    def __init__(self, consumableRecord):
        self.__consumableRecord = consumableRecord
        if self.isEmpty:
            self._consumableDBData = None
            self.__mods = []
        else:
            self._consumableDBData = db.DBLogic.g_instance.getConsumableByID(self.consumableID)
            self.__mods = self._consumableDBData.mods
            LOG_DEBUG_DEV('found consumable', consumableRecord, [ (mod.type, mod.value_) for mod in self.__mods ])
        self.eReadyToUse = Event()
        if IS_CELLAPP and not self.isEmpty:
            from Avatar import FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP
            localizationTag = self.consumableDBData.localizeTag
            self.isAutoUsable = localizationTag in FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP.itervalues()
            if self.isAutoUsable:
                self.autoRepairPartType = next((partType for partType, locTag in FIXABLE_TYPE_TO_CONSUMABLE_NAME_MAP.iteritems() if locTag == localizationTag))
            else:
                self.autoRepairPartType = None
        return

    @property
    def isEmpty(self):
        """Indicate if this consumable slot is empty
        :rtype: bool
        """
        return self.consumableID == -1

    @property
    def consumableID(self):
        """DB consumable id
        :rtype: int
        """
        return self.__consumableRecord.id

    @property
    def activeTill(self):
        """Timestamp when consumable will be deactivated if it is active at the moment, -1 else
        :rtype: float
        """
        return self.__consumableRecord.activeTill

    @activeTill.setter
    def activeTill(self, value):
        self.__consumableRecord.activeTill = value

    @property
    def cooldownTill(self):
        """Timestamp when consumable cooldown will finish or -1 if consumable is ready to use
        :rtype: float
        """
        return self.__consumableRecord.coolDownTill

    @cooldownTill.setter
    def cooldownTill(self, value):
        self.__consumableRecord.coolDownTill = value

    @property
    def chargesCount(self):
        """Consumable charges left or -1 if infinite charges available
        :rtype: int
        """
        return self.__consumableRecord.chargesCount

    @chargesCount.setter
    def chargesCount(self, value):
        self.__consumableRecord.chargesCount = value

    @cooldownTill.setter
    def cooldownTill(self, value):
        self.__consumableRecord.coolDownTill = value

    @property
    def consumableDBData(self):
        return self._consumableDBData

    def applyObjMods(self, modifiers):
        if self.__consumableRecord.isActivated:
            LOG_DEBUG_DEV('applyObjMods', self.__consumableRecord.id)
            for mod in self.__mods:
                modifiers.__dict__[ModsTypesToName[mod.type]] *= mod.value_

    def use(self, owner):
        if IS_CELLAPP:
            couldBeActivated = self._isCouldBeActivated(owner)
            if couldBeActivated and self._isReady():
                LOG_DEBUG_DEV('use consumable', self.__consumableRecord.id)
                settings = db.DBLogic.g_instance.getConsumableByID(self.__consumableRecord.id)
                for i, mod in enumerate(self.__mods):
                    action = ACTION_TABLE.get(mod.type, None)
                    if action:
                        action(owner, mod, settings)

                if self.chargesCount != ConsumableRecord.INFINITE_CHARGES_COUNT:
                    self.__consumableRecord.chargesCount -= 1
                self.__consumableRecord.coolDownTill = BigWorld.time() + settings.coolDownTime
                self.__consumableRecord.activeTill = BigWorld.time() + settings.effectTime
                return True
            else:
                LOG_DEBUG_DEV("can't use ", self.__consumableRecord.id, self.__consumableRecord, couldBeActivated)
                return False
        else:
            LOG_ERROR("It's senselessly to call this function on client")
        return

    def _isCouldBeActivated(self, owner):
        for mod in self.__mods:
            if mod.activationRequired:
                if mod.type in ACTIVATION_TABLE:
                    if not ACTIVATION_TABLE[mod.type](owner, getattr(mod, 'activationValue', 0)):
                        return False
                else:
                    LOG_ERROR('Modifier was marked as required but not registered in ACTIVATION_TABLE')
                    return False

        return True

    def _isReady(self):
        return self.__consumableRecord.isReadyToUse

    def isUsable(self, owner):
        return self._isReady() and self._isCouldBeActivated(owner)

    def update1sec(self):
        t = BigWorld.time()
        if self.__consumableRecord.isCoolDownInProgress and self.__consumableRecord.coolDownTill < t:
            LOG_DEBUG_DEV('clear coolDown', self.__consumableRecord.id)
            self.__consumableRecord.clearCoolDown()
            self.eReadyToUse(self)
        if self.__consumableRecord.isActivated and self.__consumableRecord.activeTill < t:
            LOG_DEBUG_DEV('clear activity', self.__consumableRecord.id)
            self.__consumableRecord.activeTill = -1
            return bool(self.__mods)
        return False

    def onOwnerRespawn(self, currentTime):
        """Handle Avatar.eRespawn event. Return flag indicating that modifiers update needs to be performed
        :param currentTime: Current timestamp value
        :return: True if update needed, False otherwise
        :rtype: bool
        """
        if self.isEmpty:
            return False
        if self.__consumableRecord.hasPendingCoolDown:
            self.__consumableRecord.resumeCoolDown(currentTime)
        self.chargesCount = self.consumableDBData.chargesCount
        if self.consumableDBData.readyOnRespawn:
            self.__consumableRecord.clearCoolDown()
        if self.__consumableRecord.isActivated:
            self.__consumableRecord.clearActivation()
            return bool(self.__mods)
        return False

    def onOwnerDestruction(self, currentTime):
        """Handle owner destruction event
        :param currentTime: Current timestamp value
        """
        if self.isEmpty:
            return
        if self.__consumableRecord.isCoolDownInProgress:
            self.__consumableRecord.pauseCoolDown(currentTime)