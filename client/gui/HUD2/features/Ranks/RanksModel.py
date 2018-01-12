# Embedded file name: scripts/client/gui/HUD2/features/Ranks/RanksModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, List, IntT, StringT
from gui.HUD2.features.Ranks.RanksDataSource import RanksDataSource

class RanksModel(AutoFilledDataModel):
    DATA_SOURCE = RanksDataSource
    RankItem = Structure(id=IntT, title=StringT, description=StringT, iconPath=StringT, orderIndex=IntT, requiredProgress=IntT)
    SCHEME = Structure(ranks=List(RankItem))