# Embedded file name: scripts/client/gui/HUD2/features/systemInfo/SystemInfoSource.py
import BigWorld
from consts import SERVER_TICK_LENGTH
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class SystemInfoSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).systemInfo
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._timer.eUpdate += self._update

    def _update(self):
        self._model.fps = self._getFPS()
        self._model.ping = self._calcPing()
        self._model.packLost = self._calcLost()

    def _getFPS(self):
        return int(BigWorld.getFPS()[1])

    def _calcPing(self):
        ping = BigWorld.LatencyInfo().value[3] * 1000 - SERVER_TICK_LENGTH * 0.5 * 1000
        return max(1, int(ping))

    def _calcLost(self):
        dataLost = 0
        owner = BigWorld.player()
        if owner is not None and owner.inWorld and owner.movementFilter():
            dataLost = owner.filter.dataLost
        return dataLost

    def dispose(self):
        self._timer.eUpdate -= self._update
        self._timer = None
        self._model = None
        return