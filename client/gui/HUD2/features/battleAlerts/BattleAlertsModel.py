# Embedded file name: scripts/client/gui/HUD2/features/battleAlerts/BattleAlertsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, DictT, StringT
from gui.HUD2.features.battleAlerts.BattleAlertsSource import BattleAlertsSource

class BattleAlertsModel(AutoFilledDataModel):
    DATA_SOURCE = BattleAlertsSource
    SCHEME = Structure(battleAlert=DictT)