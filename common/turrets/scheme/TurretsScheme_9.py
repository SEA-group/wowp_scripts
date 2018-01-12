# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_9.py
SETTINGS = {'DPS': 70,
 'PlaneTypeDamageFactor': {1: 0.9,
                           4: 1.0,
                           2: 1.2,
                           3: 1.6,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.02,
                         1: 0.04,
                         2: 0.06,
                         3: 0.08,
                         4: 0.1},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 19,
 'BurstTime': 8.2,
 'BurstDelay': 1.8,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 135,
 'speedAngleMax': 2.5,
 'AimingTable': {0: 17,
                 1: 22,
                 2: 27,
                 3: 32,
                 4: 37},
 'Aiming': 6,
 'MinTargetAltitude': 0,
 'Prediction': 15.3,
 'TargetLockDistance': 310,
 'TargetShootDistance': 290,
 'TargetLostDistance': 310,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.7,
                          4: 0.8,
                          2: 0.3,
                          3: 1.0,
                          5: 0.5},
 'PlaneTypeFireFactorLimit': {1: 3,
                              4: 4,
                              2: 4,
                              3: 3,
                              5: 4},
 'FireFactorTable': {0: 1.0,
                     1: 0.9,
                     2: 0.7,
                     3: 0.5,
                     4: 0.3}}

class TurretsScheme_9(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj