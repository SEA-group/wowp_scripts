# Embedded file name: scripts/common/turrets/scheme/BaseTurretsScheme.py


class BaseTurretsScheme(object):

    def __init__(self):
        self.SETTINGS = {}

    def setSettings(self, value):
        self.SETTINGS = value

    @property
    def BurstTime(self):
        return self.SETTINGS['BurstTime']

    @property
    def DPS(self):
        return self.SETTINGS['DPS']

    @property
    def BurstDelay(self):
        return self.SETTINGS['BurstDelay']

    @property
    def RPS(self):
        return self.SETTINGS['RPS']

    @property
    def MinDamageRadius(self):
        return self.SETTINGS['MinDamageRadius']

    @property
    def ExplosionRadius(self):
        return self.SETTINGS['ExplosionRadius']

    @property
    def TargetLockDistance(self):
        return self.SETTINGS['TargetLockDistance']

    @property
    def TargetShootDistance(self):
        return self.SETTINGS['TargetShootDistance']

    @property
    def TargetLostDistance(self):
        return self.SETTINGS['TargetLostDistance']

    @property
    def TurretLockTargetFromShootK(self):
        return self.SETTINGS['TurretLockTargetFromShootK']

    @property
    def TurretExplosionRadius(self):
        return self.SETTINGS['TurretExplosionRadius']

    @property
    def Aiming(self):
        return self.SETTINGS['Aiming']

    @property
    def Prediction(self):
        return self.SETTINGS['Prediction']

    @property
    def FireFactorTable(self):
        return self.SETTINGS['FireFactorTable']

    @property
    def PlaneTypeFactorTable(self):
        return self.SETTINGS['PlaneTypeFactorTable']

    @property
    def PlaneTypeFireFactorLimit(self):
        return self.SETTINGS['PlaneTypeFireFactorLimit']

    @property
    def PlaneTypeDamageFactor(self):
        return self.SETTINGS['PlaneTypeDamageFactor']

    @property
    def AimingTable(self):
        return self.SETTINGS['AimingTable']

    @property
    def DelayRandomizeTable(self):
        return self.SETTINGS['DelayRandomizeTable']

    @property
    def ShootRandomizeTable(self):
        return self.SETTINGS['ShootRandomizeTable']

    @property
    def MinTargetAltitude(self):
        return self.SETTINGS['MinTargetAltitude']

    @property
    def HighTargetShootDistanceRadius(self):
        return self.SETTINGS['HighTargetShootDistanceRadius']

    @property
    def SpeedAngle(self):
        return self.SETTINGS['speedAngle']

    @property
    def SpeedAngleMax(self):
        return self.SETTINGS['speedAngleMax']