# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairTurret/crosshairTurretModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, BoolT, IntT, DictT, StringT
from gui.HUD2.features.crosshair.crosshairTurret.crosshairTurretSource import CrosshairTurretSource

class CrosshairTurretModel(AutoFilledDataModel):
    DATA_SOURCE = CrosshairTurretSource
    SCHEME = Structure(sightPosition=DictT, sightAccuracy=FloatT, sightMinSize=IntT, onTarget=BoolT, crossRadius=IntT, isFiring=BoolT, shadePosition=DictT, isZoomed=BoolT, crossImage=StringT, critEndTime=IntT, rpm=IntT, pulsStrength=FloatT)