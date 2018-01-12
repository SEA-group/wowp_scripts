# Embedded file name: scripts/client/gui/HUD2/features/loading/LoadingModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, StringT, List, BoolT
from gui.HUD2.features.loading.LoadingController import LoadingController
from gui.HUD2.features.loading.LoadingSource import LoadingSource

class LoadingModel(AutoFilledDataModel):
    DATA_SOURCE = LoadingSource
    CONTROLLER = LoadingController
    SCHEME = Structure(progress=IntT, commonHint=StringT, planeHint=StringT, preBattleHintAvailable=BoolT, preBattleHintSkipKey=StringT, timeBetweenFinishLoadingAndStartBattle=IntT)