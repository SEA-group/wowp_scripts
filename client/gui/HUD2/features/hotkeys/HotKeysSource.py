# Embedded file name: scripts/client/gui/HUD2/features/hotkeys/HotKeysSource.py
import InputMapping
from Helpers.i18n import localizeHUD
from consts import PLANE_TYPE
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization
TAG = ' HotKeysSource :  '

class HotKeysSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).hotkeys
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self.__subscribe()
        self._setKeys()
        if self._clientArena.isAllServerDataReceived():
            self.__updateBomberAndTurrets()
        else:
            self._clientArena.onNewAvatarsInfo += self.__onNewAvatarsInfo

    def __subscribe(self):
        InputMapping.g_instance.onSaveControls += self.__updateControls
        self._playerAvatar.eRespawn += self.__onRespawn

    def _setKeys(self):
        self._model.helpKey = getKeyLocalization(InputMapping.CMD_HELP)
        self._model.teamInfoKey = getKeyLocalization(InputMapping.CMD_SHOW_TEAMS)
        self._model.moreInfoKey = getKeyLocalization(InputMapping.CMD_SHOW_PLAYERS_INFO)
        self._model.sniperModeKey = getKeyLocalization(InputMapping.CMD_SNIPER_CAMERA)
        self._model.turretModeKey = getKeyLocalization(InputMapping.CMD_GUNNER_MODE)
        self._model.bomberModeKey = getKeyLocalization(InputMapping.CMD_BATTLE_MODE)
        self._model.specialKey = getKeyLocalization(InputMapping.CMD_SKIP_INTRO)
        self._model.exitKey = getKeyLocalization(InputMapping.CMD_INTERMISSION_MENU)
        self._model.enterKey = getKeyLocalization(InputMapping.CMD_GO_TO_BATTLE)
        self._model.backKey = getKeyLocalization(InputMapping.CMD_GO_BACK)
        self._model.skipKey = getKeyLocalization(InputMapping.CMD_SKIP_DEATH)
        self._model.spectatorKey = getKeyLocalization(InputMapping.CMD_GO_TO_SPECTATOR)
        self._model.tacticalSpectatorKey = getKeyLocalization(InputMapping.CMD_GO_TO_TACTICAL_SPECTATOR)
        self._model.changeCameraKey = 'C'
        self._model.intentionsKey = getKeyLocalization(InputMapping.CMD_F8_CHAT_COMMAND)
        self._model.supportKey = getKeyLocalization(InputMapping.CMD_F9_CHAT_COMMAND)
        self._model.offenseDefenseKey = getKeyLocalization(InputMapping.CMD_F4_CHAT_COMMAND)
        self._model.affirmativeKey = getKeyLocalization(InputMapping.CMD_F2_CHAT_COMMAND)
        self._model.negativeKey = getKeyLocalization(InputMapping.CMD_F3_CHAT_COMMAND)
        self._model.dangerKey = getKeyLocalization(InputMapping.CMD_F5_CHAT_COMMAND)
        self._model.goodJobKey = getKeyLocalization(InputMapping.CMD_F6_CHAT_COMMAND)
        self._model.showTeamsKey = getKeyLocalization(InputMapping.CMD_SHOW_TEAMS)
        self._model.showPlayersInfoKey = getKeyLocalization(InputMapping.CMD_SHOW_PLAYERS_INFO)
        self._model.minimapSizeIncKey = getKeyLocalization(InputMapping.CMD_MINIMAP_SIZE_INC)
        self._model.minimapSizeDecKey = getKeyLocalization(InputMapping.CMD_MINIMAP_SIZE_DEC)
        self._model.radarZoomInKey = getKeyLocalization(InputMapping.CMD_RADAR_ZOOM_IN)
        self._model.radarZoomOutKey = getKeyLocalization(InputMapping.CMD_RADAR_ZOOM_OUT)

    def __onNewAvatarsInfo(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self.__onNewAvatarsInfo
        self.__updateBomberAndTurrets()

    def __updateControls(self):
        self._setKeys()

    def __onRespawn(self, *args, **kwargs):
        self.__updateBomberAndTurrets()

    def __updateBomberAndTurrets(self):
        __avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        __planeType = __avatarInfo['settings'].airplane.planeType
        self._model.isGunnerEnable = self._playerAvatar.hasGunner()
        isBomberModeEnable = __planeType == PLANE_TYPE.BOMBER
        self._model.isBomberModeEnable = isBomberModeEnable
        self._model.isSniperModeEnable = not isBomberModeEnable

    def __unsubscribe(self):
        InputMapping.g_instance.onSaveControls -= self.__updateControls
        self._playerAvatar.eRespawn -= self.__onRespawn
        self._clientArena.onNewAvatarsInfo -= self.__onNewAvatarsInfo

    def dispose(self):
        self.__unsubscribe()
        self._playerAvatar = None
        self._clientArena = None
        self._model = None
        return