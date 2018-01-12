# Embedded file name: scripts/common/CommonSettings.py
__author__ = 'm_kobets'
import math
import Math
from MathExt import km_to_m
from EntityHelpers import PART_ENUM
from consts import WORLD_SCALING, PLANE_TYPE, VERTICAL_AXIS, ROLL_AXIS, IS_CLIENT, IS_CELLAPP, HORIZONTAL_AXIS, TurretDamageDealer

def dtc(init_dictionary):
    """
    :param init_dictionary: dictionary
    :return: obj
    """

    class DictToCls(object):

        def __init__(self, init_dict):
            self.__dict__ = init_dict

            def __setattr__dummy(*a, **k):
                raise SyntaxError

            DictToCls.__setattr__ = __setattr__dummy

        def __repr__(self):
            return 'DictToCls(' + str(self.__dict__) + ')'

    if isinstance(init_dictionary, dict):
        return DictToCls(init_dictionary)
    raise AttributeError


class SensitivityScale_PillowSettings:
    h1 = 2 * WORLD_SCALING
    h2 = 20 * WORLD_SCALING
    min_sens = 0.25


class ModifyDirection_PillowSettings:
    h1 = 1 * WORLD_SCALING
    low_height_timing = 0.5
    h2_speed_norma1 = 10 * WORLD_SCALING
    h2_speed_norma2 = 15 * WORLD_SCALING
    speed_norma1 = km_to_m(200.0)
    speed_norma2 = km_to_m(500.0)
    horizon_angle1 = math.radians(10)
    horizon_angle2 = math.radians(45)


pillowSetting = {'normal_collision_range': 200.0 * WORLD_SCALING,
 'normal_speed': km_to_m(400),
 'stall_speed_cfc1': 1,
 'stall_speed_cfc2': 1.5,
 'up_angle_min': math.radians(15),
 'up_angle_max': math.radians(100),
 'pitch_boost_cfc': 1.75,
 'static_collision_range_cfc': 0.2,
 'back_angle_one': math.radians(90),
 'back_angle_two': math.radians(95),
 'static_normal_speed': km_to_m(1000),
 'static_normal_speed_tau': 2,
 'static_stall_speed_tau': 2.0,
 'absorption_speed_cfc': 1.0,
 'activate_pitch_rudder_value': 0.2,
 'dive_speed_tau': 2.0,
 'stall_speed_tau': 4,
 'dive_normal_angle1': math.radians(10),
 'dive_normal_angle2': math.radians(110),
 'control_up_effect_angle1': math.radians(30),
 'control_up_effect_angle2': math.radians(80)}
MOUSE_ARCADE_ROLL_SETTINGS = {PLANE_TYPE.FIGHTER: {'flip_cfc': 0.6,
                      'bobber_cfc': 0.15,
                      'no_roll_power': 2.0,
                      'rect_rollup_cfc': 1.5,
                      'rect_rolldown_cfc': 0.5,
                      'no_roll_down_zone': 0.5,
                      'no_roll_down_gradient': 10.0},
 PLANE_TYPE.NAVY: {'flip_cfc': 0.6,
                   'bobber_cfc': 0.15,
                   'no_roll_power': 2.0,
                   'rect_rollup_cfc': 1.5,
                   'rect_rolldown_cfc': 0.5,
                   'no_roll_down_zone': 0.5,
                   'no_roll_down_gradient': 10.0},
 PLANE_TYPE.HFIGHTER: {'flip_cfc': 0.8,
                       'bobber_cfc': 0.4,
                       'no_roll_power': 4.0,
                       'rect_rollup_cfc': 1.25,
                       'rect_rolldown_cfc': 0.25,
                       'no_roll_down_zone': 3.0,
                       'no_roll_down_gradient': 10.0},
 PLANE_TYPE.ASSAULT: {'flip_cfc': 1.0,
                      'bobber_cfc': 1.0,
                      'no_roll_power': 8.0,
                      'rect_rollup_cfc': 1.0,
                      'rect_rolldown_cfc': 0.0,
                      'no_roll_down_zone': 5.0,
                      'no_roll_down_gradient': 10.0},
 PLANE_TYPE.BOMBER: {'flip_cfc': 1.0,
                     'bobber_cfc': 1.0,
                     'no_roll_power': 8.0,
                     'rect_rollup_cfc': 1.0,
                     'rect_rolldown_cfc': 0.0,
                     'no_roll_down_zone': 10.0,
                     'no_roll_down_gradient': 10.0}}

def getMouseArcadeRollSettings(planeType):
    return dtc(MOUSE_ARCADE_ROLL_SETTINGS[planeType])


from collections import namedtuple
turretControlAimConeAngle = math.radians(10)
turretGunLockConeAngle = math.radians(10)
GunnerDefaultConcentration = 0.5
ZoneGunnerMaxConcentration = 0.33 * turretControlAimConeAngle
turretPartCritTime = 20
CONTROL_GUNNER_VALID_PLANE_CLASSES = [PLANE_TYPE.BOMBER,
 PLANE_TYPE.ASSAULT,
 PLANE_TYPE.FIGHTER,
 PLANE_TYPE.NAVY,
 PLANE_TYPE.HFIGHTER]
BOMB_STATE_VALID_PLANE_CLASSES = [PLANE_TYPE.BOMBER]

class GUNNER_CONTROL_STATES_MODS:
    BOT = dtc({'dealer': TurretDamageDealer.bot,
     'damageFromTimeMinK': 0.5,
     'damageFromTimeMaxK': 1,
     'turretReductionTimeK': 1,
     'burstTimeK': 1,
     'burstDaleyK': 1,
     'distanceOptimalK': 0.8,
     'critAbilityMin': 0.1,
     'critAbilityMax': 1.0,
     'damageAtDistanceMaxK': 0.5,
     'reductionReduceTime': 2.0})
    PLAYER = dtc({'dealer': TurretDamageDealer.player,
     'damageFromTimeMinK': 0.5,
     'damageFromTimeMaxK': 2.0,
     'turretReductionTimeK': 1.0,
     'burstTimeK': 10000,
     'burstDaleyK': 0.0,
     'distanceOptimalK': 0.9,
     'critAbilityMin': 0.1,
     'critAbilityMax': 4.0,
     'damageAtDistanceMaxK': 0.75,
     'reductionReduceTime': 2.0})


if IS_CLIENT:

    class CustomObject(object):
        pass


    bombMarkerCollisionRadius = 0.5
    TURRET_LOSE_BORDER_ZONE = math.radians(15)
    TURRET_BULLET_DISPERSION_MAX = math.radians(2.0)
    TURRET_BULLET_DISPERSION_MIN = math.radians(0.3)
    GunnerFireRangingSettings = dtc({'isNonTargetRanging': True,
     'isTargetRanging': True,
     'withRandom': False,
     'simpleFireTime': 2.0,
     'delayTime': 0.5})
    _effect = namedtuple('effect', ' '.join(['name', 'type', 'params']))

    class BOMBER_EFFECTS:
        idleClouds = _effect('fly_idle_bomber_target', 'createModelTargetEffect', {'offset': Math.Vector3(0, -WORLD_SCALING * 15, 0)})


    FORCE_RUDDER_BOMBER_SETTINGS = {1: math.radians(40),
     -1: math.radians(5)}
    GUNNER_CAM_LIMITED_ANGLES = dtc({'bottomPitchBound': math.radians(70.0),
     'topPitchBound': math.radians(70.0),
     'yawBound': math.radians(30.0)})
    BOMBER_CAM_LIMITED_ANGLES = dtc({'bottomPitchBound': math.radians(0.01),
     'topPitchBound': math.radians(35.0),
     'yawBound': math.radians(60.0)})
    ALTERNATIVE_BATTLE_MODE_INPUT_SETTINGS = dtc({'MOUSE_INVERT_VERT': True,
     'mouseSensitivity': 0.5,
     'VALID_PLANE_TYPES': [PLANE_TYPE.BOMBER,
                           PLANE_TYPE.ASSAULT,
                           PLANE_TYPE.FIGHTER,
                           PLANE_TYPE.NAVY,
                           PLANE_TYPE.HFIGHTER],
     'AXIS_MAX_SPEED': {VERTICAL_AXIS: 1200,
                        ROLL_AXIS: -1200,
                        HORIZONTAL_AXIS: 1200},
     'DEAD_ZONE': 0.25})
if IS_CELLAPP:
    CRITABLE_BY_TURRETS_PARTS = {TurretDamageDealer.undefined: {PART_ENUM.LEFT_WING: 1,
                                    PART_ENUM.RIGHT_WING: 1,
                                    PART_ENUM.TAIL: 1},
     TurretDamageDealer.bot: {PART_ENUM.LEFT_WING: 1,
                              PART_ENUM.RIGHT_WING: 1,
                              PART_ENUM.TAIL: 0.5,
                              PART_ENUM.ENGINE: 4,
                              PART_ENUM.PILOT: 4},
     TurretDamageDealer.player: {PART_ENUM.LEFT_WING: 1,
                                 PART_ENUM.RIGHT_WING: 1,
                                 PART_ENUM.TAIL: 0.5,
                                 PART_ENUM.ENGINE: 10,
                                 PART_ENUM.PILOT: 10}}