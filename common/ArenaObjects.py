# Embedded file name: scripts/common/ArenaObjects.py
from collections import namedtuple
import Math
import ResMgr
from consts import GAME_MODE, WORLD_SCALING
from debug_utils import *
from zlib import crc32
from EntityHelpers import PLANE_TYPE_LETTER, ENTITY_GROUPS_SET
from TeamObjectGroup import createTeamObjectsGroups
OBJECT_IDENT_EMPTY = ''
SimplePoint = namedtuple('SimplePoint', 'position groupName actualModes')

class ArenaObjects:
    __onSectionHandlers = {'SpawnPoint': {'dataReadingHandler': '_ArenaObjects__addSpawnGroup'},
     'BasePoint': {'dataReadingHandler': '_ArenaObjects__addTeamBase',
                   'editorClassName': 'TeamObject'},
     'SpaceBound': {'dataReadingHandler': '_ArenaObjects__addSpaceBound'},
     'WaterLevel': {'dataReadingHandler': '_ArenaObjects__addWaterLevel'},
     'TriggerPoint': {'dataReadingHandler': '_ArenaObjects__addTrigger',
                      'editorClassName': 'EventTrigger'},
     'SimplePoint': {'dataReadingHandler': '_ArenaObjects__addSimplePoint'}}
    CHUNK_SIZE = 100.0

    def __init__(self, spaceFileName, spaceBoundsNames):
        self.__spaceFileName = spaceFileName
        self.__spaceBoundsNames = spaceBoundsNames
        self.__spawnGroups = []
        self.__teamObjects = []
        self.__uniqueGUIDs = set()
        self.__bomberStartPoints = []
        self.__bomberEndPoints = []
        self.__triggers = []
        self.__bomberPoints = [{}, {}]
        self.__bounds = []
        self.__waterLevel = None
        self.__simplePoints = {}
        path = 'spaces/' + spaceFileName + '/gameobjects/defaults.xml'
        fileData = ResMgr.openSection(path)
        if fileData:
            for chunkData in fileData.values():
                metaData = chunkData.has_key('meta') and chunkData['meta'] or None
                chunkPos = Math.Vector3()
                if metaData:
                    chunkPos = Math.Vector3(metaData.readInt('x') * self.CHUNK_SIZE, 0, metaData.readInt('z') * self.CHUNK_SIZE)
                for id, section in chunkData.items():
                    if id == 'UserDataObject':
                        entityType = section.readString('type')
                        matrix = section.readMatrix('transform')
                        matrix.translation += chunkPos
                        description = self.__onSectionHandlers.get(entityType, None)
                        if description:
                            getattr(self, description['dataReadingHandler'])(section, matrix, description.get('editorClassName', None))

            ResMgr.purge(path, True)
            self.__fixBounds()
            self.__check()
            self.__teamObjectsCheckSum = crc32(''.join((obj['guid'] for obj in self.__teamObjects)))
        else:
            LOG_ERROR("Can't find file", path)
        for i, t in enumerate(self.__teamObjects):
            t['arenaObjID'] = i

        self.__teamObjectsGroups = createTeamObjectsGroups(self.__teamObjects)
        return

    @property
    def teamObjectsGroups(self):
        """
        :rtype: list[TeamObjectGroup.TeamObjectGroup]
        """
        return self.__teamObjectsGroups

    @property
    def teamObjectsCheckSum(self):
        return self.__teamObjectsCheckSum

    @property
    def waterLevel(self):
        return self.__waterLevel

    @property
    def spawnGroups(self):
        return self.__spawnGroups

    @property
    def bounds(self):
        return self.__bounds

    @property
    def simplePoints(self):
        return self.__simplePoints

    def getPointPosition(self, ident):
        if ident in self.simplePoints:
            return self.simplePoints[ident].position
        LOG_ERROR('There is no SimplePoint with ident: ', ident)

    def getTeamObjectData(self, objIndex):
        if 0 <= objIndex < len(self.__teamObjects):
            return self.__teamObjects[objIndex]
        else:
            LOG_ERROR('Invalid TeamObject index', objIndex, 'for space', self.__spaceFileName)
            return None
            return None

    def getFilteredTeamObjects(self, gameMode, battleLevel, generatedGroups):

        def generateFilteredList():
            for objID, record in enumerate(self.__teamObjects):
                editorClassName = record['editorClassName']
                record['teamID'] == -1 and LOG_WARNING('ignore object without teamIndex', record)
                continue
                if generatedGroups and not generatedGroups.getGroupData(record['groupName']):
                    pass
                elif editorClassName != 'TeamObject':
                    LOG_WARNING('Unsupported entity class name', editorClassName)
                else:
                    yield (objID, record)

        return dict(generateFilteredList())

    def getFilteredTriggers(self, gameMode):

        def generateFilteredList():
            for objID, record in enumerate(self.__triggers):
                if gameMode in record['actualModes']:
                    yield (objID, record)

        return dict(generateFilteredList())

    def __fixBounds(self):
        if not len(self.__bounds) == 2:
            raise AssertionError('There is error in bounds len, self.__bounds: {0}'.format(self.__bounds))
            minBound, maxBound = self.__bounds
            if minBound.x > maxBound.x:
                maxBound.x, minBound.x = minBound.x, maxBound.x
            maxBound.z, minBound.z = minBound.z > maxBound.z and minBound.z, maxBound.z
        self.__bounds = [minBound, maxBound]

    def __check(self):
        if not self.__teamObjects:
            LOG_WARNING('No one team object (Turret, Cannon, BasePoint etc) was found in the space')
        if not self.__spawnGroups:
            LOG_ERROR('Spawn groups were not found in the space')
        if len(self.__bounds) < 2:
            LOG_ERROR('Error there is not enough SpaceBound in the space')
        if self.__waterLevel is None:
            LOG_WARNING('waterLevel entity was not found in the space or has client only attribute')
            self.__waterLevel = 0
        return

    def __addSpawnGroup(self, section, matrix, editorClassName = None):
        properties = section['properties']
        prioritiesRaw = properties.readString('aircraftClassPriorities', 'A N F H').split(' ')
        priorities = [ PLANE_TYPE_LETTER[c] for c in prioritiesRaw if c != '' and c in PLANE_TYPE_LETTER ]
        self.__spawnGroups.append(dict(pos=matrix.applyToOrigin(), yaw=matrix.yaw, teamID=properties.readInt('teamID', 0), battleLevels=self.__readListOfIntsFromStringProperty('battleLevels', properties, None), flightSpline=properties.readString('flightSpline', ''), cameraPreset=properties.readString('cameraPreset', ''), aircraftClassPriorities=priorities, sectorName=properties.readString('sectorName', ''), defenderOnly=properties.readInt('defenderOnly', 0)))
        return

    def __addWaterLevel(self, section, matrix, editorClassName = None):
        pos = matrix.applyToOrigin()
        self.__waterLevel = pos.y

    def __addTrigger(self, section, matrix, editorClassName):

        def parseEntityGroups(entityGroups):
            res = 0
            for group in entityGroups.split(','):
                if not group:
                    continue
                try:
                    group = 1 << int(group)
                    if group in ENTITY_GROUPS_SET:
                        res |= group
                    else:
                        LOG_ERROR('Invalid entity group: ', group)
                except:
                    LOG_ERROR('Invalid entity groups: ', entityGroups)

            return res

        guid = section['guid'].asString
        if guid in self.__uniqueGUIDs:
            LOG_ERROR('Duplicate guid found', guid)
        else:
            self.__uniqueGUIDs.add(guid)
            properties = section['properties']
            self.__triggers.append(dict(pos=matrix.applyToOrigin(), r=properties.readInt('r') * WORLD_SCALING, h=properties.readInt('h') * WORLD_SCALING, objectsForEvent=properties.readInt('objectsForEvent', 1), event=properties.readString('event'), teamId=properties.readInt('teamId', 2), groupId=properties.readString('groupId'), DsName=properties.readString('DsName'), entityGroups=parseEntityGroups(properties.readString('entityGroups')), actualModes=self.__readListOfIntsFromStringProperty('actualModes', properties, [GAME_MODE.AREA_CONQUEST]), guid=guid, tag=properties.readInt('tag', 0)))

    def __addTeamBase(self, section, matrix, editorClassName):
        self.__addTeamObject(editorClassName, section, matrix, [GAME_MODE.AREA_CONQUEST])

    def __addTeamObject(self, editorClassName, section, matrix, defaultModes):
        guid = section['guid'].asString
        if guid in self.__uniqueGUIDs:
            LOG_ERROR('Duplicate guid found', guid)
        else:
            self.__uniqueGUIDs.add(guid)
            properties = section['properties']
            customLabel = section.asString
            modes = self.__readListOfIntsFromStringProperty('actualModes', properties, defaultModes)
            battleLevels = self.__readListOfIntsFromStringProperty('battleLevels', properties, [ i for i in xrange(1, 11) ])
            self.__teamObjects.append(dict(matrix=matrix, teamID=properties.readInt('teamID', 0), actualModes=modes, modelID=properties.readString('modelID', 'default'), groupName=properties.readString('groupName', 'default'), movementStrategyName=properties.readString('movementStrategyName', '').lower(), movementStrategyDataPath=properties.readString('movementStrategyDataPath', ''), movementStrategyStartPosPrc=properties.readFloat('movementStrategyStartPosPrc', 0.0), respawnTime=properties.readFloat('respawnTime', 0.0), battleLevels=battleLevels, editorClassName=editorClassName, turretBooster=properties.readInt('turretBooster', 0), isBigObject=properties.readInt('isBigObject', 0) != 0, scenarioName=properties.readString('scenarioName', ''), DsName=properties.readString('DsName', ''), label=customLabel, guid=guid, ACType=properties.readInt('ACType', 0)))

    def __readListOfIntsFromStringProperty(self, propertyID, properties, defaultValues):
        propertyValueStr = properties.readString(propertyID, '')
        if propertyValueStr != '':
            return map(lambda sMode: int(sMode), propertyValueStr.split(','))
        else:
            return defaultValues

    def __addSpaceBound(self, section, matrix, editorClassName = None):
        name = section['properties'].readString('ident') or OBJECT_IDENT_EMPTY
        if name in self.__spaceBoundsNames:
            position = matrix.applyToOrigin()
            self.__bounds.append(position)

    def __processBomberPoints(self):
        d = [{}, {}]
        validTeamIndexes = [0, 1]
        for sp in self.__bomberStartPoints:
            teamID = sp['teamID']
            if teamID in validTeamIndexes:
                team = d[teamID]
                index = sp['index']
                if index in team:
                    LOG_WARNING('IGNORE bomberStartPoint with the same index {i} in team {t}'.format(i=index, t=teamID))
                else:
                    team[index] = {'startPoint': sp['pos'],
                     'rotation': (0, 0, sp['yaw'])}
            else:
                LOG_WARNING('IGNORE bomberStartPoint with invalid teamID {id}'.format(id=teamID))

        for ep in self.__bomberEndPoints:
            teamID = ep['teamID']
            if teamID in validTeamIndexes:
                team = d[teamID]
                index = ep['index']
                if index not in team:
                    LOG_WARNING('IGNORE bomberEndPoint with index {i} which has no start point pair in team {t}'.format(i=index, t=teamID))
                elif 'endPoint' in team[index]:
                    LOG_WARNING('IGNORE bomberEndPoint with index {i} which is duple in team {t}'.format(i=index, t=teamID))
                else:
                    team[index]['endPoint'] = ep['pos']
            else:
                LOG_WARNING('IGNORE bomberEndPoint with invalid teamID {id}'.format(id=teamID))

        for teamID, teamData in enumerate(d):
            for key, pairData in teamData.items():
                if 'endPoint' not in pairData:
                    LOG_WARNING('IGNORE bomberEndPoint with index {i} which has no end point pair in team {t}'.format(i=key, t=teamID))
                else:
                    self.__bomberPoints[teamID][key] = pairData

        if len(self.__bomberPoints[0]) != len(self.__bomberPoints[1]):
            LOG_WARNING('There is different count of bomber point pairs for each team', self.__bomberPoints)

    def __addSimplePoint(self, section, matrix, editorClassName = None):
        defaultModes = [GAME_MODE.AREA_CONQUEST]
        guid = section['guid'].asString
        if guid in self.__uniqueGUIDs:
            LOG_ERROR('Duplicate guid found', guid)
        else:
            self.__uniqueGUIDs.add(guid)
            properties = section['properties']
            modes = self.__readListOfIntsFromStringProperty('actualModes', properties, defaultModes)
            ident = properties.readString('ident')
            groupName = properties.readString('groupName', 'default')
            self.__simplePoints[ident] = SimplePoint(matrix.applyToOrigin(), groupName, modes)