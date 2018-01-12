# Embedded file name: scripts/client/audio/AKTunes.py
RTPC_Aircraft_Engine_Boost_VDT = 5000
RTPC_Aircraft_Engine_RPM_VDT = 5000
RTPC_Aircraft_Engine_RPM_MAX = 100
RTPC_Aircraft_Camera_Zoomstate_VDT = 200
RTPC_Zoomstate_MAX = 4
FREECAM_DIST_MAX = 10
RTPC_ListenerAngle_VDT = 0
RTPC_AircraftRoll_VDT = 0
RTPC_AircraftPitch_VDT = 0
RTPC_ListenerAngle_Update_Freq = 10
RTPC_Altitude_Update_Freq = 2
RTPC_Wind_Update_Freq = 20
RTPC_Airshow_Update_Freq = 50
RTPC_DopplerEffect_Update_Freq = 20
Weapon_Orientation_Update_Freq = 60
CritParts = ['LeftWing', 'RightWing', 'Tail']
Common_Banks = ['common_ui']
Arena_Banks = ['common_battles',
 'common_explosions',
 'common_hits',
 'common_misc',
 'common_objects']
Weapon_Orientation_Update_Ms = 1.0 / Weapon_Orientation_Update_Freq
RTPC_ListenerAngle_Update_Interval = 1.0 / RTPC_ListenerAngle_Update_Freq
RTPC_Altitude_Update_Interval = 1.0 / RTPC_Altitude_Update_Freq
FREECAM_DIST_STEP = FREECAM_DIST_MAX / RTPC_Zoomstate_MAX
RTPC_Wind_Update_Interval = 1.0 / RTPC_Wind_Update_Freq
RTPC_Airshow_Update_Interval = 1.0 / RTPC_Airshow_Update_Freq
RTPC_DopplerEffect_Update_Interval = 1.0 / RTPC_DopplerEffect_Update_Freq

class SOUND_CALLBACKS_PER_TICK:
    """
    Amount of callback which should be called per one tick using SoundUpdateManager
    """
    AIRSHOW_MAIN = 10
    AIRCRAFT_SPEED_AND_ALTITUDE = 1
    PLAYER_GENERAL = 1
    WEAPON = -1
    DOPPLER = 3


class SOUND_CALLBACKS_VCD:
    """
    ms
    """
    PLAYER_GENERAL = 200
    AIRCRAFT_SPEED_AND_ALTITUDE = 200