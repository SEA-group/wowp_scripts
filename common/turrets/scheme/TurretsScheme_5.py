# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_5.py
SETTINGS = {'DPS': 34.6,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.3,
                           3: 1.0,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.17,
                         1: 0.19,
                         2: 0.21,
                         3: 0.23,
                         4: 0.25},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 15,
 'BurstTime': 7,
 'BurstDelay': 2.8,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 75,
 'speedAngleMax': 0.58,
 'AimingTable': {0: 9,
                 1: 14,
                 2: 19,
                 3: 24,
                 4: 29},
 'Aiming': 12,
 'MinTargetAltitude': 0,
 'Prediction': 9.55,
 'TargetLockDistance': 270,
 'TargetShootDistance': 250,
 'TargetLostDistance': 270,
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
                     1: 0.8,
                     2: 0.5,
                     3: 0.3,
                     4: 0.2}}

class TurretsScheme_5(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj