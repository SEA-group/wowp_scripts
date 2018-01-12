# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairSimple/CrosshairSimpleModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, StringT, IntT, BoolT
from gui.HUD2.features.crosshair.crosshairSimple.CrosshairSimpleSource import CrosshairSimpleSource

class CrosshairSimpleModel(AutoFilledDataModel):
    DATA_SOURCE = CrosshairSimpleSource
    SCHEME = Structure(crossImage=StringT, heatLevel=FloatT, heatShowLimit=FloatT, pulsation=FloatT, maxPulsationLength=IntT, crossSize=IntT, isHidden=BoolT)