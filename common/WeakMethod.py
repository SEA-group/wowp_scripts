# Embedded file name: scripts/common/WeakMethod.py
import weakref

class WeakMethod(object):

    @staticmethod
    def ref(delegate):
        return WeakMethod(delegate)

    @staticmethod
    def generateID(delegate):
        if hasattr(delegate, 'im_self'):
            return str(id(delegate.im_self)) + ':' + str(id(delegate.im_func))
        return str(id(delegate))

    def __init__(self, delegate):
        self.isValid = True
        self.errorOccurred = False
        self.id = WeakMethod.generateID(delegate)
        self._owner, self.fn = (weakref.ref(delegate.im_self), delegate.im_func) if hasattr(delegate, 'im_self') else (None, delegate)
        return

    def __call__(self, *args, **kwargs):
        self.errorOccurred = False
        if self._owner is None:
            return self.fn(*args, **kwargs)
        else:
            owner = self._owner()
            if owner:
                return self.fn(owner, *args, **kwargs)
            self.errorOccurred = True
            return