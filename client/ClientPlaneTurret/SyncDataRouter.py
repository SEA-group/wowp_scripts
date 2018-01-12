# Embedded file name: scripts/client/ClientPlaneTurret/SyncDataRouter.py


class SynDataRouter(object):

    def __init__(self, ID, owner):
        self._turretID = ID
        self._owner = owner
        self._targetID = 0
        self._isFiring = False
        owner.eTurretSetTarget += self._syncTargetID
        owner.eTurretSetFireFlag += self._syncIsFiring

    def destroy(self):
        self._owner.eTurretSetTarget -= self._syncTargetID
        self._owner.eTurretSetFireFlag -= self._syncIsFiring
        self._owner = None
        return

    def _syncTargetID(self, turretID, targetID):
        if turretID == self._turretID:
            self._targetID = targetID

    def _syncIsFiring(self, turretID, flag):
        if turretID == self._turretID:
            self._isFiring = flag

    @property
    def targetID(self):
        return self._targetID

    @property
    def isFiring(self):
        return self._isFiring