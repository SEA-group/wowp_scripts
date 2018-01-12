# Embedded file name: scripts/client/gui/HUD2/features/Minimap/MinimapSource.py
import InputMapping
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from debug_utils import LOG_DEBUG

class MinimapSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).minimap
        self._model.source = self
        self._uiSettings = features.require(Feature.UI_SETTINGS)
        self._model.currentSize = self._uiSettings.gameUI['hudMinimapSize']
        self._model.maxSize = -1
        self._processor = features.require(Feature.INPUT).commandProcessor
        self._processor.addListeners(InputMapping.CMD_MINIMAP_SIZE_INC, self.increaseMinimapSize)
        self._processor.addListeners(InputMapping.CMD_MINIMAP_SIZE_DEC, self.decreaseMinimapSize)

    def setMinimapMaxSize(self, size):
        self._model.maxSize = size

    def increaseMinimapSize(self):
        if self._model.currentSize.get() < self._model.maxSize.get():
            self._setCurrentSize(self._model.currentSize.get() + 1)

    def decreaseMinimapSize(self):
        if self._model.currentSize.get() > 0:
            self._setCurrentSize(self._model.currentSize.get() - 1)

    def _setCurrentSize(self, size):
        self._model.currentSize = size
        self._uiSettings.gameUI['hudMinimapSize'] = size

    def dispose(self):
        self._model = None
        self._processor = None
        self._uiSettings = None
        return