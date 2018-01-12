# Embedded file name: scripts/client/gui/HUD2/features/Settings/SettingsSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.core.FeatureBroker import Require

class SettingsSource(DataSource):
    uiSettings = Require('UISettings')

    def __init__(self, model):
        """
        :type model: SettingsModel.SettingsModel
        """
        self._model = model
        self._setupModel()

    def _setupModel(self):
        self._model.IsChatEnabled = self.uiSettings['isChatEnabled']

    def dispose(self):
        self._model = None
        return