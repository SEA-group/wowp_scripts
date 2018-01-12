# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_2.py
SETTINGS = {'DPS': 7.5,
 'PlaneTypeDamageFactor': {1: 0.8,
                           4: 0.9,
                           2: 1.3,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 1.5,
                         1: 1.7,
                         2: 1.9,
                         3: 2.1,
                         4: 2.3},
 'MinDamageRadius': 4.35,
 'ExplosionRadius': 8.75,
 'TurretExplosionRadius': 8.75,
 'RPS': 0.8,
 'BurstTime': 3,
 'BurstDelay': 1.17,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 55,
                 1: 60,
                 2: 65,
                 3: 70,
                 4: 75},
 'Aiming': 55,
 'MinTargetAltitude': 70,
 'HighTargetShootDistanceRadius': 210,
 'Prediction': 3.5,
 'TargetLockDistance': 520,
 'TargetShootDistance': 500,
 'TargetLostDistance': 520,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.3,
                          4: 0.7,
                          2: 0.8,
                          3: 0.6,
                          5: 1.0},
 'PlaneTypeFireFactorLimit': {1: 1,
                              4: 1,
                              2: 2,
                              3: 3,
                              5: 2},
 'FireFactorTable': {0: 1.0,
                     1: 0.6,
                     2: 0.4,
                     3: 0.1,
                     4: 0.01}}

class TurretsSchemeHigh_2(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj