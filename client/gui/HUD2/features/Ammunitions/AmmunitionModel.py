# Embedded file name: scripts/client/gui/HUD2/features/Ammunitions/AmmunitionModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT, StringT, IntT, List, DictT
from gui.HUD2.features.Ammunitions.AmmunitionSource import AmmunitionSource

class AmmunitionModel(AutoFilledDataModel):
    DATA_SOURCE = AmmunitionSource
    TagStruct = Structure(tagName=StringT, tagType=IntT)
    Ammunition = Structure(id=IntT, iconPath=StringT, shellIcon=StringT, ammoName=StringT, amount=IntT, cluster=IntT, amountMax=IntT, key=StringT, componentType=IntT, cooldownEndTime=IntT, cooldownStartTime=IntT, isAvailable=BoolT, isInstalled=BoolT, explosionRadius=IntT, explosionDamage=IntT, propsList=List(TagStruct))
    SCHEME = Structure(ammunitions=List(Ammunition))