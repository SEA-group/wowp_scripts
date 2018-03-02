# Embedded file name: scripts/client/modelManipulator/PartAnimator2.py
import BigWorld
from .PartAnimatorControllers import CONTROLLERS, PropellorControllerL, PropellorControllerR, AileronBaseController
from consts import FORCE_AXIS
_CONTROLLERS_MAP = dict(((controllerCls.__name__, controllerCls) for controllerCls in CONTROLLERS))
SHAKE_PERIOD = 0.5

class PartAnimatorController:
    """Create and control life time of animation controllers"""

    def __init__(self, settings, playerId):
        self.__controllerByAxis = {}
        self.__controllersByClass = {}
        self.__controllers = []
        self.__axisValues = {}
        self.__triggerValues = {}
        self.__settings = settings
        self.__playedId = playerId
        self.__controllerByTrigger = {}
        self.__shakableControllersByTrigger = {}
        self.__shakableControllers = []

    def __createController(self, controllerClass):
        if controllerClass not in self.__controllersByClass or not controllerClass.SINGLE:
            controller = controllerClass(self.__playedId, self.__settings)
            self.__controllersByClass[controllerClass] = controller
            self.__controllers.append(controller)
            self.__registerAxises(controller)
            self.__registerTriggers(controller)
            self.__registerShakeTriggers(controller)
            return controller
        else:
            return self.__controllersByClass[controllerClass]

    def __registerShakeTriggers(self, controller):
        if isinstance(controller, AileronBaseController):
            if controller.isShakeSettingsPresent:
                self.__shakableControllers.append(controller)
                for state in controller.triggerStates:
                    for trigger in state.shakeState.triggers:
                        try:
                            self.__shakableControllersByTrigger[trigger].append(controller)
                        except KeyError:
                            self.__shakableControllersByTrigger[trigger] = [controller]

    def __registerAxises(self, controller):
        for axis in controller.axis:
            if axis in self.__controllerByAxis:
                self.__controllerByAxis[axis].append(controller)
            else:
                self.__controllerByAxis[axis] = [controller]
            if axis in self.__axisValues:
                controller.setValue(self.__axisValues[axis], axis)

    def __registerTriggers(self, controller):
        for trigger in controller.triggers:
            if trigger in self.__controllerByTrigger:
                self.__controllerByTrigger[trigger].append(controller)
            else:
                self.__controllerByTrigger[trigger] = [controller]
            if trigger in self.__triggerValues:
                controller.setValue(self.__triggerValues[trigger], trigger)

    def onLoaded(self, context):
        for controller in self.__controllers:
            controller.onLoaded(context)

    def destroy(self):
        for controller in self.__controllers:
            controller.destroy()

        self.__settings = None
        self.__controllers = []
        self.__controllersByClass.clear()
        self.__controllerByAxis.clear()
        self.__controllerByTrigger.clear()
        self.__shakableControllersByTrigger.clear()
        self.__shakableControllers = []
        return

    def getController(self, controllerName):
        controllerClass = _CONTROLLERS_MAP.get(controllerName, None)
        if controllerClass:
            return self.__createController(controllerClass)
        else:
            return

    def showPropellorBlade(self, visible):
        if FORCE_AXIS in self.__controllerByAxis:
            for controller in self.__controllerByAxis[FORCE_AXIS]:
                if controller.__class__ is PropellorControllerL or controller.__class__ is PropellorControllerR:
                    controller.showPropellorBlade(visible)

    def setAxisValue(self, axis, value):
        self.__axisValues[axis] = value
        if axis in self.__controllerByAxis:
            for controller in self.__controllerByAxis[axis]:
                controller.setValue(value, axis)

    def setTriggerValue(self, trigger, value):
        self.__triggerValues[trigger] = value
        if trigger in self.__controllerByTrigger:
            for controller in self.__controllerByTrigger[trigger]:
                controller.trigger(trigger, value)

    def setPropellorAngle(self, left, right):
        angles = [left, right]
        id = 0
        for controller in self.__controllers:
            if controller.__class__ is PropellorControllerL or controller.__class__ is PropellorControllerR:
                controller.setAngle(angles[id % len(angles)])
                id += 1

    def setEffectVisible(self, effectName, value):
        for controller in self.__shakableControllersByTrigger.get(effectName, tuple()):
            controller.setTriggerState(effectName, value)

    def updatePlaneSpeed(self, currSpeed, engineMaxSpeed, diveSpeed):
        coef = (currSpeed - engineMaxSpeed) / (diveSpeed - engineMaxSpeed)
        coef = max(min(coef, 1.0), 0.0)
        for controller in self.__shakableControllers:
            controller.updatePlaneNormSpeed(coef)

    def reloadControllerSettings(self):
        for controller in self.__controllers:
            controller.reloadSettings()

    def onOwnerChanged(self, owner):
        for controller in self.__controllers:
            controller.onOwnerChanged(owner)