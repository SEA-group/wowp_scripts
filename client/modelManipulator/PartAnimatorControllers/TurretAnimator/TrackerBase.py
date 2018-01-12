# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/TurretAnimator/TrackerBase.py


class TrackerBase(object):

    def attachToCompound(self, cid):
        pass

    def setDefaultDirection(self):
        pass

    def setAlive(self, value):
        pass

    def rotate(self, yaw, pitch):
        pass

    def destroy(self):
        pass

    def setTargetMatrix(self, targetMatrix):
        pass

    def onOwnerChanged(self, owner):
        pass

    def canShoot(self):
        raise NotImplementedError

    def onShoot(self, delay):
        raise NotImplementedError