# Embedded file name: scripts/client/gui/HUD2/features/Freinds/FriendsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, List
from gui.HUD2.features.Freinds.FriendsController import FriendsController
from gui.HUD2.features.Freinds.FrinedsSource import FriendsSource

class FriendsModel(AutoFilledDataModel):
    DATA_SOURCE = FriendsSource
    CONTROLLER = FriendsController
    FriendsIDStruct = Structure(id=IntT, status=IntT)
    MuteIDStruct = Structure(id=IntT)
    SCHEME = Structure(userList=List(FriendsIDStruct), muteList=List(MuteIDStruct))