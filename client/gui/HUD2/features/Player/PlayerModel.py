# Embedded file name: scripts/client/gui/HUD2/features/Player/PlayerModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import IntT, Structure, StringT, UnicodeT, FloatT
from gui.HUD2.features.Player.PlayerSource import PlayerSource

class PlayerModel(AutoFilledDataModel):
    DATA_SOURCE = PlayerSource
    SCHEME = Structure(id=IntT, nickName=UnicodeT, planeName=UnicodeT, planeType=IntT, planeId=IntT, planeGlobalID=IntT, planeLevel=IntT, planePreviewIcon=StringT, planeTypeName=StringT, planeStatus=IntT, health=IntT, healthMax=IntT, teamIndex=IntT, squadIndex=IntT, state=IntT, rank=IntT, effectiveShootingDistance=FloatT, shootingDistanceMax=FloatT)