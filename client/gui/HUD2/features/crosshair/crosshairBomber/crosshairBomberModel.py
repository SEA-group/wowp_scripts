# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairBomber/crosshairBomberModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, DictT, IntT, BoolT
from gui.HUD2.features.crosshair.crosshairBomber.crosshairBomberSource import CrosshairBomberSource

class CrosshairBomberModel(AutoFilledDataModel):
    DATA_SOURCE = CrosshairBomberSource
    SCHEME = Structure(sightAngle=FloatT, compassAngle=FloatT, zoomIndex=IntT, markerPosition=DictT, isLock=BoolT)