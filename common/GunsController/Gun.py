# Embedded file name: scripts/common/GunsController/Gun.py
import Math
from consts import GUN_REDUCTION_FROM_DIST_K
from debug_utils import DBLOG_CRITICAL

def getPivot(pivotName, pivots):
    pivot = pivots.mountPoints.get(pivotName, None)
    if not pivot and pivotName:
        DBLOG_CRITICAL('Unkown pivot for gun:' + pivotName)
    return pivot


class Gun(object):

    def __init__(self, gunInfo, pivots, gunDescription):
        self.uniqueId = id(self)
        pivot = getPivot(gunInfo.flamePath, pivots)
        self.__reductionVectorLength = gunDescription.bulletFlyDist * GUN_REDUCTION_FROM_DIST_K
        self.posDelta = Math.Vector3()
        self.addRotation = Math.Vector3()
        self.gunProfileName = gunDescription.gunProfileName
        self.RPM = gunDescription.RPM
        if pivot:
            self.posDelta.set(pivot.position)
            self.addRotation.set(pivot.direction)
        self.flamePath = gunInfo.flamePath
        self.shellPath = gunInfo.shellPath if hasattr(gunInfo, 'shellPath') else None
        if self.shellPath == '_':
            self.shellPath = self.flamePath.replace('HP_flame', 'HP_shell')
        self.shellOutInterval = gunDescription.shellOutInterval if hasattr(gunDescription, 'shellOutInterval') else 1.0
        self.shellSyncTime = 0
        return

    def reductionDir(self, rpv = None):
        if rpv is None:
            rpv = Math.Vector3(0, 0, 1)
        reductionPoint = rpv * self.__reductionVectorLength
        reductionDir = reductionPoint - self.posDelta if self.posDelta.length else Math.Vector3(reductionPoint)
        return reductionDir.getNormalized()