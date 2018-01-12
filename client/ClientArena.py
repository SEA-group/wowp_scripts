# Embedded file name: scripts/client/ClientArena.py
import BigWorld
import BWLogging
from GameServiceBase import GameServiceBase
import Math
import ResMgr
import wgPickle
import Event
from debug_utils import *
from consts import *
import consts
import ClientLog
from EntityHelpers import EntitySupportedClasses, buildAndGetWeaponsInfo, translateDictThroughAnother, AvatarFlags
import db.DBLogic
from DestructibleObjectFactory import DestructibleObjectFactory
from DictKeys import NEW_AVATARS_INFO_KEYS_INVERT_DICT, REPORT_BATTLE_RESULT_KEYS_INVERT_DICT
from Descriptors import getTeamObjectDescriptorFromCompactDescriptor, getTeamObjectDescriptorFromCompactUpdateDescriptor
from _airplanesConfigurations_db import getAirplaneConfiguration, airplanesConfigurations
from ObjectsStrategies import selectTeamObjectStrategy
import VOIP
from Helpers.namesHelper import getBotName
import StaticModels
from Helpers.i18n import localizePilot, localizeAirplane, localizeBotChat, localizeLobby, localizeHUD
from adapters.ICrewMemberAdapter import CONTRY_PO_FILE_WRAPPER, FIRST_NAME_MSG_ID, CONTRY_MSG_ID_WRAPPER
import random
from config_consts import IS_DEVELOPMENT
import Helpers.BotChatHelper as BotChatHelper
from db.DBParts import buildPartsMapByPartName
from GameModeSettings.ACSettings import GROUND_OBJECT_TYPE
from ArenaHelpers import GameModes
from functools import partial
from GameActionsManagerProxy import GameActionsManagerProxy

class ClientArena(GameServiceBase):
    __onUpdate = {ARENA_UPDATE.RECEIVE_TEXT_MESSAGE: '_ClientArena__onReceiveTextMessage',
     ARENA_UPDATE.RECEIVE_MARKER_MESSAGE: '_ClientArena__onReceiveMarkerMessage',
     ARENA_UPDATE.VEHICLE_KILLED: '_ClientArena__onVehicleKilled',
     ARENA_UPDATE.TEAM_OBJECT_DESTROYED: '_ClientArena__onTeamObjectDestruction',
     ARENA_UPDATE.TEAM_DOMINATION_PRC: '_ClientArena__onUpdateDominationPrc',
     ARENA_UPDATE.BASE_IS_UNDER_ATTACK: '_ClientArena__onBaseIsUnderAttack',
     ARENA_UPDATE.PLAYER_STATS: '_ClientArena__onUpdatePlayerStats',
     ARENA_UPDATE.RECEIVE_ALL_TEAM_OBJECTS_DATA: '_ClientArena__onReceiveAllTeamObjectsData',
     ARENA_UPDATE.RECEIVE_TEAM_OBJECTS_UPDATE: '_ClientArena__onReceiveTeamObjectsUpdate',
     ARENA_UPDATE.RECEIVE_NEW_AVATARS_INFO: '_ClientArena__onNewAvatarsInfo',
     ARENA_UPDATE.TEAM_SUPERIORITY_POINTS: '_ClientArena__onUpdateTeamSuperiorityPoints',
     ARENA_UPDATE.REPORT_BATTLE_RESULT: '_ClientArena__onReportBattleResult',
     ARENA_UPDATE.RECEIVE_VOIP_CHANNEL_CREDENTIALS: '_ClientArena__onReceiveVOIPChannelCredentials',
     ARENA_UPDATE.TURRET_BOOSTER_DESTROYED: '_ClientArena__onReceiveTurretBoosterInfo',
     ARENA_UPDATE.GAME_RESULT_CHANGED: '_ClientArena__onGameResultChanged',
     ARENA_UPDATE.RECEIVE_LAUNCH: '_ClientArena__onReceiveLaunch',
     ARENA_UPDATE.GAIN_AWARD: '_ClientArena__onGainAward',
     ARENA_UPDATE.TEAM_OBJECT_PARTGROUP_DESTROYED: '_ClientArena__onTeamObjectPartGroupDestroyed',
     ARENA_UPDATE.SCENARIO_ICON: '_ClientArena__onScenarioSetIcon',
     ARENA_UPDATE.SCENARIO_TEXT: '_ClientArena__onScenarioSetText',
     ARENA_UPDATE.UPDATE_OBJECTS_DATA: '_ClientArena__onUpdateObjectsData',
     ARENA_UPDATE.UPDATE_DEBUG_INFO: '_ClientArena__onDebugInfoReceived',
     ARENA_UPDATE.RECEIVE_BATTLE_MESSAGE_REACTION_RESULT: '_ClientArena__onReceiveBattleMessageReactionResult',
     ARENA_UPDATE.ECONOMIC_EVENTS: '_ClientArena__onEconomicEvents',
     ARENA_UPDATE.ECONOMIC_DEBUG_INFO: '_ClientArena__onEconomicDebugInfo',
     ARENA_UPDATE.ECONOMIC_PLAYERS_POINTS: '_ClientArena__onEconomicPlayersPoints',
     ARENA_UPDATE.ECONOMIC_EXT_PLAYERS_DATA: '_ClientArena__onEconomicExtPlayersData',
     ARENA_UPDATE.PLANE_TYPE_RANK_UPDATED: '_ClientArena__onPlaneTypeRankUpdated'}

    def __init__(self):
        super(ClientArena, self).__init__()
        self.logger = BWLogging.getLogger(self.__class__.__name__)
        self.__sortedAvatarsIDs = dict()
        self.__avatarsDataReceived = False
        self.__isTeamObjectsReceived = False
        from gui.AlwaysVisibleObjects import AlwaysVisibleObjects
        self.__alwaysVisibleObjects = AlwaysVisibleObjects()
        self.__allObjectsData = {}
        self.__updatedObjectsData = {}
        self.__scenarioObjectMap = {}
        self.dominationPrc = [0, 0]
        self.superiorityPoints = [0, 0]
        self.avatarInfos = {}
        self.__eventManager = Event.EventManager()
        self.__ownerID = BigWorld.player().id
        self.avatarModelLoaded = 0
        self.__lastUpdateFunctionIndex = 0
        self.__waitingUpdateFunctionsPool = {}
        self.arenaData = None
        self.battleType = None
        self.__isBattleUILoaded = False
        em = self.__eventManager
        self.onGameModeCreate = Event.Event(em)
        self.onEconomicEvents = Event.Event(em)
        self.onEconomicDebugInfo = Event.Event(em)
        self.onEconomicPlayersPoints = Event.Event(em)
        self.onReceiveTextMessage = Event.Event(em)
        self.onReceiveMarkerMessage = Event.Event(em)
        self.onVehicleKilled = Event.Event(em)
        self.onGainAward = Event.Event(em)
        self.onUpdateDominationPrc = Event.Event(em)
        self.onBaseIsUnderAttack = Event.Event(em)
        self.onNewAvatarsInfo = Event.Event(em)
        self.onUpdatePlayerStats = Event.Event(em)
        self.onApplyArenaData = Event.Event(em)
        self.onReceiveAllTeamObjectsData = Event.Event(em)
        self.onReceiveTeamObjectsDataUpdate = Event.Event(em)
        self.onUpdateTeamSuperiorityPoints = Event.Event(em)
        self.onReportBattleResult = Event.Event(em)
        self.onReceiveVOIPChannelCredentials = Event.Event(em)
        self.onTeamObjectDestruction = Event.Event(em)
        self.onRecreateAvatar = Event.Event(em)
        self.onGameResultChanged = Event.Event(em)
        self.onUpdateTurretBoosterInfo = Event.Event(em)
        self.onAllServerDataReceived = Event.Event(em)
        self.onLaunch = Event.Event(em)
        self.onTeamObjectPartGroupChanged = Event.Event(em)
        self.onScenarioSetIcon = Event.Event(em)
        self.onScenarioSetText = Event.Event(em)
        self.onBattleMessageReactionResult = Event.Event(em)
        self.onAvatarChangedPlane = Event.Event(em)
        self.onBeforePlaneChanged = Event.Event(em)
        self.onAvatarPlaneTypeRankChanged = Event.Event(em)
        self.onPlayerEconomicExtDataReceived = Event.Event(em)
        self.onAvatarEnterWorld = Event.Event(em)
        self.onAvatarLeaveWorld = Event.Event(em)
        self._gameMode = None
        self._gameActionsManager = GameActionsManagerProxy()
        return

    def createGameMode(self):
        """Creates game mode instance
        """
        player = BigWorld.player()
        cls = GameModes.getGameModeClientClass(player.gameMode)
        self._gameMode = cls(self)
        self.onGameModeCreate()
        LOG_DEBUG('ClientArena::createGameMode: created {0}'.format(self._gameMode))

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.GameModeClient.GameModeClient
        """
        return self._gameMode

    @property
    def gameActionsManager(self):
        """GameActionsManagerProxy instance
        @rtype: GameActionsManagerProxy
        """
        return self._gameActionsManager

    def __callUpdateFunction(self, updateFunctionID, argStr):
        delegateName = self.__onUpdate.get(updateFunctionID, None)
        if delegateName is not None:
            getattr(self, delegateName)(argStr)
            return True
        else:
            return False

    def update(self, updateFunctionID, argStr):
        handledInArena = self.__callUpdateFunction(updateFunctionID, argStr)
        handledInGM = self.gameMode.onArenaUpdate(updateFunctionID, wgPickle.loads(wgPickle.FromServerToClient, argStr))
        if not (handledInArena or handledInGM):
            self.logger.error('function not found updateFunctionID = {0}'.format(updateFunctionID))

    def doLeaveWorld(self):
        self.__isBattleUILoaded = False
        self.__eventManager.clear()
        for avatarInfo in self.avatarInfos.values():
            self.__destroyObjectControllers(avatarInfo)

        for objData in self.__allObjectsData.itervalues():
            self.__destroyObjectControllers(objData)

        VOIP.api().unsubscribeMemberStateObserversByType(consts.VOIP.MEMBER_STATUS_OBSERVER_TYPES.ARENA_HUD)
        self.gameMode.destroy()
        self._gameActionsManager.cleanup()
        self._gameActionsManager = None
        return

    def findIDsByPlayerName(self, name):
        return [ id for id, avatarInfo in self.avatarInfos.items() if avatarInfo.has_key('playerName') and name == avatarInfo['playerName'] ]

    def getAvatarIdByDBId(self, dbId):
        """for Vivox id maping"""
        return next((info.get('avatarID') for info in self.avatarInfos.itervalues() if info.get('databaseID') == dbId), None)

    def getDBId(self, avatarID):
        return next((info.get('databaseID') for info in self.avatarInfos.values() if info.get('avatarID') == avatarID), None)

    def getObjectName(self, id):
        avatarInfo = self.avatarInfos.get(id, None)
        if avatarInfo:
            return avatarInfo['playerName']
        else:
            objName = self.__alwaysVisibleObjects.getObjectName(id)
            if objName:
                return objName
            return str(id)
            return

    def getArenaBounds(self):
        player = BigWorld.player()
        arenaType = player.arenaType
        arenaSettings = db.DBLogic.g_instance.getArenaData(arenaType)
        arenaObjects = arenaSettings.arenaObjects
        return arenaObjects.bounds

    def getTeamObjectType(self, id):
        if id in self.__allObjectsData:
            return self.__allObjectsData[id]['settings'].type
        else:
            return None

    def getScenarioObjectByDSName(self, name):
        return self.__scenarioObjectMap.get(name)

    def isTeamObjectContainsTurret(self, id):
        if id in self.__allObjectsData:
            return bool(self.__allObjectsData[id]['settings'].turretName)
        return False

    @property
    def allObjectsData(self):
        return self.__allObjectsData

    @property
    def updatedObjectsData(self):
        return self.__updatedObjectsData

    @property
    def alwaysVisibleObjects(self):
        return self.__alwaysVisibleObjects

    def __onReceiveTextMessage(self, argStr):
        senderID, messageType, messageStringID, targetID, message = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        avatarsInfo = self.avatarInfos
        senderInfo = avatarsInfo.get(senderID, None)
        if senderInfo:
            if BotChatHelper.isBotChatMessage(messageType):
                message = BotChatHelper.convertMessage(message, self.avatarInfos, senderInfo, targetID).encode('utf-8')
                messageType = BotChatHelper.convertMessageType(messageType)
                targetID = 0
            if messageType == MESSAGE_TYPE.BATTLE_ALL and senderInfo['teamIndex'] != BigWorld.player().teamIndex:
                messageType = MESSAGE_TYPE.BATTLE_ALL_FROM_OPPONENT
            try:
                msg = 'Player %s(%s) say: %s' % (self.getObjectName(senderID), senderID, unicode(message, encoding='utf-8'))
                ClientLog.g_instance.gameplay(msg.encode('utf-8'))
            except:
                LOG_ERROR('__onReceiveTextMessage', senderID, message)
                return

            self.onReceiveTextMessage(senderID, messageType, messageStringID, targetID, message, False)
        return

    def __onEconomicEvents(self, argStr):
        events = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        isKill = any((len(eventData) == 2 for eventData in events))
        if isKill:
            BigWorld.callback(0.5, partial(self.onEconomicEvents, events))
        else:
            self.onEconomicEvents(events)

    def __onEconomicDebugInfo(self, argStr):
        info = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onEconomicDebugInfo(info)

    def __onEconomicPlayersPoints(self, argStr):
        info = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onEconomicPlayersPoints(info)

    def __onReceiveMarkerMessage(self, argStr):
        senderID, posX, posZ, messageStringID = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onReceiveMarkerMessage(senderID, posX, posZ, messageStringID, False)

    def __onReceiveBattleMessageReactionResult(self, argStr):
        battleMessageType, isPositive, senderID, callerID, targetID = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onBattleMessageReactionResult(battleMessageType, isPositive, senderID, callerID, targetID)

    def __onVehicleKilled(self, argStr):
        killingInfo = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onVehicleKilled(killingInfo)

    def __onGainAward(self, argStr):
        awardInfo = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onGainAward(awardInfo)

    def __onTeamObjectDestruction(self, argStr):
        killingInfo = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        victimData = self.__allObjectsData[killingInfo['victimID']]
        superiorityPoints, superiorityPointsMax = self.getSuperiorityPoints4TeamObject(killingInfo['victimID'])
        points = killingInfo.get('points', superiorityPoints)
        self.onTeamObjectDestruction(killingInfo['killerID'], killingInfo['victimID'], victimData['settings'].type, victimData['teamIndex'], points, superiorityPointsMax)

    def __onBaseIsUnderAttack(self, argStr):
        objID = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        objectType = self.getTeamObjectType(objID)
        if objectType:
            obj = BigWorld.entities.get(objID)
            if not obj:
                obj = self.getMapEntry(objID)
            if obj and getattr(obj, 'isAlive', True):
                self.onBaseIsUnderAttack(obj.position, obj.teamIndex, objectType)
        else:
            LOG_ERROR('__onBaseIsUnderAttack - objectType undefined (%s)' % objID)

    def __onUpdatePlayerStats(self, argStr):
        stats = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        avatarInfo = self.avatarInfos.get(stats['avatarID'], None)
        if avatarInfo:
            avatarInfo['stats'] = stats
            self.onUpdatePlayerStats(avatarInfo)
        return

    def __onReceiveAllTeamObjectsData(self, argStr):
        objectsList, serverTeamObjectsCheckSum = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        LOG_INFO('__onReceiveAllTeamObjectsData')
        player = BigWorld.player()
        arenaType = player.arenaType
        arenaSettings = db.DBLogic.g_instance.getArenaData(arenaType)
        arenaObjects = arenaSettings.arenaObjects
        if arenaObjects.teamObjectsCheckSum != serverTeamObjectsCheckSum:
            CRITICAL_ERROR('Invalid teamObjectsCheckSum - sync your server with client please!')
        BigWorld.setArenaDefScripts(arenaSettings.arenaScripts)
        for r in objectsList:
            record = getTeamObjectDescriptorFromCompactDescriptor(r)
            objID = record['id']
            arenaObjID = record['arenaObjID']
            maxHealth = record['maxHealth']
            objArenaData = arenaSettings.getTeamObjectData(arenaObjID)
            modelStrID = objArenaData['modelID']
            settings = db.DBLogic.g_instance.getEntityDataByName(db.DBLogic.DBEntities.BASES, modelStrID)
            classID = EntitySupportedClasses.TeamTurret if settings.type == TYPE_TEAM_OBJECT.TURRET else EntitySupportedClasses.TeamObject
            modelID = settings.typeID
            teamIndex = record['teamIndex']
            groupName = objArenaData['groupName']
            ACType = objArenaData.get('ACType', -1)
            isRepair = ACType == GROUND_OBJECT_TYPE.REPAIR
            if isRepair:
                LOG_DEBUG('repair Zone activate', objID, groupName)
            isRecharg = ACType == GROUND_OBJECT_TYPE.RECHARGE
            if isRecharg:
                LOG_DEBUG('Recharg Zone activate', objID, groupName)
            self.createTeamObjectControllers(objID, settings)
            self.__allObjectsData[objID].update({'groupName': groupName,
             'classID': classID,
             'teamIndex': teamIndex,
             'settings': settings,
             'modelID': modelID,
             'maxHealth': maxHealth,
             'valid': True,
             'isRepair': isRepair,
             'isRecharg': isRecharg,
             'ACType': ACType})
            self.__alwaysVisibleObjects.addAllTimeVisibleObject(objID, classID, teamIndex, record['pos'], record['isAlive'], modelID)
            name = objArenaData['DsName']
            if name and name not in self.__scenarioObjectMap:
                self.__scenarioObjectMap[name] = (self.__allObjectsData[objID], objArenaData, objID)

        self.onReceiveAllTeamObjectsData()
        self.__isTeamObjectsReceived = True

    def __onReceiveTeamObjectsUpdate(self, argStr):
        self.__updatedObjectsData.clear()
        objectsList = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        for r in objectsList:
            record = getTeamObjectDescriptorFromCompactUpdateDescriptor(r)
            objID = record['id']
            self.__updatedObjectsData[objID] = record

        self.onReceiveTeamObjectsDataUpdate()

    def isAllTeamObjectsDataReceived(self):
        return self.__isTeamObjectsReceived

    def createTeamObjectControllers(self, objID, settings, owner = None, partTypes = None, partStates = None):
        partTypes = partTypes or []
        partStates = partStates or []
        objData = self.__allObjectsData.get(objID, {})
        if 'modelManipulator' not in objData:
            gunnersPartsMap = buildPartsMapByPartName('Gunner', settings.partsSettings, partTypes)
            if gunnersPartsMap:
                turretName = gunnersPartsMap[gunnersPartsMap.keys()[0]].componentXml
            else:
                turretName = ''
            controllersData = DestructibleObjectFactory.createControllers(objID, settings, settings, partTypes, partStates, turretsName=[turretName])
            objData.update(controllersData)
            self.__allObjectsData[objID] = objData
        if owner:
            selectTeamObjectStrategy(owner, owner.arenaObjID, BigWorld.player().arenaType)
            objData['movementStrategy'] = owner.controllers.get('movementStrategy', None)
        return objData

    def getMapEntry(self, objID):
        if self.__alwaysVisibleObjects:
            return self.__alwaysVisibleObjects.getMapEntry(objID)
        else:
            return None

    def initArenaData(self):
        player = BigWorld.player()
        arenaType = player.arenaType
        arenaSettings = db.DBLogic.g_instance.getArenaData(arenaType)
        arenaObjects = arenaSettings.arenaObjects
        self.battleType = player.battleType
        self.arenaData = {'waterLevel': arenaObjects.waterLevel,
         'bounds': arenaObjects.bounds,
         'battleType': player.battleType}
        self.onApplyArenaData(self.arenaData)

    def __onUpdateObjectsData(self, argStr):
        data = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        for updatableData in data:
            objID, _, __, ___ = updatableData
            objData = self.avatarInfos.get(objID, None)
            if not objData:
                objData = self.__allObjectsData.get(objID, None)
            if objData:
                if objData.has_key('classID'):
                    self.__alwaysVisibleObjects.updateTemporaryVisibleObjectData(updatableData, objData['classID'], objData['teamIndex'], objData.get('modelID', None))

        return

    def __onNewAvatarsInfo(self, argStr):
        newAvatarsList = translateDictThroughAnother(wgPickle.loads(wgPickle.FromServerToClient, argStr), NEW_AVATARS_INFO_KEYS_INVERT_DICT, True)
        LOG_INFO('__onNewAvatarsInfo', self.__ownerID, [ avatarData['avatarID'] for avatarData in newAvatarsList ])
        LOG_INFO('INFO extUpgrades', [ (avatarData['avatarID'], avatarData['extUpgrades']) for avatarData in newAvatarsList ])
        for avatarData in newAvatarsList:
            avatarID = avatarData['avatarID']
            airplaneInfo = avatarData['airplaneInfo']
            currentOwner = None
            avatarData['planeTypeRank'] = dict(avatarData['planeTypeRank'])
            avatarPrevInfo = self.avatarInfos.get(avatarID, None)
            if not avatarPrevInfo:
                self.avatarInfos[avatarID] = avatarData
            else:
                if 'airplaneInfo' in avatarPrevInfo and avatarPrevInfo['airplaneInfo']['globalID'] != airplaneInfo['globalID']:
                    self.onBeforePlaneChanged(avatarID)
                    currentOwner = self.__destroyControllers(avatarPrevInfo)
                self.avatarInfos[avatarID].update(avatarData)
            extUpgrades = dict(avatarData['extUpgrades'])
            pilotUpgradeId = extUpgrades.get(LOGICAL_PART.PILOT, 1)
            controllersData = self.createControllers(avatarID, airplaneInfo['globalID'], camouflage=airplaneInfo['camouflage'], decals=airplaneInfo['decals'], pilotUpgradeId=pilotUpgradeId)
            if currentOwner:
                currentOwner.registerControllers(controllersData)
                self.onAvatarChangedPlane(currentOwner.id)
                if currentOwner == BigWorld.player():
                    self.onRecreateAvatar()
            avatarInfo = self.avatarInfos[avatarID]
            if avatarInfo['isNPC']:
                if avatarInfo['NPCType'] == ACNPCTypes.Bomber:
                    avatarInfo['playerName'] = localizeLobby(avatarInfo['playerName'])
                elif avatarInfo['NPCType'] == ACNPCTypes.Defender:
                    avatarInfo['playerName'] = localizeHUD(avatarInfo['playerName'])
            else:
                avatarInfo['playerName'] = getBotName(avatarData['playerName'], getAirplaneConfiguration(airplaneInfo['globalID']).planeID)
            avatarInfo['maxHealth'] = avatarData['maxHealth']
            avatarInfo['equipment'] = avatarData['equipment']
            if avatarID == BigWorld.player().id:
                LOG_TRACE('ClientArena: VOIP.initialize()')
                wasInit = bool(VOIP.api())
                VOIP.initialize(avatarInfo['databaseID'])
                if not wasInit:
                    VOIP.api().onEnterArenaScreen()

        self.__sortAvatars()
        for ids in self.__sortedAvatarsIDs.values():
            for i, avatarID in enumerate(ids):
                self.avatarInfos[avatarID]['airplaneInfo']['decals'][4] = i + 1
                self.avatarInfos[avatarID]['modelManipulator'].surface.setDecalsByIds(self.avatarInfos[avatarID]['airplaneInfo']['camouflage'], self.avatarInfos[avatarID]['airplaneInfo']['decals'])

        teamMembers = dict()
        for avatarID, info in self.avatarInfos.iteritems():
            if info['teamIndex'] == BigWorld.player().teamIndex:
                teamMembers[info['databaseID']] = avatarID

        VOIP.api().unsubscribeMemberStateObserversByType(consts.VOIP.MEMBER_STATUS_OBSERVER_TYPES.ARENA_HUD)
        VOIP.api().subscribeMemberStateObserver(consts.VOIP.MEMBER_STATUS_OBSERVER_TYPES.ARENA_HUD, teamMembers)
        self.__avatarsDataReceived = True
        self.onNewAvatarsInfo(newAvatarsList)
        return

    def __sortAvatars(self):
        teams = dict()
        for avatarInfo in self.avatarInfos.values():
            level = avatarInfo['settings'].airplane.level
            teamIndex = avatarInfo['teamIndex']
            name = localizeAirplane(avatarInfo['settings'].airplane.name)
            if teamIndex not in teams:
                teams[teamIndex] = dict()
            if level not in teams[teamIndex]:
                teams[teamIndex][level] = dict()
            if name not in teams[teamIndex][level]:
                teams[teamIndex][level][name] = list()
            teams[teamIndex][level][name].append(avatarInfo)

        sortedList = list()
        for team in teams.values():
            for level in team.values():
                for name in level.values():
                    name.sort(key=lambda avatarInfo: avatarInfo['playerName'])

            sortedLevelsList = sorted(team.keys(), None, None, True)
            for levelID in sortedLevelsList:
                sortedPlaneNameList = sorted(team[levelID].keys())
                for planeName in sortedPlaneNameList:
                    sortedList.extend(team[levelID][planeName])

        for avatarInfo in sortedList:
            if avatarInfo['teamIndex'] not in self.__sortedAvatarsIDs:
                self.__sortedAvatarsIDs[avatarInfo['teamIndex']] = list()
            self.__sortedAvatarsIDs[avatarInfo['teamIndex']].append(avatarInfo['avatarID'])

        return

    def isAllServerDataReceived(self):
        return self.__avatarsDataReceived

    def __onReceiveLaunch(self, argStr):
        avatarID, shellsCount = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.avatarInfos[avatarID]['shellsCount'] = shellsCount
        self.onLaunch(avatarID)

    def __destroyControllers(self, avatarInfo):
        weapons = avatarInfo.get('weapons', None)
        if weapons:
            owner = weapons.getOwner()
            self.__destroyObjectControllers(avatarInfo)
            return owner
        else:
            return

    def __destroyObjectControllers(self, objData):
        if 'modelManipulator' in objData:
            objData['modelManipulator'].destroy()
            del objData['modelManipulator']
        if 'weapons' in objData:
            objData['weapons'].destroy()
            del objData['weapons']
        if 'turretsLogic' in objData:
            objData['turretsLogic'].setOwner(None)
            objData['turretsLogic'].destroy()
            del objData['turretsLogic']
        if 'shellController' in objData:
            objData['shellController'].destroy()
            del objData['shellController']
        if 'soundController' in objData:
            objData['soundController'].destroy()
            del objData['soundController']
        return

    def createControllers(self, avatarID, globalID, partStates = None, camouflage = None, decals = None, pilotUpgradeId = 1):
        """
        create Weapons, ShellController and ModelManipulator controllers if they are not present yet
        @param avatarID:
        @param globalID:
        @param partStates:
        @return full AvatarInfo if present of created controllers data if not.
        Any way controllers data are part of AvatarInfo
        """
        ATTRS_FOR_COPY = ('teamIndex', 'stats', 'classID')
        partStates = partStates or []
        avatarInfo = self.avatarInfos.get(avatarID, {})
        if 'modelManipulator' not in avatarInfo:
            controllersData = self.__createControllers(avatarID, globalID, partStates, camouflage, decals, pilotUpgradeId)
            avatarInfo.update(controllersData)
            self.avatarInfos[avatarID] = avatarInfo
        return avatarInfo

    def __setupPilot(self, settings, aircraftConfiguration, pilotUpgradeId):
        pilotPart = settings.airplane.partsSettings.getPartByName('pilot')
        if pilotPart is None:
            pilotPart = settings.airplane.partsSettings.getPartByName('pilot_01')
        if pilotPart is not None:
            aircraftConfiguration.partTypes.append({'key': pilotPart.partId,
             'value': pilotUpgradeId})
        else:
            LOG_WARNING('Unable to setup pilot upgrade id')
        return

    def __createControllers(self, avatarID, globalID, partStates, camouflage = None, decals = None, pilotUpgradeId = 0):
        aircraftConfiguration = getAirplaneConfiguration(globalID)
        _db = db.DBLogic.g_instance
        settings = _db.getAircraftData(aircraftConfiguration.planeID)
        turretNames = list(_db.findUpgradeNamesByGlobalIDAndType(globalID, UPGRADE_TYPE.TURRET))
        self.__setupPilot(settings, aircraftConfiguration, pilotUpgradeId)
        player = BigWorld.player()
        if player.id == avatarID:
            player.weaponsInfo = buildAndGetWeaponsInfo(settings.components.weapons2, aircraftConfiguration.weaponSlots)
        return DestructibleObjectFactory.createControllers(avatarID, settings, settings.airplane, aircraftConfiguration.partTypes, partStates, aircraftConfiguration.weaponSlots, callback=partial(self.__onAvatarModelLoaded, player.id == avatarID), camouflage=camouflage, decals=decals, turretsName=turretNames)

    def __convertServerTeamDataToOwnClientTeamData(self, data):
        ownerTeamIndex = BigWorld.player().teamIndex
        return (data[ownerTeamIndex], data[1 - ownerTeamIndex])

    def __onUpdateTeamSuperiorityPoints(self, argStr):
        score = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        ownScore, enemyScore = self.__convertServerTeamDataToOwnClientTeamData(score)
        self.onUpdateTeamSuperiorityPoints(self.superiorityPoints, ownScore, enemyScore)
        self.superiorityPoints[0], self.superiorityPoints[1] = ownScore, enemyScore

    def __onReceiveTurretBoosterInfo(self, argStr):
        teamIndex = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onUpdateTurretBoosterInfo(teamIndex == BigWorld.player().teamIndex)

    def __onUpdateDominationPrc(self, argStr):
        basesPrc = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.dominationPrc[0], self.dominationPrc[1] = self.__convertServerTeamDataToOwnClientTeamData(basesPrc)
        self.onUpdateDominationPrc(self.dominationPrc)

    def __onReportBattleResult(self, argStr):
        clientBattleResult = translateDictThroughAnother(wgPickle.loads(wgPickle.FromServerToClient, argStr), REPORT_BATTLE_RESULT_KEYS_INVERT_DICT)
        self.onReportBattleResult(clientBattleResult)

    def __onReceiveVOIPChannelCredentials(self, argStr):
        name, teamMembers = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onReceiveVOIPChannelCredentials(name, teamMembers)

    def vehiclesLoadStatus(self):
        return [self.avatarModelLoaded, len(self.avatarInfos)]

    def __onAvatarModelLoaded(self, isPlayer):
        self.avatarModelLoaded += 1
        if isPlayer:
            BigWorld.player().onModelLoadedIntoWorld()

    def doUpdateArena(self, functionIndex, updateFunctionID, argStr):
        if functionIndex == self.__lastUpdateFunctionIndex + 1:
            self.__lastUpdateFunctionIndex += 1
            self.update(updateFunctionID, argStr)
            if self.__waitingUpdateFunctionsPool:

                def filterPool():
                    indexes = self.__waitingUpdateFunctionsPool.keys()
                    indexes.sort()
                    for i in indexes:
                        if i == self.__lastUpdateFunctionIndex + 1:
                            self.__lastUpdateFunctionIndex += 1
                            try:
                                fID, fArgs = self.__waitingUpdateFunctionsPool[i]
                                self.update(fID, fArgs)
                            except Exception as msg:
                                print msg

                        else:
                            yield (i, self.__waitingUpdateFunctionsPool[i])

                self.__waitingUpdateFunctionsPool = dict(filterPool())
        else:
            self.__waitingUpdateFunctionsPool[functionIndex] = (updateFunctionID, argStr)

    def getAvatarInfoByName(self, name):
        for avatarInfo in self.avatarInfos.values():
            if avatarInfo['playerName'] == name:
                return avatarInfo

        return None

    def getAvatarInfo(self, avatarID):
        return self.avatarInfos.get(avatarID, None)

    def getSortedAvatarsIDs(self):
        return self.__sortedAvatarsIDs

    def getSortedAvatarInfosList(self):
        if self.isAllServerDataReceived():
            sortedList = list()
            for ids in self.__sortedAvatarsIDs.values():
                sortedList.extend(ids)

            return [ self.avatarInfos[id] for id in sortedList ]
        return [ avatarInfo for avatarInfo in self.avatarInfos.values() ]

    def getWaterLevel(self):
        if self.arenaData is None:
            LOG_WARNING('getWaterLevel - water level set as default value = 0.0')
            return 0.0
        else:
            return self.arenaData['waterLevel']

    def __onGameResultChanged(self, argStr):
        gameResult, winState = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onGameResultChanged(gameResult, winState)

    def onBattleUILoaded(self):
        self.__isBattleUILoaded = True

    def isLoaded(self):
        return self.__isBattleUILoaded

    def getSuperiorityPoints4TeamObject(self, teamObjectID):
        mapEntry = self.getMapEntry(teamObjectID)
        if mapEntry is not None:
            return (mapEntry.superiorityPoints, mapEntry.superiorityPointsMax)
        else:
            LOG_WARNING('getSuperiorityPoints4TeamObject - team object not in MapEntry table', teamObjectID)
            return (None, None)

    def __decSuperiorityPoints4TeamObject(self, teamObjectID, points):
        if not points:
            LOG_DEBUG('__decSuperiorityPoints4TeamObject - points = 0', teamObjectID, points)
            return
        else:
            mapEntry = self.getMapEntry(teamObjectID)
            if mapEntry is not None:
                mapEntry.superiorityPoints -= points
            else:
                LOG_WARNING('__decSuperiorityPoints4TeamObject - team object not in MapEntry table', teamObjectID, points)
            return

    def __onTeamObjectPartGroupDestroyed(self, argStr):
        for teamObjectID, points, killerID in wgPickle.loads(wgPickle.FromServerToClient, argStr):
            self.__decSuperiorityPoints4TeamObject(teamObjectID, points)
            self.onTeamObjectPartGroupChanged(killerID, teamObjectID, points)

    def __onScenarioSetIcon(self, argStr):
        groupName, iconIndex, textID, temaIndex = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onScenarioSetIcon(groupName, iconIndex, textID, temaIndex)

    def __onScenarioSetText(self, argStr):
        textID, colorID = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        self.onScenarioSetText(textID, colorID)

    def __onDebugInfoReceived(self, argStr):
        from Math import Matrix, Vector3
        positions = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        for planeID, pos in positions:
            m = Matrix()
            m.setTranslate(pos)
            BigWorld.addPoint('spawnPoint%d' % planeID, m, 4278190335L, False)

    def __onEconomicExtPlayersData(self, argStr):
        avatarID, economics = wgPickle.loads(wgPickle.FromServerToClient, argStr)
        avatarInfo = self.avatarInfos[avatarID]
        avatarInfo['economics'] = economics
        self.onPlayerEconomicExtDataReceived(avatarID)

    def __onPlaneTypeRankUpdated(self, payload):
        avatarID, rankData, bestRankPlaneID = wgPickle.loads(wgPickle.FromServerToClient, payload)
        avatarInfo = self.avatarInfos[avatarID]
        oldRankData = avatarInfo['planeTypeRank']
        avatarInfo['planeTypeRank'] = rankData
        avatarInfo['bestRankPlaneID'] = bestRankPlaneID
        for planeType, rankID in avatarInfo['planeTypeRank'].iteritems():
            oldRankID = oldRankData[planeType]
            if oldRankID != rankID:
                self.onAvatarPlaneTypeRankChanged(avatarID, planeType, oldRankID, rankID)