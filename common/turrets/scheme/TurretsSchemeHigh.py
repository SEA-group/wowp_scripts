# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh.py
SETTINGS = {'DPS': 5,
 'PlaneTypeDamageFactor': {1: 0.8,
                           4: 0.9,
                           2: 1.3,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 1.3,
                         1: 1.5,
                         2: 1.7,
                         3: 1.9,
                         4: 2.1},
 'MinDamageRadius': 4.5,
 'ExplosionRadius': 9.0,
 'TurretExplosionRadius': 9.0,
 'RPS': 0.8,
 'BurstTime': 3.0,
 'BurstDelay': 1.25,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 60,
                 1: 65,
                 2: 70,
                 3: 75,
                 4: 80},
 'Aiming': 60,
 'MinTargetAltitude': 65,
 'HighTargetShootDistanceRadius': 180,
 'Prediction': 3,
 'TargetLockDistance': 445,
 'TargetShootDistance': 425,
 'TargetLostDistance': 445,
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
                     2: 0.3,
                     3: 0.1,
                     4: 0.01}}

class TurretsSchemeHigh(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj