# Embedded file name: scripts/client/gui/HUD2/features/Sectors/SectorsGameEffectsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, IntT, DictT, List, FloatT
from gui.HUD2.features.Sectors.SectorsGameEffectsController import SectorsGameEffectsController
from gui.HUD2.features.Sectors.SectorsGameEffectsSource import SectorsGameEffectsSource

class SectorsGameEffectsModel(AutoFilledDataModel):
    DATA_SOURCE = SectorsGameEffectsSource
    CONTROLLER = SectorsGameEffectsController
    BomberIDStateStruct = Structure(id=IntT, state=IntT)
    BomberEffect = Structure(sectorID=StringT, targetSectorID=StringT, teamIndex=IntT, waveID=StringT, bomberIDsStates=List(BomberIDStateStruct), startPoint=DictT, endPoint=DictT, strikeTime=IntT, strikeState=IntT)
    RocketEffect = Structure(id=IntT, sectorID=StringT, targetSectorID=StringT, startPoint=DictT, endPoint=DictT, teamIndex=IntT, flyingTime=FloatT, startTime=FloatT)
    SCHEME = Structure(airStrikes=List(BomberEffect), rockets=List(RocketEffect), selectedPoint=DictT)