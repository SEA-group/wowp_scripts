# Embedded file name: scripts/client/ClientPlaneTurret/FireProcessor/TurretBulletsInterface.py
import math
import Math
from random import random
from db.DBLogic import g_instance as gDb
from GunsController.AmmoBelt import AmmoBelt
from consts import COMPONENT_TYPE, COLLISION_TYPE_TREE
from EntityHelpers import getBulletExplosionEffectFromMaterial, isPlayerAvatar
import CommonSettings
from consts import SERVER_TICK_LENGTH
_CLIENT_GUNNER_UPDATE_TIME = SERVER_TICK_LENGTH

class Dummy:
    pass


class BulletDescription(object):

    def __init__(self, bulletData, bulletEndPos, explosionEffect, treeEndPos, bulletSpeed, shootTime):
        self.bulletData = bulletData
        self.bulletEndPos = bulletEndPos
        self.explosionEffect = explosionEffect
        self.treeEndPos = treeEndPos
        self.bulletSpeed = bulletSpeed
        self.shootTime = shootTime


class TurretBulletsInterface(object):

    def __init__(self, avatar, gunDescription, turretPivot):
        self._avatar = avatar
        self._gunDescription = gunDescription
        self._turretPivot = turretPivot
        gunProfile = gDb.getGunProfileData(self._gunDescription.gunProfileName)
        beltDescription = gDb.getComponentByID(COMPONENT_TYPE.AMMOBELT, self._gunDescription.defaultBelt)
        self._ammoBelt = AmmoBelt(self._gunDescription, beltDescription, gunProfile)
        self._ammoBelt.registerShotRender()
        self.gun = Dummy()
        self.gun.RPM = self._gunDescription.RPM
        self.gun.uniqueId = id(self.gun)
        self.gun.shellPath = gunProfile.bulletShell if gunProfile else ''
        self.gun.shellOutInterval = gunProfile.shellOutInterval if gunProfile else ''
        self.gun.shellSyncTime = 0
        self.gun.gunProfileName = self._gunDescription.gunProfileName
        self._reloadTimer = 0.0
        self._reloadTime = 60.0 / self._gunDescription.RPM
        self._reduction = 0
        self._hasTarget = False
        self.__Q = Math.Quaternion()

    def updateReduction(self, value):
        self._reduction = value

    @property
    def bulletSpeed(self):
        return self._gunDescription.bulletSpeed

    def fire(self, hasTarget, shootPosition, gunIds):
        """
        @type hasTarget: bool
        @type shootPosition: Math.Vector3
        @type gunIds: list[int]
        """
        self._reloadTimer -= _CLIENT_GUNNER_UPDATE_TIME
        if self._reloadTimer > 0.0:
            return
        self._hasTarget = hasTarget
        while self._reloadTimer <= 0.0:
            bulletTime = -self._reloadTimer
            shootTime = self._generateBulletShootTime()
            self._reloadTimer += self._reloadTime
            self.gun.shootInfo = self._ammoBelt.extract()
            self._addBulletCluster(gunIds, bulletTime, shootTime, shootPosition - self._turretPosition)

    def reset(self):
        self.__Q = Math.Quaternion()
        self._reloadTimer = 0

    def dispose(self):
        self._avatar = None
        self._gunDescription = None
        self._turretPivot = None
        return

    @property
    def _planeVelocity(self):
        if self._hasTarget:
            return Math.Vector3(0, 0, 0)
        return self._avatar.getWorldVector()

    @property
    def _planePosition(self):
        return self._avatar.position

    @property
    def _planeRotation(self):
        return self._avatar.getRotation()

    @property
    def _turretPosition(self):
        return self._planePosition + self._planeRotation.rotateVec(self._turretPivot)

    def _generateBulletShootTime(self):
        return _CLIENT_GUNNER_UPDATE_TIME + self._reloadTimer + random() * self._ammoBelt.gunProfile.bulletGroupDispersionCfc * 60 / self._gunDescription.RPM

    def _addBulletCluster(self, gunIds, bulletTime, shootTime, bulletVector):
        for gunId in gunIds:
            bulletVector = self.__calculateBulletDispersion(bulletVector)
            bulletDescription = self._createBulletDescription(bulletTime, bulletVector, shootTime)
            self._addGunBullet(gunId, bulletDescription)
            if bulletDescription.treeEndPos:
                self._addTreeHitEffectBullet(bulletDescription)

    def _createBulletDescription(self, bulletTime, bulletVector, shootTime):
        bulletData = {'gunID': self._gunDescription.index,
         'isPlayer': self._avatar.isPlayer(),
         'bullets': []}
        timeToLive = self._getBulletTimeToLive(bulletVector)
        bulletVelocity = self._planeVelocity + bulletVector.getNormalized() * self._gunDescription.bulletSpeed
        bulletEndPos, terrainMatKind, treeEndPos = self._avatar.addBulletBody(0, self._turretPosition, bulletVelocity, bulletTime, timeToLive, False, bulletData)
        explosionEffect = self._getBulletExplosionEffect(terrainMatKind)
        return BulletDescription(bulletData, bulletEndPos, explosionEffect, treeEndPos, bulletVelocity.length, shootTime)

    def _addGunBullet(self, gunId, descr):
        actualFirePos = self._getFirePosition(gunId)
        bulletStartPos = actualFirePos if actualFirePos else self._turretPosition
        descr.bulletData['bullets'].append(self._avatar.addBullet(bulletStartPos, descr.bulletEndPos, descr.bulletSpeed, -descr.shootTime, self.gun, descr.explosionEffect, descr.shootTime, gunID=gunId, dPos=self._planeRotation.conjugate().rotateVec(bulletStartPos - self._planePosition)))

    def _getFirePosition(self, gunId):
        mm = self._avatar.controllers.get('modelManipulator')
        if mm:
            return mm.getTurretGunPos(gunId)
        else:
            return None

    def _addTreeHitEffectBullet(self, descr):
        descr.bulletData['bullets'].append(self._avatar.addInvisibleBullet(self._turretPosition, descr.treeEndPos, descr.bulletSpeed, -descr.shootTime, self.gun, self._getBulletExplosionEffect(COLLISION_TYPE_TREE)))

    def _getBulletTimeToLive(self, bulletVector):
        dy = bulletVector.y
        bulletDirection = bulletVector.getNormalized()
        timeToLive = dy / ((bulletDirection.y if bulletDirection.y else 0.1) * self._gunDescription.bulletSpeed)
        if timeToLive < 0.0:
            timeToLive = self._gunDescription.bulletFlyDist / self._gunDescription.bulletSpeed
        return timeToLive

    def _getBulletExplosionEffect(self, materialType):
        materialName = 'air' if materialType == -1 else gDb.getMaterialName(materialType)
        return getBulletExplosionEffectFromMaterial(self._ammoBelt.gunProfile, materialName)

    def __calculateBulletDispersion(self, vector):
        frontAxis = Math.Vector3(vector)
        rollAngle = 2 * math.pi * random()
        upAxis = vector.cross(Math.Vector3(0, 1, 0))
        reduction = self._reduction
        upAngle = (CommonSettings.TURRET_BULLET_DISPERSION_MAX * (1 - reduction) + CommonSettings.TURRET_BULLET_DISPERSION_MIN * reduction) * math.pow(random(), 1.5)
        self.__Q.fromAngleAxis(upAngle, upAxis)
        vector = self.__Q.rotateVec(vector)
        self.__Q.fromAngleAxis(rollAngle, frontAxis)
        vector = self.__Q.rotateVec(vector)
        return vector