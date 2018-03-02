# Embedded file name: scripts/common/ComponentModel/AircraftComponents.py
import sys
import inspect
import BigWorld
import db.DBLogic
from EntityHelpers import isAvatar
from Component import Component, InputSlot, OutputSlot
from debug_utils import LOG_ERROR

class FindAircraftIdByEntityId(Component):

    @classmethod
    def componentCategory(cls):
        return 'Aircraft'

    def slotDefinitions(self):
        return [InputSlot('entity_id', Component.SLOT_INT, None), OutputSlot('aircraft_id', Component.SLOT_INT, FindAircraftIdByEntityId._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            LOG_ERROR('[VSE] Entity does not exist: {0}'.format(entityId))
            return -1
        elif not isAvatar(e):
            LOG_ERROR('[VSE] Entity is not avatar: {0}'.format(entityId))
            return -1
        else:
            return db.DBLogic.g_instance.getPlaneIDByGlobalID(e.globalID)


class FindAircraftLevelById(Component):

    @classmethod
    def componentCategory(cls):
        return 'Aircraft'

    def slotDefinitions(self):
        return [InputSlot('aircraft_id', Component.SLOT_INT, None), OutputSlot('aircraft_level', Component.SLOT_INT, FindAircraftLevelById._execute)]

    def _execute(self, aircraftId):
        settings = db.DBLogic.g_instance.getAircraftData(aircraftId)
        if settings is None:
            LOG_ERROR('[VSE] Aircraft does not exist: {0}'.format(aircraftId))
            return -1
        else:
            return settings.airplane.level


class FindAircraftClassById(Component):

    @classmethod
    def componentCategory(cls):
        return 'Aircraft'

    def slotDefinitions(self):
        return [InputSlot('aircraft_id', Component.SLOT_INT, None), OutputSlot('aircraft_class', Component.SLOT_AIRCRAFT_CLASS, FindAircraftClassById._execute)]

    def _execute(self, aircraftId):
        settings = db.DBLogic.g_instance.getAircraftData(aircraftId)
        if settings is None:
            LOG_ERROR('[VSE] Aircraft does not exist: {0}'.format(aircraftId))
            return -1
        else:
            return settings.airplane.planeType


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))