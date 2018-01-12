# Embedded file name: scripts/common/WeaponsHelpers.py
import Math
import math
import MathExt
from consts import IS_CLIENT, IS_CELLAPP
from itertools import groupby
from EntityHelpers import getAirplaneWeaponSettings, EntityStates
_Q = Math.Quaternion()

def normalizeVictimsPartsMap(victimsMap):
    for victimId, victimPars in victimsMap.iteritems():
        normalizedParts = []
        for key, rows in groupby(victimPars, lambda x: x[0]):
            allDistances = [ dist for _, dist in rows ]
            normalizedParts.append((key, sum(allDistances) / float(len(allDistances))))

        victimsMap[victimId] = normalizedParts


def isGunGroupShooting(fireFlags, groupIndex):
    return fireFlags & 1 << groupIndex


class WeaponReductionDirHandler(object):

    def __init__(self, owner):
        self._owner = owner
        self._currCursor = None
        return

    def setOwner(self, owner):
        self._owner = owner
        self._weaponSettings = None
        return

    @property
    def _maxSpeed(self):
        if IS_CLIENT:
            return 1.2 * getattr(self._owner, 'maxPitchRotationSpeed', -1)
        if IS_CELLAPP:
            return 1.2 * self._owner.controllers['dynAttributesProxy'].maxPitchRotationSpeed
        return -1

    @property
    def weaponSettings(self):
        self._weaponSettings = self._weaponSettings or getAirplaneWeaponSettings(self._owner.settings.airplane)
        return self._weaponSettings

    def restart(self):
        self._currCursor = self._owner.getShootingControllerRotation().getAxisZ()

    def backup(self):
        return [self._currCursor]

    def restore(self, data):
        self._currCursor = data[-1]

    def dispose(self):
        self._owner = None
        return

    def _getRotationAngle(self, currAngle):
        wData = self.weaponSettings
        targetConeAngle = wData.gunFullControlAngle
        targetSmoothConeAngle = wData.gunRotationAngleMax
        maxCursorAngle = wData.cursorAngleMax
        if currAngle <= targetConeAngle:
            return currAngle
        else:
            cfc = 0
            if targetSmoothConeAngle > targetConeAngle and maxCursorAngle > targetConeAngle:
                cfc = MathExt.clamp(0, (currAngle - targetConeAngle) / (maxCursorAngle - targetConeAngle), 1)
            return targetConeAngle + (targetSmoothConeAngle - targetConeAngle) * cfc

    def _cursor(self):
        return getattr(self._owner, 'mouseDirection', None)

    def update(self, dt):
        md = self._cursor()
        baseDirection = self._owner.getShootingControllerRotation().getAxisZ()
        wData = self.weaponSettings
        validData = md is not None and self._currCursor is not None and baseDirection.angle(md) < wData.cursorAngleMax
        if not EntityStates.inState(self._owner, EntityStates.GAME):
            self._currCursor = baseDirection
        elif self._maxSpeed >= 0 and validData:
            angle = self._currCursor.angle(md)
            axis = self._currCursor.cross(md)
            _Q.fromAngleAxis(min(angle, self._maxSpeed * dt), axis)
            self._currCursor = _Q.rotateVec(self._currCursor)
        else:
            self._currCursor = md
        return

    def getShootDirection(self, shootOrientation):
        pd = shootOrientation.getAxisZ()
        if self._currCursor is not None:
            currAngle = pd.angle(self._currCursor)
            axis = pd.cross(self._currCursor)
            tq = Math.Quaternion()
            tq.fromAngleAxis(self._getRotationAngle(currAngle), axis)
            return tq.rotateVec(pd)
        else:
            return

    def getLocalShootDirection(self, shootOrientation):
        res = self.getShootDirection(shootOrientation)
        if res is not None:
            _Q = Math.Quaternion(shootOrientation)
            _Q.invert()
            return _Q.rotateVec(res)
        else:
            return