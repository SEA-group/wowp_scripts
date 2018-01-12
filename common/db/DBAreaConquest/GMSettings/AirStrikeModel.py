# Embedded file name: scripts/common/db/DBAreaConquest/GMSettings/AirStrikeModel.py
import math
from db.DBModel.DBModelBase import DBModelBase
from db.DBModel.DBProperty import DBBoolProperty, DBFloatProperty, DBPropertyBase, DBStringProperty, DBIntProperty, DBWorldScaledProperty
from consts import WORLD_SCALING
from GameModeSettings import ACSettings as DEFAULT_SETTINGS

class DBRadiansProperty(DBFloatProperty):

    def _doRead(self, section):
        return math.radians(super(DBRadiansProperty, self)._doRead(section))


class _DBLevelToIntProperty(DBPropertyBase):

    def _doRead(self, section):
        data = {}
        for v in section.values():
            data[v['level'].asInt] = v.asInt

        return data


class _DBLevelToFloatProperty(DBPropertyBase):

    def _doRead(self, section):
        data = {}
        for v in section.values():
            data[v['level'].asInt] = v.asFloat

        return data


class _DBLevelToVector2DictProperty(DBPropertyBase):

    def _doRead(self, section):
        data = {}
        for v in section.values():
            data[v['level'].asInt] = v.readVector2('')

        return data


class AirStrikeModel(DBModelBase):
    """Air strike feature settings model 
    """
    enabled = DBBoolProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.ENABLED)
    globalIDByLevel = _DBLevelToIntProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.GLOBAL_ID_BY_LEVEL)
    bombDamageByLevel = _DBLevelToIntProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.BOMB_DAMAGE_BY_LEVEL)
    firstDropDelayByLevel = _DBLevelToVector2DictProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.FIRST_DROP_DELAY_BY_LEVEL)
    markersDelayByLevel = _DBLevelToFloatProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.MARKERS_AFTER_DROPPING_BOMBS_DURATION)
    bombsLaunchDelayMin = DBFloatProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.BOMBS_LAUNCH_DELAY_MIN)
    bombsLaunchDelayMax = DBFloatProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.BOMBS_LAUNCH_DELAY_MAX)
    ignoreNeutralSectors = DBBoolProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.IGNORE_NEUTRAL_SECTORS)
    scenarioEventName = DBStringProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.SCENARIO_EVENT_NAME)
    maxHPPercent = DBFloatProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.MAX_HP_PERCENT)
    initialHPPercent = DBFloatProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.INITIAL_HP_PERCENT)
    waitTime = DBIntProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.WAIT_TIME)
    wedgeAngle = DBRadiansProperty(default=math.radians(DEFAULT_SETTINGS.BOMBER_SETTINGS.WEDGE_ANGLE))
    splinesInterval = DBWorldScaledProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.SPLINES_INTERVAL * WORLD_SCALING)
    bombersCount = DBIntProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.BOMBERS_COUNT)
    bombingRange = DBWorldScaledProperty(default=DEFAULT_SETTINGS.BOMBER_SETTINGS.BOMBING_RANGE * WORLD_SCALING)