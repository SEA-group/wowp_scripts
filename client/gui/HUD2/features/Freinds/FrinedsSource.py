# Embedded file name: scripts/client/gui/HUD2/features/Freinds/FrinedsSource.py
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
import BWLogging

class FriendsSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).friends
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._xmppChat = features.require(Feature.XMPP_CHAT)
        self._isInitChatUsers = False
        self._infoList = []
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        self._gameEnvironment.eSetUsersChatStatus += self._setUsersChatStatus
        self._gameEnvironment.eSetChatMute += self.eSetChatMute
        return

    def eSetChatMute(self, usersList = None):
        LOG_DEBUG(' FriendsSource : eSetChatMute ', usersList)
        for id in usersList:
            pass

    def _setUsersChatStatus(self, usersList = None):
        if not self._isInitChatUsers:
            for id, status in usersList:
                userId = self._getUserIDByDbID(int(id))
                self._model.userList.append(id=int(userId), status=int(status))

            self._isInitChatUsers = True
        else:
            for id, status in usersList:
                userId = self._getUserIDByDbID(int(id))
                friendData = self._model.userList.first(lambda a: a.id.get() == userId)
                if friendData:
                    friendData.status = status
                else:
                    self._model.userList.append(id=int(userId), status=int(status))

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._infoList = self._clientArena.avatarInfos.values()
        dbidList = []
        for avatar in self._infoList:
            dbid = avatar.get('databaseID')
            if dbid is not None:
                if dbid != 0:
                    dbidList.append(dbid)

        self._xmppChat.getUsersChatStatus(dbidList)
        self._xmppChat.getMuteList()
        return

    def _getUserIDByDbID(self, dbIdValue):
        for avatar in self._infoList:
            dbid = avatar.get('databaseID')
            if dbid is not None:
                if dbid == dbIdValue:
                    return avatar.get('avatarID')

        return

    def dispose(self):
        self._gameEnvironment.eSetUsersChatStatus -= self._setUsersChatStatus
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._gameEnvironment.eSetChatMute -= self.eSetChatMute