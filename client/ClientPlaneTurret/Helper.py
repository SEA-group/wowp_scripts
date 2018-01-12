# Embedded file name: scripts/client/ClientPlaneTurret/Helper.py
from CommonSettings import turretControlAimConeAngle, turretGunLockConeAngle, TURRET_LOSE_BORDER_ZONE, turretPartCritTime
from consts import WORLD_SCALING
from Math import Vector3
import BigWorld

class DummySoundObject(object):

    def play(self):
        pass

    def stop(self, value):
        pass


class Context(object):

    def __init__(self, plane, turret, gunProfile, gunDescription, sector, mmGunData):
        self.__plane = plane
        self.__turret = turret
        self.__sector = sector
        self.__gunProfile = gunProfile
        self.__gunDescription = gunDescription
        gunIDIndex = 2
        self._gunIds = [ mmd[gunIDIndex] for mmd in mmGunData ]
        self.__soundObject = DummySoundObject()

    def registerSoundObject(self, so):
        self.__soundObject = so

    def onFireStarted(self):
        self.__soundObject.play()

    def onFireEnded(self):
        self.__soundObject.stop(False)

    @property
    def critTime(self):
        return turretPartCritTime

    @property
    def time(self):
        return BigWorld.serverTime()

    @property
    def teamIndex(self):
        return self.__plane.teamIndex

    @property
    def spaceID(self):
        return self.__plane.spaceID

    @property
    def state(self):
        return self.__plane.state

    @property
    def baseRotation(self):
        return self.__plane.getRotation()

    @property
    def basePosition(self):
        return self.__plane.position

    @property
    def planeVector(self):
        return self.__plane.getWorldVector()

    @property
    def targetLockShootDistance(self):
        return self.__turret.targetLockShootDistance

    @property
    def turretControlAimConeAngle(self):
        return turretControlAimConeAngle

    @property
    def turretGunLockConeAngle(self):
        return turretGunLockConeAngle

    @property
    def turretLoseBorderZone(self):
        return TURRET_LOSE_BORDER_ZONE

    @property
    def turretAggroSwitchK(self):
        return self.__turret.aggroSwitchK

    def getAggroK(self, globalID):
        return self.__turret.aircraftClassSettings.getDataForClassByGlobalID(globalID)['aggroK']

    def getDamageK(self, globalID):
        return self.__turret.aircraftClassSettings.getDataForClassByGlobalID(globalID)['damageK']

    def inSector(self, direction):
        return self.__sector.inSector(direction)

    @property
    def sectorDirection(self):
        return self.__sector.direction

    @property
    def sectorOrientation(self):
        return self.__sector.orientation

    def getOutNormZone(self, direction, normAngle):
        return self.__sector.getOutNormZone(direction, normAngle)

    @property
    def gunIds(self):
        return self._gunIds

    @property
    def aimType(self):
        return self.__gunProfile.aimType

    @property
    def RPM(self):
        return self.__gunDescription.RPM


class PlayerGunnerDefaultContext(object):

    def __init__(self, plane):
        self.__plane = plane

    @property
    def gunIds(self):
        return []

    @property
    def teamIndex(self):
        return self.__plane.teamIndex

    @property
    def spaceID(self):
        return self.__plane.spaceID

    @property
    def state(self):
        return self.__plane.state

    @property
    def baseRotation(self):
        return self.__plane.getRotation()

    @property
    def basePosition(self):
        return self.__plane.position

    @property
    def turretControlAimConeAngle(self):
        return turretControlAimConeAngle

    @property
    def turretLoseBorderZone(self):
        return TURRET_LOSE_BORDER_ZONE

    @property
    def targetLockShootDistance(self):
        return 1000 * WORLD_SCALING


class TurretShareData(object):

    def __init__(self):
        self.targetID = -1
        self.targetDirection = Vector3(0, 0, 0)
        self.isGunnerFiring = False
        self.gunDirection = Vector3(0, 0, 0)
        self.isGunCanShoot = {}
        self.controlMatrix = None
        self.reduction = 0
        return

    def isFiring(self):
        return self.isGunnerFiring and any(self.isGunCanShoot.values())


class TurretState(object):
    alive = 0
    dead = 1