# Embedded file name: scripts/common/turrets/scheme/TurretsSchemeHigh_5.py
SETTINGS = {'DPS': 19,
 'PlaneTypeDamageFactor': {1: 0.7,
                           4: 0.8,
                           2: 1.2,
                           3: 2.2,
                           5: 1.3},
 'ShootRandomizeTable': {0: 4.5,
                         1: 4.7,
                         2: 4.9,
                         3: 5.1,
                         4: 5.3},
 'MinDamageRadius': 3.85,
 'ExplosionRadius': 7.75,
 'TurretExplosionRadius': 7.75,
 'RPS': 0.9,
 'BurstTime': 3.3,
 'BurstDelay': 1.0,
 'DelayRandomizeTable': {0: (0, 2),
                         1: (0, 3),
                         2: (1, 3),
                         3: (2, 3),
                         4: (2, 4)},
 'AimingTable': {0: 40,
                 1: 45,
                 2: 50,
                 3: 55,
                 4: 60},
 'Aiming': 40,
 'MinTargetAltitude': 105,
 'HighTargetShootDistanceRadius': 285,
 'Prediction': 5.0,
 'TargetLockDistance': 745,
 'TargetShootDistance': 725,
 'TargetLostDistance': 745,
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
                     2: 0.5,
                     3: 0.3,
                     4: 0.2}}

class TurretsSchemeHigh_5(object):

    def __init__(self):
        pass

    @property
    def SchemeSettings(self):
        return SETTINGS


def __xreload_old_new__(namespace, name, oldObj, newObj):
    namespace[name] = newObj