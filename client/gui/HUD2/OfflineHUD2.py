# Embedded file name: scripts/client/gui/HUD2/OfflineHUD2.py
import BigWorld
from HUDBase import HUDBase
from gui.HUD2.core.FeatureBroker import features

class OfflineHUD2(HUDBase):

    def _setupFeatures(self):
        features.provide('BigWorld', BigWorld)
        features.provide('PlayerModel', self._gameModel.Player)
        features.provide('SettingsModel', self._gameModel.Settings)

    def _postInit(self):
        features.providers['input'].init()