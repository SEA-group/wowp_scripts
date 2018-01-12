# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_7.py
SETTINGS = {'DPS': 49,
 'PlaneTypeDamageFactor': {1: 0.8,
                           4: 0.9,
                           2: 1.2,
                           3: 1.3,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.07,
                         1: 0.09,
                         2: 0.11,
                         3: 0.13,
                         4: 0.15},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 17,
 'BurstTime': 7.75,
 'BurstDelay': 2.25,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 105,
 'speedAngleMax': 1.5,
 'AimingTable': {0: 12,
                 1: 16,
                 2: 22,
                 3: 28,
                 4: 32},
 'Aiming': 12,
 'MinTargetAltitude': 0,
 'Prediction': 11.93,
 'TargetLockDistance': 290,
 'TargetShootDistance': 270,
 'TargetLostDistance': 290,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.7,
                          4: 0.8,
                          2: 0.3,
                          3: 1.0,
                          5: 0.5},
 'PlaneTypeFireFactorLimit': {1: 2,
                              4: 3,
                              2: 3,
                              3: 2,
                              5: 3},
 'FireFactorTable': {0: 1.0,
                     1: 0.85,
                     2: 0.6,
                     3: 0.5,
                     4: 0.2}}

class TurretsScheme_7(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj