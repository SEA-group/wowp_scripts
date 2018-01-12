# Embedded file name: scripts/common/turrets/BaseShootStratery.py
import BigWorld
import Math
import math
from debug_utils import *
from EntityHelpers import EntityStates, isTeamObject
from consts import HEALTH_DAMAGE_PART_ID, DAMAGE_REASON, ACTION_DEALER, TEAM_OBJECT_CLASS_NAMES, IS_CELLAPP, IS_CLIENT, TurretDamageDealer
from Math import Vector3, Quaternion
import db.DBLogic
from _airplanesConfigurations_db import airplanesConfigurations

def getPlaneType(globalID):
    """
    :returns: consts.PLANE_TYPE
    """
    return db.DBLogic.g_instance.getAircraftData(airplanesConfigurations[globalID].planeID).airplane.planeType


class BaseShootStrategy(object):

    def __init__(self, owner):
        self._ownerLogic = owner
        self._ownerEntity = owner._owner
        self._ignoreList = []
        self.firstShootPosition = Vector3(0, 0, 0)
        self.angelK = 1

    def setIgnoreTargetsList(self, ignoreList):
        self._ignoreList = ignoreList

    def setOwnerEntity(self, entity):
        self._ownerEntity = entity

    def destroy(self):
        self._ownerLogic = None
        self._ownerEntity = None
        return

    def _specConditions(self, pos):
        return True

    def _isValidTarget(self, target):
        return EntityStates.inState(target, EntityStates.GAME) and self._ownerEntity.teamIndex != target.teamIndex and not BigWorld.hm_collideSimple(self._ownerEntity.spaceID, self._ownerEntity.position, target.position) and target.id not in self._ignoreList

    def processTileDamage(self, targetID, startPos, targetImaginePos, damagePerTile, aliveTurretsCount, reduction):
        settings = self._ownerLogic.settings
        tileDir = targetImaginePos - startPos
        tileDir.normalise()
        tileNextTickPos = targetImaginePos + self._ownerLogic.gunDescription.bulletSpeed * 0.1 * tileDir
        tilePrevTickPos = targetImaginePos - self._ownerLogic.gunDescription.bulletSpeed * 0.1 * tileDir
        collidedParts = BigWorld.hm_collideParts(self._ownerEntity.spaceID, tilePrevTickPos, tileNextTickPos, self._ownerEntity)
        victim = None
        victimDist = 0
        precisionK = 1.0
        if collidedParts:
            for entity, partID, position in collidedParts:
                dist = (targetImaginePos - position).length
                if not isTeamObject(entity) and (not victim or dist < victimDist):
                    victim = entity
                    victimDist = dist

        if victim:
            planeType = getPlaneType(victim.globalID)
            koef = self._ownerLogic.scheme.PlaneTypeDamageFactor.get(planeType, 0.1)
            damage = damagePerTile * koef
            if damage > 0:
                victim.receiveTurretDamage(self._ownerEntity, damage, self._ownerEntity.objTypeID, self._ownerEntity.entityGroupMask, self._ownerEntity.teamIndex, self._ownerEntity.unitNumber, settings.critAbility * self._ownerLogic.TURRET_INFLICT_CRIT, self._ownerLogic.targetSkillModsActivity, DAMAGE_REASON.BULLET, TurretDamageDealer.undefined)
                actionDealer = ACTION_DEALER.TURRET if self._ownerEntity.className in TEAM_OBJECT_CLASS_NAMES else ACTION_DEALER.GUNNER
                self._ownerEntity.onHitTarget([victim], DAMAGE_REASON.AA_EXPLOSION, actionDealer)
        return

    def getRandomVector(self, syncedRandom, turretsCount):
        randomKoef = self._ownerLogic.scheme.ShootRandomizeTable.get(turretsCount, 1)
        randomVector = Math.Vector3((syncedRandom.random() - 0.5) * 2 * randomKoef, (syncedRandom.random() - 0.5) * 2 * randomKoef, (syncedRandom.random() - 0.5) * 2 * randomKoef)
        return randomVector

    def calculateImaginePosition(self, targetEntity, burst, current, syncedRandom):
        return self._calculateTargetImaginePos(targetEntity, burst, current, syncedRandom)

    def _calculateTargetImaginePos(self, targetEntity, shootsCount, shootIndex, syncedRandom):
        return self._calculateTargetImaginePosByAngel(targetEntity, shootsCount, shootIndex, syncedRandom)

    def _calculateTargetImaginePosCommon(self, targetEntity):
        oVector = self._ownerLogic.getEntityVector(self._ownerEntity)
        tVector = self._ownerLogic.getEntityVector(targetEntity)
        targetHitTime = BigWorld.collisionTime(self._ownerEntity.position, oVector, targetEntity.position, tVector, self._ownerLogic.gunDescription.bulletSpeed)
        if targetHitTime >= 0:
            return targetEntity.position + targetHitTime * tVector
        LOG_MX('Target is too fast')

    def calculateBulletsCount(self):
        return 1

    def calculateTimeToLive(self, dy, bulletDir, bulletSpeed):
        return dy / ((bulletDir.y if bulletDir.y else 0.1) * bulletSpeed)

    def __getDistanceDelta(self, shootIndex, shootsCount, turretsCount):
        aimingPercent = self._ownerLogic.scheme.AimingTable.get(turretsCount, 33)
        predictionPoint = self._ownerLogic.scheme.Prediction
        half = shootsCount * aimingPercent / 100.0 * 1.0
        shootIndex = half - shootIndex
        shootIndex = half if shootIndex > half else shootIndex
        shootIndex = 0 if shootIndex < 0 else shootIndex
        currentKoef = predictionPoint * shootIndex / half
        return currentKoef

    def _calculateTargetImaginePosByAngel(self, targetEntity, burst, current, syncedRandom):
        koef = self._ownerLogic.scheme.Prediction
        oVector = self._ownerLogic.getEntityVector(self._ownerEntity)
        tVector = Vector3(self._ownerLogic.getEntityVector(targetEntity))
        if current == 0:
            targetHitTime = BigWorld.collisionTime(self._ownerEntity.position, oVector, targetEntity.position, tVector, self._ownerLogic.gunDescription.bulletSpeed)
            result = targetEntity.position + targetHitTime * tVector * koef
            self.firstShootPosition = result
            self.angelK = self._ownerLogic.scheme.SpeedAngle
            return self.firstShootPosition
        turretsCount = targetEntity.lockedByTurretsCounter
        currentKoef = self.__getDistanceDelta(current, burst, turretsCount)
        if currentKoef <= 0.5:
            if self.angelK != self._ownerLogic.scheme.SpeedAngleMax:
                self.angelK = self._ownerLogic.scheme.SpeedAngleMax
        oVector = self._ownerLogic.getEntityVector(self._ownerEntity)
        tVector = self._ownerLogic.getEntityVector(targetEntity)
        targetHitTime = BigWorld.collisionTime(self._ownerEntity.position, oVector, targetEntity.position, tVector, self._ownerLogic.gunDescription.bulletSpeed)
        result = targetEntity.position + targetHitTime * tVector
        self.__shootDirection = self.firstShootPosition - self._ownerEntity.position
        len = self.__shootDirection.length
        k2 = self.angelK
        speedAngle = 0.0175 * k2
        rotateVector = (result - self._ownerEntity.position).getNormalized()
        tempShoot = self.__shootDirection.getNormalized()
        right = tempShoot.cross(rotateVector)
        roatateAngle = tempShoot.angle(rotateVector)
        rotAngle = roatateAngle if roatateAngle < speedAngle else speedAngle
        rot = Quaternion()
        rot.fromAngleAxis(rotAngle, right)
        tempVec = rot.rotateVec(tempShoot)
        self.firstShootPosition = self._ownerEntity.position + tempVec * len
        return self.firstShootPosition