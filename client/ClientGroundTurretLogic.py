# Embedded file name: scripts/client/ClientGroundTurretLogic.py
from random import random
import BigWorld
import Math
from SyncedRandom import SyncedRandom
from consts import SERVER_TICK_LENGTH, COLLISION_TYPE_TREE, COMPONENT_TYPE
from turrets.BaseTurretLogic import BaseTurretLogic, rotateAxisWithSpeed, rotateAxisWithSpeedEx, getRotationAnglesOnTarget
import db.DBLogic
from GunsController.AmmoBelt import AmmoBelt
from EntityHelpers import getBulletExplosionEffectFromMaterial
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG
from Event import Event, EventManager
from Math import Vector3

class Dummy:
    pass


class FakeEntity(object):

    def __init__(self, position):
        self.position = position
        self.vector = Vector3()
        self.filter = {}
        self.lockedByTurretsCounter = 1
        moveHistoryStepsCount = 4
        self.moveHistory = [ position for _ in xrange(moveHistoryStepsCount) ]


class GunnerRecord(object):

    def __init__(self, partType, isAlive, yaw, pitch, ammoBelt):
        self.partType = partType
        self.relativePos = partType.bboxes.getMainBBoxPosition()
        self.isAlive = isAlive
        self.yaw = yaw
        self.pitch = pitch
        self.position = Math.Vector3()
        self.rotation = Math.Quaternion()
        self.uniqueId = id(self)
        self.ammoBelt = ammoBelt
        ammoBelt.registerShotRender()
        self.gun = Dummy()
        self.gun.uniqueId = self.uniqueId
        self.gun.shellPath = ''
        self.gun.shellOutInterval = 1.0
        self.gun.shellSyncTime = 0


class ClientGroundTurretLogic(BaseTurretLogic):

    def __init__(self, owner, gunnersParts, turretName):
        BaseTurretLogic.__init__(self, owner, gunnersParts, turretName)
        if owner:
            self.__setUpdateCallback()
        else:
            self.__updateCallBack = None
        self.__sound = None
        self.__soundWasStarted = False
        self.__startFireTime = 0
        self.__burstTime = self.scheme.BurstTime
        self.__curBurstTilesCounter = 0
        self._createEvents()
        return

    def _createEvents(self):
        self._eventManager = EventManager()
        self.eTurretTargetChanged = Event(self._eventManager)
        self.eTurretShoot = Event(self._eventManager)
        self.eGunnerStateChanged = Event(self._eventManager)
        self.eSetControlMtx = Event(self._eventManager)

    def _initParts(self, gunnersParts):
        self.syncedRandom = SyncedRandom()
        initYaw = (self.settings.yawMax + self.settings.yawMin) * 0.5
        initPitch = (self.settings.pitchMax + self.settings.pitchMin) * 0.5
        initYaw = 0
        initPitch = 0
        beltDescription = db.DBLogic.g_instance.getComponentByID(COMPONENT_TYPE.AMMOBELT, self.gunDescription.defaultBelt)
        self.__gunners = dict(((partID, GunnerRecord(data[1], data[0], initYaw, initPitch, AmmoBelt(self.gunDescription, beltDescription, self.gunDescription))) for partID, data in gunnersParts.items()))

    def linkSound(self, turretId, so):
        self.__sound = so

    @property
    def tilesPerBurst(self):
        return self.scheme.BurstTime * self.scheme.RPS

    @property
    def battleLevel(self):
        return BigWorld.player().battleLevel

    def _makeLocalProperties(self):
        if self._owner:
            BaseTurretLogic._makeLocalProperties(self)
            self.__isFiring = False
            self.__reloadTimer = 0.0
            self.__reloadTime = 1.0 / self.scheme.RPS
            self.__gunProfile = db.DBLogic.g_instance.getGunProfileData(self.gunDescription.gunProfileName)

    @property
    def gunners(self):
        return self.__gunners

    def setOwner(self, owner):
        self._owner = owner
        self._strategy.setOwnerEntity(owner)
        if owner:
            self._makeLocalProperties()
            self.__setUpdateCallback()
        elif self.__updateCallBack:
            BigWorld.cancelCallback(self.__updateCallBack)
            self.__updateCallBack = None
        return

    def __setUpdateCallback(self):
        self.__updateCallBack = BigWorld.callback(SERVER_TICK_LENGTH, self.update)

    def destroy(self):
        BaseTurretLogic.destroy(self)
        if self.__updateCallBack:
            BigWorld.cancelCallback(self.__updateCallBack)
            self.__updateCallBack = None
        return

    def onPartStateChanged(self, part):
        gunner = self.__gunners.get(part.partID, None)
        if gunner:
            LOG_DEBUG_DEV(self._owner.id, 'onGunnerStateChanged', part.partID, part.stateID)
            gunner.isAlive = part.isAlive
        return

    def eTurretTargetChanged(self, targetId):
        pass

    def update(self, dt = 0):
        if not self._owner:
            return
        else:
            self.__setUpdateCallback()
            if hasattr(self._owner, 'turretTargetID') and self._owner.turretTargetID != -1:
                targetEntity = BigWorld.entities.get(self._owner.turretTargetID, None) if hasattr(self._owner, 'turretTargetID') else None
                matrix = Math.Matrix()
                if targetEntity and targetEntity.inWorld:
                    targetImaginePos = targetEntity.position
                    matrix.translation = targetImaginePos
                else:
                    targetImaginePos = self._owner.turretTargetPosition
                    matrix.translation = targetImaginePos
                self.eSetControlMtx(matrix)
                self.eTurretTargetChanged(self._owner.turretTargetID)
                playSound = False
                if targetImaginePos:
                    ownRotation = Math.Quaternion()
                    ownRotation.fromEuler(self._owner.roll, self._owner.pitch, self._owner.yaw)
                    for gunner in self.__gunners.values():
                        if gunner.isAlive:
                            gunner.position = self._owner.position + Math.Quaternion(ownRotation).rotateVec(gunner.relativePos)
                            yawOnTarget, pitchOnTarget = getRotationAnglesOnTarget(gunner.position, ownRotation, targetImaginePos)
                            gunner.yaw = rotateAxisWithSpeed(gunner.yaw, yawOnTarget, self.settings.yawSpeed, self.settings.yawMin, self.settings.yawMax)
                            gunner.pitch = rotateAxisWithSpeedEx(gunner.pitch, pitchOnTarget, self.settings.pitchSpeed, self.settings.pitchMin, self.settings.pitchMax)
                            gunQuat = Math.Quaternion(ownRotation)
                            gunQuat.normalise()
                            axisX = gunQuat.getAxisX()
                            axisY = gunQuat.getAxisY()
                            q = Math.Quaternion()
                            q.fromAngleAxis(-gunner.pitch, axisX)
                            gunQuat.mulLeft(q)
                            q.fromAngleAxis(gunner.yaw, axisY)
                            gunQuat.mulLeft(q)
                            gunner.rotation = gunQuat
                            if self.__isFiring:
                                self.__reloadTimer -= SERVER_TICK_LENGTH
                                if self.__reloadTimer <= 0.0:
                                    self.__shoot(gunner)
                                    playSound = True
                            elif self.__curBurstTilesCounter < self._owner.turretShootCount:
                                self.__reloadTimer -= SERVER_TICK_LENGTH
                                if self.__reloadTimer <= 0.0:
                                    self.__shoot(gunner)
                                    playSound = True

                if playSound and self.__sound and not self.__soundWasStarted:
                    self.__soundWasStarted = True
                    self.__sound.play()
                    self._owner.updateTurretsRotations(self.__gunners)
            return

    def __drawLine(self, pos):
        from DebugManager import COLORS
        BigWorld.clearGroup('shoot_xxx2')
        BigWorld.addDrawLine('shoot_xxx2', self._owner.position, pos, COLORS.RED)

    def onChangeShootingSync(self, flag):
        self.syncedRandom.state = flag

    def onChangeFiring(self, flag):
        if self.__isFiring != flag:
            self.__isFiring = flag
            self.__reloadTimer = 0.0
            if self.__isFiring:
                self.__curBurstTilesCounter = 0
                self.__startFireTime = BigWorld.time()
            elif self._owner.turretTargetID == -1:
                self.__curBurstTilesCounter = self.tilesPerBurst
            if self.__sound and not flag:
                self.__sound.stop(False)
                self.__soundWasStarted = False

    def getEntityVector(self, entity):
        return getattr(entity.filter, 'vector', Math.Vector3())

    def __shoot(self, gunner):
        targetEntity = BigWorld.entities.get(self._owner.turretTargetID, None) if hasattr(self._owner, 'turretTargetID') else None
        if not targetEntity:
            targetEntity = FakeEntity(self._owner.turretTargetPosition)
        targetImaginePos = self._strategy.calculateImaginePosition(targetEntity, self.tilesPerBurst, self.__curBurstTilesCounter, self.syncedRandom)
        if targetImaginePos is None:
            return
        else:
            bulletDir = targetImaginePos - gunner.position
            dy = bulletDir.y
            bulletDir.normalise()
            bulletVelocity = self.getEntityVector(self._owner) + bulletDir * self.gunDescription.bulletSpeed
            bulletSpeed = bulletVelocity.length
            self.__curBurstTilesCounter += 1
            self.__reloadTimer = self.__reloadTime
            count = 0
            countMax = self._strategy.calculateBulletsCount() + 1
            reloadTestTime = self.__reloadTime / countMax
            while countMax > count:
                if count > 0 or self.isHighAltitudeTurret is False:
                    bulletDir = targetImaginePos - gunner.position + self._getRandomVectorForFakeBullets()
                    dy = bulletDir.y
                    bulletDir.normalise()
                    bulletVelocity = self.getEntityVector(self._owner) + bulletDir * self.gunDescription.bulletSpeed
                    bulletSpeed = bulletVelocity.length
                data = {'gunID': self.gunDescription.index,
                 'isPlayer': self._owner.isPlayer(),
                 'bullets': []}
                bulletTime = SERVER_TICK_LENGTH - count * reloadTestTime
                shootTime = count * reloadTestTime + random() * self.__gunProfile.bulletGroupDispersionCfc * SERVER_TICK_LENGTH / countMax
                count += 1
                explosionEffect = getBulletExplosionEffectFromMaterial(self.__gunProfile, 'air')
                timeToLive = self._strategy.calculateTimeToLive(dy, bulletDir, self.gunDescription.bulletSpeed)
                if timeToLive < 0.0:
                    timeToLive = self.gunDescription.bulletFlyDist / self.gunDescription.bulletSpeed
                bulletEndPos, terrainMatKind, treeEndPos = self._owner.addBulletBody(0, gunner.position, bulletVelocity, bulletTime, timeToLive, False, data)
                if terrainMatKind != -1:
                    explosionEffect = getBulletExplosionEffectFromMaterial(self.__gunProfile, db.DBLogic.g_instance.getMaterialName(terrainMatKind))
                gunner.gun.shootInfo = gunner.ammoBelt.extract()
                if self.settings.flamePathes:
                    for i, _ in enumerate(self.settings.flamePathes):
                        actualFirePos = self.getFirePosition(gunner.gun.uniqueId + i)
                        data['bullets'].append(self._owner.addBullet(actualFirePos if actualFirePos else gunner.position, bulletEndPos, bulletSpeed, -shootTime, gunner.gun, explosionEffect, shootTime, gunID=gunner.gun.uniqueId + i))

                else:
                    data['bullets'].append(self._owner.addBullet(gunner.position, bulletEndPos, bulletSpeed, -shootTime, gunner.gun, explosionEffect))
                if treeEndPos:
                    data['bullets'].append(self._owner.addInvisibleBullet(gunner.position, treeEndPos, bulletSpeed, -shootTime, gunner.gun, getBulletExplosionEffectFromMaterial(self.__gunProfile, db.DBLogic.g_instance.getMaterialName(COLLISION_TYPE_TREE))))

            return

    def getFirePosition(self, gunId):
        if self._owner:
            if 'modelManipulator' in self._owner.controllers:
                mm = self._owner.controllers['modelManipulator']
                return mm.getTurretGunPos(gunId)
        return None

    def _getRandomVectorForFakeBullets(self):
        randomKoef = 2
        randomVector = Math.Vector3((random() - 0.5) * 2 * randomKoef, (random() - 0.5) * 2 * randomKoef, (random() - 0.5) * 2 * randomKoef)
        return randomVector