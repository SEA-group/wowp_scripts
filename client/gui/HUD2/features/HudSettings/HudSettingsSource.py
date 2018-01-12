# Embedded file name: scripts/client/gui/HUD2/features/HudSettings/HudSettingsSource.py
from config_consts import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
LOG_TAG = '  HUD_SETTINGS : '

class HudSettingsSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).hudSettings
        self._db = features.require(Feature.DB_LOGIC)
        self._setModel()

    def _setModel(self):
        LOG_DEBUG(LOG_TAG, 'isShowSectorMarkers: ', self._db.getACHudSettings().getMarkersSettings.isShowSectorMarkers)
        self._model.isShowSectorMarkers = self._db.getACHudSettings().getMarkersSettings.isShowSectorMarkers
        self._model.isDevelopment = IS_DEVELOPMENT

    def dispose(self):
        self._model = None
        return