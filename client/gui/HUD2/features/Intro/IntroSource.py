# Embedded file name: scripts/client/gui/HUD2/features/Intro/IntroSource.py
from time import time
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class IntroSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).Intro
        self._setupModel()

    def _setupModel(self):
        self._model.EndTime = time() * 1000.0 + 1000.0

    def dispose(self):
        self._model = None
        return