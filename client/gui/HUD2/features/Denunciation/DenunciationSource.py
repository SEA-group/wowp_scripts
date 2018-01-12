# Embedded file name: scripts/client/gui/HUD2/features/Denunciation/DenunciationSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class DenunciationSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).denunciation
        import BWPersonality
        self._model.denunciationsLeft = BWPersonality.g_initPlayerInfo.denunciationsLeft

    def dispose(self):
        self._model = None
        return