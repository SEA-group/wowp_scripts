# Embedded file name: scripts/client/gui/HUD2/features/control/ControlModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, BoolT, StringT, IntT
from gui.HUD2.features.control.ControlController import ControlController
from gui.HUD2.features.control.ControlSource import ControlSource

class ControlModel(AutoFilledDataModel):
    DATA_SOURCE = ControlSource
    CONTROLLER = ControlController
    SCHEME = Structure(altPress=BoolT, keyForce=StringT)