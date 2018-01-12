# Embedded file name: scripts/client/gui/HUD2/features/PlayerInfo/PlayerInfoModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import IntT, Structure, UnicodeT, List
from gui.HUD2.features.PlayerInfo.PlayerInfoSource import PlayerInfoSource

class PlayerInfoModel(AutoFilledDataModel):
    DATA_SOURCE = PlayerInfoSource
    planeScoreData = Structure(planeID=IntT, planeType=IntT, planeName=UnicodeT, battlePoints=IntT, rankID=IntT)
    SCHEME = Structure(nickName=UnicodeT, planeName=UnicodeT, planeType=IntT, planeGlobalID=IntT, planeLevel=IntT, squadIndex=IntT, teamIndex=IntT, id=IntT, state=IntT, rank=IntT, planeScoresData=List(planeScoreData))