# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_3.py
SETTINGS = {'DPS': 10,
 'PlaneTypeDamageFactor': {1: 0.8,
                           4: 0.9,
                           2: 1.3,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 2.2,
                         1: 2.4,
                         2: 2.6,
                         3: 2.8,
                         4: 3.0},
 'MinDamageRadius': 4.2,
 'ExplosionRadius': 8.4,
 'TurretExplosionRadius': 8.4,
 'RPS': 0.8,
 'BurstTime': 3.2,
 'BurstDelay': 1.1,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 50,
                 1: 55,
                 2: 60,
                 3: 65,
                 4: 70},
 'Aiming': 50,
 'MinTargetAltitude': 75,
 'HighTargetShootDistanceRadius': 235,
 'Prediction': 4,
 'TargetLockDistance': 590,
 'TargetShootDistance': 570,
 'TargetLostDistance': 590,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.3,
                          4: 0.7,
                          2: 0.8,
                          3: 0.6,
                          5: 1.0},
 'PlaneTypeFireFactorLimit': {1: 1,
                              4: 1,
                              2: 3,
                              3: 3,
                              5: 2},
 'FireFactorTable': {0: 1.0,
                     1: 0.7,
                     2: 0.4,
                     3: 0.1,
                     4: 0.01}}

class TurretsSchemeHigh_3(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj