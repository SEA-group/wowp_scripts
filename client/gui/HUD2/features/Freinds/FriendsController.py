# Embedded file name: scripts/client/gui/HUD2/features/Freinds/FriendsController.py
import VOIP
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
import BWLogging

class FriendsController(DataController):
    """
    Controller receive messages from frontend(look in HUDExternalConst.as)
    """

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).friends
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._xmppChat = features.require(Feature.XMPP_CHAT)

    @message('friends.editFriendList')
    def editFriendList(self, userId, operationType):
        dbid, name = self._getDbId(userId)
        operation = int(operationType)
        self._xmppChat.editFriendList(int(dbid), name, operation)

    @message('friends.editIgnoreList')
    def editIgnoreList(self, userId, operationType):
        dbid, name = self._getDbId(userId)
        operation = int(operationType)
        self._xmppChat.editIgnoreList(dbid, name, operation)

    @message('friends.editMuteList')
    def editMuteList(self, userId, operationType):
        self._logger.debug("editMuteList fromFlash : userId = '{0}', operationType = '{1}'".format(userId, operationType))
        operation = int(operationType)
        operation = bool(operation)
        self._logger.debug("editMuteList: userId = '{0}', operationType = '{1}'".format(userId, operation))
        VOIP.api().setAvatarMuted(userId, operationType)

    def _getDbId(self, avatarId):
        avatarInfo = self._clientArena.getAvatarInfo(int(avatarId))
        playerName = avatarInfo.get('playerName')
        self._logger.debug("_getDbId: avatarInfo  = '{0}'".format(playerName))
        dbid = avatarInfo.get('databaseID')
        return (dbid, playerName)