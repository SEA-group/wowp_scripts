# Embedded file name: scripts/client/gui/HUD2/features/Minimap/MinimapModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.Minimap.MinimapController import MinimapController
from gui.HUD2.features.Minimap.MinimapSource import MinimapSource

class MinimapModel(AutoFilledDataModel):
    DATA_SOURCE = MinimapSource
    CONTROLLER = MinimapController
    SCHEME = Structure(currentSize=IntT, maxSize=IntT)
    source = None