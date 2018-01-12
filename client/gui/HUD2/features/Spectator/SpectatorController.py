# Embedded file name: scripts/client/gui/HUD2/features/Spectator/SpectatorController.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class SpectatorController(DataController):

    def __init__(self, features):
        self._camera = features.require(Feature.CAMERA)