# Embedded file name: scripts/client/gui/HUD2/features/time/TimeModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.time.TimeSource import TimeSource

class TimeModel(AutoFilledDataModel):
    DATA_SOURCE = TimeSource
    SCHEME = Structure(time=IntT, timeMax=IntT)