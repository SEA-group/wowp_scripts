# Embedded file name: scripts/client/input/InputSubsystem/GunnerInput.py
import BigWorld
import math
import Math
from random import choice
import GameEnvironment
from InputSubsystemBase import InputSubsystemBase
from ICMultiUpdate import ICMultiUpdate
from consts import BATTLE_MODE

def inAction(foo):

    def wrapper(*args, **kwargs):
        if args[0].isActive:
            return foo(*args, **kwargs)
        else:
            return None

    return wrapper


class GunnerInput(InputSubsystemBase, ICMultiUpdate):

    def __init__(self, profile):
        self._profile = profile
        self._cameraStrategy = GameEnvironment.getCamera().getDefualtStrategies['CameraStrategyGunner']
        self._sensitivityCfc = 0.1
        self._cameraStrategy.flexibility = 0
        self._isActive = False
        self._lastDataToSend = None
        ICMultiUpdate.__init__(self, (0.1, self._sendMouseData))
        return

    @property
    def isActive(self):
        return self._isActive

    def dispose(self):
        ICMultiUpdate.dispose(self)

    def restart(self):
        ICMultiUpdate.restart(self)

    def notControlledByUser(self, value):
        pass

    def eBattleModeChange(self, value):
        self._isActive = value is BATTLE_MODE.GUNNER_MODE
        if self._isActive:
            self._tryLookAtTarget()

    @inAction
    def processMouseEvent(self, event):
        signY = 1.0 if self._profile.settings.MOUSE_INVERT_VERT else -1.0
        sensitivity = (0.1 + 0.9 * self._profile.mouseSensitivity(event)) * self._sensitivityCfc
        dx = event.dx * sensitivity
        dy = event.dy * sensitivity * signY
        self._cameraStrategy.rotateCursor(math.radians(dy), math.radians(dx))
        return True

    @inAction
    def _sendMouseData(self):
        dataToSend = self._cameraStrategy.cursorDirection
        if dataToSend != self._lastDataToSend:
            BigWorld.player().sendGunnerDirData(dataToSend)
        self._lastDataToSend = dataToSend

    def _tryLookAtTarget(self):
        player = BigWorld.player()
        aggroID = player.turretsState.getMaxAggroTargetID()
        targetEntity = BigWorld.entities.get(aggroID)
        if targetEntity is not None:
            direction = targetEntity.position - player.position
            q = Math.Quaternion()
            q.fromAngleAxis(0.5 * math.pi, direction.cross(Math.Vector3(0, 1, 0)))
            currUp = q.rotateVec(direction)
            mtx = Math.Matrix()
            mtx.lookAt(Math.Vector3(0, 0, 0), targetEntity.position - player.position, currUp)
            self._cameraStrategy.setCameraOrientation(mtx)
            mtx.invert()
            self._cameraStrategy.setCursorOrientation(mtx)
        else:
            self._cameraStrategy.reset()
        return