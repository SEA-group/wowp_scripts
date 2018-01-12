# Embedded file name: scripts/client/gui/HUD2/features/crosshair/CrosshairSource.py
import InputMapping
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from consts import PLANE_TYPE, BATTLE_MODE
from CrosshairHelper import BATTLE_STATE_TO_HUD_STATE

class CrosshairSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).crosshair
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._input = features.require(Feature.INPUT)
        self._processor = self._input.commandProcessor
        self._onSetBattleMod(BATTLE_MODE.COMBAT_MODE)
        self._input.eBattleModeChange += self._onSetBattleMod
        self.initModel()
        self._playerAvatar.eTacticalRespawnEnd += self.initModel
        self._previousCrosshairMode = self._model.crosshairMode.get()
        self._processor.addListeners(InputMapping.CMD_EXTRA_INPUT_MODE, None, None, self._setExtraMode)
        self._processor.addListeners(InputMapping.CMD_CURSOR_CAMERA, None, None, self._setExtraMode)
        return

    def initModel(self, *args, **kwargs):
        self._model.sniperAvailable = self._playerAvatar.planeType is not PLANE_TYPE.BOMBER
        self._model.bomberAvailable = self._playerAvatar.planeType is PLANE_TYPE.BOMBER
        self._model.turretAvailable = self._playerAvatar.hasGunner()

    def _onSetBattleMod(self, bState):
        self._model.crosshairMode = BATTLE_STATE_TO_HUD_STATE.get(bState, 0)

    def _setExtraMode(self, value):
        if value:
            self._previousCrosshairMode = self._model.crosshairMode.get()
            self._model.crosshairMode = BATTLE_STATE_TO_HUD_STATE.get(BATTLE_MODE.OVERVIEW_MODE, 0)
        else:
            self._model.crosshairMode = self._previousCrosshairMode

    def dispose(self):
        self._processor = None
        self._model = None
        self._input = None
        self._playerAvatar.eTacticalRespawnEnd -= self.initModel
        self._playerAvatar = None
        return