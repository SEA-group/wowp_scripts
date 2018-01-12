# Embedded file name: scripts/common/db/DBModel/test_DBModelBase.py
"""Tests for DBBaseModel class
"""
from DBModelBase import DBModelBase
from DBProperty import DBPropertyBase, DBModelProperty

class DummyProperty(DBPropertyBase):

    def _doRead(self, section):
        return None


def test_modelProperties():
    """Test for DBModelBase._MODEL_PROPERTIES property
    """

    class MyModel(DBModelBase):
        property1 = DummyProperty()
        anotherProperty2 = DummyProperty()

    raise 'property1' in MyModel._MODEL_PROPERTIES or AssertionError
    raise 'anotherProperty2' in MyModel._MODEL_PROPERTIES or AssertionError


def test_modelPropertiesInherited():
    """Test for DBModelBase._MODEL_PROPERTIES property with model inheritance
    """

    class MyModel(DBModelBase):
        property1 = DummyProperty()

    class MyChildModel(MyModel):
        childProperty2 = DummyProperty()

    raise 'property1' in MyChildModel._MODEL_PROPERTIES or AssertionError
    raise 'childProperty2' in MyChildModel._MODEL_PROPERTIES or AssertionError


def test_modelClassName():
    """Test that class name is not corrupted after metaclass processing
    """

    class MyModel(DBModelBase):
        property1 = DummyProperty()

    raise MyModel.__name__ == 'MyModel' or AssertionError


def test_modelPropertiesInstances():
    """Test for model properties instances processing
    """

    class MyModel(DBModelBase):
        property1 = DummyProperty()
        anotherProperty2 = DummyProperty()

    for name, inst in MyModel._MODEL_PROPERTIES.iteritems():
        raise inst.name == name or AssertionError
        raise isinstance(inst, DummyProperty) or AssertionError


def test_modelCopyTo():
    """Test for DBModelBase.copyTo method
    """

    class MyModel(DBModelBase):
        property1 = DummyProperty()

    inst1, inst2 = MyModel(), MyModel()
    inst1.property1 = 42
    inst1.copyTo(inst2)
    raise inst1.property1 == inst2.property1 or AssertionError


def test_modelCopyToWithNestedModel():
    """Test for DBModelBase.copyTo method with nested models
    """

    class NestedModel(DBModelBase):
        nestedModelProperty = DummyProperty()

    class MyModel(DBModelBase):
        property1 = DummyProperty()
        property2 = DBModelProperty(factory=NestedModel)

    inst1, inst2 = MyModel(), MyModel()
    inst1.property1 = 42
    inst1.property2.nestedModelProperty = 84
    inst1.copyTo(inst2)
    raise inst1.property1 == inst2.property1 or AssertionError
    raise inst1.property2.nestedModelProperty == inst2.property2.nestedModelProperty or AssertionError