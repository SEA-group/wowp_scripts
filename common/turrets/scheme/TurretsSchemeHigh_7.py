# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_7.py
SETTINGS = {'DPS': 27,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.1,
                           3: 2.5,
                           5: 1.45},
 'ShootRandomizeTable': {0: 5.8,
                         1: 6.0,
                         2: 6.2,
                         3: 6.4,
                         4: 6.6},
 'MinDamageRadius': 3.65,
 'ExplosionRadius': 7.3,
 'TurretExplosionRadius': 7.3,
 'RPS': 1.0,
 'BurstTime': 3.5,
 'BurstDelay': 0.83,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 30,
                 1: 35,
                 2: 40,
                 3: 45,
                 4: 50},
 'Aiming': 30,
 'MinTargetAltitude': 115,
 'HighTargetShootDistanceRadius': 340,
 'Prediction': 3.5,
 'TargetLockDistance': 855,
 'TargetShootDistance': 835,
 'TargetLostDistance': 855,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.3,
                          4: 0.7,
                          2: 0.8,
                          3: 0.6,
                          5: 1.0},
 'PlaneTypeFireFactorLimit': {1: 2,
                              4: 2,
                              2: 3,
                              3: 3,
                              5: 3},
 'FireFactorTable': {0: 1.0,
                     1: 0.85,
                     2: 0.6,
                     3: 0.5,
                     4: 0.2}}

class TurretsSchemeHigh_7(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj