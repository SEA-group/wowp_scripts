# Embedded file name: scripts/common/ComponentModel/EntityComponents.py
import sys
import inspect
import BigWorld
from EntityHelpers import isAvatar, isTeamObject
from Component import Component, InputSlot, OutputSlot, ArrayConnection
from ComponentLoggingHelpers import logEntityDoesNotExistError, logNotSupportedEntityError
from consts import METERS_PER_SEC_TO_KMH_FACTOR, TEAM_ID
import _performanceCharacteristics_db

class FindPlanesInArea(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    @classmethod
    def arrayConnections(cls):
        return [ArrayConnection('Destination', Component.SLOT_ENTITY)]

    def slotDefinitions(self):
        return [InputSlot('in', Component.SLOT_EVENT, FindPlanesInArea._execute),
         InputSlot('position', Component.SLOT_VECTOR3, None),
         InputSlot('radius', Component.SLOT_FLOAT, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, dst, pos, radius):
        del dst[:]
        e = BigWorld.entities[self.planEntityId]
        if isAvatar(e) and e.position.distTo(pos) <= radius:
            dst.append(e.id)
        avatars = e.entitiesInRange(radius, 'Avatar', pos) + e.entitiesInRange(radius, 'AvatarBot', pos) + e.entitiesInRange(radius, 'Bomber', pos)
        dst.extend((a.id for a in avatars))
        return 'out'


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
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            logNotSupportedEntityError(e, self)
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
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            logNotSupportedEntityError(e, self)
            return 0
        else:
            return e.getSpeed() * METERS_PER_SEC_TO_KMH_FACTOR


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
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            logNotSupportedEntityError(e, self)
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
            logEntityDoesNotExistError(entityId, self)
            return 0
        elif not isAvatar(e):
            logNotSupportedEntityError(e, self)
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
        avatar = self._tryGetAvatar(entityId)
        return avatar.heightOptimal

    def _getCritical(self, entityId):
        avatar = self._tryGetAvatar(entityId)
        return avatar.heightCritical

    def _getMax(self, entityId):
        avatar = self._tryGetAvatar(entityId)
        return avatar.heightMax

    def _tryGetAvatar(self, entityId):
        e = BigWorld.entities.get(entityId)
        if e is None:
            logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatar(e):
            logNotSupportedEntityError(e, self)
            return
        else:
            return e


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
            logEntityDoesNotExistError(entityId, self)
            return
        elif not isAvatar(e) and not isTeamObject(e):
            logNotSupportedEntityError(e, self)
            return
        else:
            e.controllers['modelManipulator'].setEffectVisible(triggerName, isOn)
            return 'out'


class TEAM_LOGICAL_STATE(object):
    NEUTRAL = 'NEUTRAL'
    ALLY = 'ALLY'
    ENEMY = 'ENEMY'


class TeamLogicalState(Component):

    @classmethod
    def componentCategory(cls):
        return 'Game Objects'

    def slotDefinitions(self):
        return [InputSlot('teamIdA', Component.SLOT_TEAM_ID, None), InputSlot('teamIdB', Component.SLOT_TEAM_ID, None), OutputSlot('res', Component.SLOT_STR, TeamLogicalState._execute)]

    def _execute(self, teamIdA, teamIdB):
        if teamIdA == teamIdB:
            return TEAM_LOGICAL_STATE.ALLY
        if teamIdA == TEAM_ID.NEUTRAL or teamIdB == TEAM_ID.NEUTRAL:
            return TEAM_LOGICAL_STATE.NEUTRAL
        return TEAM_LOGICAL_STATE.ENEMY


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))