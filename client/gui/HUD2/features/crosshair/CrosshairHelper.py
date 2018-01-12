# Embedded file name: scripts/client/gui/HUD2/features/crosshair/CrosshairHelper.py
from consts import BATTLE_MODE
from _economics import WEAPON_AIM_TYPE
BATTLE_STATE_TO_HUD_STATE = {BATTLE_MODE.COMBAT_MODE: 0,
 BATTLE_MODE.SNIPER_MODE: 1,
 BATTLE_MODE.ASSAULT_MODE: 2,
 BATTLE_MODE.GUNNER_MODE: 3,
 BATTLE_MODE.OVERVIEW_MODE: 4}
NORMAL_CROSSHAIR_SIZE = 50

def _getAimingTypes():
    """
    @rtype: dict
    """
    aimingTypes = {}
    for key, value in WEAPON_AIM_TYPE.__dict__.items():
        if isinstance(value, int):
            aimingTypes[value] = key

    return aimingTypes


AimingTypes = _getAimingTypes()