# Embedded file name: scripts/client/gui/HUD2/features/planeCharacteristics/PlaneCharacteristicsController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
import BWLogging

class PlaneCharacteristicsController(DataController):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)

    @message('planeCharacteristics.requestPlanesCharacteristics')
    def requestPlanesCharacteristics(self, globalId_1):
        self._logger.debug("requestPlanesCharacteristics : globalId= '{0}'".format(globalId_1))
        self._gameEnvironment.eGetPlanesCharacteristics([globalId_1])