# Embedded file name: scripts/common/db/DBModel/test_DBProperty.py
"""Tests for DBProperty class
"""
import pytest
import ResMgr
from consts import WORLD_SCALING
from xml.etree import ElementTree
from DBModelBase import DBModelBase
from DBProperty import DBIntProperty, DBFloatProperty, DBStringProperty, DBWorldScaledProperty, DBListProperty

class AtomicTypedPropertyTestCase(object):
    XML_TEMPLATE = '\n        <root>\n            <property1>{value}</property1>\n        </root>\n    '

    def __init__(self, propertyType, value, expectedValue):
        self.propertyType, self.value, self.expectedValue = propertyType, value, expectedValue
        xmlText = self.XML_TEMPLATE.format(value=value)
        self.dataSection = ResMgr.DataSection('root', ElementTree.XML(xmlText), '')


ATPTC = AtomicTypedPropertyTestCase
ATOMIC_TEST_CASES = (ATPTC(propertyType=DBIntProperty, value='145', expectedValue=145),
 ATPTC(propertyType=DBIntProperty, value='-8965', expectedValue=-8965),
 ATPTC(propertyType=DBFloatProperty, value='5.05', expectedValue=5.05),
 ATPTC(propertyType=DBStringProperty, value='SomeText', expectedValue='SomeText'),
 ATPTC(propertyType=DBStringProperty, value='   SomeTextWithSpaces  ', expectedValue='SomeTextWithSpaces'),
 ATPTC(propertyType=DBStringProperty, value='   Some Text With Spaces  ', expectedValue='Some Text With Spaces'),
 ATPTC(propertyType=DBWorldScaledProperty, value='42', expectedValue=42 * WORLD_SCALING))

@pytest.mark.parametrize('case', ATOMIC_TEST_CASES)
def test_atomicTypedProperty(case):

    class MyModel(DBModelBase):
        property1 = case.propertyType()

    model = MyModel()
    model.read(case.dataSection)
    raise model.property1 == case.expectedValue or AssertionError


class DBListPropertyTestCase(object):
    ELEMENT_TEMPLATE = '<{elementName}>{value}</{elementName}>'
    XML_TEMPLATE = '\n        <root>\n            <property1>\n                {elements}\n            </property1>\n        </root>\n    '

    def __init__(self, propertyType, values, expectedValues):
        self.propertyType, self.values, self.expectedValues = propertyType, values, expectedValues
        xmlValues = '\n'.join((self.ELEMENT_TEMPLATE.format(elementName=propertyType.sectionName, value=v) for v in self.values))
        self.xmlText = self.XML_TEMPLATE.format(elements=xmlValues)
        self.dataSection = ResMgr.DataSection('root', ElementTree.XML(self.xmlText), '')


DBLPTC = DBListPropertyTestCase
LIST_TEST_CASES = (DBLPTC(propertyType=DBIntProperty(sectionName='value'), values=['145', '42', '-18'], expectedValues=[145, 42, -18]),
 DBLPTC(propertyType=DBFloatProperty(sectionName='value'), values=['5.05', '-12.8'], expectedValues=[5.05, -12.8]),
 DBLPTC(propertyType=DBStringProperty(sectionName='value'), values=['SomeText', '   SomeTextWithSpaces  ', '   Some Text With Spaces  '], expectedValues=['SomeText', 'SomeTextWithSpaces', 'Some Text With Spaces']),
 DBLPTC(propertyType=DBWorldScaledProperty(sectionName='value'), values=['42', '-18'], expectedValues=[42 * WORLD_SCALING, -18 * WORLD_SCALING]))

@pytest.mark.parametrize('case', LIST_TEST_CASES)
def test_listProperty(case):

    class MyModel(DBModelBase):
        property1 = DBListProperty(elementType=case.propertyType)

    model = MyModel()
    model.read(case.dataSection)
    raise model.property1 == case.expectedValues or AssertionError