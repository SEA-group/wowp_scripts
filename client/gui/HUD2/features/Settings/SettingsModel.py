# Embedded file name: scripts/client/gui/HUD2/features/Settings/SettingsModel.py
from gui.HUD2.core.DataModel import DataModel, BoolT, Structure

class SettingsModel(DataModel):
    SCHEME = Structure(IsChatEnabled=BoolT)