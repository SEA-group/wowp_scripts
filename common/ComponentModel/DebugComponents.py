# Embedded file name: scripts/common/ComponentModel/DebugComponents.py
import sys
import inspect
from collections import defaultdict
from Component import Component, InputSlot, OutputSlot
from DebugManager import SHOW_DEBUG_OBJ, DV_OBJ_TYPES, REMOVE_VIEW_GROUP

class DebugText3d(Component):
    _debugDataByEntityId = defaultdict(dict)

    def __init__(self):
        super(DebugText3d, self).__init__()
        self._debugGroupsUsed = set()

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER, Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Debug'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, DebugText3d._execute),
         InputSlot('entity', Component.SLOT_ENTITY, None),
         InputSlot('group', Component.SLOT_STR, None),
         InputSlot('key', Component.SLOT_STR, None),
         InputSlot('value', Component.SLOT_STR, None),
         InputSlot('offset', Component.SLOT_VECTOR3, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, groupId, key, value, offset):
        containerId = str(entityId) + groupId
        debugData = self._debugDataByEntityId[containerId]
        debugData[key] = value
        self._debugGroupsUsed.add(groupId)
        SHOW_DEBUG_OBJ('VSE_DebugText3D_' + str(entityId), debugData.items(), shift=offset, entityID=entityId, type=DV_OBJ_TYPES.TEXT_3D_LOCAL, group=groupId)
        return 'out'

    def onFinishScript(self):
        self._clearDebugGroups()

    def _clearDebugGroups(self):
        for groupId in self._debugGroupsUsed:
            REMOVE_VIEW_GROUP(groupId)


class DebugLine3d(Component):

    def __init__(self):
        super(DebugLine3d, self).__init__()
        self._debugGroupsUsed = set()

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER, Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Debug'

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, DebugLine3d._execute),
         InputSlot('entity', Component.SLOT_ENTITY, None),
         InputSlot('group', Component.SLOT_STR, None),
         InputSlot('from', Component.SLOT_VECTOR3, None),
         InputSlot('to', Component.SLOT_VECTOR3, None),
         InputSlot('is_arrow', Component.SLOT_BOOL, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _execute(self, entityId, groupId, _from, to, isArrow):
        self._debugGroupsUsed.add(groupId)
        SHOW_DEBUG_OBJ('VSE_DebugLine3D_' + str(entityId), (_from, to), entityID=entityId, type=DV_OBJ_TYPES.LINE_3D, group=groupId, arrow=isArrow)
        return 'out'

    def onFinishScript(self):
        self._clearDebugGroups()

    def _clearDebugGroups(self):
        for groupId in self._debugGroupsUsed:
            REMOVE_VIEW_GROUP(groupId)


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))