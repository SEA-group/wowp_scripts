# Embedded file name: scripts/common/ComponentModel/Component.py


class Slot(object):
    """description of an input or output slot"""

    def __init__(self, isInput, name, dataType, func, editorType = None):
        self.isInput = isInput
        self.name = name
        self.dataType = dataType
        self.func = func
        self.editorType = editorType


class InputSlot(Slot):

    def __init__(self, name, dataType, func, editorType = None):
        Slot.__init__(self, True, name, dataType, func, editorType)


class OutputSlot(Slot):

    def __init__(self, name, dataType, func):
        Slot.__init__(self, False, name, dataType, func)


class ArrayConnection(object):

    def __init__(self, name, dataType):
        self.name = name
        self.dataType = dataType


class Component(object):
    """base class for all component"""
    ASPECT_SERVER = 'SERVER'
    ASPECT_CLIENT = 'CLIENT'
    SLOT_BOOL = 1
    SLOT_STR = 2
    SLOT_INT = 3
    SLOT_FLOAT = 4
    SLOT_EVENT = 5
    SLOT_VECTOR2 = 6
    SLOT_VECTOR3 = 7
    SLOT_VECTOR4 = 8
    SLOT_MATRIX = 9
    SLOT_ANGLE = 10
    SLOT_ENTITY = 11
    SLOT_TEAM_ID = 12
    SLOT_AIRCRAFT_CLASS = 13
    EDITOR_SPLINE_NAME_SELECTOR = 1

    def __init__(self):
        self.planEntityId = 0

    @classmethod
    def componentName(cls):
        return cls.__name__

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER, Component.ASPECT_CLIENT]

    @classmethod
    def componentIcon(cls):
        return ':vse/components/python'

    @classmethod
    def componentColor(cls):
        return 7189746

    @classmethod
    def componentCategory(cls):
        return 'General'

    @classmethod
    def arrayConnections(cls):
        return []

    def slotDefinitions(self):
        return []

    def captionText(self):
        return ''

    def onFinishScript(self):
        pass