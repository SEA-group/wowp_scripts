# Embedded file name: scripts/common/db/DBAreaConquest/BomberDispatcherModel.py
import collections
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBPropertyBase

class BomberDispatcherPresetModel(DBModelBase):
    """Bomber dispatcher preset settings container
    """
    bombersInPool = DBIntProperty()
    launchTickPeriod = DBIntProperty()


SplineSettings = collections.namedtuple('SplineSettings', ['name', 'teamIndex', 'actionPointIndex'])

class SectorInfluenceSettings(object):
    """Influence on sector
    @type sectorIdent: basestring
    @type splinesByTeams: dict[int, SplineSettings]
    """

    def __init__(self, sectorIdent):
        self.sectorIdent = sectorIdent
        self.splinesByTeams = {}

    def addSpline(self, settings):
        """Add spline settings
        @type settings: SplineSettings
        """
        self.splinesByTeams[settings.teamIndex] = settings


class InfluenceProperty(DBPropertyBase):
    """Custom property to read sector influence
    """

    def _doRead(self, section):
        result = {}
        for child in _iterChildren(section, 'target'):
            sectorInfluence = _readTargetSection(child)
            result[sectorInfluence.sectorIdent] = sectorInfluence

        return result


class BomberDispatcherModel(BomberDispatcherPresetModel):
    """Bomber dispatcher settings container
    """
    influenceBySectors = InfluenceProperty(sectionName='influence')


def _readTargetSection(section):
    """Read <target> section
    @type section: ResMgr.DataSection
    @rtype: SectorInfluenceSettings
    """
    sectorInfluence = SectorInfluenceSettings(sectorIdent=section['sector'].asString)
    for name, teamIndex, actionPointIndex in _readSplinesData(section):
        sectorInfluence.addSpline(SplineSettings(name, teamIndex, actionPointIndex))

    return sectorInfluence


def _readSplinesData(section):
    """Read splines from data section
    @type section: ResMgr.DataSection
    @rtype: __generator[(basestring, int, int)]
    """
    for child in _iterChildren(section, 'spline'):
        teamIndex = child['teamIndex'].asInt
        splineName = child['name'].asString
        actionPointIndex = child['actionPointIndex'].asInt
        yield (splineName, teamIndex, actionPointIndex)


def _iterChildren(section, name):
    """Iter through subsections with specified names
    @type section: ResMgr.DataSection
    @type name: basestring
    @rtype: __generator[ResMgr.DataSection]
    """
    for sectionName, child in section.items():
        if name == sectionName:
            yield child