# Embedded file name: scripts/client/gui/HUD2/features/Denunciation/DenunciationSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.HUDExecutionManager import RegicToHUDExecutionManager

class DenunciationSource(DataSource):

    def __init__(self, features):
        self.regicToExecutionManager()
        self._model = features.require(Feature.GAME_MODEL).denunciation
        self.update()

    def dispose(self):
        self.unregicFromExecutionManager()
        self._model = None
        return

    def update(self):
        import BWPersonality
        self._model.denunciationsLeft = BWPersonality.g_initPlayerInfo.denunciationsLeft