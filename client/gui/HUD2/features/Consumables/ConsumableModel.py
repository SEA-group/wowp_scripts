# Embedded file name: scripts/client/gui/HUD2/features/Consumables/ConsumableModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT, StringT, IntT, List
from gui.HUD2.features.Consumables.ConsumableController import ConsumableController
from gui.HUD2.features.Consumables.ConsumableSource import ConsumableSource

class ConsumableModel(AutoFilledDataModel):
    DATA_SOURCE = ConsumableSource
    CONTROLLER = ConsumableController
    Consumable = Structure(id=IntT, iconPath=StringT, description=StringT, consumableName=StringT, amount=IntT, coolDownTime=IntT, key=StringT, respawnEndTime=IntT, respawnStartTime=IntT, activeEndTime=IntT, isAuto=BoolT, isPassive=BoolT, isEmpty=BoolT, isReadyOnRespawn=BoolT, status=IntT)
    SCHEME = Structure(consumables=List(Consumable))