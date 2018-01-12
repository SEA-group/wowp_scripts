# Embedded file name: scripts/client/gui/HudElements/IngameChat.py
import math
import BigWorld, Settings
import GameEnvironment
from FastCommandsConfiguration import CommandTypes, NotificationType
from Singleton import singleton
from gui.Scaleform.UIHelper import SQUAD_TYPES
from Helpers.i18n import localizeHUD, convert as convertToLocal, localizeAirplane
from Helpers.i18n import localizeMessages
from clientConsts import OBJECTS_INFO, WAIT_TIME_FOR_SEND_CHAT_MSG
from messenger.filters import FilterChain, ObsceneLanguageFilter, DomainNameFilter, SpamFilter, FloodFilter
from encodings import utf_8
from consts import MESSAGE_TYPE, BATTLE_MESSAGE_TYPE, GUICursorStates, MESSAGE_MAX_SIZE
import messenger
from debug_utils import LOG_DEBUG
from EntityHelpers import EntitySupportedClasses
import BattleMessageReactionHelper
from GameServiceBase import GameServiceBase
from functools import partial
import gui.HUDconsts
ChatMessagesStringID = BATTLE_MESSAGE_TYPE
MESSAGE_SAME_COOLDOWN = 2
import InputMapping

class COLORS:
    WHITE = 16777215
    GREEN = 8443450
    YELLOW = 16761700
    RED = 14287872
    BLUE = 60159
    GREY = 13224374
    PURPLE = 8616446
    YELLOWBRIGHT = 16776960


class CHAT_STATUS:
    INACCESSIBLE = -1
    UNDEFINED = 0
    FRIEND = 1
    IGNORED = 2


class CHAT_BLOCKER:
    TAB = 1
    INTERMISSION = 2


class TEAM_TYPE:
    BATTLE_ALLY = 1
    BATTLE_OPPONENT = 2
    BATTLE_SQUAD = 3


CONVERT_CHAT_MSG_TYPE_FROM_FLASH = {0: MESSAGE_TYPE.BATTLE_ALL,
 1: MESSAGE_TYPE.BATTLE_ALLY,
 2: MESSAGE_TYPE.BATTLE_SQUAD}
CONVERT_CHAT_MSG_TYPE_TO_FLASH = {MESSAGE_TYPE.BATTLE_ALL: 0,
 MESSAGE_TYPE.BATTLE_ALLY: 1,
 MESSAGE_TYPE.BATTLE_ALL_FROM_OPPONENT: 2,
 MESSAGE_TYPE.BATTLE_SQUAD: 3,
 MESSAGE_TYPE.BATTLE_NEUTRAL: 4,
 MESSAGE_TYPE.BATTLE_NEUTRAL_UNIVERSAL: 5,
 MESSAGE_TYPE.BATTLE_FAST_COMMAND_ALL: 6,
 MESSAGE_TYPE.BATTLE_NEUTRAL_WARNING: 7}

class ChatMessageVO:

    def __init__(self):
        self.authorName = ''
        self.authorClanAbbrev = ''
        self.message = ''
        self.isOwner = False
        self.msgType = 0
        self.authorType = 0
        self.vechicleName = ''
        self.senderID = 0
        self.isHistory = False
        self.leaderType = -1
        self.teamType = 0
        self.time = BigWorld.time()


@singleton

class MessagesID(object):

    def __init__(self):
        pass

    def getLocalizedMessage(self, messageStringID, targetID = 0):
        """
        @param : int messageStringID, int targetID
        @return: localization text
        """
        if messageStringID not in self.__localize:
            return 'ERROR LOCALIZE MESSAGE'
        elif targetID != 0 and messageStringID in [ChatMessagesStringID.JOIN_ME, ChatMessagesStringID.ENEMY_MY_AIM]:
            objectType = GameEnvironment.getClientArena().getTeamObjectType(targetID)
            if objectType is not None and objectType in OBJECTS_INFO:
                objectName = localizeHUD(OBJECTS_INFO[objectType]['LOC_ID'])
            else:
                objectName = GameEnvironment.getClientArena().getObjectName(targetID)
            return localizeHUD(self.__localize[messageStringID]).format(player=objectName)
        else:
            return localizeHUD(self.__localize[messageStringID])
            return


class Chat(GameServiceBase):

    def __init__(self):
        super(Chat, self).__init__()
        self.__chatVisible = False
        self.__chatAllowed = 0
        self.__playersChatStatus = {}
        self.__initFilterChain()
        self.__lastSendTime = 0.0
        self.__chatCommandLastExecuteTime = 0.0
        self.__lastMessage = ChatMessageVO()
        self.__arenaBounds = None
        self.__zoneSymbols = 'ABCDEFGHJK'
        self.CHAT_COMMANDS_MESSAGES = {InputMapping.CMD_F8_CHAT_COMMAND: CommandTypes.INTENTIONS,
         InputMapping.CMD_F9_CHAT_COMMAND: CommandTypes.SUPPORT,
         InputMapping.CMD_F4_CHAT_COMMAND: CommandTypes.OFFENSE_DEFENSE,
         InputMapping.CMD_F2_CHAT_COMMAND: CommandTypes.AFFIRMATIVE,
         InputMapping.CMD_F3_CHAT_COMMAND: CommandTypes.NEGATIVE,
         InputMapping.CMD_F5_CHAT_COMMAND: CommandTypes.DANGER,
         InputMapping.CMD_F6_CHAT_COMMAND: CommandTypes.GOOD_JOB}
        self.CHAT_COMMANDS_MESSAGES_REVERTED = dict(([v, k] for k, v in self.CHAT_COMMANDS_MESSAGES.items()))
        self.MARKER_MESSAGES_LOC_IDS = {GUICursorStates.NORMAL_OFF: 'HUD_MINIMAP_ATTENTION_STR',
         GUICursorStates.NORMAL_ON: 'HUD_MINIMAP_ATTENTION_STR',
         GUICursorStates.FRIENDLY: 'HUD_MINIMAP_ATTENTION_MY_LOCATION_STR',
         GUICursorStates.ENEMY: 'HUD_MINIMAP_ATTENTION_ENEMY_HERE_STR'}
        return

    @property
    def chatVisible(self):
        return self.__chatVisible

    def setUI(self, ui):
        self.__ui = ui
        self.__ui.addExternalCallbacks({'hud.requestChatSend': self.__onSendChatMessage,
         'hud.onOpenChat': self.__showChat})

    def addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_SHOW_TEAMS, None, None, lambda fired: self.__switchAllowChat(CHAT_BLOCKER.TAB))
        processor.addPredicate(InputMapping.CMD_SHOW_TEAMS, lambda : not self.__chatVisible)
        return

    def destroy(self):
        self.__ui = None
        return

    def setUsersChatStatus(self, usersList):
        playersList = []
        clientArena = GameEnvironment.getClientArena()
        for userStatus in usersList:
            playerID = clientArena.getAvatarIdByDBId(int(userStatus[0]))
            if playerID is not None:
                playersList.append((playerID, userStatus[1]))
            else:
                LOG_ERROR('setUsersChatStatus: can not get playerID by dbid(%s)' % userStatus[0])

        self.__setPlayersChatStatus(playersList)
        return

    def __switchAllowChat(self, value):
        self.__chatAllowed ^= value

    def switchChat(self):
        if not self.__chatAllowed:
            self.__onVisibilityChat(not self.__chatVisible, True)

    def showTextMessageFromLobby(self, senderID, messageType, message):
        if not Settings.g_instance.getGameUI()['isChatEnabled']:
            return
        playerID = GameEnvironment.getClientArena().getAvatarIdByDBId(senderID)
        if BigWorld.player().id != playerID:
            self.__showTextMessage(playerID, messageType, 0, 0, message, False)

    def onReceiveMarkerMessage(self, senderID, posX, posZ, messageStringID, isHistory):
        if self.__arenaBounds is None:
            arena = GameEnvironment.getClientArena()
            self.__arenaBounds = self._makeBoundsObject(arena.getArenaBounds())
        percentX = 100 * (posX - self.__arenaBounds.get('left')) / (self.__arenaBounds.get('right') - self.__arenaBounds.get('left'))
        percentY = 100 * (1 - (posZ - self.__arenaBounds.get('top')) / (self.__arenaBounds.get('bottom') - self.__arenaBounds.get('top')))
        zoneSymbol = self.__zoneSymbols[self.getZoneIndex(percentY)]
        zoneNumber = 1 + self.getZoneIndex(percentX)
        message = localizeHUD(self.MARKER_MESSAGES_LOC_IDS[messageStringID]).format(grid_square=zoneSymbol + str(zoneNumber))
        messageType = MESSAGE_TYPE.BATTLE_ALLY
        if senderID != BigWorld.player().id:
            squadType = SQUAD_TYPES().getSquadType(SQUAD_TYPES().getSquadIDbyAvatarID(senderID), senderID)
            if squadType == SQUAD_TYPES.OWN:
                messageType = MESSAGE_TYPE.BATTLE_SQUAD
        self.__showTextMessage(senderID, messageType, 0, 0, message, isHistory)
        return

    def getZoneIndex(self, value):
        index = int(value / 10)
        if index > 9:
            index = 9
        return index

    def _makeBoundsObject(self, bounds):
        left = 0
        right = 0
        top = 0
        bottom = 0
        for point in bounds:
            left = min(left, point.x)
            right = max(right, point.x)
            top = min(top, point.z)
            bottom = max(bottom, point.z)

        return {'left': left,
         'right': right,
         'top': top,
         'bottom': bottom}

    def screenShotNotification(self, path):
        ownerID = BigWorld.player().id
        self.__showTextMessage(ownerID, MESSAGE_TYPE.BATTLE_NEUTRAL_UNIVERSAL, 0, -1, localizeMessages('LOBBY_MSG_SCREENSHOT').format(adress=path), False)

    def spamNotification(self, time):
        ownerID = BigWorld.player().id
        timeValue = '%.2f' % time
        self.__showTextMessage(ownerID, MESSAGE_TYPE.BATTLE_NEUTRAL_WARNING, 0, -1, localizeHUD('QUICK_MESSAGE_ERROR_TIMER').format(time_sec=timeValue), False)

    def chooseNotification(self, message):
        ownerID = BigWorld.player().id
        self.__showTextMessage(ownerID, MESSAGE_TYPE.BATTLE_NEUTRAL_WARNING, 0, -1, message, False)

    def showBattleMessageReactionResult(self, battleMessageType, isPositive, senderID, callerID, targetID):
        ownerID = BigWorld.player().id
        doShowChatMessage = ownerID == callerID
        reactionType = BattleMessageReactionHelper.BATTLE_MESSAGE_TYPE_RESULT_MAP_POSITIVE.get(battleMessageType, None) if isPositive else BATTLE_MESSAGE_TYPE.FAILURE
        if not doShowChatMessage:
            return
        else:
            arena = GameEnvironment.getClientArena()
            senderName, callerName, targetName = arena.getObjectName(senderID), arena.getObjectName(callerID), arena.getObjectName(targetID)
            textMessage = MessagesID().getLocalizedMessage(reactionType, targetID) if BattleMessageReactionHelper.USE_STANDARD_MESSAGE_TEXT else BattleMessageReactionHelper.LocalizeBattleMessageReaction(battleMessageType, isPositive, senderName, callerName, targetName)
            if BattleMessageReactionHelper.USE_COLORS:
                htmlText = textMessage.replace('>', '&gt;')
                htmlText = htmlText.replace('<', '&lt;')
                isColorBlind = Settings.g_instance.getGameUI()['alternativeColorMode']
                if isColorBlind:
                    colorCode = BattleMessageReactionHelper.POSITIVE_REACTION_COLOR_ALT if isPositive else BattleMessageReactionHelper.NEGATIVE_REACTION_COLOR_ALT
                else:
                    colorCode = BattleMessageReactionHelper.POSITIVE_REACTION_COLOR if isPositive else BattleMessageReactionHelper.NEGATIVE_REACTION_COLOR
                htmlText = '<font color="{}">{}</font>'.format(colorCode, htmlText)
                self.__showTextMessage(senderID, MESSAGE_TYPE.BATTLE_ALLY, 0, callerID, htmlText, False, isHTML=True)
                return
            self.__showTextMessage(senderID, MESSAGE_TYPE.BATTLE_ALLY, 0, callerID, textMessage, False)
            return

    def showTextMessage(self, senderID, messageType, messageStringID, targetID, message, isHistory):
        if messageType == MESSAGE_TYPE.BATTLE_PROMPT_COMMAND:
            messageType = MESSAGE_TYPE.BATTLE_ALLY
            if senderID != BigWorld.player().id:
                squadType = SQUAD_TYPES().getSquadType(SQUAD_TYPES().getSquadIDbyAvatarID(senderID), senderID)
                if squadType == SQUAD_TYPES.OWN:
                    messageType = MESSAGE_TYPE.BATTLE_SQUAD
        if not Settings.g_instance.getGameUI()['isChatEnabled'] and int(messageStringID) not in self.CHAT_COMMANDS_MESSAGES_REVERTED:
            return
        if not self.__isPlayerIgnored(senderID):
            fMessage = self.__filterMessage(message, senderID)
            self.__showTextMessage(senderID, messageType, messageStringID, targetID, fMessage, isHistory)

    def showFastCommandMessage(self, senderID, messageType, messageStringID, targetID, message, isHistory):
        self.__showTextMessage(senderID, messageType, messageStringID, targetID, message, isHistory)

    def __showTextMessage(self, senderID, msgType, messageStringID, targetID, message, isHistory, leaderType = -1, isHTML = False):
        messageT = ChatMessageVO()
        messageT.msgType = msgType
        messageT.senderID = senderID
        messageT.message = message
        messageT.isHistory = isHistory
        messageT.leaderType = leaderType
        owner = BigWorld.player()
        clientArena = GameEnvironment.getClientArena()
        if owner and clientArena:
            avatarInfo = clientArena.getAvatarInfo(senderID)
            if avatarInfo:
                messageT.authorType = avatarInfo['settings'].airplane.planeType
                messageT.authorName = avatarInfo['playerName']
                messageT.vechicleName = localizeAirplane(avatarInfo['settings'].airplane.name)
                if avatarInfo['classID'] == EntitySupportedClasses.AvatarBot:
                    messageT.authorName = messageT.authorName.replace('>', '&gt;').replace('<', '&lt;')
                messageT.authorClanAbbrev = avatarInfo['clanAbbrev']
                if avatarInfo['teamIndex'] == BigWorld.player().teamIndex:
                    squadType = SQUAD_TYPES().getSquadType(SQUAD_TYPES().getSquadIDbyAvatarID(senderID), senderID)
                    if squadType == SQUAD_TYPES.OWN:
                        messageT.teamType = TEAM_TYPE.BATTLE_SQUAD
                    else:
                        messageT.teamType = TEAM_TYPE.BATTLE_ALLY
                else:
                    messageT.teamType = TEAM_TYPE.BATTLE_OPPONENT
            else:
                LOG_DEBUG('showTextMessage - avatarInfo is None', senderID, msgType, messageStringID, targetID, message, isHistory, leaderType)
            messageT.isOwner = messageT.senderID == owner.id
            if messageT.isOwner:
                messageT.authorName = localizeHUD('HUD_YOU_MESSAGE')
                messageT.authorClanAbbrev = ''
            if messageT.message and not isHTML:
                messageT.message = messageT.message.replace('>', '&gt;').replace('<', '&lt;')
                if messageT.senderID == self.__lastMessage.senderID and messageT.msgType == self.__lastMessage.msgType and messageT.message == self.__lastMessage.message and messageT.time - self.__lastMessage.time < MESSAGE_SAME_COOLDOWN:
                    return
                self.__addChatMessage(messageT)
                self.__lastMessage = messageT

    def __showChatCommand(self, command, isFired):
        if command in self.CHAT_COMMANDS_MESSAGES:
            messageStringID = self.CHAT_COMMANDS_MESSAGES[command]
            if messageStringID in [ChatMessagesStringID.ENEMY_HERE, ChatMessagesStringID.MY_LOCATION]:
                pass
            elif isFired:
                if BigWorld.time() - self.__chatCommandLastExecuteTime <= gui.HUDconsts.HUD_ENTITY_COMMAND_WAITING_TIME:
                    return
                targetID = 0
                self.__chatCommandLastExecuteTime = BigWorld.time()
                self.__broadcastMessage('', MESSAGE_TYPE.BATTLE_PROMPT_COMMAND, messageStringID, targetID)

    def __showChat(self):
        self.__onVisibilityChat(True, False)

    def onAllIntreClosed(self):
        if self.__chatAllowed & CHAT_BLOCKER.INTERMISSION:
            self.hideChat()

    def hideChat(self):
        if self.__chatVisible:
            self.__onVisibilityChat(False, False)
        else:
            self.__switchAllowChat(CHAT_BLOCKER.INTERMISSION)

    def __onVisibilityChat(self, visible, isNeedSend):
        LOG_DEBUG('onVisibilityChat')
        if visible:
            self.__squadStateUpdate()
        self.__chatVisible = visible
        self.__ui.call_1('hud.onVisibilityChat', self.__chatVisible, isNeedSend)
        BigWorld.player().setFlyKeyBoardInputAllowed(not self.__chatVisible)

    def __isPlayerIgnored(self, playerID):
        return self.__playersChatStatus.get(playerID) == CHAT_STATUS.IGNORED

    def __filterMessage(self, text, userUid):
        owner = BigWorld.player()
        if owner and owner.id != userUid:
            if Settings.g_instance.getXmppChatSettings()['messageFilterEnabled']:
                result = self._filterChain.chainIn(convertToLocal(text), userUid, BigWorld.time())
                return utf_8.encode(result)[0]
        return text

    def __onSendChatMessage(self, message, messageType):
        message = message[:MESSAGE_MAX_SIZE]
        self.__broadcastMessage(message.encode('utf-8'), CONVERT_CHAT_MSG_TYPE_FROM_FLASH.get(messageType, -1))

    def __broadcastMessage(self, message, messageType, messageStringID = 0, targetID = 0):
        dTime = BigWorld.time() - self.__lastSendTime
        if dTime > WAIT_TIME_FOR_SEND_CHAT_MSG:
            self.__lastSendTime = BigWorld.time()
            self.__send(message, messageType, messageStringID, targetID)
        else:
            LOG_DEBUG('__broadcastMessage - waiting time=%s' % dTime)

    def __send(self, message, messageType, messageStringID = 0, targetID = 0):
        if len(message) > 0 or messageStringID != 0:
            owner = BigWorld.player()
            owner.cell.sendTextMessage(messageType, messageStringID, targetID, message)
            mHandler = messenger.g_xmppChatHandler
            if messageType == MESSAGE_TYPE.BATTLE_SQUAD and mHandler:
                mHandler.sendSquadMessage(message)

    def __setPlayersChatStatus(self, playersList):
        for playerStatus in playersList:
            self.__playersChatStatus[playerStatus[0]] = playerStatus[1]

    def __chatUpdateStatus(self):
        owner = BigWorld.player()
        vo = CustomObject()
        vo.isBanned = getattr(owner, 'isChatBan', False)
        vo.isEnabled = Settings.g_instance.gameUI['isChatEnabled']
        self.__ui.call_1('hud.chatUpdateStatus', vo)

    def __squadStateUpdate(self):
        self.__ui.call_1('hud.chatIsSquad', bool(SQUAD_TYPES.playerSquadID()))

    def __addChatMessage(self, chatMessage):
        chatMessage.msgType = CONVERT_CHAT_MSG_TYPE_TO_FLASH.get(chatMessage.msgType, -1)
        self.__ui.call_1('hud.chatMessage', chatMessage)

    def __initFilterChain(self):
        self._filterChain = FilterChain()
        self._filterChain.addFilter('olFilter', ObsceneLanguageFilter())
        self._filterChain.addFilter('domainFilter', DomainNameFilter())
        self._filterChain.addFilter('spamFilter', SpamFilter())
        self._filterChain.addFilter('floodFilter', FloodFilter())