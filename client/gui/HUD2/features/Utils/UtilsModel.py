# Embedded file name: scripts/client/gui/HUD2/features/Utils/UtilsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT
from gui.HUD2.features.Utils.UtilsController import UtilsController
from gui.HUD2.features.Utils.UtilsSource import UtilsSource

class UtilsModel(AutoFilledDataModel):
    DATA_SOURCE = UtilsSource
    CONTROLLER = UtilsController
    SCHEME = Structure(cameraIsReady=BoolT)