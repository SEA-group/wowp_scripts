# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_10.py
SETTINGS = {'DPS': 99,
 'PlaneTypeDamageFactor': {1: 0.9,
                           4: 1.0,
                           2: 1.2,
                           3: 1.6,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.01,
                         1: 0.03,
                         2: 0.05,
                         3: 0.07,
                         4: 0.09},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 20,
 'BurstTime': 7.5,
 'BurstDelay': 1.0,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 150,
 'speedAngleMax': 5.0,
 'AimingTable': {0: 20,
                 1: 25,
                 2: 30,
                 3: 35,
                 4: 40},
 'Aiming': 20,
 'MinTargetAltitude': 0,
 'Prediction': 16.23,
 'TargetLockDistance': 320,
 'TargetShootDistance': 300,
 'TargetLostDistance': 320,
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
                     2: 0.8,
                     3: 0.5,
                     4: 0.3}}

class TurretsScheme_10(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj