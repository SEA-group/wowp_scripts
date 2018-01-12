# Embedded file name: scripts/client/audio/AKConsts.py
AkCurveInterpolation_Log3 = 0
AkCurveInterpolation_Sine = 1
AkCurveInterpolation_Log1 = 2
AkCurveInterpolation_InvSCurve = 3
AkCurveInterpolation_Linear = 4
AkCurveInterpolation_SCurve = 5
AkCurveInterpolation_Exp1 = 6
AkCurveInterpolation_SineRecip = 7
AkCurveInterpolation_Exp3 = 8
AkCurveInterpolation_LastFadeCurve = 8
AkCurveInterpolation_Constant = 9

class PartState:
    Normal = 1
    Damaged = 2
    Destructed = 3
    RepairedPartly = 4
    Repaired = 5


class ENGINE_OVERHEAT:
    COOLDOWN_TIME = 0.5
    RTPC_ENGINE_TEMPERATURE = 'RTPC_Overheat_Scale'
    READY = 0
    PROCESS = 1
    END = 2


DEBUG_AUDIO_TAG = '[AUDIO]'
SPEED_OF_SOUND = 1191

class SOUND_MODES:
    SWITCH = 'SWITCH_Sound_Mode'
    SPECTATOR = 0
    AVATAR = 1
    PLAYER = 2
    WWISE = {SPECTATOR: 'Spectator',
     AVATAR: 'NPC',
     PLAYER: 'Player'}


CURRENT_PLAYER_MODE = SOUND_MODES.PLAYER

class SOUND_CASES:
    HANGAR = 0
    ARENA = 1
    VOICEOVER = 2


INIT_BANK_NAME = 'init_wowp'
WEAPONS_BANK_NAME = 'wpn'
VOICEOVERS_QUEUE_SIZE = 2

class VOICEOVERS_BANKS:
    COORDINATOR = 'vo_coordinator'


class VOICEOVER_NOISE:
    START = 'vo_c_noise_start'
    STOP = 'vo_c_noise_stop'


class VOICE:
    LAST_PLAYER = 'vo_c_last_player'
    LAST_ENEMY = 'vo_c_last_enemy'
    BATTLE_START = 'vo_c_battle_start'
    CLOSE_TO_WIN = 'vo_c_close_to_win'
    CLOSE_TO_LOSE = 'vo_c_close_to_lose'
    TEAM_WIN = 'vo_c_team_win'
    TEAM_LOSE = 'vo_c_team_lose'
    FACTORY_CAPTURED = 'vo_c_factory_captured'
    AIRFIELD_CAPTURED = 'vo_c_airfield_captured'
    CENTER_CAPTURED = 'vo_c_center_captured'
    BASE_CAPTURED = 'vo_c_base_captured'
    ALL_AIRFIELDS_CAPTURED = 'vo_c_all_airfields_captured'
    ALL_FACTORIES_CAPTURED = 'vo_c_all_factories_captured'
    ALL_BASES_CAPTURED = 'vo_c_all_bases_captured'
    ALL_CENTERS_CAPTURED = 'vo_c_all_centers_captured'
    ALL_SECTORS_CAPTURED = 'vo_c_all_sectors_captured'
    ALL_SECTORS_LOST = 'vo_c_all_sectors_lost'
    CDOWN_THUNDERHEAD_START = 'vo_c_cdown_thunderhead_start'
    CDOWN_THUNDERHEAD_END = 'vo_c_cdown_thunderhead_end'
    CDOWN_COUNTERSTRIKE_START = 'vo_c_cdown_counterstrike_start'
    CDOWN_COUNTERSTRIKE_END = 'vo_c_cdown_counterstrike_end'
    MAP_LOADED = 'vo_c_map_loaded'
    TARGET_FACTORY = 'vo_c_target_factory'
    TARGET_AIRFIELD = 'vo_c_target_airfield'
    TARGET_BASE = 'vo_c_target_base'
    TARGET_CENTER = 'vo_c_target_center'
    AIRSTRIKE_SPAWNED = 'vo_c_airstrike_spawned'
    AIRFIELD_ALARM = 'vo_c_airfield_alarm'
    FACTORY_ALARM = 'vo_c_factory_alarm'
    BASE_ALARM = 'vo_c_base_alarm'
    CENTER_ALARM = 'vo_c_center_alarm'
    FACTORY_LOST = 'vo_c_factory_lost'
    BASE_LOST = 'vo_c_base_lost'
    CENTER_LOST = 'vo_c_center_lost'
    AIRFIELD_LOST = 'vo_c_airfield_lost'
    BATTLE_TIME_NOTIFY_NEG = 'vo_c_battle_time_notify_neg'
    BATTLE_TIME_NOTIFY_POS = 'vo_c_battle_time_notify_pos'
    BATTLE_30SEC_NOTIFY = 'vo_c_battle_30sec_notify'
    AIRSTRIKE_DEFEATED = 'vo_c_airstrike_defeated'
    FAU2_LAUNCH_NEG = 'vo_c_fau2_launch_neg'
    FAU2_LAUNCH_POS = 'vo_c_fau2_launch_pos'


class SECTOR_VOICES_TYPE:
    CAPTURE = 0
    CAPTURE_ALL = 1
    ALARM = 2
    LOST = 3


class SECTOR_VOICES:
    from consts import SECTOR_GAMEPLAY_TYPE
    VOICES = {SECTOR_VOICES_TYPE.CAPTURE: {SECTOR_GAMEPLAY_TYPE.AIRFIELD: VOICE.AIRFIELD_CAPTURED,
                                  SECTOR_GAMEPLAY_TYPE.FACTORY: VOICE.FACTORY_CAPTURED,
                                  SECTOR_GAMEPLAY_TYPE.MILITARY_BASE: VOICE.BASE_CAPTURED,
                                  SECTOR_GAMEPLAY_TYPE.RADAR: VOICE.CENTER_CAPTURED},
     SECTOR_VOICES_TYPE.CAPTURE_ALL: {SECTOR_GAMEPLAY_TYPE.AIRFIELD: VOICE.ALL_AIRFIELDS_CAPTURED,
                                      SECTOR_GAMEPLAY_TYPE.FACTORY: VOICE.ALL_FACTORIES_CAPTURED,
                                      SECTOR_GAMEPLAY_TYPE.MILITARY_BASE: VOICE.ALL_BASES_CAPTURED,
                                      SECTOR_GAMEPLAY_TYPE.RADAR: VOICE.ALL_CENTERS_CAPTURED},
     SECTOR_VOICES_TYPE.ALARM: {},
     SECTOR_VOICES_TYPE.LOST: {SECTOR_GAMEPLAY_TYPE.AIRFIELD: VOICE.AIRFIELD_LOST,
                               SECTOR_GAMEPLAY_TYPE.FACTORY: VOICE.FACTORY_LOST,
                               SECTOR_GAMEPLAY_TYPE.MILITARY_BASE: VOICE.BASE_LOST,
                               SECTOR_GAMEPLAY_TYPE.RADAR: VOICE.CENTER_LOST}}

    @staticmethod
    def getEvent(voice_type, sector_gameplay_type):
        if voice_type in SECTOR_VOICES.VOICES:
            voices = SECTOR_VOICES.VOICES[voice_type]
            if sector_gameplay_type in voices:
                return voices[sector_gameplay_type]
        return ''


class AIRCRAFT_SFX:

    class CATEGORY:
        MISC = 'Misc'
        STATE = 'State'

    class TYPE:
        FLAPS = 'Flaps'
        FIRE = 'Fire'
        CRIT = 'Crit'
        NO_AMMO = 'NoAmmo'


class ENGINE_POV_STATES:
    MAIN = 'main'
    NPC = 'npc'
    SNIPER_MODE = 'sm'
    BOMBING_MODE = 'sm'
    GUNNER_MODE = 'main'


class SNIPER_MODE_STATES:
    ON = 'set_snipermode_on'
    OFF = 'set_snipermode_off'


class SFX_SHELL_MECHANICS:
    BOMB = 'Play_mechanics_bomb_drop'
    ROCKET = 'Play_mechanics_rocket_start'


class SOUND_OBJECT_TYPES:
    WWISE = 0
    ENGINE = 1
    REVERSE_ENGINE = 2
    SFX = 3
    AIRSHOW = 4
    CAMERA = 5
    EFFECT = 6
    EXPLOSION = 7
    HIT = 8
    MUSIC = 9
    SHELL = 10
    UI = 12
    VOICEOVER = 13
    WIND = 14
    WEAPONS = {0: 15,
     1: 16,
     2: 17,
     3: 18,
     4: 19}

    @staticmethod
    def TURRET(turretId):
        return 'turret_{0}'.format(turretId)


class WIND_SOUND:

    class EVENT:
        LOADIND = 'Play_wind_loading_screen'
        PLAYER = 'Play_wind_gameplay_main'
        SPECTATOR = 'Play_wind_spectator'

    class RTPC:
        CRITICAL_LANDSCAPE = 'RTPC_Wind_Critical_Landscape'
        CRITICAL_MANEUVERS = 'RTPC_Wind_Critical_Maneuvers'
        CRITICAL_CAMERA_SPEED = 'RTPC_Wind_Camera_Speed'
        WIND_AIRCRAFT_SPEED = 'RTPC_Wind_Aircraft_Speed'
        AIRCRAFT_LISTENER_ANGLE = 'RTPC_Aircraft_Listener_Angle'


class AIRSHOW_SOUND:

    class EVENT:
        PLAY = 'Play_flyby_NPC'

    class SWITCH:
        TIME = 'SWITCH_Aishow_Flyby_Time_Interval'
        FLYBY_TYPE = 'SWITCH_Aishow_Flyby_Type'

    FLYBY_TYPE_TAG = 'FlybyType'

    class FLYBY_TYPES:
        DEAD = 'Dead'
        JET = 'Jet'
        PISTON = 'Piston'


class MUSIC_SOUND:
    AMBIENT = 0
    MUSIC = 1
    MAP_ID_TAG = {AMBIENT: 'AmbientEvent',
     MUSIC: 'MusicEvent'}
    HANGAR_ID_TAG = {AMBIENT: 'Ambient',
     MUSIC: 'Music'}

    class EVENT:
        BATTLE_MUSIC = 'music_battle'

    STINGER_COOLDOWN_TIME = 30

    class MUSIC_STINGER:
        POSITIVE = 'music_battle_stinger_pos'
        NEGATIVE = 'music_battle_stinger_neg'
        NEUTRAL = ''


class GLOBAL_EVENTS:
    LOAD_HANGAR = 'e_on_hangar_load'
    UNLOAD_HANGAR = 'e_on_hangar_unload'
    LOAD_ARENA = 'e_on_arena_load'
    UNLOAD_ARENA = 'e_on_arena_unload'


class INTERACTIVE_MIX_TYPES:
    GAME_PHASE = 0
    MIX_FOCUS = 1


class TURRET_SOUND:

    class SWITCH:
        TARGET = 'sw_AA_focus'
        TARGET_MAIN = 'main'
        TARGET_UNFOCUSED = 'unfocused'
        TARGET_FOCUSED = 'focused'


class CAMERA_SOUND:

    class MODE:
        MAIN = 'set_mode_main'
        SNIPER_MODE = 'set_mode_snipermode'
        TAILGUNNER = 'set_mode_tailgunner'
        BOMBING = 'set_mode_bombing'

    class PILLOW:
        PLAY_EVENT_ID = 'Play_Camera_FX'
        STOP_EVENT_ID = 'Stop_Camera_FX'
        SWITCH_MATERIAL = 'SWITCH_Camera_FX_Material'

    class FORSAGE:
        STATE = 'state_engine_boost'
        ON = 'on'
        OFF = 'off'


class SOUND_CALLBACK_QUEUE_TYPES:
    AIRSHOW_MAIN = 0
    AIRCRAFT_SPEED_AND_ALTITUDE = 1
    PLAYER_GENERAL = 2
    WEAPON = 3
    DOPPLER = 4


RTPC_AIRCRAFT_HEIGHT = 'RTPC_Aircraft_Height'
RTPC_AIRCRAFT_SPEED = 'RTPC_Aircraft_Body_Speed'

class SOUND_UI_EVENTS:
    RESPAWN = 'ui_respawn'
    UNABLE_ROCKET_BOMB = 'ui_notify_unable'
    MINIMAP_CLICK = 'ui_click_mmap'
    TIMER = 'ui_timer'
    TIMER_LAST = 'ui_timer_last'
    CAMERA_SWITCH = 'ui_camera_switch'
    SCR_RESULT = 'ui_scr_result'
    PLANE_APPEAR = 'ui_plane_appear'


class SOUND_BANKS:
    WIND = 'common_wind'
    WEAPONS = 'wpn'