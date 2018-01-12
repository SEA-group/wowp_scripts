# Embedded file name: scripts/common/turrets/BaseTurretLogic.py
import db.DBLogic
from AvatarControllerBase import AvatarControllerBase
from DirectStrategy import DirectStrategy
from EntityHelpers import isTeamObject
from HighAltitudeTurretStrategy import HighAltitudeTurretStrategy
from MathExt import *
from consts import SERVER_TICK_LENGTH, IS_CLIENT
from debug_utils import LOG_ERROR
from turrets import TurretsSchemeFactory

def getRotationAnglesOnTarget(pos, rotation, targetPos):
    ownerRotationInv = Math.Quaternion(rotation)
    ownerRotationInv.invert()
    localPos = ownerRotationInv.rotateVec(targetPos - pos)
    localPos.normalise()
    yawOnTarget = clampAngle2Pi(math.atan2(localPos.x, localPos.z))
    pitchOnTarget = math.asin(clamp(-1.0, localPos.y, 1.0))
    return (yawOnTarget, pitchOnTarget)


def calcDeltaAngle(curAngle, angleOnTarget):
    dAngle = angleOnTarget - curAngle
    if abs(dAngle) > math.pi:
        return dAngle - math.copysign(math.pi * 2.0, dAngle)
    else:
        return dAngle


def rotateAxisWithSpeed(var, angleOnTarget, speed, minValue, maxValue):
    speedDeltaAngle = speed * SERVER_TICK_LENGTH
    curDeltaAngle = calcDeltaAngle(var, angleOnTarget)
    if speedDeltaAngle > abs(curDeltaAngle):
        var = angleOnTarget
    else:
        var += math.copysign(speedDeltaAngle, curDeltaAngle)
    var = clampAngle2Pi(var)
    if var < minValue:
        var = minValue
    elif var > maxValue:
        var = maxValue
    return var


def rotateAxisWithSpeedEx(var, angleOnTarget, speed, minValue, maxValue):
    speedDeltaAngle = speed * SERVER_TICK_LENGTH
    curDeltaAngle = calcDeltaAngle(var, angleOnTarget)
    if speedDeltaAngle > abs(curDeltaAngle):
        var = angleOnTarget
    else:
        var += math.copysign(speedDeltaAngle, curDeltaAngle)
    if var < minValue:
        var = minValue
    elif var > maxValue:
        var = maxValue
    return var


class BaseTurretLogic(AvatarControllerBase):

    def __init__(self, owner, gunnersParts, turretName):
        """
        @param owner: owner entity of Avatar or TeamObject class
        @param turretSettings:
        @param gunnersParts: {partID: partTypeData}
        """
        AvatarControllerBase.__init__(self, owner)
        turretSettings = db.DBLogic.g_instance.getTurretData(turretName)
        if not turretSettings:
            self._onInvalidSettings('object has invalid turretName: %s' % turretName)
        self.settings = turretSettings
        self.gunDescription = db.DBLogic.g_instance.getGunData(turretSettings.gunName)
        if not self.gunDescription:
            self._onInvalidSettings('object has invalid gunName: %s' % turretSettings.gunName)
        if gunnersParts:
            self._initParts(gunnersParts)
        else:
            self._onInvalidSettings('object has no Gunner parts')
        self.isHighAltitudeTurret = turretName == 't_h'
        turretsScheme = TurretsSchemeFactory.getTurretsSchemeByBattleLevel(self.battleLevel, self.isHighAltitudeTurret)
        self.scheme = turretsScheme
        self._makeLocalProperties()
        self._strategy = HighAltitudeTurretStrategy(self) if self.isHighAltitudeTurret else DirectStrategy(self)
        self.TURRET_FOCUS = 1.0
        self.TURRET_INFLICT_CRIT = 1.0
        self.GUNNER_ENEMYHP_WATCHER = False

    def destroy(self):
        self._strategy.destroy()
        AvatarControllerBase.destroy(self)

    def _onInvalidSettings(self, message):
        if self._owner:
            if isTeamObject(self._owner):
                if IS_CLIENT:
                    arenaSettings = db.DBLogic.g_instance.getArenaData(BigWorld.player().arenaType)
                else:
                    arenaSettings = db.DBLogic.g_instance.getArenaData(self._owner.arenaType)
                objData = arenaSettings.getTeamObjectData(self._owner.arenaObjID)
                LOG_ERROR('TeamObject', message, objData['guid'])
            else:
                LOG_ERROR('Avatar', message, self._owner.globalID)
        else:
            LOG_ERROR(message)

    def _initParts(self, gunnersParts):
        pass

    @property
    def battleLevel(self):
        return 0

    @property
    def targetSkillModsActivity(self):
        return 0

    def _makeLocalProperties(self):
        self._battleSettings = self.settings.battleLevelsSettingsTurrets.getDataForLevel(self.battleLevel)

    def restart(self):
        self._makeLocalProperties()

    @property
    def curTargetID(self):
        return self._owner.turretTargetID

    def setCurTarget(self, curEntityId):
        prevTargetID = self._owner.turretTargetID
        self._owner.turretTargetID = curEntityId
        self._updateTargetSyncPosition()
        if prevTargetID != self._owner.turretTargetID:
            self._onTargetChanged(prevTargetID)

    def _updateTargetSyncPosition(self):
        targetEntity = BigWorld.entities.get(self._owner.turretTargetID, None)
        self._owner.turretTargetPosition = targetEntity.position if targetEntity else Math.Vector3(0, 0, 0)
        return

    def _onTargetChanged(self, prevTargetID):
        pass

    def _isPossibleToFire(self, gunPos, targetImagePos, gunYaw, gunPitch, distToTarget, yawOnTarget, pitchOnTarget):
        return distToTarget <= self.scheme.TargetShootDistance

    def getEntityVector(self, entity):
        pass