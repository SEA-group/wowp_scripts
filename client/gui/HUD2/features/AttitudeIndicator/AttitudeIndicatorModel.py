# Embedded file name: scripts/client/gui/HUD2/features/AttitudeIndicator/AttitudeIndicatorModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.AttitudeIndicator.AttitudeIndicatorSource import AttitudeIndicatorSource

class AttitudeIndicatorModel(AutoFilledDataModel):
    DATA_SOURCE = AttitudeIndicatorSource
    SCHEME = Structure(attitudeMode=IntT)