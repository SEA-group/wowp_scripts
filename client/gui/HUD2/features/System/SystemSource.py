# Embedded file name: scripts/client/gui/HUD2/features/System/SystemSource.py
from consts import SERVER_TICK_LENGTH
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.core.FeatureBroker import Require

class SystemSource(DataSource):
    BigWorld = Require('BigWorld')

    def __init__(self, model):
        """
        :type model: SystemModel.SystemModel
        """
        self._model = model

    def update1sec(self):
        self._model.FPS = self._getFPS()
        self._model.Ping = self._calcPing()

    def _getFPS(self):
        return int(self.BigWorld.getFPS()[1])

    def _calcPing(self):
        ping = self.BigWorld.LatencyInfo().value[3] * 1000 - SERVER_TICK_LENGTH * 0.5 * 1000
        return max(1, int(ping))