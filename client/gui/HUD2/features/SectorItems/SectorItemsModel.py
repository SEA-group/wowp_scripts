# Embedded file name: scripts/client/gui/HUD2/features/SectorItems/SectorItemsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, List, StringT, IntT
from gui.HUD2.features.SectorItems.SectorItemsSource import SectorItemsSource

class SectorItemsModel(AutoFilledDataModel):
    DATA_SOURCE = SectorItemsSource
    SectorItem = Structure(id=IntT, nameLocalID=StringT, iconPath=StringT, itemType=StringT)
    SCHEME = Structure(sectorItems=List(SectorItem))