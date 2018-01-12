# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_4.py
SETTINGS = {'DPS': 27,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.4,
                           3: 1.0,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.19,
                         1: 0.21,
                         2: 0.23,
                         3: 0.25,
                         4: 0.27},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 14,
 'BurstTime': 6,
 'BurstDelay': 3.0,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 60,
 'speedAngleMax': 0.44,
 'AimingTable': {0: 8,
                 1: 13,
                 2: 18,
                 3: 23,
                 4: 28},
 'Aiming': 14,
 'MinTargetAltitude': 0,
 'Prediction': 8.1,
 'TargetLockDistance': 250,
 'TargetShootDistance': 230,
 'TargetLostDistance': 250,
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
                     1: 0.7,
                     2: 0.5,
                     3: 0.3,
                     4: 0.01}}

class TurretsScheme_4(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj