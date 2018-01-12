# Embedded file name: scripts/client/GameActionsManagerProxy.py
from Event import Event, EventManager
from EventHelpers import CompositeSubscription, EventSubscription

class GameActionsManagerProxy(object):

    def __init__(self):
        self._entity = None
        self._subscription = None
        self._eManager = EventManager()
        self.eWaveAdded = Event(self._eManager)
        self.eWaveRemoved = Event(self._eManager)
        self.eWaveStateChanged = Event(self._eManager)
        self.eBomberStateChanged = Event(self._eManager)
        return

    @property
    def activeASWaves(self):
        if self._entity:
            return self._entity.activeASWaves
        return []

    def onManagerEnterWorld(self, entity):
        raise not self._entity or AssertionError('Attempt to override registered manager, old = {0}, new = {1}'.format(self._entity, entity))
        self._entity = entity
        self._subscribeOn(entity)

    def onManagerLeaveWorld(self, entity):
        raise self._entity is entity or AssertionError('Attempt to unregister unknown manager: {0}, registered: {1}'.format(entity, self._entity))
        self._unsubscribe()
        self._entity = None
        return

    def cleanup(self):
        self._eManager.clear()

    def _subscribeOn(self, entity):
        raise self._subscription is None or AssertionError('Attempt to override subscription')
        self._subscription = CompositeSubscription(EventSubscription(entity.eWaveAdded, self.eWaveAdded), EventSubscription(entity.eWaveRemoved, self.eWaveRemoved), EventSubscription(entity.eWaveStateChanged, self.eWaveStateChanged), EventSubscription(entity.eBomberStateChanged, self.eBomberStateChanged))
        self._subscription.subscribe()
        return

    def _unsubscribe(self):
        raise self._subscription or AssertionError('Subscription is None')
        self._subscription.unsubscribe()
        self._subscription = None
        return