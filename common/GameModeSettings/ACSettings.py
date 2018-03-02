# Embedded file name: scripts/common/GameModeSettings/ACSettings.py
import math
from consts import DEFENDER_TYPE, SECTOR_STATE, PLANE_TYPE, WORLD_SCALING
BATTLE_DURATION = 720
BATTLE_DURATION_DYNAMIC_DEFAULT = -1
ENABLE_IN_TRAINING_ROOM = True
ENABLE_GLOBAL_SHELL_RESPAWN = False
GLOBAL_TICK_PERIOD = 5
SUPERIORITY_GLOBAL_TICK_PERIOD = 1
POINTS_TO_WIN = 700
HOLDING_POINTS_TO_WIN_DEFENCE = 0
HOLDING_POINTS_TO_WIN_OFFENSE = 0
WIN_BY_TIMEOUT = -1
WIN_BY_DYNAMIC_TIMEOUT = -1
ELIMINATION_BY_DEFENCE = False
ELIMINATION_BY_OFFENSE = False
DEFAULT_RESOURCE_POINTS_TO_START = -1
FIGHT_TIME = 5
STOP_WHEN_ONLY_BOTS_LEFT = True

class SHELLS_AUTO_RECHARGE:
    ENABLED = True
    BOMBS_DPS_RATE = 0.01
    ROCKETS_DPS_RATE = 0.015
    CLASS_RATE = {PLANE_TYPE.ASSAULT: 1,
     PLANE_TYPE.FIGHTER: 3,
     PLANE_TYPE.HFIGHTER: 2,
     PLANE_TYPE.NAVY: 1.5,
     PLANE_TYPE.BOMBER: 0.25}
    LEVEL_RATE = {1: 2.0,
     2: 1.8,
     3: 1.55,
     4: 1.3,
     5: 1.1,
     6: 0.95,
     7: 0.8,
     8: 0.69,
     9: 0.58,
     10: 0.5}


class RESPAWN_TYPE:
    TEAM = 'team'
    INDIVIDUAL = 'individual'
    INDIVIDUAL_TL = 'individual_tl'
    ALL = (INDIVIDUAL, INDIVIDUAL_TL, TEAM)


class RESPAWN:
    AVATAR_LIVES = 3
    UNLIMITED = True
    SPAWN_POINT_COOLDOWN = 5
    DEFAULT_TYPE = RESPAWN_TYPE.INDIVIDUAL
    AUTO_RESPAWN_TIME = 15


class INDIVIDUAL_RESPAWN:
    COOLDOWN_BASE = 5
    COOLDOWN_MINIMAL = 10
    COOLDOWN_REDUCE_STEP = 10
    COOLDOWN_DEATH_PENALTY = 15
    DEATH_LIMIT = 0


class TEAM_RESPAWN:
    COOLDOWN_BASE = 15
    COOLDOWN_MINIMAL = 10
    COOLDOWN_REDUCE_STEP = 10
    COOLDOWN_DEATH_PENALTY = 1


class CAPTURE_MODE:
    DESTROY_ALL_DEFENSE = 0
    GROUND_ONLY = 1
    AIR_ONLY = 2
    CONTEST = 3


class REGENERATION_MODE:
    NONE = 0
    MIXED = 1
    SIMPLE = 2


class SECTOR:
    CAPTURE_MODE = CAPTURE_MODE.CONTEST
    REGENERATION_MODE = REGENERATION_MODE.SIMPLE
    INDIVIDUAL_CAPTURE_POINTS = True
    NEUTRAL_CAPTURE_POINTS = 280
    OWNED_CAPTURE_POINTS = 160
    NEUTRAL_GROUND_DEFENDER_RESPAWN_TIME = 90
    NEUTRAL_AIR_DEFENDER_RESPAWN_TIME = 80
    OWNED_GROUND_DEFENDER_RESPAWN_TIME = 120
    OWNED_AIR_DEFENDER_RESPAWN_TIME = 80
    REGENERATION_TICK_PERIOD = 40
    REGENERATION_POINTS_COUNT = 0
    KILL_DEFENSE_IN_LOCKED_STATE = True
    DEFENSE_SUICIDE_TIME_INTERVAL = 5
    SHORT_LOCK_TIME = 10


class DEFENDER:
    PLANE_NAMES = {1: {DEFENDER_TYPE.LIGHT: 'Defender_I-5',
         DEFENDER_TYPE.HEAVY: 'Defender_Di-6'},
     2: {DEFENDER_TYPE.LIGHT: 'Defender_I-5-2',
         DEFENDER_TYPE.HEAVY: 'Defender_Di-6-2'},
     3: {DEFENDER_TYPE.LIGHT: 'Defender_He-51',
         DEFENDER_TYPE.HEAVY: 'Defender_AO-192'},
     4: {DEFENDER_TYPE.LIGHT: 'Defender_He-51-2',
         DEFENDER_TYPE.HEAVY: 'Defender_AO-192-2'},
     5: {DEFENDER_TYPE.LIGHT: 'Defender_Boomerang',
         DEFENDER_TYPE.HEAVY: 'Defender_Beaufighter'},
     6: {DEFENDER_TYPE.LIGHT: 'Defender_Boomerang-2',
         DEFENDER_TYPE.HEAVY: 'Defender_Beaufighter-2'},
     7: {DEFENDER_TYPE.LIGHT: 'Defender_P-40',
         DEFENDER_TYPE.HEAVY: 'Defender_P-38F'},
     8: {DEFENDER_TYPE.LIGHT: 'Defender_A6M2',
         DEFENDER_TYPE.HEAVY: 'Defender_J4M'},
     9: {DEFENDER_TYPE.LIGHT: 'Defender_bf109G',
         DEFENDER_TYPE.HEAVY: 'Defender_Me-410'},
     10: {DEFENDER_TYPE.LIGHT: 'Defender_Spitfire-IX',
          DEFENDER_TYPE.HEAVY: 'Defender_d-h-103'}}
    PERFORMANCE_TEST = False
    RANDOM_SPAWN_RADIUS = 400
    RANDOM_SPAWN_HEIGHT = 1000


class REPAIR_ZONE:
    ENABLED = True
    HP_PRC_RECOVERY_PER_SECOND = 0.1
    RADIUS = 750
    PART_FULL_REPAIR_DELAY = 3.0


class RECHARGE_ZONE:
    COOLDOWN = 10
    RADIUS = 400


class GRADUAL_HEALING:
    ENABLED = True
    RATE_PER_LEVEL = {1: 0.3,
     2: 0.4,
     3: 0.5,
     4: 0.75,
     5: 1.0,
     6: 1.2,
     7: 1.5,
     8: 1.65,
     9: 1.8,
     10: 2.0}
    SEGMENTS_PER_TYPE = {PLANE_TYPE.FIGHTER: 5,
     PLANE_TYPE.NAVY: 6,
     PLANE_TYPE.HFIGHTER: 10,
     PLANE_TYPE.ASSAULT: 10,
     PLANE_TYPE.BOMBER: 10}
    RATE_PER_TYPE = {PLANE_TYPE.FIGHTER: {1: 5.0,
                          2: 4.0,
                          3: 0.0,
                          4: 0.0,
                          5: 0.0},
     PLANE_TYPE.NAVY: {1: 4.5,
                       2: 3.5,
                       3: 0.0,
                       4: 0.0,
                       5: 0.0,
                       6: 0.0},
     PLANE_TYPE.HFIGHTER: {1: 4.5,
                           2: 3.5,
                           3: 2.0,
                           4: 0.0,
                           5: 0.0,
                           6: 0.0,
                           7: 0.0,
                           8: 0.0,
                           9: 0.0,
                           10: 0.0},
     PLANE_TYPE.ASSAULT: {1: 6.5,
                          2: 5.5,
                          3: 0.0,
                          4: 0.0,
                          5: 0.0,
                          6: 0.0,
                          7: 0.0,
                          8: 0.0,
                          9: 0.0,
                          10: 0.0},
     PLANE_TYPE.BOMBER: {1: 6.0,
                         2: 5.0,
                         3: 2.0,
                         4: 0.0,
                         5: 0.0,
                         6: 0.0,
                         7: 0.0,
                         8: 0.0,
                         9: 0.0,
                         10: 0.0}}
    SAFEZONE_PER_LEVEL = {1: 550,
     2: 600,
     3: 750,
     4: 800,
     5: 880,
     6: 1030,
     7: 1170,
     8: 1330,
     9: 1450,
     10: 1550}


LOW_HEALTH_STATE_PER_TYPE = dict(((planeType, sum((v > 0 for v in data.itervalues()), 0.0) / GRADUAL_HEALING.SEGMENTS_PER_TYPE[planeType]) for planeType, data in GRADUAL_HEALING.RATE_PER_TYPE.iteritems()))

class ACTION:
    PLANE_KILLING = 0
    DEFENDER_KILLING = 1
    REPAIR_TEAM_OBJECT_KILLING = 5
    RECHARGE_TEAM_OBJECT_KILLING = 6
    SECTOR_DEFENSE = 7
    SECTOR_CAPTURE = 8
    SMALL_TO_KILLING = 9
    SMALL_ARM_TO_KILLING = 10
    MEDIUM_TO_KILLING = 11
    MEDIUM_ARM_TO_KILLING = 12
    MEDIUM_ARM2_TO_KILLING = 13
    SPECIAL_MILITARY_TO_KILLING = 14
    SPECIAL_COMMAND_TO_KILLING = 15
    SPECIAL_FACTORY_TO_KILLING = 16
    SPECIAL_FACTORY2_TO_KILLING = 17
    SPECIAL_AIRFIELD_TO_KILLING = 18
    ANY_TO_KILLING = (SMALL_TO_KILLING,
     SMALL_ARM_TO_KILLING,
     MEDIUM_TO_KILLING,
     MEDIUM_ARM_TO_KILLING,
     MEDIUM_ARM2_TO_KILLING,
     SPECIAL_MILITARY_TO_KILLING,
     SPECIAL_COMMAND_TO_KILLING,
     SPECIAL_FACTORY_TO_KILLING,
     SPECIAL_FACTORY2_TO_KILLING,
     SPECIAL_AIRFIELD_TO_KILLING,
     REPAIR_TEAM_OBJECT_KILLING,
     RECHARGE_TEAM_OBJECT_KILLING)


ACTION_SETTINGS = {ACTION.PLANE_KILLING: {'points': 60,
                        'globalScore': False,
                        'sectorScore': True,
                        'playerEfficiency': True,
                        'hudMessage': True,
                        'hudLocalId': 'HUD_ENEMY_PLANES'},
 ACTION.DEFENDER_KILLING: {'points': 40,
                           'globalScore': False,
                           'sectorScore': True,
                           'playerEfficiency': True,
                           'hudMessage': True,
                           'hudLocalId': 'HUD_PLANES_DEFENDER'},
 ACTION.REPAIR_TEAM_OBJECT_KILLING: {'points': 0,
                                     'globalScore': False,
                                     'sectorScore': True,
                                     'playerEfficiency': True,
                                     'hudMessage': True,
                                     'hudLocalId': 'SMALL_FACTORY_TEAM_OBJECT_KILLING'},
 ACTION.RECHARGE_TEAM_OBJECT_KILLING: {'points': 0,
                                       'globalScore': False,
                                       'sectorScore': True,
                                       'playerEfficiency': True,
                                       'hudMessage': True,
                                       'hudLocalId': 'SMALL_AERODROME_TEAM_OBJECT_KILLING'},
 ACTION.SECTOR_DEFENSE: {'points': 40,
                         'globalScore': False,
                         'sectorScore': True,
                         'playerEfficiency': True,
                         'hudMessage': True,
                         'hudLocalId': 'HUD_ENEMY_PLANES'},
 ACTION.SECTOR_CAPTURE: {'points': 0,
                         'globalScore': True,
                         'sectorScore': True,
                         'playerEfficiency': True,
                         'hudMessage': True,
                         'hudLocalId': 'MEDIUM_AERODROME_TEAM_OBJECT_KILLING'},
 ACTION.SMALL_TO_KILLING: {'points': 15,
                           'globalScore': False,
                           'sectorScore': True,
                           'playerEfficiency': True,
                           'hudMessage': True,
                           'hudLocalId': 'HUD_SMALL_OBJECT'},
 ACTION.SMALL_ARM_TO_KILLING: {'points': 20,
                               'globalScore': False,
                               'sectorScore': True,
                               'playerEfficiency': True,
                               'hudMessage': True,
                               'hudLocalId': 'HUD_SMALL_ARMORED_OBJECT'},
 ACTION.MEDIUM_TO_KILLING: {'points': 20,
                            'globalScore': False,
                            'sectorScore': True,
                            'playerEfficiency': True,
                            'hudMessage': True,
                            'hudLocalId': 'HUD_MEDIUM_OBJECT'},
 ACTION.MEDIUM_ARM_TO_KILLING: {'points': 30,
                                'globalScore': False,
                                'sectorScore': True,
                                'playerEfficiency': True,
                                'hudMessage': True,
                                'hudLocalId': 'HUD_MEDIUM_ARMORED_OBJECT'},
 ACTION.MEDIUM_ARM2_TO_KILLING: {'points': 50,
                                 'globalScore': False,
                                 'sectorScore': True,
                                 'playerEfficiency': True,
                                 'hudMessage': True,
                                 'hudLocalId': 'HUD_HEAVY_ARMORED_OBJECT'},
 ACTION.SPECIAL_MILITARY_TO_KILLING: {'points': 80,
                                      'globalScore': False,
                                      'sectorScore': True,
                                      'playerEfficiency': True,
                                      'hudMessage': True,
                                      'hudLocalId': 'HUD_NAME_SECTOR_MILITARYBASE'},
 ACTION.SPECIAL_COMMAND_TO_KILLING: {'points': 50,
                                     'globalScore': False,
                                     'sectorScore': True,
                                     'playerEfficiency': True,
                                     'hudMessage': True,
                                     'hudLocalId': 'HUD_COMMAND_OBJECT'},
 ACTION.SPECIAL_FACTORY_TO_KILLING: {'points': 70,
                                     'globalScore': False,
                                     'sectorScore': True,
                                     'playerEfficiency': True,
                                     'hudMessage': True,
                                     'hudLocalId': 'HUD_WORKSHOP_OBJECT'},
 ACTION.SPECIAL_FACTORY2_TO_KILLING: {'points': 80,
                                      'globalScore': False,
                                      'sectorScore': True,
                                      'playerEfficiency': True,
                                      'hudMessage': True,
                                      'hudLocalId': 'HUD_ARMORED_WORKSHOP_OBJECT'},
 ACTION.SPECIAL_AIRFIELD_TO_KILLING: {'points': 35,
                                      'globalScore': False,
                                      'sectorScore': True,
                                      'playerEfficiency': True,
                                      'hudMessage': True,
                                      'hudLocalId': 'HUD_NAME_SECTOR_AIRFIELD'}}
USE_SECTOR_RADIUS_TABLE = True
SECTOR_RADIUS_TABLE = {1: 200,
 2: 240,
 3: 280,
 4: 310,
 5: 340,
 6: 360,
 7: 375,
 8: 390,
 9: 400,
 10: 410}

class SECTOR_EFFECT:
    GROUND_SUPERIORITY = 0
    AIR_SUPERIORITY = 1
    RADIO_SILENCE = 2
    FROM_STRING = {'ground_superiority': GROUND_SUPERIORITY,
     'air_superiority': AIR_SUPERIORITY,
     'radio_silence': RADIO_SILENCE}


EFFECT_SWITCH_SECTOR_STATE = SECTOR_STATE.LOCKED
ALL_SECTOR_EFFECTS = frozenset(SECTOR_EFFECT.FROM_STRING.values())
SECTOR_EFFECT_SETTINGS = {SECTOR_EFFECT.GROUND_SUPERIORITY: {'duration': 120},
 SECTOR_EFFECT.AIR_SUPERIORITY: {'duration': 120,
                                 'shooting': {'roundTime': 2,
                                              'breakTime': 3}},
 SECTOR_EFFECT.RADIO_SILENCE: {'duration': 90}}

class GROUND_OBJECT_TYPE:
    REPAIR = 3
    RECHARGE = 4
    SMALL = 8
    SMALL_ARM = 5
    MEDIUM = 9
    MEDIUM_ARM = 12
    MEDIUM_ARM2 = 6
    SPECIAL_MILITARY = 13
    SPECIAL_COMMAND = 10
    SPECIAL_FACTORY = 16
    SPECIAL_FACTORY2 = 7
    SPECIAL_AIRFIELD = 17
    IGNORE_SUICIDE = {REPAIR, RECHARGE}

    @classmethod
    def iterate(cls):
        """Iterate over enum values
        @return: Generator that yields (value, name) pairs
        @rtype: __generator[tuple]
        """
        for name, value in vars(cls).iteritems():
            if name.startswith('__') or not isinstance(value, int):
                continue
            yield (value, name)

    @classmethod
    def getName(cls, value):
        """Return enum item name by value
        @param value: Value to get name for
        @return: Enum item name
        @rtype: basestring
        """
        for v, n in cls.iterate():
            if v == value:
                return n

        raise ValueError('Value {0} not found in {1}'.format(value, cls.__name__))


GROUND_OBJECT_KILLING_ACTIONS = {GROUND_OBJECT_TYPE.REPAIR: ACTION.REPAIR_TEAM_OBJECT_KILLING,
 GROUND_OBJECT_TYPE.RECHARGE: ACTION.RECHARGE_TEAM_OBJECT_KILLING,
 GROUND_OBJECT_TYPE.SMALL: ACTION.SMALL_TO_KILLING,
 GROUND_OBJECT_TYPE.SMALL_ARM: ACTION.SMALL_ARM_TO_KILLING,
 GROUND_OBJECT_TYPE.MEDIUM: ACTION.MEDIUM_TO_KILLING,
 GROUND_OBJECT_TYPE.MEDIUM_ARM: ACTION.MEDIUM_ARM_TO_KILLING,
 GROUND_OBJECT_TYPE.MEDIUM_ARM2: ACTION.MEDIUM_ARM2_TO_KILLING,
 GROUND_OBJECT_TYPE.SPECIAL_MILITARY: ACTION.SPECIAL_MILITARY_TO_KILLING,
 GROUND_OBJECT_TYPE.SPECIAL_COMMAND: ACTION.SPECIAL_COMMAND_TO_KILLING,
 GROUND_OBJECT_TYPE.SPECIAL_FACTORY: ACTION.SPECIAL_FACTORY_TO_KILLING,
 GROUND_OBJECT_TYPE.SPECIAL_FACTORY2: ACTION.SPECIAL_FACTORY2_TO_KILLING,
 GROUND_OBJECT_TYPE.SPECIAL_AIRFIELD: ACTION.SPECIAL_AIRFIELD_TO_KILLING}

class PREDICATE_TYPE:
    TIMER = 'timer'
    ALL = (TIMER,)


class BATTLE_EVENT_TYPE:
    COUNTER_STRIKE = 0
    RESPAWN_DISABLE = 1

    @classmethod
    def iterate(cls):
        """Iterate through enum values
        @rtype: __generator[tuple]
        """
        for name, value in vars(cls).iteritems():
            if name.startswith('__'):
                continue
            yield (name, value)

    @classmethod
    def getName(cls, itemValue):
        """Return item name by value
        @param itemValue: Item value
        @return: Item name
        @rtype: basestring
        """
        for name, value in cls.iterate():
            if itemValue == value:
                return name

        raise ValueError('Value {0} not found in {1}'.format(itemValue, cls.__name__))

    @classmethod
    def getValue(cls, itemName):
        """Return item value by name
        @param itemName: Item name
        @return: Item value
        @rtype: int
        """
        for name, value in cls.iterate():
            if itemName == name:
                return value

        raise ValueError('Name {0} not found in {1}'.format(itemName, cls.__name__))


class COUNTER_STRIKE:
    SHELLING_START_PERIOD = 3
    SHELLING_DURATION = 15
    SHOT_PROFILE = 'ballistic2'
    SHOT_HEIGHT = 20
    SHOT_MIN_RADIUS = 20
    SHOT_MAX_RADIUS = 100
    SHOT_AMOUNT = 4


class TACTICAL_RESPAWN_MODE:
    EVERYWHERE = 'everywhere'
    WITH_SPECIAL_SECTOR_ONLY = 'with_special_sector_only'
    ALL = (EVERYWHERE, WITH_SPECIAL_SECTOR_ONLY)


class TACTICAL_RESPAWN:
    """Settings related to tactical respawn feature
    """
    ENABLED = True
    MODE = TACTICAL_RESPAWN_MODE.WITH_SPECIAL_SECTOR_ONLY


class ROCKET_V2_SETTINGS:
    """Common settings for Rocket Launch mechanic
    """
    BALLISTIC_PROFILE = 'ballistic_v2_rocket'
    SHOT_HEIGHT = 2000
    RADIUS = 10

    class DEBUG:
        ENABLED = False
        LINE_COLOUR = 4278255360L
        LINE_GROUP_NAME = 'ROCKET_V2_{sectorId}'
        SECTOR_LINE_COLOUR = 4278190335L
        SECTOR_LINE_GROUP_NAME = 'ROCKET_V2_INFLUENCE_{sectorId}'


class BOMBER_SETTINGS:
    """Common settings for bomber dispatcher feature
    """
    ENABLED = True
    GLOBAL_ID_BY_LEVEL = {1: 2064919657,
     2: 2064919657,
     3: 2064919657,
     4: 782129052,
     5: 898303226,
     6: -1100281169,
     7: -1732444440,
     8: 1779337118,
     9: 274347614,
     10: 1609615449}
    BOMB_DAMAGE_BY_LEVEL = {1: 210,
     2: 215,
     3: 325,
     4: 435,
     5: 612,
     6: 800,
     7: 928,
     8: 1145,
     9: 1245,
     10: 1385}
    FIRST_DROP_DELAY_BY_LEVEL = {1: (12.0, 14.0),
     2: (11.0, 13.0),
     3: (10.0, 12.0),
     4: (9.0, 11.0),
     5: (8.0, 10.0),
     6: (7.0, 9.0),
     7: (6.0, 8.0),
     8: (5.0, 7.0),
     9: (4.0, 6.0),
     10: (3.0, 5.0)}
    MARKERS_AFTER_DROPPING_BOMBS_DURATION = {1: 6.5,
     2: 6.0,
     3: 5.5,
     4: 5.0,
     5: 4.5,
     6: 4.0,
     7: 3.5,
     8: 3.0,
     9: 2.5,
     10: 2.0}
    BOMBS_WARNING_DURATION = 5
    BOMBS_LAUNCH_DELAY_MIN = 0.7
    BOMBS_LAUNCH_DELAY_MAX = 1.5
    IGNORE_NEUTRAL_SECTORS = True
    VISUAL_BOMBS_COUNT = 10
    SCENARIO_EVENT_NAME = 't0_bomber_01'
    MAX_HP_PERCENT = 1.0
    INITIAL_HP_PERCENT = 1.0
    WAIT_TIME = 1
    WEDGE_ANGLE = 90
    BOMBERS_COUNT = 5
    SPLINES_INTERVAL = 80
    BOMBING_RANGE = 650

    class DEBUG:
        ENABLED = False

    class FADE_OUT:
        INITIAL_DELAY_RANGE = (0.0, 3.0)
        ANGLE_RANGE = (40, 50)
        TIME_RANGE = (20, 25)


class SIGNAL_FLARE_TYPE:
    ALLY = 0
    ENEMY = 1
    NEUTRAL = 2


SIGNAL_FLARE_EFFECTS = {SIGNAL_FLARE_TYPE.ALLY: 'signal_flare_green',
 SIGNAL_FLARE_TYPE.ENEMY: 'signal_flare_red',
 SIGNAL_FLARE_TYPE.NEUTRAL: 'signal_flare_white'}

class SECTOR_BONUS_TYPE:
    """Enum that describes sector bonus types
    """
    POINTS = 'points'
    ROCKET_LAUNCH = 'rocket_launch'
    AIR_STRIKE = 'air_strike'


DEFAULT_LOCK_TIME = 30
RESAPWN_TO_TIME_FOR_PERMANENT_LOCK = 10

class TEAM_OBJECTS_PAINTING:
    TILES_COUNT = 4
    ALLY_INDEX = 1
    ENEMY_INDEX = 0
    NEUTRAL_INDEX = 3


BOMBER_LOCALIZATION_TAG = 'PREBATTLE_PLANE_TYPE_BOMBER'
DEFENDER_LOCALIZATION_TAGS = {DEFENDER_TYPE.LIGHT: 'HUD_DEFENDER_FIGHTER',
 DEFENDER_TYPE.HEAVY: 'HUD_DEFENDER_HEAVY'}

class ATTRITION_WARFARE_SETTINGS:
    MULTIPLY = {0: 1.0,
     1: 1.0,
     2: 2.0,
     3: 3.0,
     4: 4.0,
     5: 5.0,
     6: 6.0,
     7: 7.0,
     8: 8.0,
     9: 9.0,
     10: 10.0}
    POINTS_FOR_KILL = 1


AI_PLAYER_GAME_MODE_PLAN = 'ai/ACPlayer'

def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj