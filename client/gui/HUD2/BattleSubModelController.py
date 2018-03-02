# Embedded file name: scripts/client/gui/HUD2/BattleSubModelController.py
from consts import GAME_MODE
from gui.HUD2.hudFeatures import Feature

class BattleGameModelController:

    def __init__(self):
        self._clientArena = None
        self._gameModeName = GAME_MODE.NAME_DEFAULT
        return

    def init(self, features):
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameModeName = self._clientArena.gameModeName

    @property
    def gameModeName(self):
        return self._gameModeName