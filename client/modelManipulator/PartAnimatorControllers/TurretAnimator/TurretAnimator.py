# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/TurretAnimator/TurretAnimator.py
from collections import defaultdict
import BigWorld
from consts import IS_EDITOR
from clientConsts import TURRET_TRACKER_AXIS
from debug_utils import LOG_WARNING
from TurretTracker import TurretTracker
from HeadTracker import HeadTracker
from modelManipulator.PartAnimatorControllers._base import PartAnimatorBase

class TurretAnimator(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.axis = [TURRET_TRACKER_AXIS]
        self.__trackers = defaultdict(dict)
        self.__nodeForGunLookup = {}
        self.__controlMtx = {}
        self._isAttachToCompound = False
        self._lazySetGunnerState = {}
        self._lazySetGunnerTarget = {}
        self.__owner = None
        return

    def createTurretTracker(self, gunnerId, nodeId, turretSettings, gunIds = -1, path = '', entityId = -1):
        for gunner, trackers in self.__trackers.iteritems():
            tracker = trackers.get(nodeId, None)
            if tracker is not None:
                return tracker

        if not IS_EDITOR:
            self.__owner = BigWorld.entities.get(entityId)
        tracker = TurretTracker(nodeId, turretSettings, path=path)
        for i, gunId in enumerate(gunIds):
            if gunId in self.__nodeForGunLookup:
                LOG_WARNING('createTracker: gun already added!')
            self.__nodeForGunLookup[gunId] = (nodeId, gunnerId)

        self.__trackers[gunnerId][nodeId] = tracker
        return tracker

    def createHeadTracker(self, gunnerId, nodeId, modelId, settings, entityId):
        for gunner, trackers in self.__trackers.iteritems():
            tracker = trackers.get(nodeId, None)
            if tracker is not None:
                return tracker

        if not IS_EDITOR:
            self.__owner = BigWorld.entities.get(entityId)
        tracker = HeadTracker(nodeId, modelId, settings)
        self.__trackers[gunnerId][nodeId] = tracker
        return tracker

    @property
    def trackers(self):
        return [ tracker for trackers in self.__trackers.itervalues() for tracker in trackers.itervalues() ]

    @property
    def gunners(self):
        return self.__trackers.iterkeys()

    def onOwnerChanged(self, owner):
        if self.__owner != owner:
            for trackers in self.__trackers.itervalues():
                for tracker in trackers.itervalues():
                    tracker.onOwnerChanged(owner)

            self.__owner = owner

    def canShoot(self, gunId):
        if gunId in self.__nodeForGunLookup:
            nodeId, gunnerId = self.__nodeForGunLookup[gunId]
            return self.__trackers[gunnerId][nodeId].canShoot()
        return True

    def onGunnerControlMatrixChanged(self, gunnerId, mtx):
        self.__controlMtx[gunnerId] = mtx

    def onGunnerStateChanged(self, gunnerId, isAlive):
        if self._isAttachToCompound:
            trackers = self.__trackers.get(gunnerId, None)
            if trackers is not None:
                for tracker in trackers.itervalues():
                    tracker.setAlive(isAlive)

        else:
            self._lazySetGunnerState[gunnerId] = isAlive
        return

    def onGunnerTargetChanged(self, gunnerId, targetId):
        if self._isAttachToCompound:
            trackers = self.__trackers.get(gunnerId, None)
            if trackers is not None:
                for tracker in trackers.itervalues():
                    if not IS_EDITOR:
                        if targetId is not None:
                            targetEntity = BigWorld.entities.get(targetId, None)
                            tracker.setTargetMatrix(targetEntity.matrix if targetEntity else self.__controlMtx.get(gunnerId))
                        else:
                            tracker.setTargetMatrix(self.__controlMtx.get(gunnerId))

        else:
            self._lazySetGunnerTarget[gunnerId] = targetId
        return

    def onTurretShoot(self, gunId, delay):
        if gunId in self.__nodeForGunLookup:
            nodeId, gunnerId = self.__nodeForGunLookup[gunId]
            self.__trackers[gunnerId][nodeId].onShoot(delay)

    def destroy(self):
        for trackers in self.__trackers.itervalues():
            for item in trackers.itervalues():
                item.destroy()

            trackers.clear()

        self.__trackers.clear()
        self.__owner = None
        PartAnimatorBase.destroy(self)
        return

    def _tryLazyUpdateTrackers(self):
        self._isAttachToCompound = True
        if self._lazySetGunnerTarget:
            for gunnerId, targetID in self._lazySetGunnerTarget.iteritems():
                self.onGunnerTargetChanged(gunnerId, targetID)

            self._lazySetGunnerTarget = {}
        if self._lazySetGunnerState:
            for gunnerId, isAlive in self._lazySetGunnerState.iteritems():
                self.onGunnerStateChanged(gunnerId, isAlive)

            self._lazySetGunnerState = {}

    def onLoaded(self, context):
        for trackers in self.__trackers.itervalues():
            for item in trackers.itervalues():
                item.attachToCompound(context.cidProxy.handle)

        self._tryLazyUpdateTrackers()