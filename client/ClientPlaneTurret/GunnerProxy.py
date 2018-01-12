# Embedded file name: scripts/client/ClientPlaneTurret/GunnerProxy.py
from Math import Vector3

class GunnerProxy(object):

    def __init__(self, SyncDataAdapter):
        self._syncDataAdapter = SyncDataAdapter

    def reset(self):
        pass

    def setState(self, newState):
        pass

    def destroy(self):
        self._syncDataAdapter.destroy()

    def update(self, dt, shareData):
        shareData.targetID = self._syncDataAdapter.targetID
        shareData.isGunnerFiring = self._syncDataAdapter.isFiring
        shareData.targetDirection = Vector3(0, 0, 0)
        shareData.controlMatrix = None
        shareData.reduction = 0
        return