# Embedded file name: scripts/client/ClientPlaneTurret/TurretSector.py
import Math
from MathExt import sign, clamp

class FireSector(object):

    def __init__(self, orientation, pitchUp, pitchDown, yawLeft, yawRight):
        self._orientation = orientation
        self._sectorDirection = orientation.getAxisZ()
        self._invOrientation = Math.Quaternion(orientation)
        self._invOrientation.invert()
        self._pitchUp = pitchUp
        self._pitchDown = pitchDown
        self._yawLeft = yawLeft
        self._yawRight = yawRight

    @property
    def orientation(self):
        return self._orientation

    @property
    def direction(self):
        return self._sectorDirection

    def inSector(self, direction):
        ld = self._toSectorLocal(direction)
        in_pitch = self._pitchUp > self._getPitchAngle(ld) > self._pitchDown
        in_yaw = self._yawRight > self._getYawAngle(ld) > self._yawLeft
        return in_pitch and in_yaw

    def _toSectorLocal(self, direction):
        return self._invOrientation.rotateVec(direction)

    @staticmethod
    def _getPitchAngle(direction):
        yzProjection = Math.Vector3(direction.x, 0, direction.z)
        return sign(direction.y) * direction.angle(yzProjection)

    @staticmethod
    def _getYawAngle(direction):
        xzProjection = Math.Vector3(direction.x, 0, direction.z)
        return sign(-direction.x) * xzProjection.angle(Math.Vector3(0, 0, 1))

    def getOutNormZone(self, direction, normAngle):
        halfNorm = normAngle
        norm = 2 * normAngle
        ld = self._toSectorLocal(direction)
        pitchDir = self._getPitchAngle(ld)
        yawDir = self._getYawAngle(ld)
        res = Math.Vector2(0, 0)
        pB = pitchDir + halfNorm
        pD = pitchDir - halfNorm
        if pB > self._pitchUp:
            res.y = clamp(-1, (pB - self._pitchUp) / norm, 1)
        elif pD < self._pitchDown:
            res.y = clamp(-1, (pD - self._pitchDown) / norm, 1)
        ySign = sign(yawDir)
        y = yawDir + ySign * halfNorm
        if self._yawRight < y or y < self._yawLeft:
            edgeAngle = self._yawRight if ySign >= 0 else self._yawLeft
            res.x = -clamp(-1, (y - edgeAngle) / norm, 1)
        return res