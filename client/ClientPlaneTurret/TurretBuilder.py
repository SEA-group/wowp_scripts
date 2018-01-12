# Embedded file name: scripts/client/ClientPlaneTurret/TurretBuilder.py
import Math
import db.DBLogic
from ClientPlaneTurret.Helper import Context
from ClientPlaneTurret.Turret import Turret
from ClientPlaneTurret.TurretGun import TurretGun
from ClientPlaneTurret.SyncDataRouter import SynDataRouter
from ClientPlaneTurret.GunnerProxy import GunnerProxy
from ClientPlaneTurret.FireProcessor.FireProcessor import FireProcessor
from ClientPlaneTurret.FireProcessor.TurretBulletsInterface import TurretBulletsInterface
from ClientPlaneTurret.TurretSector import FireSector

def prepareSectorData(ly, ry, pu, pd):
    dirYaw = (ly + ry) * 0.5
    orientation = Math.Quaternion()
    orientation.fromEuler(0, 0, dirYaw)
    ly = dirYaw - ly
    ry = dirYaw - ry
    return (orientation,
     pu,
     pd,
     ly,
     ry)


class TurretDataAdapter(object):

    def __init__(self, turretName, gunnerPart):
        self._gunnerPart = gunnerPart
        self._turretSettings = db.DBLogic.g_instance.getTurretData(turretName)
        self._gunDescription = db.DBLogic.g_instance.getGunData(self._turretSettings.gunName)
        self._profile = db.DBLogic.g_instance.getGunProfileData(self._gunDescription.gunProfileName)
        self._uniqueId = id(self)
        self._mmGunData = []
        for i, flamePath in enumerate(self._turretSettings.flamePathes):
            shellPath = self._turretSettings.shellPathes[i] if self._turretSettings.shellPathes and i < len(self._turretSettings.shellPathes) else ''
            self._mmGunData.append((flamePath,
             self._profile.bulletShot[0],
             self._uniqueId + i,
             shellPath,
             self._profile.bulletShell))

    def turretData(self):
        return self._turretSettings

    def mmData(self):
        return self._mmGunData

    def sectorData(self):
        ts = self._turretSettings
        return prepareSectorData(ts.yawMax, ts.yawMin, ts.pitchMax, ts.pitchMin)

    def bulletInterfaceData(self):
        return (self._gunDescription, Math.Vector3(self._gunnerPart.bboxes.getMainBBoxPosition()))

    @property
    def gunProfile(self):
        return self._profile


class PrepareTurretData(object):

    def __init__(self, tdb):
        self._turretSoundIDsByTurretID = {}
        self._turretGunsData = []
        self._turretsData = {}
        for ID, data in tdb.iteritems():
            adaptedData = TurretDataAdapter(*data)
            self._turretsData[ID] = adaptedData
            self._turretSoundIDsByTurretID[ID] = adaptedData.gunProfile.sounds.weaponSoundID
            self._turretGunsData.extend(adaptedData.mmData())

    @property
    def turretsData(self):
        return self._turretsData

    @property
    def turretSoundIDsByTurretID(self):
        return self._turretSoundIDsByTurretID

    @property
    def turretGunsData(self):
        return self._turretGunsData


class PlaneTurretBuilder(object):

    def __init__(self, turretsData):
        self._turretsData = turretsData

    @staticmethod
    def _createTurret(ID, owner, data):
        """
        @type ID: int
        @type data: TurretDataAdapter
        @rtype: Turret
        """
        sector = FireSector(*data.sectorData())
        gunDescription, pivot = data.bulletInterfaceData()
        context = Context(owner, data.turretData(), data.gunProfile, gunDescription, sector, data.mmData())
        gun = TurretGun(ID, context, pivot, owner.controllers['modelManipulator'].getTurretController())
        gunner = GunnerProxy(SynDataRouter(ID, owner))
        fire = FireProcessor(context, TurretBulletsInterface(owner, gunDescription, pivot))
        return Turret(context, gun, gunner, fire)

    def create(self, owner):
        return dict(((ID, self._createTurret(ID, owner, data)) for ID, data in self._turretsData.iteritems()))