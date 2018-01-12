# Embedded file name: scripts/client/gui/HUD2/features/PlaneData/BasePlaneDataController.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class BasePlaneDataController(DataController):

    def __init__(self, features):
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)

    @message('planes.getBasePlaneData')
    def getBasePlaneData(self, planeID):
        LOG_DEBUG(' TEST PLANE DATA:  getBasePlaneData: ', planeID)
        self._gameEnvironment.eGetHudPlaneData(int(planeID))