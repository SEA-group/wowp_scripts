# Embedded file name: scripts/client/gui/HUD2/features/crosshair/CrosshairModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT, IntT
from gui.HUD2.features.crosshair.CrosshairSource import CrosshairSource
from gui.HUD2.features.crosshair.crosshairSimple.CrosshairSimpleModel import CrosshairSimpleModel
from gui.HUD2.features.crosshair.crosshairSniper.crosshairSniperModel import CrosshairSniperModel
from gui.HUD2.features.crosshair.crosshairBomber.crosshairBomberModel import CrosshairBomberModel
from gui.HUD2.features.crosshair.crosshairTurret.crosshairTurretModel import CrosshairTurretModel

class CrosshairModel(AutoFilledDataModel):
    DATA_SOURCE = CrosshairSource
    SCHEME = Structure(crosshairMode=IntT, sniperAvailable=BoolT, bomberAvailable=BoolT, turretAvailable=BoolT, simple=CrosshairSimpleModel, sniper=CrosshairSniperModel, bomber=CrosshairBomberModel, turret=CrosshairTurretModel)