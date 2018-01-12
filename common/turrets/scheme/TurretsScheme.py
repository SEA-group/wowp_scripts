# Embedded file name: scripts/common/turrets/scheme/TurretsScheme.py
SETTINGS = {'DPS': 8,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.7,
                           3: 1.0,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.28,
                         1: 0.3,
                         2: 0.32,
                         3: 0.34,
                         4: 0.36},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 11,
 'BurstTime': 3,
 'BurstDelay': 3.6,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 15,
 'speedAngleMax': 0.2,
 'AimingTable': {0: 3,
                 1: 8,
                 2: 13,
                 3: 18,
                 4: 23},
 'Aiming': 3,
 'MinTargetAltitude': 0,
 'Prediction': 4.78,
 'TargetLockDistance': 140,
 'TargetShootDistance': 120,
 'TargetLostDistance': 140,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.7,
                          4: 0.8,
                          2: 0.3,
                          3: 1.0,
                          5: 0.5},
 'PlaneTypeFireFactorLimit': {1: 2,
                              4: 2,
                              2: 2,
                              3: 2,
                              5: 3},
 'FireFactorTable': {0: 1.0,
                     1: 0.6,
                     2: 0.3,
                     3: 0.1,
                     4: 0.01}}

class TurretsScheme(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj