# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_2.py
SETTINGS = {'DPS': 13.5,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.6,
                           3: 1.0,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.25,
                         1: 0.27,
                         2: 0.29,
                         3: 0.31,
                         4: 0.33},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 12,
 'BurstTime': 4,
 'BurstDelay': 3.4,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 30,
 'speedAngleMax': 0.26,
 'AimingTable': {0: 5,
                 1: 10,
                 2: 15,
                 3: 20,
                 4: 25},
 'Aiming': 5,
 'MinTargetAltitude': 0,
 'Prediction': 5.72,
 'TargetLockDistance': 170,
 'TargetShootDistance': 150,
 'TargetLostDistance': 170,
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
                     2: 0.4,
                     3: 0.1,
                     4: 0.01}}

class TurretsScheme_2(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj