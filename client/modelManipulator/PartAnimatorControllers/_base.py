# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/_base.py
import math
import BigWorld
import consts
import config_consts
import db.DBLogic
from EntityHelpers import EntityStates, isAvatar
from Helpers.decorators import CachedProperty
from consts import HORIZONTAL_AXIS, VERTICAL_AXIS
from db.DBSakingPartsProfiles import Profile, ShakeSettings
FORCE_VALUE_LOW = -1
FORCE_VALUE_NORMAL = 0
FORCE_VALUE_FOSAGE = 1
PROPELLER_SOLID = 0
PROPELLER_NORMAL = 1
PROPELLER_FORSAGE = 2

class PartAnimatorBase(object):
    """Base class for animators"""
    SINGLE = True

    def __init__(self, playerId, settings):
        self.matrixProvider = None
        self.settings = settings
        self.axis = []
        self.triggers = []
        self._triggersState = {}
        self._playerId = playerId
        return

    @CachedProperty
    def _player(self):
        if consts.IS_CLIENT:
            return BigWorld.entities.get(self._playerId)
        else:
            return None
            return None

    def onLoaded(self, context):
        pass

    def destroy(self):
        pass

    def setValue(self, value, axis):
        pass

    def setTriggerState(self, trigger, state):
        """
        @type trigger: str
        @type state: bool
        @return: None
        """
        pass

    def updatePlaneNormSpeed(self, normalizedSpeed):
        pass

    def reloadSettings(self):
        pass

    def onOwnerChanged(self, owner):
        pass


class _TriggerState(object):

    def __init__(self, shakableState):
        """
        @type shakableState: db.DBParts.ShakeState
        """
        self._triggers = {trigger:False for trigger in shakableState.triggers}
        self.shakeState = shakableState

    def updateTriggerState(self, trigger, state):
        old_state = self._triggers.get(trigger, None)
        if old_state is not None and old_state != state:
            self._triggers[trigger] = state
            return True
        else:
            return False

    @property
    def anyActive(self):
        return any(self._triggers.itervalues())


class AileronBaseController(PartAnimatorBase):

    def __init__(self, playerId, settings):
        PartAnimatorBase.__init__(self, playerId, settings)
        self.reversed = False
        self._normalizedSpeed = 0.0
        self._shakableAxis = consts.ROTATION_AXIS.PITCH
        self.delay = 0
        self._shakeSettings = None
        self.maxAngle = self.settings.visualSettings.aileronMaxAngle
        self._triggerStates = tuple()
        self.activeShakeState = None
        self.matrixProvider = BigWorld.AileronMatrixProvider()
        self.reloadSettings()
        return

    @property
    def triggerStates(self):
        """
        @rtype: list of _TriggerState
        """
        return self._triggerStates

    def __chooseShakeSettings(self):
        if self.settings.shakingProfile:
            try:
                profile = db.DBLogic.g_instance.shakingPartsProfiles.getProfileById(self.settings.shakingProfile)
                self._shakeSettings = profile.getPartData(self.__class__.__name__)
            except (Profile.DoesNotExist, ShakeSettings.DoesNotExist):
                self._shakeSettings = None

        else:
            self._shakeSettings = None
        return

    def _init_states(self):
        if self._shakeSettings is not None:
            self._triggerStates = tuple(map(_TriggerState, self._shakeSettings.states))
            self.activeShakeState = self._shakeSettings.defaultState
        else:
            self._triggerStates = tuple()
            self.activeShakeState = None
        return

    def reloadSettings(self):
        self.__chooseShakeSettings()
        self._init_states()
        self._updateMatrixValues()
        if self._shakeSettings:
            setattr(self.matrixProvider, 'fadeTime', self._shakeSettings.fadeTime)
            setattr(self.matrixProvider, 'interpolationFunc', self._shakeSettings.fadeInterpolationFunc)

    def setValue(self, value, axis):
        self.matrixProvider.pitch = self.maxAngle * value
        if self.reversed:
            self.matrixProvider.pitch = -self.matrixProvider.pitch

    def setTriggerState(self, trigger, state):
        changed = False
        for triggerState in self._triggerStates:
            if triggerState.updateTriggerState(trigger, state):
                changed = True

        if changed and self._playerId == BigWorld.player().id:
            self._updateActiveShakeState()

    def _updateActiveShakeState(self):
        self.activeShakeState = self._shakeSettings.defaultState
        for triggerState in self._triggerStates:
            if triggerState.anyActive:
                if self.activeShakeState != triggerState.shakeState:
                    self.activeShakeState = triggerState.shakeState
                    self._updateMatrixValues()
                break

    def updatePlaneNormSpeed(self, normalizedSpeed):
        self._normalizedSpeed = normalizedSpeed
        self._updateMatrixValues()

    def _updateMatrixValues(self):
        slowShakeAmplitude = 0.0
        slowShakePeriod = 0.0
        fastShakeAmplitude = 0.0
        fastShakePeriod = 0.0
        delay = 0.0
        shakable = self.shakable
        if shakable and self.activeShakeState is not None:
            slowShakeAmplitude = self._slowAmplitude
            slowShakePeriod = self._slowPeriod
            fastShakeAmplitude = self._fastAmplitude
            fastShakePeriod = self._fastPeriod
            delay = self._delay
        self.matrixProvider.setShakingSettings(self._shakableAxis, shakable, self.maxAngle, fastShakeAmplitude, fastShakePeriod, slowShakeAmplitude, slowShakePeriod, delay)
        return

    @property
    def shakable(self):
        if self.isShakeSettingsPresent:
            return consts.IS_CLIENT and self._shakeSettings.shakable and isAvatar(self._player) and EntityStates.inState(self._player, EntityStates.GAME)
        return False

    @property
    def isShakeSettingsPresent(self):
        """
        @rtype: bool
        """
        return self._shakeSettings is not None

    @property
    def _slowAmplitude(self):
        return math.radians(self.activeShakeState.getSlowAmplitude(self._normalizedSpeed))

    @property
    def _fastAmplitude(self):
        return math.radians(self.activeShakeState.getFastAmplitude(self._normalizedSpeed))

    @property
    def _slowPeriod(self):
        return self.activeShakeState.getSlowPeriod(self._normalizedSpeed)

    @property
    def _fastPeriod(self):
        return self.activeShakeState.getFastPeriod(self._normalizedSpeed)

    @property
    def _delay(self):
        return self._shakeSettings.delay / 100.0


class MixedBaseController(AileronBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axisValues = {}

    def setValue(self, value, axis):
        self.axisValues[axis] = value
        self.animateValues()

    def animateValues(self):
        pass


class MixedRudderElevatorBaseController(MixedBaseController):

    def __init__(self, playerId, settings):
        AileronBaseController.__init__(self, playerId, settings)
        self.axis = [HORIZONTAL_AXIS, VERTICAL_AXIS]
        self.axisValues = {HORIZONTAL_AXIS: 0.0,
         VERTICAL_AXIS: 0.0}
        self.matrixProvider.speed = math.radians(settings.visualSettings.elevatorSpeed)

    def animateValues(self):
        rudder = self.settings.visualSettings.rudderMaxAngle * self.axisValues[HORIZONTAL_AXIS]
        if self.reversed:
            rudder = -rudder
        self.matrixProvider.pitch = (rudder + self.settings.visualSettings.elevatorMaxAngle * self.axisValues[VERTICAL_AXIS]) / 2