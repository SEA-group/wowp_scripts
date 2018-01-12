# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairSniper/crosshairSniperModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, BoolT, IntT
from gui.HUD2.features.crosshair.crosshairSniper.crosshairSniperSource import CrosshairSniperSource

class CrosshairSniperModel(AutoFilledDataModel):
    DATA_SOURCE = CrosshairSniperSource
    SCHEME = Structure(toggleForsage=BoolT, scopeSize=FloatT, scopeMaxSize=IntT, pulsation=FloatT, scopeShakeLength=IntT)