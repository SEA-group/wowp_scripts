# Embedded file name: scripts/client/gui/HUD2/features/battleEvent/BattleLogModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, DictT, StringT
from gui.HUD2.features.battleEvent.BattleLogSource import BattleLogSource

class BattleLogModel(AutoFilledDataModel):
    DATA_SOURCE = BattleLogSource
    SCHEME = Structure(battleEvent=DictT, totalPoints=IntT, totalExp=IntT)