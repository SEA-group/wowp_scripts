# Embedded file name: scripts/client/gui/HUD2/features/AttitudeIndicator/AttitudeIndicatorSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class AttitudeIndicatorSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).attitudeIndicator
        self._uiSettings = features.require(Feature.UI_SETTINGS)
        self._uiSettings.eAttitudeModeChanged += self._updateAttitudeMode
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        return

    def _setupModel(self, newInfos):
        self._model.attitudeMode = self._uiSettings.gameUI['attitudeMode']

    def _updateAttitudeMode(self, *args, **kwargs):
        self._model.attitudeMode = self._uiSettings.gameUI['attitudeMode']

    def dispose(self):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._uiSettings.eAttitudeModeChanged += self._updateAttitudeMode
        self._model = None
        self._uiSettings = None
        self._clientArena = None
        return