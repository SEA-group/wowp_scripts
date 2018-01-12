# Embedded file name: scripts/client/ClientPlaneTurret/TurretComponent.py
from AvatarControllerBase import AvatarControllerBase
from ICMultiUpdate import ICMultiUpdate
from ClientPlaneTurret.Helper import TurretState
from ClientPlaneTurret.IGunnerPlayer import IGunnerPlayer

class TurretComponent(AvatarControllerBase, ICMultiUpdate):

    def __init__(self, owner, tb):
        AvatarControllerBase.__init__(self, owner)
        self._tb = tb
        self._turrets = {}
        self._controlledGunner = IGunnerPlayer()
        dt = 0.1
        ICMultiCallback = lambda : self.update(dt)
        ICMultiUpdate.__init__(self, (dt, ICMultiCallback))

    def destroy(self):
        AvatarControllerBase.destroy(self)
        ICMultiUpdate.dispose(self)

    def restart(self):
        ICMultiUpdate.restart(self)

    def setOwner(self, owner):
        AvatarControllerBase.setOwner(self, owner)
        map(lambda t: t.destroy(), self._turrets.itervalues())
        self._turrets = {}
        if owner is not None:
            self._turrets = self._tb.create(owner)
        return

    def setPlayerGunner(self, gunner):
        if gunner is not None:
            self._controlledGunner = gunner
        else:
            self._controlledGunner.destroy()
            self._controlledGunner = IGunnerPlayer()
        return

    def update(self, dt):
        for turret in self._turrets.itervalues():
            self._controlledGunner.tryCatchTurret(turret)
            turret.update(dt)

    def linkSound(self, turretId, soundObj):
        self._turrets[turretId].context.registerSoundObject(soundObj)

    def onPartStateChanged(self, part):
        turret = self._turrets.get(part.partID)
        if turret is not None:
            turret.setState(TurretState.alive if part.isAlive else TurretState.dead)
        return