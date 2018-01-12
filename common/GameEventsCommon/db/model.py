# Embedded file name: scripts/common/GameEventsCommon/db/model.py
from contextlib import contextmanager

class Model(object):
    registered = set()
    NAME = 'base'
    DESCRIPTION = 'Base model for any object provided by backend'

    def __init__(self, backend, instance = None, filters = None):
        self._backend = backend
        self._context = None
        self._instance = instance
        self._filters = filters
        self._contextInstances = []
        self.__class__.registered.add(self)
        self._prepareBackend()
        return

    def _prepareBackend(self):
        self.idsList = [ item.id for item in self.all() ]

    def switchBackend(self, backend):
        self._backend = backend
        self._prepareBackend()

    def asDict(self, structure, items = None):
        result = {}
        items = items or self.all(includeNested=False)
        for item in items:
            children = self.asDict(structure, self.filter(parent=item.id))
            result[item.id] = structure(item, children)

        return result

    def asListOfDicts(self, structure, items = None):
        result = []
        items = items or self.all(includeNested=False)
        for item in items:
            children = self.asListOfDicts(structure, self.filter(parent=item.id))
            result.append(structure(item, children))

        return result

    @classmethod
    def getModelByClassName(cls, name):
        for model in cls.registered:
            if name == model.__class__.__name__:
                return model

    @contextmanager
    def use(self, context):
        self._contextInstances = []
        self._context = context
        yield self
        while self._contextInstances:
            obj = self._contextInstances.pop()
            obj._context = None
            obj.attrs = None
            obj.model = None
            del obj

        self._context = None
        return

    def _adapt(self, obj):
        if self._instance and obj:
            return self._instance(obj, self._context, self)
        return obj

    def all(self, type_ = None, includeNested = True):
        for obj in self._backend.all(type_, includeNested):
            adapted = self._adapt(obj)
            if self._context:
                self._contextInstances.append(adapted)
            yield adapted

    def get(self, **attrs):
        adapted = self._adapt(self._backend.get(**attrs))
        if adapted:
            if self._context:
                self._contextInstances.append(adapted)
        return adapted

    def has(self, *attrs):
        for obj in self._backend.has(*attrs):
            adapted = self._adapt(obj)
            if self._context:
                self._contextInstances.append(adapted)
            yield adapted

    def filter(self, **attrs):
        if not attrs:
            for obj in self.all():
                yield obj

        else:
            for obj in self._backend.filter(**attrs):
                adapted = self._adapt(obj)
                if self._context:
                    self._contextInstances.append(adapted)
                yield adapted