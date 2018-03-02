# Embedded file name: scripts/common/ExecutionManager.py
import weakref
from functools import partial
from BWLogging import getLogger

class ExecutionManager(object):
    instance = None

    @classmethod
    def call(cls, func_, *args, **kwargs):
        cls.instance.direct_call(func_, *args, **kwargs)

    def __init__(self):
        type(self).instance = self
        self.objects = {}
        self.calls = []
        self.logger = getLogger(type(self).__name__)

    def destroy(self):
        self.objects = {}
        self.calls = []
        self.logger = None
        type(self).instance = None
        return

    def __del__(self):
        pass

    def regicClass(self, object_):
        raise object_.__class__ not in self.objects or AssertionError
        self.objects[object_.__class__] = weakref.ref(object_)

    def unregicClass(self, object_):
        if object_.__class__ in self.objects:
            del self.objects[object_.__class__]

    def direct_call(self, func_, *args, **kwargs):
        classObject = self.objects.get(func_.im_class, None)
        raise classObject is not None or AssertionError('Object is not registered')
        return self.__call(classObject, func_, *args, **kwargs)

    def __call(self, obj_ref, func_, *args, **kwargs):
        obj = obj_ref()
        if obj:
            return func_(obj, *args, **kwargs)
        else:
            self.logger.error('{0} Error: object owner for method "{1}" not valid'.format(self.__class__.__name__, func_.__name__))
            return None


class RegicToExecutionManager(object):
    ManagerClass = ExecutionManager

    def __init__(self):
        self.__classRegistered = False
        self.regicClass()

    def __del__(self):
        self.unregicClass()

    def regicClass(self):
        self.ManagerClass.instance.regicClass(self)
        self.__classRegistered = True

    def unregicClass(self):
        if self.__classRegistered:
            self.ManagerClass.instance.unregicClass(self)
            self.__classRegistered = False