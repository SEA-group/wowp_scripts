# Embedded file name: scripts/common/ComponentModel/SectorComponents.py
import sys
import inspect
from itertools import ifilter
import BigWorld
from Component import Component, InputSlot, OutputSlot, ArrayConnection
from ComponentLoggingHelpers import logEntityDoesNotExistError, logNotSupportedEntityError, logError
from EntityHelpers import isSector
from consts import SECTOR_STATE, TEAM_ID

class FindSectorsInBattle(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    @classmethod
    def arrayConnections(cls):
        return [ArrayConnection('Destination', Component.SLOT_ENTITY)]

    def slotDefinitions(self):
        return [InputSlot('in', Component.SLOT_EVENT, FindSectorsInBattle._execute), OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, dst):
        del dst[:]
        e = BigWorld.entities[self.planEntityId]
        if isSector(e) and not e.settings.isBase and not e.settings.isFreeZone:
            dst.append(e.id)
        sectorEntities = ifilter(lambda s: not s.settings.isBase and not s.settings.isFreeZone, e.entitiesInRange(10000, 'ACSector', (0, 0, 0)))
        dst.extend((s.id for s in sectorEntities))
        return 'out'


class SectorPreset(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    def slotDefinitions(self):
        return [InputSlot('sector_entity', Component.SLOT_ENTITY, None), OutputSlot('preset_name', Component.SLOT_STR, SectorPreset._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return ''
        elif not isSector(e):
            logNotSupportedEntityError(e, self)
            return ''
        else:
            return e.settings.presetName


class SectorLockTimeLeft(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    def slotDefinitions(self):
        return [InputSlot('sector_entity', Component.SLOT_ENTITY, None), OutputSlot('seconds', Component.SLOT_FLOAT, SectorLockTimeLeft._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isSector(e):
            logNotSupportedEntityError(e, self)
            return 0
        elif e.stateContainer.state != SECTOR_STATE.LOCKED:
            return 0
        else:
            return e.stateContainer.nextStateTimestamp - BigWorld.time()


class SectorCapturePoints(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    def slotDefinitions(self):
        return [InputSlot('sector_entity', Component.SLOT_ENTITY, None), InputSlot('team_id', Component.SLOT_TEAM_ID, None), OutputSlot('res', Component.SLOT_INT, SectorCapturePoints._execute)]

    def _execute(self, entityId, teamId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isSector(e):
            logNotSupportedEntityError(e, self)
            return 0
        elif teamId not in TEAM_ID.CHOSEN:
            logError(self, 'Invalid team id, team code: ' + str(teamId))
            return 0
        else:
            return e.captureStatus[teamId]


class SectorCapturePointsMax(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    def slotDefinitions(self):
        return [InputSlot('sector_entity', Component.SLOT_ENTITY, None), OutputSlot('res', Component.SLOT_INT, SectorCapturePointsMax._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isSector(e):
            logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.capturePoints


class SectorRadius(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Sectors'

    def slotDefinitions(self):
        return [InputSlot('sector_entity', Component.SLOT_ENTITY, None), OutputSlot('res', Component.SLOT_FLOAT, SectorRadius._execute)]

    def _execute(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isSector(e):
            logNotSupportedEntityError(e, self)
            return 0
        else:
            center, radius = e.settings.geometry.boundingCircle
            return radius


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))