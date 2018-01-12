# Embedded file name: scripts/common/GunsController/GunGroup.py
import db.DBLogic
import math
from consts import COOLING_PER_SEC_TEMPERATURE_PRC, GUN_OVERHEATING_TEMPERATURE, calculateGunDPS
from debug_utils import LOG_ERROR
import Event
from SyncedRandom import SyncedRandom
from .AmmoBelt import AmmoBelt
from .Gun import Gun

class WeaponGroup(object):

    def __init__(self, containerID, pivots, gunDescription, gunInfos, ammoBelt, planeID):
        self.NOT_FREE_GUNS_FIRING = True
        self.__guns = [ Gun(gunInfo, pivots, gunDescription) for gunInfo in gunInfos ]
        self.__size = len(self.__guns)
        self.__containerID = containerID
        self.__groupID = gunInfos[0].weaponGroup
        self.gunDescription = gunDescription
        self.__dispersionAngle = gunInfos[0].dispersionAngle
        self.__autoguiderAngle = gunInfos[0].autoguiderAngle
        self.__recoilDispersion = gunInfos[0].recoilDispersion
        self.__overheatingFullTime = gunInfos[0].overheatingFullTime
        self.gunName = gunInfos[0].name
        self.__coolingCFC = gunInfos[0].coolingCFC
        self.__gunOverheatingK = 1.0
        self.__reductionAngle = 0.0
        self.__recoilThrust = 0.0
        self.syncedRandom = SyncedRandom()
        self.clientProcessedBulletCount = 0
        gunProfileName = db.DBLogic.g_instance.getGunProfileName(gunDescription, planeID)
        self.__gunProfile = db.DBLogic.g_instance.getGunProfileData(gunProfileName)
        if not self.__gunProfile:
            LOG_ERROR('invalid gun profile', gunProfileName)
        self.__eventManager = Event.EventManager()
        self.eGunOverHeat = Event.Event(self.__eventManager)
        self.ammoBelt = AmmoBelt(self.gunDescription, ammoBelt, self.__gunProfile)
        self.restart()

    def destroy(self):
        self.__eventManager.clear()

    @property
    def guns(self):
        return self.__guns

    @property
    def groupID(self):
        return self.__groupID

    @property
    def size(self):
        return self.__size

    @property
    def gunProfile(self):
        return self.__gunProfile

    @property
    def dispersionAngle(self):
        return self.__dispersionAngle

    @property
    def reductionAngle(self):
        return self.__reductionAngle

    @property
    def recoilThrust(self):
        return self.__recoilThrust * self.__size

    @property
    def autoguiderAngle(self):
        return self.__autoguiderAngle

    def __dispersionCalc(self, dt, vibr, ampl, angBraking):
        return (vibr - ampl) * math.exp(-dt / angBraking) + ampl

    def reductionIncrease(self, dt):
        self.__reductionAngle = self.__dispersionCalc(dt, self.__reductionAngle, self.__recoilDispersion, self.__overheatingFullTime / 3.0)

    def reductionDecrease(self, dt):
        self.__reductionAngle = self.__dispersionCalc(dt, self.__reductionAngle, 0.0, self.__overheatingFullTime / 6.0)

    @property
    def dps(self):
        """
        calculate DPS for this Gun with current ammo belt
        function does the heavy calculations if necessary reuse caches the result
        """
        dps = calculateGunDPS('firePower', self.ammoBelt.shotData, self.gunDescription, self.__dispersionAngle, self.__recoilDispersion, self.__overheatingFullTime)
        return dps * self.__size

    @property
    def fullDPS(self):
        """
        calculate fullDPS for this Gun with current ammo belt
        """
        return self.gunDescription.DPS * self.__size

    def backup(self):
        return {'temperature': self.temperature,
         'timers': self.getReloadTimer()}

    def restoreFromBackup(self, backup):
        self.setReloadTimer(backup['timers'])
        self.temperature = backup['temperature']

    def restart(self):
        self.reload()
        self.temperature = 0.0
        self.__reductionAngle = 0.0
        self.__recoilThrust = 0.0

    def getSyncData(self):
        return self.temperature

    def sync(self, temperature, reloadTimer):
        self.temperature = temperature
        self.__reloadTimer = reloadTimer

    def reload(self):
        self.__reloadTimer = 0.0

    def update(self, dt, isFiring):
        if isFiring:
            self.__reloadTimer -= dt
            self.reductionIncrease(dt)
            gunData = self.gunDescription
            self.__recoilThrust = gunData.bulletMass * gunData.bulletSpeed * gunData.RPM / 60.0
        else:
            if self.__reloadTimer > 0:
                self.__reloadTimer -= dt
            if self.__reloadTimer <= 0:
                self.__reloadTimer = 0.0
                self.temperature = max(self.temperature - COOLING_PER_SEC_TEMPERATURE_PRC * dt * self.__coolingCFC, 0.0)
            self.reductionDecrease(dt)
        if isFiring:
            self.reductionIncrease(dt)
            gunData = self.gunDescription
            self.__recoilThrust = gunData.bulletMass * gunData.bulletSpeed * gunData.RPM / 60.0
        else:
            self.reductionDecrease(dt)
            self.__recoilThrust = 0

    def clearTemperature(self, prc):
        if self.temperature > 0:
            self.temperature = max(0, self.temperature - GUN_OVERHEATING_TEMPERATURE * prc)
            return True
        return False

    def isReady(self):
        return self.__reloadTimer <= 0

    def shoot(self, dt):
        shootTime = dt + self.__reloadTimer
        reloadTime = 60.0 / (self.gunDescription.RPM if self.temperature < GUN_OVERHEATING_TEMPERATURE else self.gunDescription.RPM * self.gunDescription.overheatedRPM)
        self.__reloadTimer += reloadTime
        if self.NOT_FREE_GUNS_FIRING:
            newTemp = min(self.temperature + GUN_OVERHEATING_TEMPERATURE / self.__overheatingFullTime * self.__gunOverheatingK * reloadTime, GUN_OVERHEATING_TEMPERATURE)
            if newTemp == GUN_OVERHEATING_TEMPERATURE and self.temperature < GUN_OVERHEATING_TEMPERATURE:
                self.temperature = GUN_OVERHEATING_TEMPERATURE
                self.eGunOverHeat()
            else:
                self.temperature = newTemp
        return shootTime

    def getReloadTimer(self):
        return self.__reloadTimer

    def setReloadTimer(self, v):
        self.__reloadTimer = v

    def onArmamentFreeUseChanged(self, flag):
        self.NOT_FREE_GUNS_FIRING = not flag