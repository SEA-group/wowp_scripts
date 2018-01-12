# Embedded file name: scripts/client/gui/HUD2/features/Sectors/CurrentSectorModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, DictT
from gui.HUD2.features.Sectors.CurretntSectorSource import CurrentSectorSource

class CurrentSectorModel(AutoFilledDataModel):
    DATA_SOURCE = CurrentSectorSource
    SCHEME = Structure(sectorID=StringT, sectorLog=DictT)