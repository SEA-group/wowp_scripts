# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_8.py
SETTINGS = {'DPS': 30,
 'PlaneTypeDamageFactor': {1: 0.6,
                           4: 0.7,
                           2: 1.1,
                           3: 2.8,
                           5: 1.6},
 'ShootRandomizeTable': {0: 6.0,
                         1: 6.2,
                         2: 6.4,
                         3: 6.6,
                         4: 6.8},
 'MinDamageRadius': 3.6,
 'ExplosionRadius': 7.2,
 'TurretExplosionRadius': 7.2,
 'RPS': 1.1,
 'BurstTime': 3.6,
 'BurstDelay': 0.8,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 25,
                 1: 30,
                 2: 35,
                 3: 40,
                 4: 45},
 'Aiming': 25,
 'MinTargetAltitude': 125,
 'HighTargetShootDistanceRadius': 365,
 'Prediction': 1.5,
 'TargetLockDistance': 920,
 'TargetShootDistance': 900,
 'TargetLostDistance': 920,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.3,
                          4: 0.7,
                          2: 0.8,
                          3: 0.6,
                          5: 1.0},
 'PlaneTypeFireFactorLimit': {1: 3,
                              4: 3,
                              2: 4,
                              3: 4,
                              5: 3},
 'FireFactorTable': {0: 1.0,
                     1: 0.85,
                     2: 0.7,
                     3: 0.5,
                     4: 0.2}}

class TurretsSchemeHigh_8(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj