# Embedded file name: scripts/common/Event.py
from debug_utils import *
import weakref
from WeakMethod import WeakMethod

class ObserverException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Event(object):

    def __init__(self, manager = None, silently = not config_consts.IS_DEVELOPMENT):
        self._isCalling = False
        self._silently = silently
        self.__delegates = dict()
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args, **kw):
        self._isCalling = True
        for key, weakMethod in self.__delegates.items():
            try:
                if not weakMethod.isValid:
                    del self.__delegates[key]
                    continue
                weakMethod(*args, **kw)
                if weakMethod.errorOccurred:
                    del self.__delegates[key]
                    if not self._silently:
                        self._raiseException(weakMethod)
            except:
                LOG_CURRENT_EXCEPTION()

        self._isCalling = False

    def __iadd__(self, delegate):
        if not self._silently and delegate is None:
            raise ObserverException('EVENT ERROR: Callback is None')
        wMt = WeakMethod.ref(delegate)
        self.__delegates[wMt.id] = wMt
        return self

    def __isub__(self, delegate):
        dlgID = WeakMethod.generateID(delegate)
        if self._isCalling:
            wMt = self.__delegates.get(dlgID, None)
            if wMt:
                wMt.isValid = False
        else:
            self.__delegates.pop(dlgID, None)
        return self

    def clear(self):
        self.__delegates.clear()

    def __repr__(self):
        return 'Event(%s):%s' % (len(self.__delegates), repr(self.__delegates))

    def isSubscribed(self, delegate):
        wMt = WeakMethod.ref(delegate)
        return self.__delegates.has_key(wMt.id)

    def delegatesCount(self):
        return len(self.__delegates)

    def _raiseException(self, weakMethod):
        from traceback import print_stack
        print_stack()
        errorMsg = 'EVENT ERROR: Callback not valid because owner object was destroyed! Method: {0}: {1} / {2}'.format(weakMethod.fn.__name__, weakMethod.fn.func_code.co_filename, str(weakMethod.fn.func_code.co_firstlineno))
        raise ObserverException(errorMsg)


class LazyEvent(Event):

    def __init__(self, manager = None):
        Event.__init__(self, manager)
        self._lastArgs = []
        self._lastKwargs = {}

    def __call__(self, *args, **kw):
        self._lastArgs = args
        self._lastKwargs = kw
        Event.__call__(self, *args, **kw)

    def __iadd__(self, delegate):
        res = Event.__iadd__(self, delegate)
        try:
            delegate(*self._lastArgs, **self._lastKwargs)
        except TypeError:
            pass

        return res

    def clear(self):
        Event.clear(self)
        self._lastKwargs = {}
        self._lastArgs = []


class EventOrdered(object):

    def __init__(self, manager = None):
        self.__delegates = list()
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args, **kw):
        for delegate in self.__delegates:
            try:
                delegate(*args, **kw)
            except:
                LOG_CURRENT_EXCEPTION()

    def __iadd__(self, delegate):
        if delegate not in self.__delegates:
            self.__delegates.append(delegate)
        return self

    def __isub__(self, delegate):
        if delegate in self.__delegates:
            self.__delegates.remove(delegate)
        return self

    def clear(self):
        self.__delegates = list()

    def __repr__(self):
        return 'Event(%s):%s' % (len(self.__delegates), repr(self.__delegates))


class BlockingEvent(object):

    def __init__(self, manager = None):
        self.__delegates = list()
        if manager is not None:
            manager.register(self)
        return

    def insert(self, index, delegate):
        if delegate not in self.__delegates:
            self.__delegates.insert(index, delegate)

    def remove(self, delegate):
        self.__delegates.remove(delegate)

    def __call__(self, *args):
        for delegate in self.__delegates:
            try:
                if delegate(*args):
                    return True
            except:
                LOG_CURRENT_EXCEPTION()

        return False

    def __iadd__(self, delegate):
        if delegate not in self.__delegates:
            self.__delegates.append(delegate)
        return self

    def __isub__(self, delegate):
        self.__delegates.remove(delegate)
        return self

    def clear(self):
        self.__delegates[:] = []

    def __repr__(self):
        return 'Event(%s):%s' % (len(self.__delegates), repr(self.__delegates))


class Handler(object):

    def __init__(self, manager = None):
        self.__delegate = None
        if manager is not None:
            manager.register(self)
        return

    def __call__(self, *args):
        if self.__delegate is not None:
            return self.__delegate(*args)
        else:
            return

    def set(self, delegate):
        self.__delegate = delegate

    def clear(self):
        self.__delegate = None
        return


class EventManager(object):

    def __init__(self):
        self.__events = []

    def register(self, event):
        self.__events.append(event)

    def clear(self):
        for event in self.__events:
            event.clear()


class SmartProperty(object):

    def __init__(self, value):
        self.onChange = Event()
        self.value = value

    @property
    def value(self):
        if callable(self.__value):
            return self.__value()
        return self.__value

    @value.setter
    def value(self, val):
        self.__value = val
        if val.__class__ is SmartProperty:
            val.onChange += self.onChange
        self.onChange()

    def __nonzero__(self):
        return bool(self.value)

    def __and__(self, other):
        res = SmartProperty(lambda : self.value and other.value)
        self.onChange += res.onChange
        other.onChange += res.onChange
        return res

    def __or__(self, other):
        res = SmartProperty(lambda : self.value or other.value)
        self.onChange += res.onChange
        other.onChange += res.onChange
        return res

    def __invert__(self):
        res = SmartProperty(lambda : not self.value)
        self.onChange += res.onChange
        return res


class EventDispatcher(object):
    ignoreEvents = tuple()

    def __init__(self):
        self._subscribers = set()
        self._eventHandlers = {}
        cls = self.__class__
        for name in dir(cls):
            attr = getattr(cls, name)
            events = getattr(attr, '_events_', set())
            for event in events:
                raise callable(attr) or AssertionError(attr)
                method = attr.__get__(self, cls)
                self._eventHandlers.setdefault(event, []).append(method)

    def dispatch(self, event, *args, **kwargs):
        if event in self.ignoreEvents:
            return
        for h in self._eventHandlers.get(event, []):
            h(*args, **kwargs)

        for s in self._subscribers:
            s.dispatch(event, *args, **kwargs)

    def addEventHandler(self, event, method):
        self._eventHandlers.setdefault(event, []).append(method)

    def removeEventHandler(self, event, method):
        if event in self._eventHandlers:
            self._eventHandlers.get(event).remove(method)

    def subscribe(self, obj):
        raise isinstance(obj, EventDispatcher) or AssertionError(obj)
        self._subscribers.add(obj)

    def unsubscribe(self, obj):
        raise isinstance(obj, EventDispatcher) or AssertionError(obj)
        self._subscribers.discard(obj)

    def clear(self):
        self._eventHandlers.clear()
        for s in self._subscribers:
            s.clear()

        self._subscribers.clear()


def eventHandler(event):

    def wrapper(func):
        events = getattr(func, '_events_', set())
        events.add(event)
        func._events_ = events
        return func

    return wrapper