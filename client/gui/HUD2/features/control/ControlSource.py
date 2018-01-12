# Embedded file name: scripts/client/gui/HUD2/features/control/ControlSource.py
import InputMapping
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class ControlSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).control
        self._input = features.require(Feature.INPUT)
        self._processor = self._input.commandProcessor
        self._processor.addListeners(InputMapping.CMD_SHOW_PLAYERS_INFO, self._onShowPlayerInfo, self._onHidePlayerInfo)

    def _onShowPlayerInfo(self):
        self._model.altPress = True

    def _onHidePlayerInfo(self):
        self._model.altPress = False

    def dispose(self):
        self._model = None
        self._processor = None
        self._input = None
        return