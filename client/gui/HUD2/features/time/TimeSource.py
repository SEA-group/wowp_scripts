# Embedded file name: scripts/client/gui/HUD2/features/time/TimeSource.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class TimeSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).time
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._timer.eUpdate1Sec += self._onUpdate
        self._time = 0
        self._model.timeMax = self._clientArena.gameMode.arenaTypeData._gameModeSettings.battleDuration

    def _onUpdate(self):
        serverTime = self._bigWorld.serverTime()
        arenaStartTime = self._player.arenaStartTime
        currentTime = int(round(serverTime - arenaStartTime))
        if arenaStartTime > 0:
            self._model.time = currentTime

    def dispose(self):
        self._timer.eUpdate1Sec -= self._onUpdate
        self._timer = None
        self._model = None
        return