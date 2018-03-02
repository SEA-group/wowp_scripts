# Embedded file name: scripts/common/db/DBAreaConquest/SectorModel.py
from consts import SECTOR_GEOMETRY_TYPE, SECTOR_GAMEPLAY_TYPE
from db.DBHelpers import findSection
from db.DBModel.DBProperty import DBStringProperty, DBModelProperty
from debug_utils import LOG_WARNING
from SectorPresetModel import SectorPresetModel, SectorHudBaseModel, PRESET_KEY
from SectorGeometry import SectorGeometryCircle, SectorGeometryPolygon
from BomberDispatcherModel import BomberDispatcherModel
from RocketV2Model import RocketV2Model
from GameModeSettings.ACSettings import SECTOR_BONUS_TYPE

class SectorHudModel(SectorHudBaseModel):
    """HUD settings container
    """
    markerPointName = DBStringProperty(sectionName='markerPoint')

    def __init__(self):
        super(SectorHudModel, self).__init__()
        self.markerPoint = None
        return

    def convertPoints(self, provider):
        self.markerPoint = provider(self.markerPointName)


class SectorModel(SectorPresetModel):
    """Static sector settings container
    """
    positionPointName = DBStringProperty(sectionName='positionPoint')
    hudSettings = DBModelProperty(factory=SectorHudModel, sectionName='hud')
    rocketV2 = DBModelProperty(factory=RocketV2Model)
    bomberDispatcher = DBModelProperty(factory=BomberDispatcherModel)

    def __init__(self, gameModeDir):
        super(SectorModel, self).__init__(gameModeDir)
        self.ident = ''
        self.effects = {}
        self.positionPoint = None
        self.presetName = ''
        return

    @property
    def rocketV2Settings(self):
        """V2 rocket settings
        @rtype: RocketV2Model
        """
        if self.rocketV2.loadedFromDB:
            return self.rocketV2
        else:
            return None

    @property
    def geometry(self):
        """Sector geometry
        @rtype: SectorGeometry.SectorGeometryBase
        """
        return self._geometry

    @property
    def bomberDispatcherSettings(self):
        """Bomber dispatcher settings
        @rtype: BomberDispatcherModel
        """
        if self.bomberDispatcher.loadedFromDB:
            return self.bomberDispatcher
        else:
            return None

    @property
    def bonusType(self):
        """Sector bonus type
        @rtype: basestring
        """
        if self.gameplayType == SECTOR_GAMEPLAY_TYPE.CITADEL:
            return SECTOR_BONUS_TYPE.ROCKET_LAUNCH
        elif self.gameplayType == SECTOR_GAMEPLAY_TYPE.COMMANDCENTER:
            return SECTOR_BONUS_TYPE.AIR_STRIKE
        else:
            return SECTOR_BONUS_TYPE.POINTS

    def read(self, section):
        super(SectorModel, self).read(section)
        self._readGeometryData(section)
        if section.has_key(PRESET_KEY):
            self.presetName = section[PRESET_KEY].asString

    def convertPoints(self, provider):
        self.geometry.convertPoints(provider)
        self.positionPoint = provider(self.positionPointName) if self.positionPointName else self.geometry.position
        self.hudSettings.convertPoints(provider)
        if self.rocketV2Settings:
            self.rocketV2Settings.convertPoints(provider)

    def _readGeometryData(self, section):
        """Read geometry data from section and create corresponding geometry instance
        @type section: ResMgr.DataSection
        """
        if section.has_key('type'):
            geometryType = section['type'].asString
        else:
            geometryType = SECTOR_GEOMETRY_TYPE.POLYGON
            LOG_WARNING('Type section not found for {0}, using polygon'.format(self.ident))
        if not geometryType in SECTOR_GEOMETRY_TYPE.ALL:
            raise AssertionError('Wrong sector geometry type: {0}, valid values: {1}'.format(geometryType, SECTOR_GEOMETRY_TYPE.ALL))
            vertexes = findSection(section, 'sectorVertexes').readStrings('vertex')
            position = geometryType == SECTOR_GEOMETRY_TYPE.CIRCLE and vertexes[0]
            radius = section['radius'].asFloat
            self._geometry = SectorGeometryCircle(position, radius)
        else:
            self._geometry = SectorGeometryPolygon(vertexes)

    @property
    def isBase(self):
        return self.gameplayType == SECTOR_GAMEPLAY_TYPE.SPAWNPOINT

    @property
    def isFreeZone(self):
        return self.gameplayType == SECTOR_GAMEPLAY_TYPE.NEUTRAL