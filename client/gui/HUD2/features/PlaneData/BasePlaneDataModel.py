# Embedded file name: scripts/client/gui/HUD2/features/PlaneData/BasePlaneDataModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, StringT, UnicodeT, List
from gui.HUD2.features.PlaneData.BasePlaneDataController import BasePlaneDataController
from gui.HUD2.features.PlaneData.BasePlaneDataSource import BasePlaneDataSource

class BasePlaneDataModel(AutoFilledDataModel):
    DATA_SOURCE = BasePlaneDataSource
    CONTROLLER = BasePlaneDataController
    Plane = Structure(planeID=IntT, planeNameShort=UnicodeT, planeLevel=IntT, prevIconPath=StringT, planeType=IntT, nation=IntT, planeStatus=IntT, typeIconPath=StringT)
    SCHEME = Structure(planes=List(Plane))