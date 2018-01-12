# Embedded file name: scripts/client/gui/Scaleform/main_interfaces.py
from gui.HUD2.HudUI import HudUI
from gui.Scaleform.Login import Login
from gui.Scaleform.Lobby import Lobby
from gui.Scaleform.GameOptions.GameOptions import GameOptions
from gui.Scaleform.Prebattle import Prebattle
from gui.Scaleform.Interview import Interview
GUI_SCREEN_LOGIN = 'login'
GUI_SCREEN_LOBBY = 'lobby'
GUI_SCREEN_OPTIONS = 'options'
GUI_SCREEN_UI = 'ui'
GUI_SCREEN_PREBATTLE = 'prebattle'
GUI_SCREEN_INTERVIEW = 'interview'
idict = {GUI_SCREEN_LOGIN: Login,
 GUI_SCREEN_LOBBY: Lobby,
 GUI_SCREEN_OPTIONS: GameOptions,
 GUI_SCREEN_UI: HudUI,
 GUI_SCREEN_PREBATTLE: Prebattle,
 GUI_SCREEN_INTERVIEW: Interview}