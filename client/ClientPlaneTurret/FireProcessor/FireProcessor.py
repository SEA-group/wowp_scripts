# Embedded file name: scripts/client/ClientPlaneTurret/FireProcessor/FireProcessor.py
import Math
import BigWorld

class FireProcessor(object):

    def __init__(self, context, bulletInterface):
        """
        @type context: ClientPlaneTurret.Helper.Context
        @type bulletInterface: ClientPlaneTurret.FireProcessor.TurretBulletsInterface.TurretBulletsInterface
        """
        self._context = context
        self._bulletInterface = bulletInterface
        self._isFireActive = False
        self.__Q = Math.Quaternion()

    def reset(self):
        self.__Q = Math.Quaternion()
        self._bulletInterface.reset()

    def destroy(self):
        self._bulletInterface.dispose()
        self._context = None
        self._bulletInterface = None
        return

    def update(self, dt, shareData):
        """
        @type dt: float
        @type shareData: ClientPlaneTurret.Helper.TurretShareData
        """
        isFiring = shareData.isFiring()
        if not isFiring:
            self._setIsFireActive(False)
            return
        else:
            shootPosition = self._findTargetShootPosition(shareData)
            if shootPosition is None:
                self._setIsFireActive(False)
                return
            self._setIsFireActive(True)
            gunIds = [ gunId for gunId, isGunCanShoot in shareData.isGunCanShoot.iteritems() if isGunCanShoot ]
            self._bulletInterface.updateReduction(shareData.reduction)
            self._bulletInterface.fire(shareData.targetID > 0, shootPosition, gunIds)
            return

    def _setIsFireActive(self, isActive):
        if isActive == self._isFireActive:
            return
        self._isFireActive = isActive
        if self._isFireActive:
            self._context.onFireStarted()
        else:
            self._context.onFireEnded()

    def _findTargetShootPosition(self, shareData):
        """
        @type shareData: ClientPlaneTurret.Helper.TurretShareData
        @rtype: Math.Vector3
        """
        targetId = shareData.targetID
        turretDirection = shareData.gunDirection
        targetEntity = BigWorld.entities.get(targetId)
        planePosition = self._context.basePosition
        if targetEntity is None:
            return planePosition + turretDirection * self._context.targetLockShootDistance
        else:
            targetShootPosition = self._findTargetEntityShootCollisionPos(targetEntity)
            if targetShootPosition is None:
                return
            targetShootPosition = self._clipByFireCone(turretDirection, targetShootPosition)
            return targetShootPosition

    def _findTargetEntityShootCollisionPos(self, targetEntity):
        planePosition = self._context.basePosition
        targetPosition = targetEntity.position
        targetVector = targetEntity.getWorldVector()
        targetHitTime = BigWorld.collisionTime(planePosition, Math.Vector3(), targetPosition, targetVector, self._bulletInterface.bulletSpeed)
        if targetHitTime < 0:
            return None
        else:
            return targetPosition + targetHitTime * targetVector

    def _clipByFireCone(self, turretDirection, targetShootPosition):
        planePosition = self._context.basePosition
        onEnemyDir = targetShootPosition - planePosition
        angle = turretDirection.angle(onEnemyDir)
        if angle > self._context.turretControlAimConeAngle:
            self.__Q.fromAngleAxis(angle - self._context.turretControlAimConeAngle, onEnemyDir.cross(turretDirection))
            onEnemyDir = self.__Q.rotateVec(onEnemyDir)
            targetShootPosition = onEnemyDir + planePosition
        return targetShootPosition