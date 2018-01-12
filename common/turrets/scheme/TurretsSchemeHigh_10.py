# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_10.py
SETTINGS = {'DPS': 45,
 'PlaneTypeDamageFactor': {1: 0.6,
                           4: 0.7,
                           2: 1.1,
                           3: 2.8,
                           5: 1.6},
 'ShootRandomizeTable': {0: 5.4,
                         1: 5.6,
                         2: 5.8,
                         3: 6.0,
                         4: 6.2},
 'MinDamageRadius': 3.5,
 'ExplosionRadius': 7.0,
 'TurretExplosionRadius': 7.0,
 'RPS': 1.2,
 'BurstTime': 3.7,
 'BurstDelay': 0.7,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 15,
                 1: 20,
                 2: 25,
                 3: 30,
                 4: 35},
 'Aiming': 15,
 'MinTargetAltitude': 145,
 'HighTargetShootDistanceRadius': 415,
 'Prediction': 1.0,
 'TargetLockDistance': 1070,
 'TargetShootDistance': 1050,
 'TargetLostDistance': 1070,
 'TurretLockTargetFromShootK': 1.2,
 'PlaneTypeFactorTable': {1: 0.3,
                          4: 0.7,
                          2: 0.8,
                          3: 0.6,
                          5: 1.0},
 'PlaneTypeFireFactorLimit': {1: 3,
                              4: 3,
                              2: 4,
                              3: 4,
                              5: 3},
 'FireFactorTable': {0: 1.0,
                     1: 0.9,
                     2: 0.8,
                     3: 0.5,
                     4: 0.3}}

class TurretsSchemeHigh_10(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj