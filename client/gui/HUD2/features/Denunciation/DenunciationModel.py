# Embedded file name: scripts/client/gui/HUD2/features/Denunciation/DenunciationModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.Denunciation.DenunciationController import DenunciationController
from gui.HUD2.features.Denunciation.DenunciationSource import DenunciationSource

class DenunciationModel(AutoFilledDataModel):
    DATA_SOURCE = DenunciationSource
    CONTROLLER = DenunciationController
    SCHEME = Structure(denunciationsLeft=IntT)