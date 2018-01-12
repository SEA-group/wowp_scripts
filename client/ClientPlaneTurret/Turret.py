# Embedded file name: scripts/client/ClientPlaneTurret/Turret.py
from ClientPlaneTurret.Helper import TurretState, TurretShareData

class Turret(object):

    def __init__(self, context, gun, gunner, fireProcessor):
        self._context = context
        self._gun = gun
        self._gunners = [gunner]
        self._fireProcessor = fireProcessor
        self._shareData = TurretShareData()
        self._state = TurretState.alive
        self._critEndTime = 0

    def destroy(self):
        self._gun.destroy()
        self._gunners[0].destroy()
        self._fireProcessor.destroy()

    @property
    def context(self):
        return self._context

    def update(self, dt):
        self._gunner.update(dt, self._shareData)
        self._gun.update(dt, self._shareData)
        self._fireProcessor.update(dt, self._shareData)

    def catch(self, controlGunner):
        controlGunner.tieUp(self._gunner)
        self._gunners.append(controlGunner)

    def free(self):
        self._gunners.pop()

    def setState(self, state):
        self._state = state
        self._gun.setState(state)
        if state is TurretState.dead:
            self._shareData = TurretShareData()
            self._gunner.reset()
            self._critEndTime = self._context.time + self._context.critTime
        elif state is TurretState.alive:
            self._critEndTime = 0
        self._gunner.setState(state)

    @property
    def isAlive(self):
        return self._state is TurretState.alive

    @property
    def endCritTime(self):
        return self._critEndTime

    @property
    def _gunner(self):
        return self._gunners[-1]