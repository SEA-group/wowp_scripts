# Embedded file name: scripts/client/gui/HUD2/features/BattleReplay/BattleReplayModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, FloatT, BoolT, StringT
from gui.HUD2.features.BattleReplay.BattleReplayController import BattleReplayController
from gui.HUD2.features.BattleReplay.BattleReplaySource import BattleReplaySource

class BattleReplayModel(AutoFilledDataModel):
    DATA_SOURCE = BattleReplaySource
    CONTROLLER = BattleReplayController
    SCHEME = Structure(panelVisibility=BoolT, speed=StringT, isPaused=BoolT, timeMax=FloatT, timeCurrent=FloatT)
    source = None