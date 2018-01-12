# Embedded file name: scripts/client/gui/HUD2/features/control/ControlController.py
from debug_utils import LOG_DEBUG
from gui import Cursor
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature

class ControlController(DataController):
    """
    Controller receive messages from frontend(look in HUDExternalConst.as)
    """

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self.__stateManager = features.require(Feature.STATE_MANAGER)

    @message('control.showCursor')
    def showCursor(self):
        self.__stateManager().checkMouseState()

    @message('control.hideCursor')
    def hideCursor(self):
        pass

    @message('control.exitToHangar')
    def exitToHangar(self):
        self._playerAvatar.exitGame()

    @message('control.exitGame')
    def exitGame(self):
        self._bigWorld.quit()

    @message('control.allClosed')
    def allInterClosed(self):
        self._gameEnvironment.eAllIntreClosed()