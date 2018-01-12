# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/TurretAnimator/HeadTracker.py
import math
import Math
import BigWorld
from TrackerBase import TrackerBase

class HeadTracker(TrackerBase):

    def __init__(self, nodeId, modelId, settings):
        self.haveTarget = False
        self.isAlive = True
        self.nodeId = nodeId
        self.modelId = modelId
        self.settings = settings
        self.__enableIdle = False
        self._cid = None
        self.tracker = BigWorld.Tracker()
        self.tracker.maxLod = 0
        self.tracker.directionProvider = BigWorld.TurretDirectionProvider(None, None, None, self.settings.yawMin, self.settings.yawMax, self.settings.pitchMin, self.settings.pitchMax)
        self.tracker.directionProvider.canLostTarget = False
        self.tracker.relativeProvider = True
        self.setDefaultDirection()
        return

    def attachToCompound(self, cid):
        self._cid = cid
        nodeMatrixProvider = BigWorld.CompoundNodeMP()
        nodeMatrixProvider.handle = cid
        nodeMatrixProvider.nodeIdx = self.nodeId
        self.tracker.directionProvider.source = nodeMatrixProvider
        self.tracker.mParentMp = nodeMatrixProvider
        trackerNodeInfo = BigWorld.TrackerNodeInfo(cid, self.modelId, self.settings.nodeName, [], self.settings.nodeName, self.settings.pitchMin, self.settings.pitchMax, self.settings.yawMin, self.settings.yawMax, self.settings.angularVelocity, self.settings.angularThreshold, self.settings.angularHalflife)
        trackerNodeInfo.idleFrequencyScalerX = self.settings.idleFrequencyScalerX
        trackerNodeInfo.idleAmplitudeScalerX = self.settings.idleAmplitudeScalerX
        trackerNodeInfo.idleFrequencyScalerY = self.settings.idleFrequencyScalerY
        trackerNodeInfo.idleAmplitudeScalerY = self.settings.idleAmplitudeScalerY
        trackerNodeInfo.enableIdleAnimation = self.settings.enableIdleAnimation
        self.tracker.nodeInfo = trackerNodeInfo

    def setAlive(self, value):
        self.isAlive = value
        if value:
            self.tracker.nodeInfo.enableIdleAnimation = self.settings.enableIdleAnimation
            if not self.haveTarget:
                self.setDefaultDirection()
            else:
                self.tracker.directionProvider.enabled = True
        else:
            self.tracker.nodeInfo.enableIdleAnimation = False
            self.rotate(math.radians(self.settings.animatorDieDirection[0]), math.radians(self.settings.animatorDieDirection[1]))

    def setDefaultDirection(self):
        self.rotate(math.radians(self.settings.animatorDirectionDefault[0]), math.radians(self.settings.animatorDirectionDefault[1]))

    def rotate(self, yaw, pitch):
        self.tracker.directionProvider.enabled = False
        q = Math.Quaternion()
        q.fromEuler(0.0, math.radians(self.settings.animatorDirectionOffset[1]) + pitch, math.radians(self.settings.animatorDirectionOffset[0]) + yaw)
        self.tracker.directionProvider.staticOrientation = q

    def setTargetMatrix(self, targetMatrix):
        self.haveTarget = targetMatrix is not None
        if self.haveTarget:
            self.tracker.directionProvider.target = targetMatrix
            if self.isAlive:
                self.tracker.directionProvider.enabled = True
            self.tracker.nodeInfo.enableIdleAnimation = False
        elif self.isAlive:
            self.setDefaultDirection()
            self.tracker.nodeInfo.enableIdleAnimation = self.settings.enableIdleAnimation
        return

    def onOwnerChanged(self, owner):
        pass

    def destroy(self):
        if self.tracker is not None:
            self.tracker.directionProvider = None
            self.tracker = None
        return