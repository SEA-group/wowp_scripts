# Embedded file name: scripts/client/ClientPlaneTurret/TurretGun.py
import BigWorld
from ClientPlaneTurret.Helper import TurretState

class TurretGun(object):

    def __init__(self, Id, context, pivot, turretAnimator):
        self._context = context
        self._turretAnimator = turretAnimator
        self._turretPivot = pivot
        self._gunnerId = Id
        self._oldTargetId = None
        self._oldCtrlMtx = None
        return

    @property
    def _gunIds(self):
        return self._context.gunIds

    def reset(self):
        self._oldTargetId = None
        return

    def destroy(self):
        self._context = None
        self._turretAnimator = None
        return

    @property
    def _turretPosition(self):
        return self._context.basePosition + self._context.baseRotation.rotateVec(self._turretPivot)

    def update(self, dt, shareData):
        """
        @type shareData: ClientPlaneTurret.Helper.TurretShareData
        """
        targetId = shareData.targetID
        ctrlMtx = shareData.controlMatrix
        shareData.gunDirection = self._calcGunDirection(shareData.targetDirection, shareData.targetID)
        forceSetTarget = False
        if ctrlMtx != self._oldCtrlMtx:
            self._turretAnimator.onGunnerControlMatrixChanged(self._gunnerId, ctrlMtx)
            self._oldCtrlMtx = ctrlMtx
            forceSetTarget = True
        if targetId != self._oldTargetId or forceSetTarget:
            self._turretAnimator.onGunnerTargetChanged(self._gunnerId, targetId)
            self._oldTargetId = targetId
        shareData.isGunCanShoot = {}
        for gunId in self._gunIds:
            shareData.isGunCanShoot[gunId] = self._turretAnimator.canShoot(gunId)

    def _calcGunDirection(self, targetDirection, targetId):
        if targetDirection.lengthSquared > 0 and targetId <= 0:
            return self._context.baseRotation.rotateVec(targetDirection - self._turretPivot)
        else:
            targetEntity = BigWorld.entities.get(targetId)
            if targetEntity is not None:
                return targetEntity.position - self._turretPosition
            return self._context.sectorDirection

    def setState(self, gunnerState):
        self._turretAnimator.onGunnerStateChanged(self._gunnerId, gunnerState is TurretState.alive)