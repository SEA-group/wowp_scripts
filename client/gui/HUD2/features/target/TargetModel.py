# Embedded file name: scripts/client/gui/HUD2/features/target/TargetModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, DictT, FloatT
from gui.HUD2.features.target.TargetSource import TargetSource

class TargetModel(AutoFilledDataModel):
    DATA_SOURCE = TargetSource
    SCHEME = Structure(targetId=IntT, targetModules=DictT, targetCurrentDamage=FloatT)