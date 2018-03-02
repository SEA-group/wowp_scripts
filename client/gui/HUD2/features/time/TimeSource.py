# Embedded file name: scripts/client/gui/HUD2/features/time/TimeSource.py
from debug_utils import LOG_DEBUG
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class TimeSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).time
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._gameMode.addEventHandler(AC_EVENTS.DYNAMIC_TIMER_UPDATE, self._onDynamicTimerUpdate)
        self._timer.eUpdate1Sec += self._onUpdate
        self._time = 0
        self._model.timeMax = self._clientArena.gameMode.arenaTypeData._gameModeSettings.battleDuration

    def _onDynamicTimerUpdate(self, dynamicTime, *args, **kwargs):
        currentTime = self._getCurTime()
        self._model.timeMax = int(dynamicTime)
        self._model.time = currentTime

    def _onUpdate(self):
        arenaStartTime = self._player.arenaStartTime
        currentTime = self._getCurTime()
        if arenaStartTime > 0:
            self._model.time = currentTime

    def _getCurTime(self):
        serverTime = self._bigWorld.serverTime()
        arenaStartTime = self._player.arenaStartTime
        currentTime = int(round(serverTime - arenaStartTime))
        return currentTime

    def dispose(self):
        self._gameMode.removeEventHandler(AC_EVENTS.DYNAMIC_TIMER_UPDATE, self._onDynamicTimerUpdate)
        self._timer.eUpdate1Sec -= self._onUpdate
        self._gameMode = None
        self._timer = None
        self._model = None
        return