# Embedded file name: scripts/client/gui/HUD2/features/Utils/UtilsController.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.core.MessageRouter import message

class UtilsController(DataController):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).utils
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._camera = features.require(Feature.CAMERA)

    @message('utils.prepareSpectatorCamera')
    def prepareSpectatorCamera(self):
        self._playerAvatar.skipDeadFallState()
        self._camera.switchToSpectator()
        LOG_DEBUG(' respawn.prepareSpectatorCamera')

    @message('utils.prepareBattleCamera')
    def prepareBattleCamera(self):
        self._camera.reset()
        LOG_DEBUG(' respawn.prepareBattleCamera')