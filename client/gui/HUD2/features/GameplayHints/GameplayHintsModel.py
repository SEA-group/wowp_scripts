# Embedded file name: scripts/client/gui/HUD2/features/GameplayHints/GameplayHintsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, DictT, IntT, FloatT, StringT
from gui.HUD2.features.GameplayHints.GameplayHintsSource import GameplayHintsSource
from gui.HUD2.features.GameplayHints.GameplayHintsController import GamePlayHintsController

class GameplayHintsModel(AutoFilledDataModel):
    DATA_SOURCE = GameplayHintsSource
    CONTROLLER = GamePlayHintsController
    SCHEME = Structure(startHintID=IntT, shootingHintID=IntT, sectorData=DictT, shootingHintTime=IntT, startHintTime=IntT)