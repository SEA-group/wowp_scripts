# Embedded file name: scripts/client/gui/HUD2/features/measurement/MeasurementSource.py
from clientConsts import SI_TO_IMPERIAL_METER, SI_TO_IMPERIAL_KMH
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
TAG = ' MeasurementSourceLOG : '

class MeasurementSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).measurementSystem
        self._uiSettings = features.require(Feature.UI_SETTINGS)
        self._ms = features.require(Feature.MEASUREMENT_SYSTEM)
        self._uiSettings.onMeasurementSystemChanged += self._onSetMeasurementSystem
        self._model.measurementSystem = self._uiSettings.gameUI['measurementSystem']
        self._model.SI_TO_IMPERIAL_METER = SI_TO_IMPERIAL_METER
        self._model.SI_TO_IMPERIAL_KMH = SI_TO_IMPERIAL_KMH
        self._model.WORLD_SCALING = 4.5

    def _onSetMeasurementSystem(self, *args, **kwargs):
        self._ms.onMeasurementSystemChanged()
        self._model.measurementSystem = self._uiSettings.gameUI['measurementSystem']
        LOG_DEBUG(TAG, '_onSetMeasurementSystem ', self._model.measurementSystem)

    def dispose(self):
        self._uiSettings.onMeasurementSystemChanged -= self._onSetMeasurementSystem
        self._model = None
        self._uiSettings = None
        self._ms = None
        return