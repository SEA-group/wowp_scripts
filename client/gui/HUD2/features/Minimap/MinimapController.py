# Embedded file name: scripts/client/gui/HUD2/features/Minimap/MinimapController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
from debug_utils import LOG_DEBUG

class MinimapController(DataController):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).minimap

    @message('minimap.setMinimapMaxSize')
    def setMinimapMaxSize(self, size):
        self._model.source.setMinimapMaxSize(int(size))

    @message('minimap.increaseMinimapSize')
    def increaseMinimapSize(self):
        self._model.source.increaseMinimapSize()

    @message('minimap.decreaseMinimapSize')
    def decreaseMinimapSize(self):
        self._model.source.decreaseMinimapSize()

    def dispose(self):
        self._model = None
        return