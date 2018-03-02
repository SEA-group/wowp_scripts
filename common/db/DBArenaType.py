# Embedded file name: scripts/common/db/DBArenaType.py
import copy
import math
import ResMgr
from db.DBAreaConquest.Hud.ACHudSector import ACHudSector
from debug_utils import *
from consts import IS_CLIENT, IS_BASEAPP, CAMOUFLAGE_ARENA_TYPE, ARENA_TYPE, LANDSCAPE_PATH
from DBHelpers import readValue, readDataWithDependencies, findSection
from Curve import Curve
from DBObjectGroups import ObjectGroups
from DBSoundsStingers import SoundsStingers
from ArenaObjects import ArenaObjects, OBJECT_IDENT_EMPTY
from DBBaseClass import DBBaseClass
from DBSpawnGroup import DBSpawnGroup
from DBAreaConquest import Sectors
from DBAreaConquest.GMSettings.ArenaGameModeSettingsModel import ArenaGameModeSettingsModel
from consts import GAME_MODE, GAME_MODE_PATH_NAMES
if IS_CLIENT:
    from Helpers import i18n

class ArenaType(DBBaseClass):

    def __init__(self, typeID, fileName, data, isArenaHidden = False):
        DBBaseClass.__init__(self, typeID, fileName)
        self.settings, self.geometry, self.geometryName, self.spaceBoundsNames = self.readGeometryData(data)
        self.__arenaObjects = ArenaObjects(self.geometryName, self.spaceBoundsNames)
        self.__bounds = None
        self._textureMaterials = {}
        self.sectors = Sectors.Sectors()
        self.__isArenaHidden = isArenaHidden
        self._gameModeSettings = None
        if IS_BASEAPP:
            self.objectGroups = ObjectGroups()
        if IS_CLIENT:
            self._loadTextureMaterials(self.geometry)
            self.offlineObjectGroups = ObjectGroups()
        readDataWithDependencies(self, data, 'arena_defs')
        self.camouflageArenaTypeID = CAMOUFLAGE_ARENA_TYPE.getValueByName(self.camouflageArenaType)
        if not self.camouflageArenaTypeID:
            self.__raiseWrongXml("wrong 'camouflageArenaType' value %s" % self.camouflageArenaType)
        if IS_BASEAPP:
            import _battle_entry_points
            if not self.battleEntryPoint or not all((battleEntryPoint in _battle_entry_points.EntryPoints for battleEntryPoint in self.battleEntryPoint)):
                self.__raiseWrongXml("wrong 'battleEntryPoint' value")
        return

    @property
    def isArenaHidden(self):
        return self.__isArenaHidden

    @property
    def bounds(self):
        return self.__bounds

    @property
    def arenaObjects(self):
        return self.__arenaObjects

    @property
    def spawnGroupDescription(self):
        try:
            return self.__spawnGroupDescription
        except:
            LOG_ERROR("Can't find spawnGroup for arena", self.typeName)

    @property
    def gameModeSettings(self):
        """Game mode settings container
        @rtype: ArenaGameModeSettings.ArenaGameModeSettings
        """
        return self._gameModeSettings

    def getTeamObjectData(self, objID):
        return self.__arenaObjects.getTeamObjectData(objID)

    def __parseBounds(self, geometry):
        terrain = ResMgr.openSection(geometry + '/terrain.xml/terrain', False)
        if terrain:
            numChunks = terrain.readInt('numChunks', 1)
            numChunksPerSide = math.sqrt(numChunks)
            maxX = numChunksPerSide / 2
            maxY = numChunksPerSide / 2
            minX = -1 * maxX
            minY = -1 * maxY
            maxX = maxX - (1 - numChunksPerSide % 2)
            maxY = maxY - (1 - numChunksPerSide % 2)
            normalize = lambda x: x * 100.0
            self.__bounds = ((normalize(minX), normalize(minY)), (normalize(maxX), normalize(maxY)))

    def __parseSpaceScripts(self, settings):
        scriptsSection = ResMgr.openSection(settings + '/spaceScripts', False)
        if scriptsSection:
            self.spaceScripts = scriptsSection.readStrings('scrips')
        else:
            self.spaceScripts = ()

    def readData(self, data):
        if not data:
            return
        else:
            for propName in ['exclusiveGameMods', 'excludeArenaType']:
                propData = findSection(data, propName)
                if propData:
                    setattr(self, propName, set([ ARENA_TYPE.getValueByName(k) for k in propData.keys() ]))
                else:
                    setattr(self, propName, set())

            spawnGroupData = findSection(data, 'spawnGroup')
            if spawnGroupData:
                self.__spawnGroupDescription = DBSpawnGroup(spawnGroupData)
            readValue(self, data, 'gameType', 'SaD')
            gameModeEnum = GAME_MODE.NAME_TO_MODE.get(self.gameType, GAME_MODE.AREA_CONQUEST)
            self._readGameModeSettings(data)
            sectorData = findSection(data, 'sectors')
            if sectorData:
                self.sectors.fillSectorData(sectorData, GAME_MODE_PATH_NAMES.MODE_TO_PATH[gameModeEnum])
                self.sectors.convertPoints(self.arenaObjects.getPointPosition)
            if IS_CLIENT:
                self._readHudSectorsSettings(data)
            readValue(self, data, 'camouflageArenaType', '')
            readValue(self, data, 'hudIcoPath', '')
            self.__parseBounds(self.geometry)
            self.__parseSpaceScripts(self.settings)
            readValue(self, data, 'minPlayersInTeam', 0)
            self.trainingRoomIcoPathSelected = data.readString('trainingRoomIcoPath/selected', '')
            self.trainingRoomIcoPathUnselected = data.readString('trainingRoomIcoPath/unselected', '')
            self.trainingRoomIcoPathPreview = data.readString('trainingRoomIcoPath/preview', '')
            self.trainingRoomIcoPathPreviewBig = data.readString('trainingRoomIcoPath/previewBig', '')
            readValue(self, data, 'trainingRoomDescription', '')
            if self.minPlayersInTeam < 0:
                self.__raiseWrongXml("wrong 'minPlayersInTeam' value")
            readValue(self, data, 'maxPlayersInTeam', 0)
            if self.maxPlayersInTeam < 0:
                self.__raiseWrongXml("wrong 'maxPlayersInTeam' value")
            if self.maxPlayersInTeam < self.minPlayersInTeam:
                self.__raiseWrongXml("'maxPlayersInTeam' value < 'minPlayersInTeam' value")
            readValue(self, data, 'roundLength', 0)
            if self.roundLength < 0:
                self.__raiseWrongXml("wrong 'roundLength' value")
            bottomLeft = data.readVector2('boundingBox/bottomLeft')
            upperRight = data.readVector2('boundingBox/upperRight')
            if bottomLeft[0] >= upperRight[0] or bottomLeft[1] >= upperRight[1]:
                LOG_UNEXPECTED("wrong 'boundingBox' values", self.typeName)
            self.boundingBox = (bottomLeft, upperRight)
            readValue(self, data, 'isPvEReady', True)
            readValue(self, data, 'visibleEnable', 1)
            readValue(self, data, 'minPlayerCount', 0)
            readValue(self, data, 'selectionPriority', 0)
            readValue(self, data, 'minAircraftLevel', 1)
            readValue(self, data, 'maxAircraftLevel', 10)
            readValue(self, data, 'sunAngle', 70.0)
            readValue(self, data, 'daytime', 8.31)
            readValue(self, data, 'sunStealthFactor', Curve())
            readValue(self, data, 'cloudStealthFactorDistance', 120.0)
            readValue(self, data, 'seaLevelForFlightMdel', 0.0)
            readValue(self, data, 'altitudeMap', 0.0)
            readValue(self, data, 'anyTeamObjectsCount', 5)
            readValue(self, data, 'randomObjectsCount', 5)
            visualScripts = findSection(data, 'visualScripts')
            if visualScripts:
                self.arenaScripts = visualScripts.readStrings('scripts')
            else:
                self.arenaScripts = ()
            if IS_CLIENT:
                readValue(self, data, 'name', '')
                readValue(self, data, 'secondName', ' @ NEED LOCALE ')
                readValue(self, data, 'trainingRoomName', '')
                readValue(self, data, 'trainingRoomSecondName', '')
                readValue(self, data, 'description', '')
                readValue(self, data, 'outroScenario', '')
                readValue(self, data, 'outroTimeline', '')
                readValue(self, data, 'music', '')
                readValue(self, data, 'musicPrefix', '')
                readValue(self, data, 'ambientSound', '')
                readValue(self, data, 'umbraEnabled', 0)
                readValue(self, data, 'batchingEnabled', 0)
                stingersSection = findSection(data, 'stingers')
                self.stingers = SoundsStingers(stingersSection) if stingersSection else None
                self.waterTexScale = data.readFloat('water/texScale', 0.5)
                self.waterFreqX = data.readFloat('water/freqX', 1.0)
                self.waterFreqZ = data.readFloat('water/freqZ', 1.0)
            if IS_BASEAPP:
                readValue(self, data, 'kickAfterFinishWaitTime', 0)
                readValue(self, data, 'battleEntryPoint', '', True)
                if self.kickAfterFinishWaitTime < 0:
                    self.__raiseWrongXml("wrong 'kickAfterFinishWaitTime' value")
                readValue(self, data, 'arenaStartDelay', 0)
                if self.arenaStartDelay <= 0:
                    self.__raiseWrongXml("wrong 'arenaStartDelay' value")
                groups = findSection(data, 'objectGroups')
                if groups:
                    for groupID, groupData in groups.items():
                        self.objectGroups.addGroup(groupID, groupData)

                selectGroups = findSection(data, 'selectGroups')
                if selectGroups:
                    self.objectGroups.readSpawnSequence(selectGroups)
            if IS_CLIENT:
                weatherPath = self.settings + '/weatherSettings/'
                weatherData = ResMgr.openSection(weatherPath)
                if weatherData:
                    self.weatherWindSpeed = weatherData.readVector2('windSpeed')
                    self.weatherWindGustiness = weatherData.readFloat('windGustiness', 0.0)
                    ResMgr.purge(weatherPath)
                else:
                    self.weatherWindSpeed = (0.0, 0.0)
                    self.weatherWindGustiness = 0.0
                groups = findSection(data, 'objectGroups')
                if groups:
                    for groupID, groupData in groups.items():
                        self.offlineObjectGroups.addGroup(groupID, groupData)

                selectGroups = findSection(data, 'selectGroups')
                if selectGroups:
                    self.offlineObjectGroups.readSpawnSequence(selectGroups)
            return

    def _loadTextureMaterials(self, geometry):
        path = geometry + '/textures_materials.xml'
        materials = ResMgr.openSection(path)
        if materials is None:
            DBLOG_ERROR('ArenaType: _loadTextureMaterials: unknown materials ({p})'.format(p=path))
            return
        else:
            self._textureMaterials = {v['texture_layer'].asInt - 1:v['material_id'].asInt for v in materials.values()}
            ResMgr.purge(path)
            return

    def getTextureMaterialID(self, textureIndex):
        return self._textureMaterials.get(textureIndex)

    @staticmethod
    def readGeometryData(section):
        """Reads geometry name and space bounds idents from data section
        @type section: ResMgr.DataSection
        @return: Geometry path, geometry name, space bounds idents
        @rtype: (basestring, basestring, (basestring, basestring))
        """
        settings = section['space'].asString
        LOG_INFO('readGeometryData: settings = ', settings)
        settings_section = ResMgr.openSection(settings)
        LOG_INFO('readGeometryData: settings_section = ', settings_section)
        geometryPath = settings_section['geometry'].asString
        LOG_INFO('readGeometryData: geometry = ', geometryPath)
        geometryName = geometryPath.rsplit('/')[-1]
        boundsNames = (OBJECT_IDENT_EMPTY, OBJECT_IDENT_EMPTY)
        if section.has_key('spaceBounds'):
            boundsNames = section['spaceBounds'].readStrings('vertex') or boundsNames
        boundsCount = len(boundsNames)
        raise boundsCount == 2 or AssertionError('Expected 2 SpaceBound, {0} got: {1}'.format(boundsCount, boundsNames))
        return (settings,
         geometryPath,
         geometryName,
         boundsNames)

    def _readGameModeSettings(self, data):
        self._gameModeSettings = ArenaGameModeSettingsModel()
        section = findSection(data, 'gameModeSettings')
        if section:
            self._gameModeSettings.read(section)

    if IS_CLIENT:

        def _readHudSectorsSettings(self, data):
            self._hudSector = ACHudSector(data)

        @property
        def hudSector(self):
            """hud sectors Settings
            @rtype: ACHudSector
            """
            return self._hudSector

    def __raiseWrongXml(self, msg):
        raise Exception, "wrong arena type XML '%s': %s" % (self.typeID, msg)