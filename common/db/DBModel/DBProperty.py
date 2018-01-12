# Embedded file name: scripts/common/db/DBModel/DBProperty.py
from consts import WORLD_SCALING, PLANE_TYPE_NAME_REVERSED, PLANE_TYPE

class DBPropertyBase(object):
    """Base class for model properties
    """

    def __init__(self, default = None, sectionName = None):
        self._name = None
        self._default = default
        self.sectionName = sectionName
        return

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.sectionName = self.sectionName or self._name

    @property
    def default(self):
        return self._default

    def get(self, instance):
        return instance.getPropertyValue(self.name)

    def set(self, instance, value):
        instance.setPropertyValue(self.name, value)

    def __get__(self, instance, owner):
        if not instance:
            return self
        return self.get(instance)

    def __set__(self, instance, value):
        self.set(instance, value)

    def read(self, section, instance = None):
        """Read data from section
        @param section: Root data section to read from
        @type section: ResMgr.DataSection
        @param instance: Optional argument providing root model instance.
        If provided - new value will be updated on instance
        @type instance: DBModelBase.DBModelBase | None
        @return: Read result in format (flag, value),
        where value is actual property value read from section if flag is True and None otherwise
        @rtype: (bool, Any)
        """
        if section and section.has_key(self.sectionName):
            value = self._doRead(section[self.sectionName])
            if instance:
                self.set(instance, value)
            return (True, value)
        else:
            return (False, None)

    def doRead(self, section):
        """Public interface for _doRead method
        @type section: ResMgr.DataSection
        @return: Extracted value from data section
        """
        return self._doRead(section)

    def _doRead(self, section):
        """Internal reading logic, have to be implemented in child classes
        @type section: ResMgr.DataSection
        @return: Extracted value from data section
        """
        raise NotImplementedError()


class DBStringProperty(DBPropertyBase):

    def _doRead(self, section):
        return section.asString


class DBStringListProperty(DBPropertyBase):

    def _doRead(self, section):
        st = section.asString
        return st.split(',')


class DBIntProperty(DBPropertyBase):

    def _doRead(self, section):
        return section.asInt


class DBFloatProperty(DBPropertyBase):

    def _doRead(self, section):
        return section.asFloat


class DBWorldScaledProperty(DBFloatProperty):

    def _doRead(self, section):
        return super(DBWorldScaledProperty, self)._doRead(section) * WORLD_SCALING


class DBBoolProperty(DBPropertyBase):

    def _doRead(self, section):
        return section.asBool


class DBModelProperty(DBPropertyBase):

    def __init__(self, factory, sectionName = None):
        self.factory = factory
        super(DBModelProperty, self).__init__(None, sectionName)
        return

    @property
    def default(self):
        return self.factory()

    def read(self, section, instance = None):
        if section and section.has_key(self.sectionName):
            modelData = section[self.sectionName]
            if instance:
                model = self.get(instance)
                model.read(modelData)
            else:
                model = self._doRead(modelData)
            return (True, model)
        else:
            return (False, None)

    def _doRead(self, section):
        model = self.default
        model.read(section)
        return model


class DBListProperty(DBPropertyBase):
    """Property containing array-like data. Usage:
    
        class MyModel(DBModelBase):
            array = DBListProperty(elementType=DBIntProperty(sectionName="element"))
    
    This corresponds to following XML file:
    
        <root>
            <array>
                <element> 15 </element>
                <element> 42 </element>
                <element> -180 </element>
                 ...
    
            </array>
        </root>
    """

    def __init__(self, elementType, sectionName = None):
        self.elementType = elementType
        super(DBListProperty, self).__init__(None, sectionName)
        return

    @property
    def default(self):
        return []

    def read(self, section, instance = None):
        if section and section.has_key(self.sectionName):
            result = self._doRead(section[self.sectionName])
            if instance:
                self.set(instance, result)
            return (True, result)
        else:
            return (False, None)

    def _doRead(self, section):
        result = []
        for name, child in section.items():
            if name == self.elementType.sectionName:
                result.append(self.elementType.doRead(child))

        return result


class DBPlaneTypesProperty(DBStringListProperty):

    def _strToPlaneType(self, s, section):
        res = PLANE_TYPE_NAME_REVERSED.get(s.strip(), None)
        if not res:
            raise ValueError('DBPlaneTypesProperty Error: conversion from {0} to plane type! (file: {1}; section: {2})'.format(s, section.filename, section.name))
        return res

    def _doRead(self, section):
        return map(lambda s: self._strToPlaneType(s, section), super(DBPlaneTypesProperty, self)._doRead(section))