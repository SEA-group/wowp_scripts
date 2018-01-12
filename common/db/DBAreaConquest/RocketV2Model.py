# Embedded file name: scripts/common/db/DBAreaConquest/RocketV2Model.py
from consts import WORLD_SCALING
from GameModeSettings import ACSettings as DEFAULT_SETTINGS
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBIntProperty, DBWorldScaledProperty, DBStringProperty, DBPropertyBase

class SETTINGS_KEYS:
    """Keys container for data in xml
    """
    SILO = 'silo'
    SILOS = 'silos'
    SECTOR = 'sector'


class RocketV2PresetModel(DBModelBase):
    """Common settings for V2 rocket
    """
    launchTickPeriod = DBIntProperty()
    explosionDamage = DBIntProperty()
    explosionRadius = DBWorldScaledProperty()
    explosionRadiusEffective = DBWorldScaledProperty()
    radius = DBWorldScaledProperty(default=DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.RADIUS * WORLD_SCALING)
    shotHeight = DBWorldScaledProperty(default=DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.SHOT_HEIGHT * WORLD_SCALING)
    ballisticProfileName = DBStringProperty(default=DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.BALLISTIC_PROFILE)


class SectorTargetsProperty(DBPropertyBase):
    """Property to store <sectorTargets> data
    """

    def _doRead(self, section):
        return section.readStrings(SETTINGS_KEYS.SECTOR)


class SilosNamesProperty(DBPropertyBase):
    """Property to store <silos> data
    """

    def _doRead(self, section):
        return section.readStrings(SETTINGS_KEYS.SILO)


class RocketV2Model(RocketV2PresetModel):
    """Sector specific settings for V2 rocket
    """
    silosNames = SilosNamesProperty(sectionName=SETTINGS_KEYS.SILOS)
    sectorTargets = SectorTargetsProperty()

    def __init__(self):
        super(RocketV2Model, self).__init__()
        self._silos = None
        return

    @property
    def silos(self):
        """Silo positions
        @rtype: Math.Vector3
        """
        return self._silos

    def convertPoints(self, provider):
        """Convert points from string idents to Vector3
        @param provider: Point positions provider
        @type provider: (basestring) -> Math.Vector3
        """
        self._silos = map(provider, self.silosNames)