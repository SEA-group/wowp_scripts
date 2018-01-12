# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/TurretAnimator/TurretsLogicAnimatorAdapter.py
from BWLogging import getLogger
from AvatarControllerBase import AvatarControllerBase
TURRET_ANIMATOR_ADAPTER_CONTROLLER_NAME = 'turretAnimatorAdapterControllerName'

class TurretsLogicAnimatorAdapter(AvatarControllerBase):

    def __init__(self, owner):
        super(TurretsLogicAnimatorAdapter, self).__init__(owner)
        self._log = getLogger(self)
        self._subscribe()

    def destroy(self):
        self._unsubscribe()
        super(TurretsLogicAnimatorAdapter, self).destroy()

    def _subscribe(self):
        self._log.trace('subscribing to events')
        self._turretsLogic.eTurretTargetChanged += self.onTurretTargetChanged
        self._turretsLogic.eGunnerStateChanged += self.onGunnerStateChanged
        self._turretsLogic.eSetControlMtx += self.onSetControlMtx

    def _unsubscribe(self):
        self._log.trace('unsubscribing from events')
        self._turretsLogic.eTurretTargetChanged -= self.onTurretTargetChanged
        self._turretsLogic.eGunnerStateChanged -= self.onGunnerStateChanged
        self._turretsLogic.eSetControlMtx -= self.onSetControlMtx

    def onTurretTargetChanged(self, targetId):
        for gunnerId in self._turretAnimator.gunners:
            self._turretAnimator.onGunnerTargetChanged(gunnerId, targetId)

    def onGunnerStateChanged(self, gunnerId, isAlive):
        self._turretAnimator.onGunnerStateChanged(gunnerId, isAlive)

    def onSetControlMtx(self, mtx):
        for gunnerId in self._turretAnimator.gunners:
            self._turretAnimator.onGunnerControlMatrixChanged(gunnerId, mtx)

    @property
    def _turretAnimator(self):
        """
        @rtype: modelManipulator.PartAnimatorControllers.TurretAnimator.TurretAnimator.TurretAnimator
        """
        return self._owner.controllers['modelManipulator'].getTurretController()

    @property
    def _turretsLogic(self):
        return self._owner.controllers['turretsLogic']