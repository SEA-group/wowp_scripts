# Embedded file name: scripts/client/CameraStrategyLegacyProxy.py
import math
import Math
from consts import LOGICAL_PART, WORLD_SCALING, SPEED_SCALING
import BigWorld
from BigWorld import *
import CameraEffect
import GameEnvironment
from consts import FORCE_AXIS, FLAPS_AXIS, HORIZONTAL_AXIS, VERTICAL_AXIS, ROLL_AXIS, FREE_HORIZONTAL_CAM, FREE_VERTICAL_CAM
from debug_utils import LOG_DEBUG
from MathExt import clamp
from itertools import chain
import ResMgr
from db.DBHelpers import readValue
from Curve import Curve

class SplineEasing(object):

    def __init__(self, params, count = 20):
        self._count = count
        self._reInit(params)

    @staticmethod
    def _getVectorData(params):
        if isinstance(params, basestring):
            allValues = params.split(', ')
            return map(lambda x, y: Math.Vector2(float(x), float(y)), allValues[::2], allValues[1::2])
        return params

    @staticmethod
    def _strFormat(params):
        if isinstance(params, basestring):
            return params
        return ', '.join(map(lambda e: str(e), chain(*params)))

    def _reInit(self, params):
        self._params = self._strFormat(params)
        allVectors = self._getVectorData(params)
        X = sorted(map(lambda e: e.x, allVectors))
        minX, maxX = X[0], X[-1]
        Y = sorted(map(lambda e: e.y, allVectors))
        minY, maxY = Y[0], Y[-1]
        diffX = maxX - minX
        diffY = maxY - minY
        for vector in allVectors:
            vector.x -= minX
            vector.x /= diffX
            vector.y -= minY
            vector.y /= diffY

        self._curve = Math.Curve(allVectors, self._count)
        self._curve.refresh()

    def calcInterpolation(self, minValue, maxValue, t, d):
        t = clamp(0.0, t / d, 1.0)
        return minValue + (maxValue - minValue) * self._curve.calc(t)

    def __call__(self, minValue, maxValue, t, d):
        return self.calcInterpolation(minValue, maxValue, t, d)

    def __str__(self, *args, **kwargs):
        return self.getParams()

    def getParams(self):
        return self._params

    def setParams(self, params):
        return self._reInit(params)


class Timeline(SplineEasing):

    def calcInterpolation(self, minValue, maxValue, t, d):
        return self._curve.calc(t)

    def __call__(self, minValue, maxValue, t, d):
        return self.calcInterpolation(minValue, maxValue, t, d)

    def __init__(self, params, count = 20):
        SplineEasing.__init__(self, params, count)

    def _reInit(self, params):
        self._params = self._strFormat(params)
        self._curve = Math.Curve(self._getVectorData(params), self._count)
        self._curve.refresh()


class CameraStrategyLegacyProxy(object):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix, cursor):
        self.defaultFov = 0.0
        self.fovMultiplier = 1.0
        self.__needUpdate = 1
        self.__behaviorHorizon = 1
        self.__isInDebugMode = False
        self._planeMtxProvider = Math.MatrixProduct()
        self._planeMtxProvider.a = sourceMatrix
        self._planeMtxProvider.b = Math.Matrix()
        self._planeMtxProvider.b.setIdentity()
        self._cursorProvider = Math.MatrixProduct()
        self._cursorProvider.b = Math.Matrix()
        self._cursorProvider.b.setIdentity()
        self._cursor = cursor
        self._cursor.sourceMatrix = self._planeMtxProvider
        self._cursorProvider.a = self._cursor.matrix
        fov = BigWorld.CameraComponentGround()
        fov.minPositionSettings.planeDistance = 0.0
        fov.maxPositionSettings.planeDistance = 0.0
        fov.minFovMultiplier = 1.0
        fov.maxFovMultiplier = 1.0
        fov.interpolationFunc = SplineEasing([Math.Vector2(0, 0), Math.Vector2(1, 1)])
        fov.minArgumentValue = 0
        fov.maxArgumentValue = 1
        fov.duration = 0.01
        speed = BigWorld.CameraComponentGround()
        speed.maxPositionSettings.rotationAngle = math.radians(0.0)
        speed.maxPositionSettings.horizontalOffset = 1.0
        speed.maxPositionSettings.verticalOffset = 1.0
        speed.maxPositionSettings.planeDistance = -2
        speed.minPositionSettings.rotationAngle = math.radians(0.0)
        speed.minPositionSettings.horizontalOffset = 1.0
        speed.minPositionSettings.verticalOffset = 1.0
        speed.minPositionSettings.planeDistance = 0.0
        speed.maxFovMultiplier = 1.0
        speed.minFovMultiplier = 1.0
        speed.interpolationFunc = BigWorld.EaseInOutSinusoidal
        speed.minArgumentValue = 200
        speed.maxArgumentValue = 750
        speed.duration = 0.01
        ground = BigWorld.CameraComponentGround()
        ground.maxArgumentValue = 100.0
        ground.minArgumentValue = 1.0
        ground.maxPositionSettings.verticalOffset = 1.0
        ground.minPositionSettings.verticalOffset = 0.7
        ground.interpolationFunc = BigWorld.EaseInOutSinusoidal
        ground.duration = 10.0
        forsage = BigWorld.CameraComponentForsage()
        forsage.positionSettings.rotationAngle = math.radians(0.0)
        forsage.positionSettings.horizontalOffset = 1.0
        forsage.positionSettings.verticalOffset = 1.0
        forsage.maxFovMultiplier = 1.1
        forsage.durationIn = 1.5
        forsage.interpolationFuncIn = SplineEasing('0.0, 0.0, 1.0, 1.0')
        forsage.durationOut = 5.0
        forsage.interpolationFuncOut = SplineEasing('0.0, 0.0, 1.0, 1.0')
        forsage.shakeDuration = 1.0
        forsage.shakeAmplitude = math.radians(0.0)
        forsage.shakeMultiplier = 4.0
        forsage.maxArgumentValue = 1.0
        forsage.minArgumentValue = 0.0
        forsage.planeMatrix = self._planeMtxProvider
        forsage.cursorMatrix = self._cursorProvider
        brake = BigWorld.CameraComponentForsage()
        brake.positionSettings.rotationAngle = math.radians(0.0)
        brake.positionSettings.horizontalOffset = 1.0
        brake.positionSettings.verticalOffset = 1.0
        brake.maxFovMultiplier = 0.9
        brake.durationIn = 5.0
        brake.interpolationFuncIn = SplineEasing('0.0, 0.0, 1.0, 1.0')
        brake.durationOut = 5.0
        brake.interpolationFuncOut = SplineEasing('0.0, 0.0, 1.0, 1.0')
        brake.shakeDuration = 1.0
        brake.shakeAmplitude = math.radians(0.0)
        brake.shakeMultiplier = 4.0
        brake.maxArgumentValue = -1.0
        brake.minArgumentValue = 0.0
        brake.planeMatrix = self._planeMtxProvider
        brake.cursorMatrix = self._cursorProvider
        overlook = BigWorld.CameraComponentOverlook()
        overlook.maxFovMultiplier = 1.0
        overlook.duration = 0.005
        overlook.interpolationFunc = BigWorld.EaseInOutExponential
        overviewMode = BigWorld.CameraComponentForsage()
        overviewMode.maxFovMultiplier = 1.0
        overviewMode.positionSettings.planeDistance = -2
        overviewMode.durationIn = 0.4
        overviewMode.interpolationFuncIn = BigWorld.EaseInOutCubic
        overviewMode.durationOut = 0.4
        overviewMode.interpolationFuncOut = BigWorld.EaseInOutCubic
        overviewMode.maxArgumentValue = 1.0
        overviewMode.minArgumentValue = 0.0
        overviewMode.planeMatrix = Math.Matrix()
        overviewMode.planeMatrix.setIdentity()
        overviewMode.cursorMatrix = Math.Matrix()
        overviewMode.cursorMatrix.setIdentity()
        self.__offsetProvider = Math.Vector4Combiner()
        self.__offsetProvider.a = BigWorld.EllipticalPositionProvider()
        self.__offsetProvider.a.position = cameraPosition
        self.__offsetProvider.b = Math.Vector4(0.0, 0.0, 0.0, 0.0)
        self.__targetProvider = Math.Vector4Combiner()
        self.__targetProvider.a = cameraTarget
        self.__targetProvider.b = Math.Vector4(0.0, 0.0, 0.0, 0.0)
        self._cameraBasis = Math.MatrixProduct()
        self._cameraBasis.b = self._cursorProvider
        self._cameraBasis.a = overlook.effectMatrix
        self._input = BigWorld.CameraInput()
        self._input.accelerationDuration = 0.075
        self._input.decelerationDuration = 0.075
        self._input.planeMatrix = self._planeMtxProvider
        self._input.cursorMatrix = self._cursorProvider
        self._components = {'zoomStateFov': fov,
         'forsage': forsage,
         'brake': brake,
         'speed': speed,
         'ground': ground,
         'overlook': overlook,
         'overviewMode': overviewMode}
        self.__camera = BigWorld.CombatCamera(self.__offsetProvider, self.__targetProvider, Math.Vector4(0.0, 1.0, 0.0, 0.0), self._cameraBasis)

    def disableCourseComponents(self):
        self._components['forsage'].isActive = False
        self._components['brake'].isActive = False
        self._components['speed'].isActive = False
        self._components['ground'].isActive = False

    def enableCourseComponents(self):
        self._components['forsage'].isActive = True
        self._components['brake'].isActive = True
        self._components['speed'].isActive = True
        self._components['ground'].isActive = True

    def handleAxisInput(self, axis, value):
        if FORCE_AXIS == axis:
            self._components['forsage'].setTargetValue(value)
            self._components['brake'].setTargetValue(value)
        if FLAPS_AXIS == axis:
            pass
        if HORIZONTAL_AXIS == axis:
            self._input.handleAxisHorizontalInput(-value)
        if VERTICAL_AXIS == axis:
            self._input.handleAxisVerticalInput(value)
        if ROLL_AXIS == axis:
            self._input.handleAxisRollInput(value)
        if FREE_HORIZONTAL_CAM == axis:
            self._components['overlook'].handleHorizontalInput(value)
        if FREE_VERTICAL_CAM == axis:
            self._components['overlook'].handleVerticalInput(value)

    def ShadowUpdate(self, dt):
        self._input.update(dt)
        self._cursor.update(dt, self._input.freeVerticalInput, self._input.freeHorizontalInput)
        if self.__needUpdate == 0:
            return
        self._components['speed'].targetArgumentValue = BigWorld.player().getSpeed() * 3.6
        self._components['ground'].targetArgumentValue = BigWorld.player().getAltitudeAboveObstacle()
        rotationAngle = 0.0
        normalizedRotation = 0.0
        horizontalOffset = 1.0
        verticalOffset = 1.0
        planeDistance = 0.0
        fovMultiplier = 1.0
        position = Math.Vector3(0.0, 0.0, 0.0)
        for component in self._components.itervalues():
            component.Update(dt)
            rotationAngle += component.positionEffects.rotationAngle
            normalizedRotation += component.positionEffects.normalizedRotation
            horizontalOffset *= component.positionEffects.horizontalOffset
            verticalOffset *= component.positionEffects.verticalOffset
            planeDistance += component.positionEffects.planeDistance
            fovMultiplier *= component.fovMultiplier
            position += component.positionEffects.cameraPosition

        self.fovMultiplier = fovMultiplier
        self.__offsetProvider.a.normalizedRotation = normalizedRotation
        self.__offsetProvider.a.maxRotationAngle = rotationAngle
        self.__offsetProvider.a.horizontalOffset = horizontalOffset
        self.__offsetProvider.a.verticalOffset = verticalOffset
        self.__offsetProvider.a.planeDistance = planeDistance
        if position.max() > 0.0:
            self.__offsetProvider.a.position = Math.Vector4(position.x, position.y, position.z, 0.0)
        self.__camera.Update(dt)

    def Update(self, dt):
        if self.__needUpdate:
            self.ShadowUpdate(dt)
        return self.__camera.viewMatrix

    def setZoomStateFov(self, newNormFov):
        self._components['zoomStateFov'].targetArgumentValue = newNormFov

    def setZoomStateInitialData(self, **data):
        fov = self._components['zoomStateFov']
        fov.minPositionSettings.planeDistance = data.get('minPosition', 0)
        fov.maxPositionSettings.planeDistance = data.get('maxPosition', 0)
        fov.minFovMultiplier = data.get('minFovMultiplier', 1)
        fov.maxFovMultiplier = data.get('maxFovMultiplier', 1)
        fov.duration = data.get('duration', 0.01)

    def onSpeedStateMachineInitialized(self, minSpeed, maxSpeed):
        speed = self._components['speed']
        speed.minArgumentValue = minSpeed / WORLD_SCALING * SPEED_SCALING
        speed.maxArgumentValue = maxSpeed / WORLD_SCALING * SPEED_SCALING

    def rotateCursor(self, pitch, yaw):
        self._input.handleFreeInput(pitch, yaw)

    def lockCursor(self):
        self._input.lock()

    def unlockCursor(self):
        self._input.unlock()

    def setCursorOrientation(self, mtx):
        self._cursor.setOrientation(mtx)
        self._input.reset()

    def setCameraOrientation(self, mtx):
        self.__camera.SetOrientation(mtx)

    def isCursorLocked(self):
        return self._input.isInputBlocked

    def reset(self):
        self._input.reset()
        self._cursor.reset()
        self.__camera.Reset()
        for component in self._components.itervalues():
            component.Reset()

    def resetComponents(self):
        for component in self._components.itervalues():
            component.Reset()

    def getModifiers(self):
        return self._components

    def Activate(self):
        self.__needUpdate = 1

    def Deactivate(self):
        self.__needUpdate = 0

    def overviewModeEnable(self):
        self._components['overviewMode'].setTargetValue(1.0)

    def overviewModeDisable(self):
        self._components['overviewMode'].setTargetValue(0.0)

    @property
    def isDebugEnabled(self):
        return self.__isInDebugMode

    @isDebugEnabled.setter
    def isDebugEnabled(self, value):
        self._cursor.isDebugEnabled = value
        self.__camera.isDebugEnabled = value

    @property
    def sourceMatrix(self):
        return self._planeMtxProvider

    @sourceMatrix.setter
    def sourceMatrix(self, value):
        self._planeMtxProvider.a = value

    @property
    def offsetProvider(self):
        return self.__offsetProvider

    @offsetProvider.setter
    def offsetProvider(self, value):
        self.__offsetProvider.a = value

    @property
    def targetProvider(self):
        return self.__targetProvider

    @targetProvider.setter
    def targetProvider(self, value):
        self.__targetProvider.a = value

    @property
    def flexibility(self):
        return 0.0

    @flexibility.setter
    def flexibility(self, value):
        pass

    @property
    def cursorMatrixProvider(self):
        return self._cursorProvider

    @property
    def cursorDirection(self):
        return self._cursor.direction

    @property
    def cursorUp(self):
        return self._cursor.up

    @property
    def cameraDirection(self):
        return self.__camera.direction

    def getState(self):
        return {'cameraBasis': Math.Matrix(self._cameraBasis)}

    def setState(self, state):
        pass


class CameraStrategyMouse(CameraStrategyLegacyProxy):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix):
        CameraStrategyLegacyProxy.__init__(self, cameraPosition, cameraTarget, sourceMatrix, BigWorld.CursorFree())
        self.__horizontalStrafe = BigWorld.CameraComponentStrafe()
        self.__horizontalStrafe.positionSettings.normalizedRotation = 0.85
        self.__horizontalStrafe.position = cameraPosition
        self.__horizontalStrafe.planeMatrix = self._planeMtxProvider
        self.__horizontalStrafe.cursorMatrix = self._cursorProvider
        self.__horizontalStrafe.targetEntityId = BigWorld.player().id
        self._components['horizontalStrafe'] = self.__horizontalStrafe
        self._overlook = False
        self._input.isContinuousFreeInput = False
        self._input.accelerationDuration = 0.075
        self._input.decelerationDuration = 0.075
        self.__behaviorHorizon = 1

    @property
    def overlookData(self):
        return self._overlookData

    @property
    def behaviorHorizon(self):
        return self.__behaviorHorizon

    @behaviorHorizon.setter
    def behaviorHorizon(self, value):
        self.__behaviorHorizon = value

    def ShadowUpdate(self, dt):
        self._cursor.isfollowingPlane = self._input.isInputBlocked
        CameraStrategyLegacyProxy.ShadowUpdate(self, dt)

    def overviewModeEnable(self):
        self._overlook = True
        snapCursorMatrix = Math.Matrix()
        snapCursorMatrix.set(self._cursorProvider)
        self.__horizontalStrafe.cursorMatrix = snapCursorMatrix
        CameraStrategyLegacyProxy.overviewModeEnable(self)

    def overviewModeDisable(self):
        self._overlook = False
        self.__horizontalStrafe.cursorMatrix = self._cursorProvider
        CameraStrategyLegacyProxy.overviewModeDisable(self)

    @property
    def isInOverview(self):
        return self._overlook

    def applyOverviewDistance(self, dz):
        pass

    @property
    def bottomPitchBound(self):
        return self._cursor.bottomPitchLimit

    @bottomPitchBound.setter
    def bottomPitchBound(self, value):
        self._cursor.bottomPitchLimit = value

    @property
    def topPitchBound(self):
        return self._cursor.topPitchLimit

    @topPitchBound.setter
    def topPitchBound(self, value):
        self._cursor.topPitchLimit = value

    @property
    def isPitchLimited(self):
        return self._cursor.isPitchLimited

    @isPitchLimited.setter
    def isPitchLimited(self, value):
        self._cursor.isPitchLimited = value

    @property
    def yawLimit(self):
        return self._cursor.yawLimit

    @yawLimit.setter
    def yawLimit(self, value):
        self._cursor.yawLimit = value

    @property
    def isYawLimited(self):
        return self._cursor.isYawLimited

    @isYawLimited.setter
    def isYawLimited(self, value):
        self._cursor.isYawLimited = value


class CameraStrategyGamepad(CameraStrategyMouse):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix):
        CameraStrategyMouse.__init__(self, cameraPosition, cameraTarget, sourceMatrix)
        self._input.isContinuousFreeInput = True

    def rotateCursorSpeed(self, pitch, yaw):
        self._input.handleFreeInput(pitch * math.radians(1.0), yaw * math.radians(1.0))


class CameraStrategyJoystick(CameraStrategyLegacyProxy):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix):
        cursor = BigWorld.Cursor()
        cursor.alignmentSpeedUp = 1000.0
        CameraStrategyLegacyProxy.__init__(self, cameraPosition, cameraTarget, sourceMatrix, cursor)
        self._components['overlook'].duration = 1.5
        self._input.isContinuousFreeInput = True


class CameraStrategyGunner(CameraStrategyLegacyProxy):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix):
        CameraStrategyLegacyProxy.__init__(self, cameraPosition, cameraTarget, sourceMatrix, BigWorld.CursorFree())
        self.__addComponents()
        self._input.isContinuousFreeInput = False
        self._input.accelerationDuration = 0.075
        self._input.decelerationDuration = 0.075
        self._cursor = BigWorld.CursorFree()
        self._cursor.sourceMatrix = self._planeMtxProvider
        self._cursor.planeFollowingSpeed = 3.0
        self._cursor.targetUp = Math.Vector4(0, 1, 0, 0)
        self._cursor.alignmentSpeedUp = 10000.0
        self._cursorProvider.a = self._cursor.matrix
        self._cameraBasis.b = BigWorld.ShiftedMatrixProvider(self._cursorProvider, Math.Vector3(0.0, 0.0, 0.0))

    def __addComponents(self):
        self.disableCourseComponents()
        sectorDist = BigWorld.CameraComponentGround()
        sectorDist.minPositionSettings.planeDistance = 0.0
        sectorDist.maxPositionSettings.planeDistance = 0.0
        sectorDist.interpolationFunc = SplineEasing([Math.Vector2(0, 0), Math.Vector2(1, 1)])
        sectorDist.minArgumentValue = 0
        sectorDist.maxArgumentValue = 1
        sectorDist.duration = 0.01
        sectorHeight = BigWorld.CameraComponentGround()
        sectorHeight.minPositionSettings.planeDistance = 0.0
        sectorHeight.maxPositionSettings.planeDistance = 0.0
        sectorHeight.interpolationFunc = SplineEasing([Math.Vector2(0, 0), Math.Vector2(1, 1)])
        sectorHeight.minArgumentValue = 0
        sectorHeight.maxArgumentValue = 1
        sectorHeight.duration = 0.01
        self._components['gunnerSectorDist'] = sectorDist
        self._components['gunnerSectorHeight'] = sectorHeight

    def setSectorDistSettings(self, **data):
        duration = data.get('duration', 0.01)
        sectorDist = self._components['gunnerSectorDist']
        sectorDist.duration = duration
        sectorDist.minPositionSettings.planeDistance = data.get('minPosition', 0)
        sectorDist.maxPositionSettings.planeDistance = data.get('maxPosition', 0)
        sectorDist.interpolationFunc = SplineEasing(data.get('distanceCurvePoints', [Math.Vector2(0, 0), Math.Vector2(1, 1)]))
        sectorHeight = self._components['gunnerSectorHeight']
        sectorHeight.duration = duration
        sectorHeight.minPositionSettings.planeDistance = data.get('minHeight', 0)
        sectorHeight.maxPositionSettings.planeDistance = data.get('maxHeight', 0)
        sectorHeight.interpolationFunc = SplineEasing(data.get('heightCurvePoints', [Math.Vector2(0, 0), Math.Vector2(1, 1)]))

    def ShadowUpdate(self, dt):
        CameraStrategyLegacyProxy.ShadowUpdate(self, dt)
        normalizedAngle = self.cursorDirection.angle(Math.Vector3(0, 1, 0)) / math.pi
        self._components['gunnerSectorDist'].targetArgumentValue = normalizedAngle
        self._components['gunnerSectorHeight'].targetArgumentValue = normalizedAngle
        currHeight = self._components['gunnerSectorHeight'].positionEffects.planeDistance
        self._cameraBasis.b.offset = Math.Vector3(0.0, currHeight, 0.0)

    def applyCursorToDirection(self, direction):
        self._cursor.applyToDirection(direction)
        self._input.reset()

    @property
    def bottomPitchBound(self):
        return self._cursor.bottomPitchLimit

    @bottomPitchBound.setter
    def bottomPitchBound(self, value):
        self._cursor.bottomPitchLimit = value

    @property
    def topPitchBound(self):
        return self._cursor.topPitchLimit

    @topPitchBound.setter
    def topPitchBound(self, value):
        self._cursor.topPitchLimit = value

    @property
    def isPitchLimited(self):
        return self._cursor.isPitchLimited

    @isPitchLimited.setter
    def isPitchLimited(self, value):
        self._cursor.isPitchLimited = value


class CameraStrategyDebug(object):

    def __init__(self, cameraPosition, cameraTarget, sourceMatrix, cursor):
        self._planeMtxProvider = Math.MatrixProduct()
        self._planeMtxProvider.a = sourceMatrix
        self._planeMtxProvider.b = Math.Matrix()
        self._planeMtxProvider.b.setIdentity()
        self.__camera = BigWorld.CombatCamera(cameraPosition, cameraTarget, Math.Vector4(0.0, 1.0, 0.0, 0.0), self._planeMtxProvider)
        self.__camera.Reset()

    def reset(self):
        self.__camera.Reset()

    def ShadowUpdate(self, dt):
        self.__camera.Update(dt)

    def Update(self, dt):
        self.ShadowUpdate(dt)
        return self.__camera.viewMatrix

    @property
    def cursorMatrixProvider(self):
        return self._planeMtxProvider

    def handleAxisInput(self, axis, value):
        pass

    @property
    def sourceMatrix(self):
        return self._planeMtxProvider

    @sourceMatrix.setter
    def sourceMatrix(self, value):
        self._planeMtxProvider.a = value
        self.reset()

    @property
    def cursorDirection(self):
        m = Math.Matrix()
        m.set(self._planeMtxProvider)
        return m.applyToAxis(2)