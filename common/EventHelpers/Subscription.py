# Embedded file name: scripts/common/EventHelpers/Subscription.py
"""This module contains helper classes for managing event subscriptions
"""
from abc import ABCMeta, abstractmethod

class SubscriptionBase(object):
    """Base class for subscriptions.
    Subscription is object that holds event sender and and event handler
    and define subscribe and unsubscribe actions.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe(self):
        """Subscribe handler to event sender
        """
        raise NotImplementedError()

    @abstractmethod
    def unsubscribe(self):
        """Unsubscribe handler from event sender
        """
        raise NotImplementedError()


class EventSubscription(SubscriptionBase):
    """Subscription for Event.Event objects.
    Usage example:
    
        eAvatarCreated = Event.Event()
    
        def onAvatarCreated(avatar):
            pass
    
        subscription = EventSubscription(eAvatarCreated, onAvatarCreated)
        subscription.subscribe()  # Now onAvatarCreated is subscribed to eAvatarCreated
    
        ...
        subscription.unsubscribe()  # Now onAvatarCreated is not subscribed to eAvatarCreated
    """

    def __init__(self, dispatcher, handler):
        super(EventSubscription, self).__init__()
        self._dispatcher = dispatcher
        self._handler = handler

    def subscribe(self):
        self._dispatcher += self._handler

    def unsubscribe(self):
        self._dispatcher -= self._handler


class EDSubscription(SubscriptionBase):
    """Subscription for Event.EventDispatcher objects.
    Usage example:
    
        gameModeDispatcher = Event.EventDispatcher()
    
        def onAvatarCreated(avatar):
            pass
    
        subscription = EventSubscription(gameModeDispatcher, EVENT.AVATAR_CREATED, onAvatarCreated)
        subscription.subscribe()  # Now onAvatarCreated is subscribed to gameModeDispatcher on EVENT.AVATAR_CREATED
    
        ...
        subscription.unsubscribe()  # Now onAvatarCreated is not subscribed to gameModeDispatcher
    """

    def __init__(self, dispatcher, eType, handler):
        super(EDSubscription, self).__init__()
        self._dispatcher = dispatcher
        self._eType = eType
        self._handler = handler

    def subscribe(self):
        self._dispatcher.addEventHandler(self._eType, self._handler)

    def unsubscribe(self):
        self._dispatcher.removeEventHandler(self._eType, self._handler)


class CompositeSubscription(SubscriptionBase):
    """Composite pattern implementation for subscriptions
    """

    def __init__(self, *subscriptions):
        super(CompositeSubscription, self).__init__()
        self._subscriptions = list(subscriptions)

    def subscribe(self):
        for subscription in self._subscriptions:
            subscription.subscribe()

    def unsubscribe(self):
        for subscription in self._subscriptions:
            subscription.unsubscribe()

    def extend(self, *subscriptions):
        """Add subscriptions to container.
        CAn be used for dynamic container updates instead of providing all subscriptions in constructor
        @param subscriptions: Subscriptions to add
        """
        self._subscriptions.extend(subscriptions)