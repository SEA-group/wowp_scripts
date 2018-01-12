# Embedded file name: scripts/common/turrets/scheme/TurretsScheme_6.py
SETTINGS = {'DPS': 42,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.2,
                           3: 1.0,
                           5: 2.7},
 'ShootRandomizeTable': {0: 0.15,
                         1: 0.17,
                         2: 0.19,
                         3: 0.21,
                         4: 0.23},
 'MinDamageRadius': 6,
 'ExplosionRadius': 10,
 'TurretExplosionRadius': 10,
 'RPS': 16,
 'BurstTime': 7.5,
 'BurstDelay': 2.55,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'speedAngle': 90,
 'speedAngleMax': 0.85,
 'AimingTable': {0: 10,
                 1: 15,
                 2: 20,
                 3: 25,
                 4: 30},
 'Aiming': 10,
 'MinTargetAltitude': 0,
 'Prediction': 10.5,
 'TargetLockDistance': 280,
 'TargetShootDistance': 260,
 'TargetLostDistance': 280,
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
                     2: 0.6,
                     3: 0.3,
                     4: 0.2}}

class TurretsScheme_6(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj