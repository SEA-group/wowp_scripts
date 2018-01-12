# Embedded file name: scripts/client/Helpers/ActionMatcher.py
import BigWorld
import math
import Math
from consts import *
from clientConsts import SLATS_AXIS, ACTIONMATCHER_ANIMATION_DISTANCE
from MathExt import *
from _performanceCharacteristics_db import airplanes as airplanes_PC
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV
from ActionMatcherSettings import SHELL_LAUNCHED_TRIGGER_NAMES
ACTON_MATCH_TIME = 0.25
LOFT_MIN_TIME = 0.5
LOFT_MIN_ROTATION_DEVIATION = 0.15
INTRO_LOFT_MIN_ROTATION_DEVIATION = 0.02
AILERON_LOFT_ANGLE = 19
AILERON_LOFT_SPEED_K = 0.65
YAW_MAX_SPEED = math.radians(10.0)
PITCH_MAX_SPEED = math.radians(10.0)
ROLL_MAX_SPEED = math.radians(10.0)

def isUpdateAvatarAnimation(targetPosition, updateDist = ACTIONMATCHER_ANIMATION_DISTANCE):
    camToOwner = targetPosition - BigWorld.camera().position
    return camToOwner.lengthSquared < updateDist ** 2 and camToOwner.dot(BigWorld.camera().direction) > 0


class ActionMatcher:

    def __init__(self, owner, isPlayer, minLoftRotationDeviation = LOFT_MIN_ROTATION_DEVIATION):
        self.__owner = owner
        self.__isPlayer = isPlayer
        self.__updateCallBack = None
        self.__oldRotate = Math.Vector3(owner.roll, owner.pitch, owner.yaw)
        self.__loftTime = 0
        self.__isSlate = owner.settings.airplane.visualSettings.slateOffset > 0
        self.__slateOnAngle = math.radians(owner.settings.airplane.visualSettings.slateOnAngle)
        self.__minLoftSpeed = 1.4 * airplanes_PC[owner.globalID].stallSpeed / 3.6
        self.__minLoftRotationDeviation = minLoftRotationDeviation
        self.__minAileronLoftSpeed = AILERON_LOFT_SPEED_K * airplanes_PC[owner.globalID].maxSpeed / 3.6
        self.__minAileronLoftAngle = math.radians(AILERON_LOFT_ANGLE)
        self._subscribe()
        self.__modelManipulator = self.__owner.controllers['modelManipulator']
        self._effects = {'AILERON_LOFT': None,
         'ATTACKANGLE': None,
         'LOFT': None}
        if isPlayer:
            self.__updatePlayerAvatar()
        else:
            self.__updateAvatar()
            self.setEffectVisible('AILERON_LOFT', False)
        return

    def _subscribe(self):
        self.__owner.shellLaunched += self.onShellLaunched

    def _unsubscribe(self):
        self.__owner.shellLaunched -= self.onShellLaunched

    def onShellLaunched(self, shellIndex):
        triggerName = SHELL_LAUNCHED_TRIGGER_NAMES.get(shellIndex)
        if triggerName is not None:
            self._setEffectTriggerValue(triggerName, False)
            self._setEffectTriggerValue(triggerName, True)
        else:
            LOG_ERROR('Unsupported shell index by ActionMatcher. See ActionMatcherSettings')
        return

    def _setEffectTriggerValue(self, triggerName, value):
        LOG_DEBUG_DEV('_setEffectTriggerValue', self.__owner.id, triggerName, value)
        modelManipulator = self.__owner.controllers['modelManipulator']
        modelManipulator.setEffectVisible(triggerName, value)

    def __updatePlayerAvatar(self):
        speed = self.__owner.getSpeed()
        self.__updateLofts(speed)
        self.__updateAileronEffects(speed)
        if self.__slateOnAngle:
            self.__updateAttackAngle()
        self.__updateCallBack = BigWorld.callback(ACTON_MATCH_TIME, self.__updatePlayerAvatar)

    def __updateAvatar(self):
        updateAvatarAnimation = isUpdateAvatarAnimation(self.__owner.position)
        if updateAvatarAnimation:
            self.__updateInputAxisAnimation()
        if self.__slateOnAngle and updateAvatarAnimation:
            self.__updateAttackAngle()
        self.__updateCallBack = BigWorld.callback(ACTON_MATCH_TIME, self.__updateAvatar)

    def __updateAttackAngle(self):
        invRotation = self.__owner.getRotation()
        invRotation.invert()
        localSpeed = invRotation.rotateVec(self.__owner.getWorldVector())
        airFlowAnglePitch = -math.atan2(localSpeed.y, localSpeed.z)
        if self.__isSlate:
            self.__modelManipulator.setAxisValue(SLATS_AXIS, airFlowAnglePitch)
        self.setEffectVisible('ATTACKANGLE', airFlowAnglePitch >= self.__slateOnAngle)

    def __updateInputAxisAnimation(self):
        modelManipulator = self.__modelManipulator
        ownerYaw, ownerPitch, ownerRoll = self.__owner.filter.rotationSpeed
        yaw = -ownerYaw / YAW_MAX_SPEED
        pitch = -ownerPitch / PITCH_MAX_SPEED
        roll = ownerRoll / ROLL_MAX_SPEED
        modelManipulator.setAxisValue(HORIZONTAL_AXIS, clamp(-1.0, yaw, 1.0))
        modelManipulator.setAxisValue(VERTICAL_AXIS, clamp(-1.0, pitch, 1.0))
        modelManipulator.setAxisValue(ROLL_AXIS, clamp(-1.0, roll, 1.0))

    def __updateLofts(self, speed):
        modelManipulator = self.__modelManipulator
        newRotate = Math.Vector3(self.__owner.roll, self.__owner.pitch, self.__owner.yaw)
        if (newRotate - self.__oldRotate).length > self.__minLoftRotationDeviation and speed > self.__minLoftSpeed:
            self.__loftTime += ACTON_MATCH_TIME
            if self.__loftTime > LOFT_MIN_TIME and not modelManipulator.getEffectState('LOFT_LARGE'):
                self.setEffectVisible('LOFT', True)
        else:
            self.setEffectVisible('LOFT', False)
        self.__oldRotate = newRotate

    def __updateAileronEffects(self, speed):
        modelManipulator = self.__modelManipulator
        minAileronLoftAngle = self.__minAileronLoftAngle
        doAileronLoft = speed > self.__minAileronLoftSpeed and (abs(modelManipulator.getLeftAileronAngle()) > minAileronLoftAngle or abs(modelManipulator.getRightAileronAngle()) > minAileronLoftAngle)
        if doAileronLoft:
            self.setEffectVisible('AILERON_LOFT', True)

    def setEffectVisible(self, name, value):
        if self._effects[name] != value:
            self.__modelManipulator.setEffectVisible(name, value)
            self._effects[name] = value

    def destroy(self):
        self._unsubscribe()
        if self.__updateCallBack is not None:
            BigWorld.cancelCallback(self.__updateCallBack)
        self.__modelManipulator = None
        self.__owner = None
        return

    def setVector(self, old):
        pass