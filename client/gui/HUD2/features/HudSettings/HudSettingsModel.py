# Embedded file name: scripts/client/gui/HUD2/features/HudSettings/HudSettingsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT
from gui.HUD2.features.HudSettings.HudSettingsSource import HudSettingsSource

class HudSettingsModel(AutoFilledDataModel):
    DATA_SOURCE = HudSettingsSource
    SCHEME = Structure(isShowSectorMarkers=BoolT, isDevelopment=BoolT)