# Embedded file name: scripts/client/gui/HUD2/features/PlaneScheme/PlaneSchemeModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT, List, StringT
from gui.HUD2.features.PlaneScheme.PlaneSchemeSource import PlaneSchemeSource

class PlaneSchemeModel(AutoFilledDataModel):
    DATA_SOURCE = PlaneSchemeSource
    Damage = Structure(partName=StringT, state=IntT, normal=StringT, damage=StringT, crit=StringT)
    SCHEME = Structure(scheme=StringT, damage=List(Damage))