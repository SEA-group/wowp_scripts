# Embedded file name: scripts/client/gui/HUD2/features/FastCommands/FastCommandManager.py
import random
from functools import partial
import BigWorld
import GameEnvironment
import InputMapping
from Helpers.i18n import localizeHUD
from consts import BATTLE_MESSAGE_TYPE, MESSAGE_TYPE
from debug_utils import LOG_DEBUG
from gui.HUD2.hudFeatures import Feature
from FastCommandsConfiguration import *
TAG = ' FAST_COMMANDS_MANAGER: '
WAIT_TIME_FOR_SEND_CHAT_MSG = 4
LOC_MAP_INTENTIONS = {NotificationType.IN_FLYING_TO_ATTACK: 'QUICK_MESSAGE_F2_1',
 NotificationType.IN_FLYING_TO_PROTECT: 'QUICK_MESSAGE_F2_2',
 NotificationType.IN_FLYING_TO: 'QUICK_MESSAGE_F2_3'}
LOC_MAP_SUPPORT = {NotificationType.SUP_ATTACK_NEED_SUPPORT: 'QUICK_MESSAGE_F3_1',
 NotificationType.SUP_PROTECTED_NEED_SUPPORT: 'QUICK_MESSAGE_F3_2',
 NotificationType.SUP_NEED_SUPPORT: 'QUICK_MESSAGE_F3_NEED_HELP'}
LOC_MAP_OFFENSE_DEFENSE = {NotificationType.OFD_ATTACK_PLANE: 'QUICK_MESSAGE_F4_1',
 NotificationType.OFD_COVER_PLANE: 'QUICK_MESSAGE_F4_2',
 NotificationType.OFD_ATTACK_BOMBERS: 'QUICK_MESSAGE_F4_3',
 NotificationType.OFD_COVER_BOMBERS: 'QUICK_MESSAGE_F4_4'}
LOC_MAP_DANGER = {NotificationType.OK: 'QUICK_MESSAGE_F5_1'}
LOC_MAP_AFFIRMATIVE = {NotificationType.OK: 'HELP_SO_ACCURATELY'}
LOC_MAP_NEGATIVE = {NotificationType.OK: 'HELP_NO_WAY'}
LOC_MAP_GOOD_JOB = {NotificationType.OK: 'QUICK_MESSAGE_F8_1'}
FAST_LOC_COMMAND_MAP = {CommandTypes.INTENTIONS: LOC_MAP_INTENTIONS,
 CommandTypes.SUPPORT: LOC_MAP_SUPPORT,
 CommandTypes.OFFENSE_DEFENSE: LOC_MAP_OFFENSE_DEFENSE,
 CommandTypes.DANGER: LOC_MAP_DANGER,
 CommandTypes.AFFIRMATIVE: LOC_MAP_AFFIRMATIVE,
 CommandTypes.NEGATIVE: LOC_MAP_NEGATIVE,
 CommandTypes.GOOD_JOB: LOC_MAP_GOOD_JOB}
FAST_LOC_COMMAND_ERROR = {CommandTypes.INTENTIONS: 'QUICK_MESSAGE_ERROR_COMPLEX',
 CommandTypes.OFFENSE_DEFENSE: 'QUICK_MESSAGE_ERROR_PLANE'}

class FastCommandManager(object):

    def __init__(self, features, model):
        self._model = model
        self.__lastSendTime = 0
        self.__targetID = 0
        self._targetsRequestMap = {}
        self.__callID = 0
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._input = features.require(Feature.INPUT)
        self._processor = self._input.commandProcessor
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._waveInfoManager = self._gameMode.waveInfoManager
        self._db = features.require(Feature.DB_LOGIC)
        self._player.eLeaveWorldEvent += self._unsubscribeFromPlayer
        self._player.eOnFastCommandResponse += self.__onGetDataFromServer
        self._gameEnvironment.eOnTargetEntity += self.__onSelectTarget
        self._gameEnvironment.eGetTargetsFromFlash += self.__onSelectTargetFromFlash
        self.__subscribe()

    def __subscribe(self):
        self.NEED_TARGET_COMMANDS = [CommandTypes.INTENTIONS, CommandTypes.OFFENSE_DEFENSE]
        self.CHAT_COMMANDS_MESSAGES = {InputMapping.CMD_F8_CHAT_COMMAND: CommandTypes.INTENTIONS,
         InputMapping.CMD_F9_CHAT_COMMAND: CommandTypes.SUPPORT,
         InputMapping.CMD_F4_CHAT_COMMAND: CommandTypes.OFFENSE_DEFENSE,
         InputMapping.CMD_F2_CHAT_COMMAND: CommandTypes.AFFIRMATIVE,
         InputMapping.CMD_F3_CHAT_COMMAND: CommandTypes.NEGATIVE,
         InputMapping.CMD_F5_CHAT_COMMAND: CommandTypes.DANGER,
         InputMapping.CMD_F6_CHAT_COMMAND: CommandTypes.GOOD_JOB}
        for command in InputMapping.CHAT_COMMANDS:
            self._processor.addListeners(command, partial(self.__showChatCommand, command))

    def _unsubscribeFromPlayer(self):
        self._player.eOnFastCommandResponse -= self.__onGetDataFromServer
        self._player.eLeaveWorldEvent -= self._unsubscribeFromPlayer

    def __onSelectTarget(self, entityId):
        self.__targetID = entityId

    def __showChatCommand(self, command):
        if command in self.CHAT_COMMANDS_MESSAGES:
            messageStringID = self.CHAT_COMMANDS_MESSAGES[command]
            dTime = BigWorld.time() - self.__lastSendTime
            if dTime > WAIT_TIME_FOR_SEND_CHAT_MSG:
                if messageStringID in self.NEED_TARGET_COMMANDS:
                    self.__requestTargets(messageStringID)
                else:
                    self.__sendToServer(messageStringID)
                self.__lastSendTime = BigWorld.time()
            else:
                chat = GameEnvironment.getChat()
                lastTime = WAIT_TIME_FOR_SEND_CHAT_MSG - dTime
                chat.spamNotification(lastTime)

    def __sendToServer(self, messageStringID, targetList = None):
        requestData = map(lambda item: item.toFCRequestData(), targetList) if targetList else []
        self._player.requestFastCommand(messageStringID, requestData)

    def __requestTargets(self, messageStringID):
        if messageStringID == CommandTypes.OFFENSE_DEFENSE:
            self.__callID += 1
            self._targetsRequestMap[self.__callID] = messageStringID
            self._model.plane.call = self.__callID
        if messageStringID == CommandTypes.INTENTIONS:
            self.__callID += 1
            self._targetsRequestMap[self.__callID] = messageStringID
            self._model.sector.call = self.__callID

    def __onSelectTargetFromFlash(self, targetList, callID):
        if not self._targetsRequestMap.__contains__(callID):
            return
        messageStringID = self._targetsRequestMap[callID]
        self.__sendToServer(messageStringID, targetList)

    def _sendToFlash(self, senderID, messageStringID, targetID, notificationID, waveID):
        sectorData = {}
        sectorData['senderID'] = senderID
        sectorData['messageType'] = messageStringID
        sectorData['targetID'] = targetID
        sectorData['notificationID'] = notificationID
        if waveID != -1:
            sectorData['waveID'] = waveID
        sectorData['callID'] = random.random()
        self._model.commandData = sectorData

    def __onGetDataFromServer(self, authorID, commandType, notificationID, targetID):
        if commandType == CommandTypes.OFFENSE_DEFENSE:
            waveID = self._waveInfoManager.getWaveByPlaneID(targetID)
        else:
            waveID = -1
        self._sendToFlash(authorID, commandType, targetID, notificationID, waveID)
        locale = self._getLocal(commandType, notificationID, targetID)
        chat = GameEnvironment.getChat()
        if notificationID == -1:
            chat.chooseNotification(locale)
            self.__lastSendTime = BigWorld.time() - WAIT_TIME_FOR_SEND_CHAT_MSG
        else:
            chat.showFastCommandMessage(authorID, MESSAGE_TYPE.BATTLE_FAST_COMMAND_ALL, commandType, targetID, locale, False)

    def _getLocal(self, typeID, notificationID, targetID):
        if notificationID == -1:
            loc = FAST_LOC_COMMAND_ERROR.get(typeID, '')
            return localizeHUD(loc)
        else:
            commandMap = FAST_LOC_COMMAND_MAP.get(typeID, {})
            loc = commandMap.get(notificationID, '')
            if targetID != -1:
                if typeID == CommandTypes.OFFENSE_DEFENSE:
                    objectName = self._clientArena.getObjectName(int(targetID))
                    message = localizeHUD(loc).format(player_name=objectName)
                else:
                    sectorName = self.__getSectorName(targetID)
                    message = localizeHUD(loc).format(sector=sectorName)
            else:
                message = localizeHUD(loc)
            return '$FC:%(fastCommandType)s$%(message)s' % {'fastCommandType': loc,
             'message': message}

    def __getSectorName(self, targetID):
        self._arenaTypeData = self._db.getArenaData(BigWorld.player().arenaType)
        for sectorData in self._arenaTypeData.sectors.sectors.values():
            if sectorData.ident == targetID:
                return localizeHUD(sectorData.hudSettings.localizationID)

        return ''

    def dispose(self):
        self._targetsRequestMap = None
        self._unsubscribeFromPlayer()
        self._gameEnvironment.eOnTargetEntity -= self.__onSelectTarget
        self._gameEnvironment.eGetTargetsFromFlash -= self.__onSelectTargetFromFlash
        self._player.eLeaveWorldEvent -= self._unsubscribeFromPlayer
        self._player.eOnFastCommandResponse -= self.__onGetDataFromServer
        self._waveInfoManager = None
        self._clientArena = None
        self._gameMode = None
        self._gameEnvironment = None
        self._player = None
        self._input = None
        self._processor = None
        return