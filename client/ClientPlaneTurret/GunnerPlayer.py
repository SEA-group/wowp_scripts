# Embedded file name: scripts/client/ClientPlaneTurret/GunnerPlayer.py
import BigWorld
import math
import GameEnvironment
from time import time
from random import random
from CommonSettings import GunnerFireRangingSettings, GunnerDefaultConcentration
from Math import Quaternion, Vector2, Vector3, Matrix, MatrixProduct, MatrixCombiner
from EntityHelpers import EntityStates
from ClientPlaneTurret.Helper import PlayerGunnerDefaultContext, TurretState
from IGunnerPlayer import IGunnerPlayer

class ControlledGunnerOutInterface(object):
    _outAttributeList = ['isOnTarget',
     'getScopeRadius',
     'getReduction',
     'isClientFiring',
     'getTurretZoneRectangle',
     'isClientInAction',
     'activate',
     'setControlMtx',
     'shootDistance',
     'isActiveGun']

    def __init__(self, inst):
        self._inst = inst

    def __getattr__(self, item):
        if item in self._outAttributeList:
            return getattr(self._inst, item)
        raise AttributeError


class FireRanging(object):

    def __init__(self, setting):
        self._settings = setting
        self._startFiring = -1
        self._lastFireTime = -1

    def isFiring(self, isTarget, isFiring, reduction):
        if isFiring:
            if isTarget:
                return self._onTargetFiring(reduction)
            return self._nonTargetFiring()
        self._startFiring = -1
        return isFiring

    def _onTargetFiring(self, reduction):
        if not self._settings.isTargetRanging:
            return True

        def modeF(norma):
            if self._settings.withRandom:
                return norma * (0.5 + 0.5 * random())
            return norma

        def modeD(norma):
            return modeF(norma) * (1 - (reduction - GunnerDefaultConcentration) / (1 - GunnerDefaultConcentration))

        return self._calcIsFiring(modeF, modeD)

    def _nonTargetFiring(self):
        if not self._settings.isNonTargetRanging:
            return True

        def mode(norma):
            if self._settings.withRandom:
                return norma * (0.5 + 0.5 * random())
            return norma

        return self._calcIsFiring(mode, mode)

    def _calcIsFiring(self, modeF, modeD):
        currTime = time()
        if self._startFiring < 0:
            self._startFiring = currTime
        if currTime - self._startFiring < modeF(self._settings.simpleFireTime):
            self._lastFireTime = currTime
            return True
        if currTime - self._lastFireTime > modeD(self._settings.delayTime):
            self._startFiring = currTime
        return False


class GunnerPlayer(IGunnerPlayer):

    def __init__(self, owner, lockingAdapter):
        self._owner = owner
        self._active = False
        self._turret = None
        self._fired = False
        self._gunnerProxy = None
        self._controlMtx = None
        self.__playerDirection = Vector3(0, 0, 0)
        self._lockingAdapter = lockingAdapter
        self._defaultContext = PlayerGunnerDefaultContext(owner)
        self._fireRanging = FireRanging(GunnerFireRangingSettings)
        self._targetID = 0
        self._lastTargetID = 0
        self._lastHUDLockTarget = None
        self._turretRangeMod = 1
        return

    def destroy(self):
        self._tryFreeTurret(True)
        self._defaultContext = None
        self._lockingAdapter.destroy()
        self._controlMtx = None
        self._owner = None
        return

    def _resetAttributes(self):
        self._fired = False
        self._targetID = 0
        self._lastTargetID = 0
        self._lastHUDLockTarget = None
        return

    def reset(self):
        self._tryFreeTurret(True)
        self._trySetTargetMtx(self._getCurrTargetID())

    def update(self, dt, dataTable):
        self._gunnerProxy.update(dt, dataTable)
        self._targetID = dataTable.targetID
        reduction = self.getReduction()
        self._fired = self._fireRanging.isFiring(self._targetID > 0, dataTable.isGunnerFiring, reduction)
        self._lockingAdapter.onSetTarget(self._targetID)
        dataTable.controlMatrix = self._controlMtx
        dataTable.targetID = self._getCurrTargetID()
        dataTable.targetDirection = self._getDirection(self._context)
        dataTable.reduction = reduction
        dataTable.isGunnerFiring = self._isFiring
        self._tryFreeTurret(not self._context.inSector(self._playerDirection(self._context)))
        self._trySetTargetMtx(self._getCurrTargetID())

    def activate(self, active):
        self._active = active
        if not active:
            self.reset()

    def setDirection(self, direction):
        if self._active:
            self.__playerDirection = direction

    def tieUp(self, gunnerProxy):
        self._gunnerProxy = gunnerProxy

    def tryCatchTurret(self, turret):
        if self._active and self._turret is None and turret.context.inSector(self._playerDirection(turret.context)):
            turret.catch(self)
            self._turret = turret
            self._onTurretCatch()
        return

    def _tryFreeTurret(self, condition):
        if self._turret is not None and condition:
            self._onTurretFree()
            self._gunnerProxy = None
            self._turret.free()
            self._turret = None
            self._resetAttributes()
        return

    @property
    def _isFiring(self):
        return self._fired and self._targetID == self._getCurrTargetID()

    @property
    def _context(self):
        if self._turret is not None:
            return self._turret.context
        else:
            return self._defaultContext

    def _playerDirection(self, context):
        blDirection = self.__playerDirection * context.targetLockShootDistance * self._turretRangeMod
        ir = Quaternion(context.baseRotation)
        ir.invert()
        return ir.rotateVec(blDirection)

    def _getDirection(self, context):
        target = BigWorld.entities.get(self._getCurrTargetID())
        if target is not None:
            blDirection = target.position - context.basePosition
        else:
            blDirection = self.__playerDirection * context.targetLockShootDistance * self._turretRangeMod
        ir = Quaternion(context.baseRotation)
        ir.invert()
        return ir.rotateVec(blDirection)

    def _getCurrTargetID(self):
        if self._targetID <= 0 and self._active:
            targetEntity = BigWorld.entities.get(self._lastTargetID, None)
            if targetEntity is not None and EntityStates.inState(targetEntity, EntityStates.GAME) and self._context.basePosition.distTo(targetEntity.position) < self._context.targetLockShootDistance and self.__playerDirection.angle(targetEntity.position - self._context.basePosition) < self._context.turretLoseBorderZone:
                return self._lastTargetID
        self._lastTargetID = self._targetID
        return self._lastTargetID

    def setControlMtx(self, mtx):
        translation = Matrix()
        translation.translation = Vector3(0, 0, BigWorld.player().reductionPoint)
        self._controlMtx = MatrixProduct()
        self._controlMtx.b = mtx
        self._controlMtx.a = translation

    def _setCrossHairTargetMtx(self, targetID):
        if self._active:
            resMtx = self._controlMtx
            targetEntity = BigWorld.entities.get(targetID, None)
            if targetEntity is not None:
                sMtx = self._owner.realMatrix
                tMtx = targetEntity.matrix
                tm = BigWorld.TurretDirectionProvider(sMtx, tMtx, sMtx, 0, 0, 0, 0)
                resMtx = MatrixCombiner()
                resMtx.r = tm
                resMtx.t = tMtx
            GameEnvironment.getCamera().leSetMovingTargetMatrix(resMtx)
        return

    def _trySetTargetMtx(self, targetID, force = False):
        if targetID != self._lastHUDLockTarget or force:
            self._setCrossHairTargetMtx(targetID)
            self._lastHUDLockTarget = targetID

    def _onTurretCatch(self):
        GameEnvironment.g_instance.ePlayerGunnerChangedTurret(self._context.aimType, self._context.RPM)
        GameEnvironment.g_instance.eTurretEndCritTimeChange(self._turret.endCritTime)

    def _onTurretFree(self):
        GameEnvironment.g_instance.eTurretEndCritTimeChange(0)

    def setState(self, newState):
        if newState is TurretState.alive:
            GameEnvironment.g_instance.eTurretEndCritTimeChange(self._turret.endCritTime)

    def isActiveGun(self, gunId):
        return gunId in self._context.gunIds

    def isOnTarget(self):
        te = BigWorld.entities.get(self._getCurrTargetID())
        if te is not None:
            rect = self.getTurretZoneRectangle(te.position - self._context.basePosition)
            if abs(rect.x) < 0.5 and abs(rect.y) < 0.5:
                return True
        return False

    def getScopeRadius(self, direction):
        dirNorm = direction.getNormalized() * self._context.targetLockShootDistance
        if dirNorm.angle(Vector3(0, 1, 0)):
            axis = dirNorm.cross(Vector3(0, 1, 0)).getNormalized()
        else:
            axis = dirNorm.cross(Vector3(1, 0, 0)).getNormalized()
        dirNorm += axis * dirNorm.length * math.tan(self._context.turretControlAimConeAngle) + self._context.basePosition
        res = BigWorld.worldToScreen(dirNorm) - Vector3(0.5 * BigWorld.screenWidth(), 0.5 * BigWorld.screenHeight(), 1)
        return res.length

    @property
    def shootDistance(self):
        return self._context.targetLockShootDistance

    @property
    def isClientFiring(self):
        return bool(self._active and self._isFiring)

    @property
    def isClientInAction(self):
        return self._active

    def getReduction(self):
        if self._targetID > 0:
            return self._owner.turretReduction
        return 0.0

    def getTurretZoneRectangle(self, direction):
        if self._turret is None:
            return Vector2(1, 1)
        else:
            normAngle = self._context.turretControlAimConeAngle
            ir = Quaternion(self._context.baseRotation)
            ir.invert()
            direction = ir.rotateVec(direction)
            return self._context.getOutNormZone(direction, normAngle)