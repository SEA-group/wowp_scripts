# Embedded file name: scripts/client/gui/HUD2/features/DeathInfo/DeathInfoModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import StringT, Structure, IntT
from gui.HUD2.features.DeathInfo.DeathInfoSource import DeathInfoSource

class DeathInfoModel(AutoFilledDataModel):
    DATA_SOURCE = DeathInfoSource
    SCHEME = Structure(killerID=IntT, deathReason=IntT)