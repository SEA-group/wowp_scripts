# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_9.py
SETTINGS = {'DPS': 36,
 'PlaneTypeDamageFactor': {1: 0.6,
                           4: 0.7,
                           2: 1.1,
                           3: 2.8,
                           5: 1.6},
 'ShootRandomizeTable': {0: 5.65,
                         1: 5.85,
                         2: 6.05,
                         3: 6.25,
                         4: 6.45},
 'MinDamageRadius': 3.55,
 'ExplosionRadius': 7.1,
 'TurretExplosionRadius': 7.1,
 'RPS': 1.1,
 'BurstTime': 3.6,
 'BurstDelay': 0.77,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 20,
                 1: 25,
                 2: 30,
                 3: 35,
                 4: 40},
 'Aiming': 20,
 'MinTargetAltitude': 140,
 'HighTargetShootDistanceRadius': 390,
 'Prediction': 1.25,
 'TargetLockDistance': 1020,
 'TargetShootDistance': 1000,
 'TargetLostDistance': 1020,
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
                     2: 0.7,
                     3: 0.5,
                     4: 0.3}}

class TurretsSchemeHigh_9(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj