# Embedded file name: scripts/common/ComponentModel/CameraComponents.py
import sys
import inspect
import BigWorld
import Math
import math
from db import DBLogic
from Component import Component, InputSlot, OutputSlot
from consts import IS_CLIENT, IS_EDITOR
from MathExt import clamp
from debug_utils import LOG_ERROR
if IS_CLIENT:
    from CameraStates import CameraState
    from gui.Scaleform.utils.HangarSpace import g_hangarSpace
hangarCameraOldMatrix = Math.Matrix()
isFreeHangarCamera = False

class FreeHangarCamera(Component):

    @classmethod
    def componentCategory(cls):
        return 'Camera'

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, FreeHangarCamera._onInput), InputSlot('enable', Component.SLOT_BOOL, None), OutputSlot('out', Component.SLOT_EVENT, None)]

    def _onInput(self, enable):
        global isFreeHangarCamera
        global hangarCameraOldMatrix
        if IS_CLIENT:
            if g_hangarSpace is not None:
                clientHangarSpace = g_hangarSpace.space
                if clientHangarSpace:
                    if enable and not isFreeHangarCamera:
                        hangarCameraOldMatrix = BigWorld.camera().parentMatrix
                        clientHangarSpace.hangarCamera.setState(CameraState.SuperFree)
                        isFreeHangarCamera = True
                    if not enable and isFreeHangarCamera:
                        BigWorld.camera().parentMatrix = hangarCameraOldMatrix
                        clientHangarSpace.hangarCamera.setDirectAngle(0, 0)
                        clientHangarSpace.hangarCamera.leaveState()
                        isFreeHangarCamera = False
        return 'out'


class SetCameraPosAndTarget(Component):
    FRAMES_TO_SKIP = 20

    def __init__(self):
        self._parent = Math.Matrix()
        self._matrix = Math.Matrix()
        self._inverted = Math.Matrix()
        self.prevYaw = None
        self.skipFrames = 0
        self.prevMatrixYaw = None
        self.prevMatrixPitch = None
        self.prevMatrixRoll = None
        return

    @classmethod
    def componentCategory(cls):
        return 'Camera'

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetCameraPosAndTarget._onInput),
         InputSlot('reset_yaw', Component.SLOT_EVENT, SetCameraPosAndTarget._onReset),
         InputSlot('position', Component.SLOT_VECTOR3, None),
         InputSlot('target', Component.SLOT_VECTOR3, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _onReset(self, position, targetPos):
        self.prevYaw = None
        self.skipFrames = 0
        self.prevMatrixYaw = None
        self.prevMatrixPitch = None
        self.prevMatrixRoll = None
        return

    def _onInput(self, position, targetPos):
        localPos = targetPos - position
        localPos.normalise()
        yawOnTarget = math.atan2(localPos.x, localPos.z)
        pitchOnTarget = -math.asin(clamp(-1.0, localPos.y, 1.0))
        if self.prevYaw:
            alternativeYaw = yawOnTarget - math.pi if yawOnTarget > 0 else yawOnTarget + math.pi
            if math.fabs(alternativeYaw - self.prevYaw) < math.fabs(yawOnTarget - self.prevYaw):
                yawOnTarget = alternativeYaw
                pitchOnTarget = math.pi - pitchOnTarget if pitchOnTarget > 0 else -math.pi - pitchOnTarget
        self.prevYaw = yawOnTarget
        self._matrix.setRotateYPR((yawOnTarget, pitchOnTarget, 0))
        self._matrix.translation = position
        if self.prevMatrixYaw:
            if math.fabs(self.prevMatrixYaw - self._matrix.yaw) > 0.1:
                self.skipFrames = SetCameraPosAndTarget.FRAMES_TO_SKIP
            elif math.fabs(self.prevMatrixPitch - self._matrix.pitch) > 0.1:
                self.skipFrames = SetCameraPosAndTarget.FRAMES_TO_SKIP
            elif math.fabs(self.prevMatrixRoll - self._matrix.roll) > 0.1:
                self.skipFrames = SetCameraPosAndTarget.FRAMES_TO_SKIP
        else:
            self.prevMatrixYaw = self._matrix.yaw
            self.prevMatrixPitch = self._matrix.pitch
            self.prevMatrixRoll = self._matrix.roll
        if self.skipFrames > 0:
            self.skipFrames = self.skipFrames - 1
            self._parent.translation = self._matrix.translation
        else:
            self._parent.set(self._matrix)
            if math.fabs(math.fabs(self.prevMatrixYaw) - math.fabs(self._matrix.yaw)) < 0.05 and math.fabs(math.fabs(self.prevMatrixPitch) - math.fabs(self._matrix.pitch)) < 0.05:
                self.prevMatrixYaw = self._matrix.yaw
                self.prevMatrixPitch = self._matrix.pitch
                self.prevMatrixRoll = self._matrix.roll
        if IS_CLIENT:
            if g_hangarSpace is not None:
                clientHangarSpace = g_hangarSpace.space
                if clientHangarSpace:
                    strategy = clientHangarSpace.hangarCamera.getStateStrategy()
                    if strategy and isinstance(strategy, BigWorld.CameraStrategySuperFree):
                        strategy.parentProvider = self._parent
                        BigWorld.camera().parentMatrix = self._parent
                        clientHangarSpace.hangarCamera.setDirectAngle(yawOnTarget, pitchOnTarget)
        else:
            import WorldEditor
            self._inverted.set(self._parent)
            self._inverted.invert()
            WorldEditor.camera(0).view = self._inverted
        return 'out'


class SetCameraPosAndRotation(Component):

    def __init__(self):
        self._source = Math.Matrix()
        self._target = Math.Matrix()
        self._parent = Math.Matrix()

    @classmethod
    def componentCategory(cls):
        return 'Camera'

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetCameraPosAndRotation._onInput),
         InputSlot('position', Component.SLOT_VECTOR3, None),
         InputSlot('yaw', Component.SLOT_ANGLE, None),
         InputSlot('pitch', Component.SLOT_ANGLE, None),
         InputSlot('roll', Component.SLOT_ANGLE, None),
         OutputSlot('out', Component.SLOT_EVENT, None)]

    def _onInput(self, position, yaw, pitch, roll):
        self._parent.setRotateYPR(Math.Vector3(yaw, pitch, roll))
        self._parent.translation = position
        if IS_CLIENT:
            if g_hangarSpace is not None:
                clientHangarSpace = g_hangarSpace.space
                if clientHangarSpace:
                    strategy = clientHangarSpace.hangarCamera.getStateStrategy()
                    if strategy and isinstance(strategy, BigWorld.CameraStrategySuperFree):
                        direction = Math.Vector3(self._parent.get(2, 0), self._parent.get(2, 1), self._parent.get(2, 2))
                        fakeTarget = Math.Vector3(position.x + direction.x, position.y + direction.y, position.z + direction.z)
                        self._source.setTranslate(position)
                        self._target.setTranslate(fakeTarget)
                        strategy.sourceProvider = self._source
                        strategy.targetProvider = self._target
                        BigWorld.camera().parentMatrix = self._parent
        else:
            import WorldEditor
            self._parent.invert()
            WorldEditor.camera(0).view = self._parent
        return 'out'


class SplinePoint(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('spline_id', Component.SLOT_STR, None, Component.EDITOR_SPLINE_NAME_SELECTOR),
         InputSlot('time', Component.SLOT_FLOAT, None),
         OutputSlot('position', Component.SLOT_VECTOR3, SplinePoint._getSplinePos),
         OutputSlot('yaw', Component.SLOT_ANGLE, SplinePoint._getSplineYaw),
         OutputSlot('pitch', Component.SLOT_ANGLE, SplinePoint._getSplinePitch),
         OutputSlot('roll', Component.SLOT_ANGLE, SplinePoint._getSplineRoll)]

    def _getSplinePos(self, splineId, time):
        sp = DBLogic.g_instance.getSpline(splineId)
        if sp:
            return sp.getPointForTime(time)
        LOG_ERROR('[VSE] Spline does not exist: {0}'.format(splineId))
        return Math.Vector3(0, 0, 0)

    def _getSplineYaw(self, splineId, time):
        spline = DBLogic.g_instance.getSpline(splineId)
        if not spline:
            LOG_ERROR('[VSE] Spline does not exist: {0}'.format(splineId))
            return 0.0
        if IS_CLIENT:
            return spline.bwSpline.getYawForTime(time)
        A = spline.getPointForTime(time - 1.0)
        C = spline.getPointForTime(time + 1.0)
        return math.atan2(C.x - A.x, C.z - A.z)

    def _getSplineRoll(self, splineId, time):
        return 0.0

    def _getSplinePitch(self, splineId, time):
        return 0.0


class SplineDuration(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('spline_id', Component.SLOT_STR, None, Component.EDITOR_SPLINE_NAME_SELECTOR), OutputSlot('duration', Component.SLOT_FLOAT, SplineDuration._getSplineDuration)]

    def _getSplineDuration(self, splineId):
        sp = DBLogic.g_instance.getSpline(splineId)
        if sp:
            return sp.totalTime
        LOG_ERROR('[VSE] Spline does not exist: {0}'.format(splineId))
        return 0.0


class CameraFov(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    @classmethod
    def componentCategory(cls):
        return 'Camera'

    def slotDefinitions(self):
        return [OutputSlot('res', Component.SLOT_ANGLE, CameraFov._getFov)]

    def _getFov(self):
        if IS_CLIENT:
            return BigWorld.projection().fov
        else:
            import WorldEditor
            return WorldEditor.getCameraFOV()


class SetCameraFov(Component):

    @classmethod
    def componentCategory(cls):
        return 'Camera'

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_CLIENT]

    def slotDefinitions(self):
        return [InputSlot('input', Component.SLOT_EVENT, SetCameraFov._onInput), InputSlot('fov', Component.SLOT_ANGLE, None), OutputSlot('out', Component.SLOT_EVENT, None)]

    def _onInput(self, fov):
        if fov <= 0.017:
            LOG_ERROR('[VSE] Wrong Camera FOV: {0}'.format(fov))
        elif fov >= 3.1416:
            LOG_ERROR('[VSE] Wrong Camera FOV: {0}'.format(fov))
        elif IS_CLIENT:
            BigWorld.projection().fov = fov
        else:
            import WorldEditor
            WorldEditor.setCameraFOV(fov)
        return 'out'


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))