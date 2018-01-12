# Embedded file name: scripts/client/gui/HUD2/features/Player/Equipment/EquipmentModel.py
from gui.HUD2.core.DataModel import DataModel, StringT, FloatT, IntT, List, Structure

class EquipmentModel(DataModel):
    SCHEME = Structure(Consumables=List(Structure(ID=IntT, IcoPath=StringT, IcoPathBig=StringT, Description=StringT, ChargesCount=IntT, CoolDownTill=IntT, CoolDownTillMax=IntT, ActiveTill=IntT, ActiveTillMax=IntT)))