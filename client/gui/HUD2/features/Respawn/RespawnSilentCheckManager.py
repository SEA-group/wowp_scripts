# Embedded file name: scripts/client/gui/HUD2/features/Respawn/RespawnSilentCheckManager.py
from debug_utils import LOG_DEBUG
import GlobalEvents
from Event import EventManager, Event
from gui.HUD2.hudFeatures import Feature
REST_DELAY = 15

class RespawnSilentCheckManager(object):

    def __init__(self, features, needState):
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._state = needState
        self._eventManager = EventManager()
        self.eRestDelay = Event(self._eventManager)
        self._lastCheckTime = 0
        self._currentCheckTime = 0
        self._isChecking = False
        self._subscribe()

    def startCheck(self, value = True):
        LOG_DEBUG(' RespawnSilentCheckManager: startCheck ', value)
        self._isChecking = value
        self._currentCheckTime = self._bigWorld.serverTime()
        self._lastCheckTime = self._bigWorld.serverTime()

    def _subscribe(self):
        self._timer.eUpdate1Sec += self._onUpdateTime
        GlobalEvents.onMouseEvent.insert(0, self.handleMouseEvent)
        GlobalEvents.onKeyEvent += self.handleKeyEvent
        GlobalEvents.onAxisEvent += self.handleAxisEvent

    def _unsubscribe(self):
        self._timer.eUpdate1Sec -= self._onUpdateTime
        GlobalEvents.onMouseEvent.remove(self.handleMouseEvent)
        GlobalEvents.onKeyEvent -= self.handleKeyEvent
        GlobalEvents.onAxisEvent -= self.handleAxisEvent

    def changeState(self, newValue):
        if newValue & self._state:
            self.startCheck()
        else:
            self.startCheck(False)

    def handleKeyEvent(self, event):
        self._onUpdateControlEvent()

    def handleMouseEvent(self, event):
        self._onUpdateControlEvent()

    def handleAxisEvent(self, event):
        self._onUpdateControlEvent()

    def _onUpdateTime(self):
        LOG_DEBUG(' RespawnSilentCheckManager: _onUpdateTime ', self._isChecking)
        if self._isChecking:
            self._currentCheckTime = self._bigWorld.serverTime()
            restTime = self._currentCheckTime - self._lastCheckTime
            if restTime > REST_DELAY:
                self.startCheck(False)
                self.eRestDelay()

    def _onUpdateControlEvent(self):
        if self._isChecking:
            self._lastCheckTime = self._bigWorld.serverTime()

    def dispose(self):
        self._unsubscribe()
        self._bigWorld = None
        self._timer = None
        self._eventManager = None
        return