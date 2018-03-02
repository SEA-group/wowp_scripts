# Embedded file name: scripts/client/gui/HUD2/features/Utils/UtilsSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class UtilsSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).utils
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._playerAvatar.onObserver += self._onObserver
        self._model.cameraIsReady = False

    def _onObserver(self):
        self._model.cameraIsReady = True
        self._model.cameraIsReady = False

    def dispose(self):
        self._playerAvatar.onObserver -= self._onObserver