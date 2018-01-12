# Embedded file name: scripts/client/gui/HUD2/features/AmmoBelts/AmmoBeltsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, IntT, List, FloatT
from gui.HUD2.features.AmmoBelts.AmmoBeltsSource import AmmoBeltsSource

class AmmoBeltsModel(AutoFilledDataModel):
    DATA_SOURCE = AmmoBeltsSource
    AmmoBeltSpec = Structure(specName=StringT, specType=IntT, value=FloatT)
    TagStruct = Structure(tagName=StringT, tagType=IntT)
    AmmoBelt = Structure(id=IntT, iconPath=StringT, status=IntT, count=IntT, caliber=FloatT, dps=IntT, rpm=IntT, effectiveDistance=IntT, gunName=StringT, beltName=StringT, beltType=StringT, beltIconSmall=StringT, specs=List(AmmoBeltSpec), propsList=List(TagStruct))
    SCHEME = Structure(ammoBelts=List(AmmoBelt))