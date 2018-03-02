# Embedded file name: scripts/client/gui/HUD2/features/GameMode/offenseDefenceUiSettingsModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, BoolT, IntT, List, StringT
from gui.HUD2.features.GameMode.OffenseDefenceUiSettingsSource import OffenseDefenceUiSettingsSource

class OffenseDefenceUiSettingsModel(AutoFilledDataModel):
    DATA_SOURCE = OffenseDefenceUiSettingsSource
    UiSettings = Structure(viewTeamIndex=IntT, isShowSetorsView=BoolT, isShowDominationView=BoolT, isShowTeamRespawnsView=BoolT)
    SCHEME = Structure(settings=List(UiSettings), title=StringT)