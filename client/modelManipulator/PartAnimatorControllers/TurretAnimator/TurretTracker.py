# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/TurretAnimator/TurretTracker.py
import math
import Math
import BigWorld
from debug_utils import LOG_DEBUG
from consts import IS_EDITOR
import db.DBLogic
from TrackerBase import TrackerBase
from MathExt import convGlobalToRelativeRotation

class TurretTracker(TrackerBase):

    def __init__(self, nodeId, turretSettings, path = ''):
        self.haveTarget = False
        self.isAlive = True
        self.nodeId = nodeId
        if IS_EDITOR:
            self.mountPoint = path
        self.settings = turretSettings
        for key, settings in turretSettings.visualSettings.iteritems():
            keyPath = key.split('/')
            if len(keyPath) > 0 and keyPath[-1] == path:
                path = key
                break

        self.visualSettings = turretSettings.visualSettings[path if path in turretSettings.visualSettings else '']
        self.__owner = None
        self.compoundMatrix = None
        self.tracker = BigWorld.Tracker()
        self.tracker.maxLod = 0
        sector = convGlobalToRelativeRotation(self.visualSettings.trackYawMax, self.visualSettings.trackYawMin, self.visualSettings.trackPitchMax, self.visualSettings.trackPitchMin)
        self.tracker.directionProvider = BigWorld.TurretDirectionProvider(None, None, None, sector[2], sector[3], sector[1], sector[0], False)
        self.tracker.directionProvider.canLostTarget = False
        self.tracker.relativeProvider = True
        self.setDefaultDirection()
        return

    def onOwnerChanged(self, owner):
        self.__owner = owner
        if owner is None:
            self.tracker.directionProvider.gunnerPos = None
            self.tracker.directionProvider.enabled = False
        else:
            self.tracker.directionProvider.gunnerPos = self.__owner.matrix
        return

    def attachToCompound(self, cid):
        self.compoundMatrix = BigWorld.CompoundNodeMP()
        self.compoundMatrix.handle = cid
        self.compoundMatrix.nodeIdx = self.nodeId
        self.tracker.mParentMp = self.compoundMatrix
        self.tracker.directionProvider.source = self.compoundMatrix
        try:
            sector = convGlobalToRelativeRotation(self.visualSettings.yawMax, self.visualSettings.yawMin, self.visualSettings.pitchMax, self.visualSettings.pitchMin)
            trackerNodeInfo = BigWorld.TurretNodeAnimator(cid, self.visualSettings.pitchNodeName, self.visualSettings.yawNodeName, self.visualSettings.directionNodeName, self.visualSettings.shootingNodeName, sector[1], sector[0], sector[2], sector[3], int(self.visualSettings.axisDirections.x), int(self.visualSettings.axisDirections.y), self.visualSettings.angularVelocity, self.visualSettings.angularThreshold, self.visualSettings.angularHalflife)
        except Exception as e:
            LOG_DEBUG('Failed to create TurretNodeAnimator!', e)
            return

        trackerNodeInfo.idleFrequencyScalerX = self.visualSettings.idleFrequencyScalerX
        trackerNodeInfo.idleAmplitudeScalerX = self.visualSettings.idleAmplitudeScalerX
        trackerNodeInfo.idleFrequencyScalerY = self.visualSettings.idleFrequencyScalerY
        trackerNodeInfo.idleAmplitudeScalerY = self.visualSettings.idleAmplitudeScalerY
        trackerNodeInfo.shootCooldownTime = self.visualSettings.shootCooldownTime
        trackerNodeInfo.enableIdleAnimation = self.visualSettings.enableIdleAnimation
        gunProfile = db.DBLogic.g_instance.getGunData(self.settings.gunName) if not IS_EDITOR else None
        if self.visualSettings.useGunProfile and gunProfile is not None:
            trackerNodeInfo.shootTime = 2.0 / (gunProfile.RPM / 60.0)
        else:
            trackerNodeInfo.shootTime = self.visualSettings.shootTime
        trackerNodeInfo.setShotRecoilCurve(list(self.visualSettings.recoilCurve.p))
        self.tracker.nodeInfo = trackerNodeInfo
        return

    def setTargetMatrix(self, targetMatrix):
        self.haveTarget = targetMatrix is not None
        if self.haveTarget:
            if self.visualSettings.enableIdleAnimation:
                self.tracker.nodeInfo.enableIdleAnimation = False
            self.tracker.directionProvider.target = targetMatrix
            if self.isAlive:
                self.tracker.directionProvider.enabled = True
        elif self.isAlive:
            if self.visualSettings.enableIdleAnimation:
                self.tracker.nodeInfo.enableIdleAnimation = True
            self.setDefaultDirection()
        return

    def setAlive(self, value):
        self.isAlive = value
        if value:
            self.tracker.nodeInfo.enableIdleAnimation = self.visualSettings.enableIdleAnimation
            if not self.haveTarget:
                self.setDefaultDirection()
            else:
                self.tracker.directionProvider.enabled = True
        else:
            self.tracker.directionProvider.enabled = False
            self.tracker.nodeInfo.enableIdleAnimation = False
            q = Math.Quaternion()
            q.fromEuler(0.0, math.radians(self.visualSettings.animatorDirectionOffset[1] + self.visualSettings.animatorDieDirection[1]), math.radians(self.visualSettings.animatorDirectionOffset[0] + self.visualSettings.animatorDieDirection[0]))
            self.tracker.directionProvider.staticOrientation = q

    def setDefaultDirection(self):
        q = Math.Quaternion()
        q.fromEuler(0.0, math.radians(self.visualSettings.animatorDirectionOffset[1] + self.visualSettings.animatorDirectionDefault[1]), math.radians(self.visualSettings.animatorDirectionOffset[0] + self.visualSettings.animatorDirectionDefault[0]))
        self.tracker.directionProvider.enabled = False
        self.tracker.directionProvider.staticOrientation = q

    def canShoot(self):
        return not self.tracker.directionProvider.clipped

    def onShoot(self, delay):
        if self.tracker.nodeInfo:
            self.tracker.nodeInfo.playShootAnimation(delay)

    def destroy(self):
        self.compoundMatrix = None
        self.__owner = None
        if self.tracker is not None:
            self.tracker.directionProvider.source = Math.Matrix()
            self.tracker.directionProvider.target = Math.Matrix()
            self.tracker.directionProvider = None
            self.tracker = None
        return