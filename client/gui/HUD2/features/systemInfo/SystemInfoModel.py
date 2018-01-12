# Embedded file name: scripts/client/gui/HUD2/features/systemInfo/SystemInfoModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, IntT
from gui.HUD2.features.systemInfo.SystemInfoSource import SystemInfoSource

class SystemInfoModel(AutoFilledDataModel):
    DATA_SOURCE = SystemInfoSource
    SCHEME = Structure(ping=IntT, fps=IntT, packLost=IntT)