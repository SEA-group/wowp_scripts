# Embedded file name: scripts/client/gui/HUD2/features/Radar/RadarController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
import BWLogging

class RadarController(DataController):
    """
    Controller receive messages from frontend(look in HUDExternalConst.as)
    """

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).radar

    @message('radar.radarZoomIn')
    def radarZoomIn(self):
        self._logger.debug('radarZoomIn')
        self._model.source.radarZoomIn()

    @message('radar.radarZoomOut')
    def radarZoomOut(self):
        self._logger.debug('radarZoomOut')
        self._model.source.radarZoomOut()

    @message('radar.onIncreaseMap')
    def onIncreaseMap(self):
        self._model.source.onIncreaseMap()
        self._logger.debug('onIncreaseMap')

    @message('radar.onDecreaseMap')
    def onDecreaseMap(self):
        self._model.source.onDecreaseMap()
        self._logger.debug('onDecreaseMap')

    @message('radar.onSetMapMaxSize')
    def onSetMapMaxSize(self, maxSize):
        self._model.source.onSetMapMaxSize(int(maxSize))
        self._logger.debug('onSetMapMaxSize')