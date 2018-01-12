# Embedded file name: scripts/client/ArenaHelpers/GameModes/__init__.py
from consts import GAME_MODE
from ArenaHelpers.GameModes import GameModeClient
from ArenaHelpers.GameModes.AreaConquest import ACGameModeClient
from EntityHelpers import extractGameMode
DEFAULT_GAME_MODE_CLASS = GameModeClient.GameModeClient
GAME_MODE_CLASSES = {GAME_MODE.AREA_CONQUEST: ACGameModeClient.ACGameModeClient}

def getGameModeClientClass(gameMode):
    """Return game mode client class
    @type gameMode: int
    @return: Game mode client class for specified game mode
    """
    return GAME_MODE_CLASSES.get(extractGameMode(gameMode), DEFAULT_GAME_MODE_CLASS)