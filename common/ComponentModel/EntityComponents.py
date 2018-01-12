# Embedded file name: scripts/common/ComponentModel/EntityComponents.py
import sys
import inspect
import BigWorld
from EntityHelpers import isAvatar, isTeamObject
from Component import Component, InputSlot, OutputSlot
from debug_utils import LOG_ERROR
from consts import METERS_PER_SEC_TO_KMH_FACTOR
import _performanceCharacteristics_db
import _preparedBattleData_db

class HeightAboveGroundByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('height', Component.SLOT_FLOAT, HeightAboveGroundByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.getAltitudeAboveObstacle()


class SpeedByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('speed', Component.SLOT_FLOAT, SpeedByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.getSpeed() * METERS_PER_SEC_TO_KMH_FACTOR


class HeightAboveWaterByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('height', Component.SLOT_FLOAT, HeightAboveWaterByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.getAltitudeAboveWaterLevel()


class WepSpeedByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('wep_speed', Component.SLOT_FLOAT, WepSpeedByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return 0
        else:
            return _performanceCharacteristics_db.airplanes[e.globalID].maxSpeed


class MaxSpeedByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('max_speed', Component.SLOT_FLOAT, MaxSpeedByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.engineSettings.maxSpeed * METERS_PER_SEC_TO_KMH_FACTOR


class HeightLevelsByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None),
         OutputSlot('optimal', Component.SLOT_FLOAT, HeightLevelsByEntityId._getOptimal),
         OutputSlot('critical', Component.SLOT_FLOAT, HeightLevelsByEntityId._getCritical),
         OutputSlot('max', Component.SLOT_FLOAT, HeightLevelsByEntityId._getMax)]

    def _getOptimal(self, entityId):
        pbd = self._getPreparedBattleData(entityId)
        if pbd is not None:
            return pbd.altimeter[4] * pbd.altimeter[-1]
        else:
            return 0

    def _getCritical(self, entityId):
        pbd = self._getPreparedBattleData(entityId)
        if pbd is not None:
            return pbd.altimeter[5] * pbd.altimeter[-1]
        else:
            return 0

    def _getMax(self, entityId):
        pbd = self._getPreparedBattleData(entityId)
        if pbd is not None:
            return pbd.altimeter[-1]
        else:
            return 0

    def _getPreparedBattleData(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatar(e):
            _logNotSupportedEntityError(e, self)
            return
        else:
            return _preparedBattleData_db.preparedBattleData[e.globalID]


class SetEffectTriggerByEntityId(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetEffectTriggerByEntityId._execute),
         InputSlot('entity_id', Component.SLOT_INT, None),
         InputSlot('trigger_name', Component.SLOT_STR, None),
         InputSlot('is_on', Component.SLOT_BOOL, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, triggerName, isOn):
        e = BigWorld.entities.get(entityId)
        if e is None:
            _logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatar(e) and not isTeamObject(e):
            _logNotSupportedEntityError(e, self)
            return
        else:
            e.controllers['modelManipulator'].setEffectVisible(triggerName, isOn)
            return 'out'


def _logError(component, message):
    LOG_ERROR('[VSE][{}] {}'.format(component.__class__.__name__, message))


def _logNotSupportedEntityError(e, component):
    _logError(component, 'This type of entity is not supported yet: {}'.format(e.className))


def _logEntityDoesNotExistError(entityId, component):
    _logError(component, 'Entity does not exist: {}'.format(entityId))


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))