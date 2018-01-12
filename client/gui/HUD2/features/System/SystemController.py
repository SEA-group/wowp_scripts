# Embedded file name: scripts/client/gui/HUD2/features/System/SystemController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.FeatureBroker import Require

class SystemController(DataController):
    BigWorld = Require('BigWorld')

    def __init__(self, model):
        """
        :type model: SystemModel.SystemModel
        """
        self._model = model