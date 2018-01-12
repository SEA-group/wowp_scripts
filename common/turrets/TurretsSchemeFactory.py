# Embedded file name: scripts/common/turrets/TurretsSchemeFactory.py
from turrets import TURRET_TYPE_LIGHT, TURRET_TYPE_HEAVY
from turrets.scheme.BaseTurretsScheme import BaseTurretsScheme
from turrets.scheme.TurretsScheme import TurretsScheme
from turrets.scheme.TurretsScheme_2 import TurretsScheme_2
from turrets.scheme.TurretsScheme_3 import TurretsScheme_3
from turrets.scheme.TurretsScheme_4 import TurretsScheme_4
from turrets.scheme.TurretsScheme_5 import TurretsScheme_5
from turrets.scheme.TurretsScheme_6 import TurretsScheme_6
from turrets.scheme.TurretsScheme_7 import TurretsScheme_7
from turrets.scheme.TurretsScheme_8 import TurretsScheme_8
from turrets.scheme.TurretsScheme_9 import TurretsScheme_9
from turrets.scheme.TurretsScheme_10 import TurretsScheme_10
from turrets.scheme.TurretsSchemeHigh import TurretsSchemeHigh
from turrets.scheme.TurretsSchemeHigh_2 import TurretsSchemeHigh_2
from turrets.scheme.TurretsSchemeHigh_3 import TurretsSchemeHigh_3
from turrets.scheme.TurretsSchemeHigh_4 import TurretsSchemeHigh_4
from turrets.scheme.TurretsSchemeHigh_5 import TurretsSchemeHigh_5
from turrets.scheme.TurretsSchemeHigh_6 import TurretsSchemeHigh_6
from turrets.scheme.TurretsSchemeHigh_7 import TurretsSchemeHigh_7
from turrets.scheme.TurretsSchemeHigh_8 import TurretsSchemeHigh_8
from turrets.scheme.TurretsSchemeHigh_9 import TurretsSchemeHigh_9
from turrets.scheme.TurretsSchemeHigh_10 import TurretsSchemeHigh_10
TurretsSchemeDict = {1: {TURRET_TYPE_LIGHT: TurretsScheme,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh},
 2: {TURRET_TYPE_LIGHT: TurretsScheme_2,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_2},
 3: {TURRET_TYPE_LIGHT: TurretsScheme_3,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_3},
 4: {TURRET_TYPE_LIGHT: TurretsScheme_4,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_4},
 5: {TURRET_TYPE_LIGHT: TurretsScheme_5,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_5},
 6: {TURRET_TYPE_LIGHT: TurretsScheme_6,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_6},
 7: {TURRET_TYPE_LIGHT: TurretsScheme_7,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_7},
 8: {TURRET_TYPE_LIGHT: TurretsScheme_8,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_8},
 9: {TURRET_TYPE_LIGHT: TurretsScheme_9,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh_9},
 10: {TURRET_TYPE_LIGHT: TurretsScheme_10,
      TURRET_TYPE_HEAVY: TurretsSchemeHigh_10}}

def getTurretsSchemeByBattleLevel(level, isHigh):
    key = TURRET_TYPE_HEAVY if isHigh else TURRET_TYPE_LIGHT
    scheme = BaseTurretsScheme()
    currentScheme = TurretsSchemeDict.get(level, {TURRET_TYPE_LIGHT: TurretsScheme,
     TURRET_TYPE_HEAVY: TurretsSchemeHigh})[key]()
    scheme.setSettings(currentScheme.SchemeSettings)
    return scheme