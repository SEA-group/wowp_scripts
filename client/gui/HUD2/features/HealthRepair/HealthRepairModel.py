# Embedded file name: scripts/client/gui/HUD2/features/HealthRepair/HealthRepairModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import BoolT, FloatT, Structure
from HealthRepairSource import HealthRepairSource

class HealthRepairModel(AutoFilledDataModel):
    DATA_SOURCE = HealthRepairSource
    SCHEME = Structure(isRepair=BoolT, isUnderRepairZoneInfluence=BoolT, critPoint=FloatT)