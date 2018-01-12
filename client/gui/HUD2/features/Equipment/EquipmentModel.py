# Embedded file name: scripts/client/gui/HUD2/features/Equipment/EquipmentModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, IntT, List
from gui.HUD2.features.Equipment.EquipmentSource import EquipmentSource

class EquipmentModel(AutoFilledDataModel):
    DATA_SOURCE = EquipmentSource
    Equipment = Structure(id=IntT, iconPath=StringT, description=StringT, equipmentName=StringT)
    SCHEME = Structure(equipments=List(Equipment))