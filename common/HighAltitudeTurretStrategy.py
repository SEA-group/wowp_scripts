# Embedded file name: scripts/common/HighAltitudeTurretStrategy.py
import BigWorld
import Math
import math
from debug_utils import *
from Math import Vector3, Quaternion
from EntityHelpers import isTeamObject
from consts import DAMAGE_REASON, HEALTH_DAMAGE_PART_ID, ACTION_DEALER, TURRET_RATION_FOR_EXTREMUM_TARGET_ALTITUDE, IS_CLIENT, TurretDamageDealer
from random import random
from turrets.BaseShootStratery import BaseShootStrategy, getPlaneType
TARGET_SPEED_K = 1.1

class HighAltitudeTurretStrategy(BaseShootStrategy):

    def __init__(self, owner):
        super(HighAltitudeTurretStrategy, self).__init__(owner)
        self.firstShootPosition = Math.Vector3(1, 1, 1)

    def _isValidTarget(self, target):
        vDist = target.position.y - self._ownerEntity.position.y
        isHeightGood = self._ownerLogic.scheme.MinTargetAltitude <= vDist <= self._ownerLogic.scheme.TargetShootDistance
        posXZ = Vector3(self._ownerEntity.position.x, 0, self._ownerEntity.position.z)
        intentPosXZ = Vector3(target.position.x, 0, target.position.z)
        isCloseEnough = posXZ.distTo(intentPosXZ) < self._ownerLogic.scheme.HighTargetShootDistanceRadius
        return isHeightGood and isCloseEnough and BaseShootStrategy._isValidTarget(self, target)

    def processTileDamage(self, targetID, startPos, targetImaginePos, damagePerTile, aliveTurretsCount, reduction):
        closestParts = BigWorld.hm_closestParts(self._ownerEntity.spaceID, targetImaginePos, self._ownerLogic.explosionRadius)
        if closestParts:
            victimsMap = {}
            for victim, partID, closestPos, dist in closestParts:
                isFriendlyVictim = victim.teamIndex == self._ownerEntity.teamIndex
                if not (isFriendlyVictim or isTeamObject(victim)):
                    prevData = victimsMap.get(victim, (partID, dist))
                    if dist <= prevData[1]:
                        victimsMap[victim] = (partID, dist)

            for victim, victimData in victimsMap.items():
                partID, dist = victimData
                self.__onDamageToVictimPart(victim, dist, damagePerTile, aliveTurretsCount, reduction)

        else:
            victim = BigWorld.entities.get(targetID)
            if victim:
                self.__onDamageToVictimPart(victim, (targetImaginePos - victim.position).length, damagePerTile, aliveTurretsCount, reduction)

    def __onDamageToVictimPart(self, victim, dist, damagePerTile, aliveTurretsCount, reduction):
        settings = self._ownerLogic.settings
        if dist > self._ownerLogic.explosionRadius:
            return
        planeType = getPlaneType(victim.globalID)
        koef = self._ownerLogic.scheme.PlaneTypeDamageFactor.get(planeType, 0.1)
        damage = damagePerTile * (1 - dist / self._ownerLogic.explosionRadius) * koef
        if damage > 0:
            victim.receiveTurretDamage(self._ownerEntity, damage, self._ownerEntity.objTypeID, self._ownerEntity.entityGroupMask, self._ownerEntity.teamIndex, self._ownerEntity.unitNumber, settings.critAbility, self._ownerLogic.targetSkillModsActivity, DAMAGE_REASON.AA_EXPLOSION, TurretDamageDealer.undefined)
            self._ownerEntity.onHitTarget([victim], DAMAGE_REASON.AA_EXPLOSION, ACTION_DEALER.TURRET)

    def _calculateTargetImaginePos(self, targetEntity, burst, current, syncedRandom):
        return self._calculateTargetImagineInTurn(targetEntity, burst, current, syncedRandom)

    def _calculateTargetImagineInTurn(self, targetEntity, burst, current, syncedRandom):
        shootIndex = current
        shootsCount = burst
        turretsCount = targetEntity.lockedByTurretsCounter
        aimingPercent = self._ownerLogic.scheme.AimingTable.get(turretsCount, 30)
        predictionPoint = self._ownerLogic.scheme.Prediction
        half = shootsCount * aimingPercent / 100.0 * 1.0
        shootIndex = half - shootIndex
        shootIndex = half if shootIndex > half else shootIndex
        shootIndex = 0 if shootIndex < 0 else shootIndex
        currentKoef = predictionPoint * shootIndex / half
        historyPosition = targetEntity.moveHistory
        position_A = historyPosition[0]
        position_B = historyPosition[1]
        position_C = historyPosition[2]
        AB = position_B - position_A
        BC = position_C - position_B
        CD = targetEntity.position - position_C
        BE = BC - AB
        CF = CD - BC
        DY = 2 * CF - BE
        DY = DY * 12
        DX = DY + CD
        shootDir = DX.getNormalized()
        oVector = self._ownerLogic.getEntityVector(self._ownerEntity)
        tVector = Vector3(self._ownerLogic.getEntityVector(targetEntity))
        flyTime = BigWorld.collisionTime(self._ownerEntity.position, oVector, targetEntity.position, tVector, self._ownerLogic.gunDescription.bulletSpeed)
        roatateAngle = DX.angle(tVector)
        roatateAngle2 = DX.angle(CD)
        roatateAngle = roatateAngle * 180 / math.pi
        roatateAngle2 = roatateAngle2 * 180 / math.pi
        if roatateAngle2 < 8:
            if currentKoef > 0:
                tVector += tVector * currentKoef
        else:
            length = tVector.length
            len2 = 2
            DY2 = DX - CD
            targetFuturePosition = targetEntity.position + flyTime * DY2.getNormalized() * length * len2
            return targetFuturePosition
        length = tVector.length
        turretsCount = targetEntity.lockedByTurretsCounter
        randomVector = self.getRandomVector(syncedRandom, turretsCount)
        targetFuturePosition = targetEntity.position + flyTime * shootDir * length * 1.1 + randomVector
        result = targetFuturePosition
        return result