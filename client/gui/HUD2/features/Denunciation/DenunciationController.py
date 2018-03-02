# Embedded file name: scripts/client/gui/HUD2/features/Denunciation/DenunciationController.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.HUDExecutionManager import HUDExecutionManager
from gui.HUD2.features.Denunciation.DenunciationSource import DenunciationSource
TAG = 'Denunciation'

class DenunciationController(DataController):
    """
    Controller receive messages from frontend(look in HUDExternalConst.as)
    """

    def __init__(self, features):
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._model = features.require(Feature.GAME_MODEL).denunciation

    @message('denunciation.makeDenunciation')
    def makeDenunciation(self, playerID, demId):
        playerID = int(playerID)
        demId = int(demId)
        avatarInfo = self._clientArena.getAvatarInfo(playerID)
        violatorKind = 2 if avatarInfo['teamIndex'] == self._playerAvatar.teamIndex else 1
        DBId = self._clientArena.getDBId(playerID)
        LOG_DEBUG(TAG + ' ', playerID, demId, violatorKind)
        if DBId is not None:
            self.onDenunciation(DBId, demId, violatorKind)
            HUDExecutionManager.call(DenunciationSource.update)
        else:
            LOG_ERROR(TAG + '__onDenunciation - playerID(%s) not in voipMap, or voipMap not defined' % playerID)
        return

    def onDenunciation(self, DBId, denunciationID, violatorKind):
        """
        @param <int> DBId:
        @param denunciationID:  see class consts.DENUNCIATION
        @param <int> violatorKind:    1 - enemy, 2 - ally
        """
        BigWorld.player().base.makeDenunciation(DBId, denunciationID, violatorKind)
        import BWPersonality
        BWPersonality.g_initPlayerInfo.denunciationsLeft -= 1 if BWPersonality.g_initPlayerInfo.denunciationsLeft > 0 else 0