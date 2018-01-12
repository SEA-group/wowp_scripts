# Embedded file name: scripts/client/gui/HUD2/features/FastCommands/FastCommandModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, DictT, IntT, FloatT
from gui.HUD2.features.FastCommands.FactCommandController import FactCommandController
from gui.HUD2.features.FastCommands.FastCommandSource import FastCommandSource

class FastCommandModel(AutoFilledDataModel):
    DATA_SOURCE = FastCommandSource
    CONTROLLER = FactCommandController
    Sector = Structure(call=IntT, radiusCoef=FloatT)
    Plane = Structure(call=IntT, radiusCoef=FloatT)
    SCHEME = Structure(commandData=DictT, sector=Sector, plane=Plane)