# Embedded file name: scripts/client/gui/HUD2/features/GameplayHints/GameplayHintsController.py
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.core.MessageRouter import message
from consts import HINTS_TYPE
from gui.HUD2.HUDExecutionManager import HUDExecutionManager
from gui.HUD2.features.GameplayHints.GameplayHintsSource import GameplayHintsSource

class GamePlayHintsController(DataController):

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._model = features.require(Feature.GAME_MODEL).gameplayHints
        self._gamePlayHints = features.require(Feature.GAME_PLAY_HINTS)

    @message('hints.closeStartHint')
    def closeStartHint(self):
        self._playerAvatar.closeGamePlayHint(self._model.startHintID.get(), HINTS_TYPE.START, True)
        HUDExecutionManager.call(GameplayHintsSource.onCloseGamePlayHint, HINTS_TYPE.START)
        self._gamePlayHints.setHintVisibility(False)
        if self._model.shootingHintID.get() > 0:
            HUDExecutionManager.call(GameplayHintsSource.onShowHint, HINTS_TYPE.SHOOTING)

    @message('hints.closeShootingHint')
    def closeShootingHint(self):
        if self._model.shootingHintID.get() > 0:
            self._playerAvatar.closeGamePlayHint(self._model.shootingHintID.get(), HINTS_TYPE.SHOOTING, True)
            HUDExecutionManager.call(GameplayHintsSource.onCloseGamePlayHint, HINTS_TYPE.SHOOTING)

    @message('hints.disableShootingHint')
    def disableShootingHint(self):
        self._playerAvatar.closeGamePlayHint(self._model.shootingHintID.get(), HINTS_TYPE.SHOOTING)
        HUDExecutionManager.call(GameplayHintsSource.onCloseGamePlayHint, HINTS_TYPE.SHOOTING)