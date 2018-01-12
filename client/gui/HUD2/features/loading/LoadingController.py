# Embedded file name: scripts/client/gui/HUD2/features/loading/LoadingController.py
import Settings
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class LoadingController(DataController):

    def __init__(self, features):
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)

    @message('loading.gotoIntro')
    def goToIntro(self):
        self._gameEnvironment.eSkipLoading()