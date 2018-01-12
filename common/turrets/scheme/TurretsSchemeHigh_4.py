# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_4.py
SETTINGS = {'DPS': 14,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.2,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 3.35,
                         1: 3.55,
                         2: 3.75,
                         3: 3.95,
                         4: 4.15},
 'MinDamageRadius': 4.0,
 'ExplosionRadius': 8.0,
 'TurretExplosionRadius': 8.0,
 'RPS': 0.9,
 'BurstTime': 3.2,
 'BurstDelay': 1.05,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 45,
                 1: 50,
                 2: 55,
                 3: 60,
                 4: 65},
 'Aiming': 45,
 'MinTargetAltitude': 85,
 'HighTargetShootDistanceRadius': 260,
 'Prediction': 4.5,
 'TargetLockDistance': 670,
 'TargetShootDistance': 650,
 'TargetLostDistance': 670,
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
                     1: 0.7,
                     2: 0.5,
                     3: 0.3,
                     4: 0.01}}

class TurretsSchemeHigh_4(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj