# Embedded file name: scripts/client/gui/HUD2/features/hotkeys/HotKeysModel.py
from gui.HUD2.core.AutoFilledDataModel import AutoFilledDataModel
from gui.HUD2.core.DataModel import Structure, StringT, BoolT
from gui.HUD2.features.hotkeys.HotKeysSource import HotKeysSource

class HotKeysModel(AutoFilledDataModel):
    DATA_SOURCE = HotKeysSource
    SCHEME = Structure(helpKey=StringT, teamInfoKey=StringT, moreInfoKey=StringT, sniperModeKey=StringT, bomberModeKey=StringT, turretModeKey=StringT, specialKey=StringT, skipKey=StringT, spectatorKey=StringT, tacticalSpectatorKey=StringT, changeCameraKey=StringT, exitKey=StringT, backKey=StringT, enterKey=StringT, isGunnerEnable=BoolT, isBomberModeEnable=BoolT, isSniperModeEnable=BoolT, intentionsKey=StringT, supportKey=StringT, offenseDefenseKey=StringT, affirmativeKey=StringT, negativeKey=StringT, dangerKey=StringT, goodJobKey=StringT, showTeamsKey=StringT, showPlayersInfoKey=StringT, minimapSizeIncKey=StringT, minimapSizeDecKey=StringT, radarZoomInKey=StringT, radarZoomOutKey=StringT)