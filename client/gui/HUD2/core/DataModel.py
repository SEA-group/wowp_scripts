# Embedded file name: scripts/client/gui/HUD2/core/DataModel.py
import weakref
from itertools import ifilter
from debug_utils import LOG_DEBUG

class Type:

    def __init__(self, baseType):
        self._baseType = baseType

    @property
    def baseType(self):
        return self._baseType

    @property
    def defaultValue(self):
        return self._baseType()


IntT = Type(int)
StringT = Type(str)
UnicodeT = Type(unicode)
FloatT = Type(float)
BoolT = Type(bool)
DictT = Type(dict)

class Structure(Type):

    def __init__(self, **kwargs):
        Type.__init__(self, {}.__class__)
        self._fields = kwargs

    @property
    def fields(self):
        return self._fields.items()

    def __getattr__(self, item):
        if item.startswith('__'):
            return object.__getattr__(self, item)
        raise item in self._fields or AssertionError('Wrong item: {0}, fields: {1}'.format(item, self._fields))
        return self._fields[item]


class List(Type):

    def __init__(self, type):
        Type.__init__(self, [].__class__)
        self._type = type

    @property
    def itemType(self):
        return self._type


class ModelAttr(object):

    def __init__(self, name, type_, parent):
        """
        :type name: str
        :type parent: ModelStructure
        """
        raise name is not None or AssertionError
        self._type = type_
        self._name = name
        self._parent = weakref.ref(parent) if parent is not None else None
        self._nameOfInterest = self._findNameOfInterest(parent)
        return

    def _findNameOfInterest(self, parent):
        result = self.fullName
        while parent is not None:
            if isinstance(parent, ModelList):
                result = parent.fullName
            parent = parent.parent

        return result

    def updateName(self, value):
        self._name = value

    @property
    def parent(self):
        if self._parent is not None:
            return self._parent()
        else:
            return

    @property
    def type(self):
        return self._type

    @property
    def name(self):
        return self._name

    @property
    def fullName(self):
        if self.parent is not None and self.parent.name != 'root':
            return self.parent.fullName + '.' + self.name
        else:
            return self.name

    @property
    def nameOfInterest(self):
        return self._nameOfInterest


class ModelField(ModelAttr):

    def __init__(self, name, type_, parent):
        """
        :type name: str
        :type type_: Type
        :type parent: ModelStructure
        """
        super(ModelField, self).__init__(name, type_, parent)
        raise parent is not None or AssertionError
        raise type_ is not None or AssertionError
        self._model = None
        self._value = type_.defaultValue
        self._notificationEnabled = True
        return

    def setNotification(self, value):
        self._notificationEnabled = value

    def setModel(self, model):
        self._model = model

    def get(self):
        return self._value

    def set(self, value):
        if not type(value) is self._type.baseType:
            raise AssertionError('Invalid value type: {0}. Field: {1}'.format(type(value), self._name))
            if self._value != value:
                self._value = value
                self._notificationEnabled and self._model.onFieldChanged(self)

    def __repr__(self):
        return str(self._value)


class ModelStructure(ModelAttr):

    def __init__(self, name, type_, parent):
        super(ModelStructure, self).__init__(name, type_, parent)
        self._fields = {}
        self._model = None
        return

    @property
    def fields(self):
        return self._fields

    def setFields(self, fields):
        self._fields = fields
        for name, field in fields.iteritems():
            setattr(self, name, field)

    def setModel(self, model):
        for field in self._fields.itervalues():
            field.setModel(model)

        self._model = model

    def set(self, **kwargs):
        for fieldName, value in kwargs.iteritems():
            raise fieldName in self._fields or AssertionError
            field = getattr(self, fieldName)
            field.setNotification(False)
            field.set(value)
            field.setNotification(True)

        self._model.onFieldChanged(self)

    def setSilently(self, **kwargs):
        for fieldName, value in kwargs.iteritems():
            raise fieldName in self._fields or AssertionError
            field = getattr(self, fieldName)
            field.setNotification(False)
            field.set(value)
            field.setNotification(True)

    def __setattr__(self, name, value):
        if not name.startswith('_') and hasattr(self, name):
            attr = getattr(self, name)
            attr.set(value)
        else:
            object.__setattr__(self, name, value)

    def __repr__(self):
        return str(self._fields)


class ModelList(ModelField):

    def __init__(self, name, type_, parent):
        super(ModelList, self).__init__(name, type_, parent)
        self._items = []
        self.__appendStarted = False

    @property
    def items(self):
        raise not self.__appendStarted or AssertionError('Appending silently not finished')
        return self._items

    def append(self, *args, **kwargs):
        if not not self.__appendStarted:
            raise AssertionError('Appending silently not finished')
            raise len(args) == 0 or len(kwargs) == 0 or AssertionError("You can't use both interfaces to set value at the same time")
            item = self._makeItemContainer()
            raise len(args) != 0 and (len(args) == 1 or AssertionError)
            item.set(args[0])
        else:
            item.set(**kwargs)
        self._items.append(item)
        self._model.onItemAppended(self)
        return item

    def appendSilently(self, *args, **kwargs):
        if not (len(args) == 0 or len(kwargs) == 0):
            raise AssertionError("You can't use both interfaces to set value at the same time")
            self.__appendStarted = True
            item = self._makeItemContainer()
            raise len(args) != 0 and (len(args) == 1 or AssertionError)
            item.set(args[0])
        else:
            item.setSilently(**kwargs)
        self._items.append(item)

    def finishAppending(self):
        if not self.__appendStarted:
            return
        self.__appendStarted = False
        self._model.onFieldChanged(self)

    def splice(self, item):
        raise not self.__appendStarted or AssertionError('Appending silently not finished')
        i = self._items.index(item)
        self._items.remove(item)
        self._model.onItemSpliced(self, i)
        for item in self._items:
            itemName = '{index}'.format(index=self._items.index(item))
            item.updateName(itemName)

    def clean(self):
        raise not self.__appendStarted or AssertionError('Appending silently not finished')
        self._items = []
        self._model.onListClean(self)

    def set(self, value):
        raise not self.__appendStarted or AssertionError('Appending silently not finished')
        self.clean()
        for e in value:
            self.append(**e)

    def get(self, index, quiet = False):
        if not not self.__appendStarted:
            raise AssertionError('Appending silently not finished')
            indexInRange = index < len(self._items)
            raise quiet or indexInRange or AssertionError
            return indexInRange and self.__getitem__(index)
        else:
            return None

    def first(self, pred):
        """
        Returns first element that satisfies predicate or None
        """
        return next(ifilter(pred, self._items), None)

    def _makeItemContainer(self):
        itemName = '{index}'.format(index=len(self._items))
        item = DataModel.createField(self._model.__class__, itemName, self, self._type.itemType)
        item.setModel(self._model)
        return item

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return str(self._items)


class DataModel(object):
    MODEL_FIELD_CLASS = ModelField
    MODEL_STRUCTURE_CLASS = ModelStructure
    MODEL_LIST_CLASS = ModelList
    SCHEME = None
    _SCHEME_FIELDS = []

    def __new__(cls, *args, **kwargs):
        instance = super(DataModel, cls).__new__(cls)
        scheme = cls.SCHEME
        if not (scheme is not None and scheme.__class__ is Structure):
            raise AssertionError
            root = DataModel.createFields(cls, scheme, 'root', None)
            for fieldName, field in root._fields.items():
                setattr(instance, fieldName, field)

            instance.SCHEME_FIELDS = root.fields
        return instance

    @staticmethod
    def createFields(modelCls, scheme, name, parent):
        """
        :type modelCls: DataModel
        """
        raise scheme.__class__ is Structure or AssertionError
        res = modelCls.MODEL_STRUCTURE_CLASS(name, scheme, parent)
        fields = {}
        for name, t in scheme.fields:
            field = DataModel.createField(modelCls, name, res, t)
            if field is None:
                continue
            fields[name] = field

        res.setFields(fields)
        return res

    @staticmethod
    def createField(modelCls, name, parent, type_):
        if isinstance(type_, Structure):
            return DataModel.createFields(modelCls, type_, name, parent)
        if isinstance(type_, List):
            return modelCls.MODEL_LIST_CLASS(name, type_, parent)
        if isinstance(type_, (type(IntT), type(FloatT), type(StringT))):
            return modelCls.MODEL_FIELD_CLASS(name, type_, parent)
        if issubclass(type_, DataModel):
            return DataModel.createFields(type_, type_.SCHEME, name, parent)
        raise False or AssertionError('Unsupported type. Field: {0} Type: {1}'.format(name, type_))

    def __init__(self):
        for e in self.SCHEME_FIELDS:
            getattr(self, e).setModel(weakref.proxy(self))

        self._proxyView = None
        self._interestedRoutes = set()
        return

    def destroy(self):
        self._SCHEME_FIELDS = None
        return

    def __setattr__(self, name, value):
        if not name.startswith('_') and hasattr(self, name):
            getattr(self, name).set(value)
        else:
            object.__setattr__(self, name, value)

    def registerProxyView(self, proxyView):
        """
        :param proxyView: ProxyView
        """
        self._proxyView = weakref.proxy(proxyView)

    def getFieldByName(self, fieldName, quiet = False):
        tokens = fieldName.split('.')
        field = self
        for t in tokens:
            if isinstance(field, ModelList):
                field = field.get(int(t), quiet)
            else:
                field = getattr(field, t, None)

        return field

    def subscribeField(self, propFullName):
        raise propFullName not in self._interestedRoutes or AssertionError('Already registered for %s' % propFullName)
        raise self.getFieldByName(propFullName, True) is not None or AssertionError('No such field in model: ' + propFullName)
        self._interestedRoutes.add(propFullName)
        return

    def unsubscribeField(self, propFullName):
        raise propFullName in self._interestedRoutes or AssertionError('Not registered for %s' % propFullName)
        self._interestedRoutes.remove(propFullName)

    def onFieldChanged(self, field):
        """
        Called in children on field change
        :type field: ModelField
        """
        if field.nameOfInterest in self._interestedRoutes:
            self._proxyView.onFieldChanged(field)

    def onItemAppended(self, field):
        """
        Called in children on item append
        :type field: ModelField
        """
        if field.nameOfInterest in self._interestedRoutes:
            self._proxyView.onItemAppended(field)

    def onItemSpliced(self, field, index):
        if field.nameOfInterest in self._interestedRoutes:
            self._proxyView.onItemSpliced(field, index)

    def onListClean(self, field):
        if field.nameOfInterest in self._interestedRoutes:
            self._proxyView.onListClean(field)