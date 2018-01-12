# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_6.py
SETTINGS = {'DPS': 24,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.2,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 5.65,
                         1: 5.85,
                         2: 6.05,
                         3: 6.25,
                         4: 6.45},
 'MinDamageRadius': 3.7,
 'ExplosionRadius': 7.4,
 'TurretExplosionRadius': 7.4,
 'RPS': 1.0,
 'BurstTime': 3.4,
 'BurstDelay': 0.87,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 35,
                 1: 40,
                 2: 45,
                 3: 50,
                 4: 55},
 'Aiming': 35,
 'MinTargetAltitude': 110,
 'HighTargetShootDistanceRadius': 312,
 'Prediction': 5.5,
 'TargetLockDistance': 820,
 'TargetShootDistance': 800,
 'TargetLostDistance': 820,
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
                     1: 0.8,
                     2: 0.6,
                     3: 0.3,
                     4: 0.2}}

class TurretsSchemeHigh_6(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj