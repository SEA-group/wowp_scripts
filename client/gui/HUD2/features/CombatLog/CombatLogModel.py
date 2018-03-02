# Embedded file name: scripts/client/gui/HUD2/features/CombatLog/CombatLogModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, DictT, BoolT
from gui.HUD2.features.CombatLog.CombatLogSource import CombatLogSource

class CombatLogModel(AutoFilledDataModel):
    DATA_SOURCE = CombatLogSource
    SCHEME = Structure(isActive=BoolT, planeModelFlag=BoolT, clanFlag=BoolT, combatEvent=DictT)