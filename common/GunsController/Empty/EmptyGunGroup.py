# Embedded file name: scripts/common/GunsController/Empty/EmptyGunGroup.py
import Event
from ..Gun import Gun
from .EmptyAmmoBelt import EmptyAmmoBelt
from SyncedRandom import SyncedRandom
from .EmptyGunGroupSettings import bulletFlyDist, RPM, aimType, name, mass, caliber, gunProfileName, flamePath, bulletSpeed, bulletShot

class EmptyGunInfo(object):

    def __init__(self):
        pass

    @property
    def flamePath(self):
        return flamePath


class EmptyGunDescription(object):

    def __init__(self):
        pass

    @property
    def bulletFlyDist(self):
        return bulletFlyDist

    @property
    def bulletSpeed(self):
        return bulletSpeed

    @property
    def gunProfileName(self):
        return gunProfileName

    @property
    def RPM(self):
        return RPM

    @property
    def caliber(self):
        return caliber

    @property
    def name(self):
        return name

    @property
    def mass(self):
        return mass


class EmptyGunProfile(object):

    class DummySound(object):
        weaponSoundID = -1

    def __init__(self):
        self.sounds = EmptyGunProfile.DummySound()

    @property
    def aimType(self):
        return aimType

    @property
    def bulletShot(self):
        return bulletShot


class EmptyGunGroup(object):

    def __init__(self, pivots, *args, **kwargs):
        self.syncedRandom = SyncedRandom()
        self.gunDescription = EmptyGunDescription()
        self.clientProcessedBulletCount = 0
        self.gunName = name
        self.temperature = 0.0
        self.__guns = [Gun(EmptyGunInfo(), pivots, EmptyGunDescription())]
        self.__eventManager = Event.EventManager()
        self.eGunOverHeat = Event.Event(self.__eventManager)
        self.ammoBelt = EmptyAmmoBelt(EmptyGunDescription(), EmptyGunProfile())

    def destroy(self):
        self.__eventManager.clear()

    def restart(self):
        pass

    @property
    def guns(self):
        return self.__guns

    @property
    def groupID(self):
        return 0

    @property
    def size(self):
        return 1

    @property
    def gunProfile(self):
        return EmptyGunProfile()

    @property
    def dispersionAngle(self):
        return 0

    @property
    def reductionAngle(self):
        return 0

    @property
    def recoilThrust(self):
        return 0

    @property
    def autoguiderAngle(self):
        return 0

    def reductionIncrease(self, dt):
        pass

    def reductionDecrease(self, dt):
        pass

    @property
    def dps(self):
        return 0

    @property
    def fullDPS(self):
        return 0

    def backup(self):
        return {}

    def restoreFromBackup(self, backup):
        pass

    def getSyncData(self):
        return 0

    def sync(self, temperature, reloadTimer):
        pass

    def reload(self):
        pass

    def update(self, dt, isFiring):
        pass

    def clearTemperature(self, prc):
        return False

    def isReady(self):
        return False

    def shoot(self, dt):
        return dt

    def getReloadTimer(self):
        return 0

    def setReloadTimer(self, v):
        pass

    def onArmamentFreeUseChanged(self, flag):
        pass