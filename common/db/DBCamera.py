# Embedded file name: scripts/common/db/DBCamera.py
import math
import Math
from DBHelpers import readValue, findSection
from consts import WORLD_SCALING
from collections import namedtuple

class ZoomData(object):

    def __init__(self, data = None, baseFov = 60.0):
        if data is not None:
            readValue(self, data, 'position', Math.Vector3(0, 0, 0))
            readValue(self, data, 'minScrollPosition', Math.Vector3(0, 0, -12.0))
            readValue(self, data, 'maxScrollPosition', Math.Vector3(0, 0, -34.0))
            readValue(self, data, 'fovPercent', 60.0)
            readValue(self, data, 'angle', 0.0)
            readValue(self, data, 'hideModel', 0)
            self.position *= WORLD_SCALING
            if self.fovPercent > 5.0:
                self.fovPercent /= baseFov
        return


ZoomPreset = namedtuple('ZoomPreset', ('normal', 'sniper'))

class DestroyedFallStateSettings(object):

    def __init__(self, data = None):
        if data is not None:
            readValue(self, data, 'stateInterpolationTime', 0.0)
            readValue(self, data, 'animationNeedTime', 0.0)
            readValue(self, data, 'animationStartTime', 0.0)
            readValue(self, data, 'animationPitch', 0.0)
            readValue(self, data, 'animationYaw', 0.0)
            readValue(self, data, 'animationPitchClockwise', True)
            readValue(self, data, 'animationYawClockwise', True)
            readValue(self, data, 'animationDistance', 0.0)
            readValue(self, data, 'animationTime', 0.0)
            readValue(self, data, 'animationFov', 90.0)
            readValue(self, data, 'animationFadeInTime', 0.0)
            readValue(self, data, 'animationFadeOutTime', 0.0)
            readValue(self, data, 'animationGroundNeedTime', 0.0)
            readValue(self, data, 'animationGroundTime', 0.0)
            readValue(self, data, 'animationGroundFov', 0.0)
            readValue(self, data, 'animationGroundSpawnRadius', 0.0)
            readValue(self, data, 'animationGroundHeight', 0.0)
            self.__postLoadTransform()
        return

    def __postLoadTransform(self):
        self.animationDistance *= WORLD_SCALING
        self.animationFov = math.radians(self.animationFov)
        self.animationGroundFov = math.radians(self.animationGroundFov)
        self.animationGroundSpawnRadius *= WORLD_SCALING
        self.animationGroundHeight *= WORLD_SCALING


class DestroyedLandedStateSettings(object):

    def __init__(self, data = None):
        if data is not None:
            readValue(self, data, 'stateInterpolationTime', 0.0)
            readValue(self, data, 'fov', 0.0)
            readValue(self, data, 'pitch', 0.0)
            readValue(self, data, 'pitchMin', 0.0)
            readValue(self, data, 'yaw', 0.0)
            readValue(self, data, 'rotationSpeed', 0.0)
            readValue(self, data, 'distance', 0.0)
            self.__postLoadTransform()
        return

    def __postLoadTransform(self):
        self.pitch = math.radians(self.pitch)
        self.pitchMin = math.radians(self.pitchMin)
        self.yaw = math.radians(self.yaw)
        self.distance *= WORLD_SCALING


class GunnerStateSettings(object):

    def __init__(self, data = None):
        if data is not None:
            readValue(self, data, 'duration', 0.0)
            distanceCurvePoints = self.readPoints(findSection(data, 'distanceCurve'))
            self.distanceCurvePoints = distanceCurvePoints['points']
            self.minDeltaPosition = distanceCurvePoints['minValue']
            self.maxDeltaPosition = distanceCurvePoints['maxValue']
            heightCurvePoints = self.readPoints(findSection(data, 'heightCurve'))
            self.heightCurvePoints = heightCurvePoints['points']
            self.minHeight = heightCurvePoints['minValue']
            self.maxHeight = heightCurvePoints['maxValue']
        return

    def readPoints(self, data):
        points = [Math.Vector2(-90, 0), Math.Vector2(90, 0)]
        if data is not None:
            points = data.readVector2s('point')
        ySortedCurvePoints = sorted(points, key=lambda e: e.y)
        minValue = ySortedCurvePoints[0].y
        maxValue = ySortedCurvePoints[-1].y
        norma = maxValue > minValue
        for p in points:
            p.x = (0.5 * math.pi - math.radians(p.x)) / math.pi
            p.y = (p.y - minValue) / (maxValue - minValue) if norma else 0

        points = sorted(points, key=lambda e: e.x)
        minValue *= WORLD_SCALING
        maxValue *= WORLD_SCALING
        return {'points': points,
         'minValue': minValue,
         'maxValue': maxValue}


class CameraSettings(object):

    def __init__(self, data = None):
        self.destroyedFall = None
        self.destroyedLanded = None
        self.gunnerStateSettings = None
        self.zoomPresets = dict()
        self.readData(data)
        return

    def __postLoadTransform(self):
        self.backCamPos *= WORLD_SCALING
        self.targetCamPos *= WORLD_SCALING
        self.rearViewCamPos *= WORLD_SCALING
        self.rearViewCamDir *= WORLD_SCALING
        self.leftCamPos *= WORLD_SCALING
        self.rightCamPos *= WORLD_SCALING
        self.topCamPos *= WORLD_SCALING
        self.bottomCamPos *= WORLD_SCALING
        self.pivotDistMax *= WORLD_SCALING
        self.pivotDistMin *= WORLD_SCALING
        self.freeCamFovNear = math.radians(self.freeCamFovNear)
        self.freeCamFovFar = math.radians(self.freeCamFovFar)

    def readData(self, data):
        if data != None:
            readValue(self, data, 'minMouseCombatFov', 70.0)
            readValue(self, data, 'targetCamPos', Math.Vector3(0, 0, -34.0))
            readValue(self, data, 'camSpeedYawPitch', 6.0)
            readValue(self, data, 'camSpeedRoll', 6.0)
            readValue(self, data, 'targetCamSpeed', 30.0)
            readValue(self, data, 'camSniperSpeedYawPitch', 6.0)
            readValue(self, data, 'camSniperSpeedRoll', 6.0)
            readValue(self, data, 'camSniperSpeedTarget', 30.0)
            readValue(self, data, 'defaultFov', 60.0)
            readValue(self, data, 'fovRampCurvature', 0.7)
            readValue(self, data, 'backCamPos', Math.Vector3(0, 3, -4.2))
            readValue(self, data, 'backCamSpeed', 30.0)
            readValue(self, data, 'backTargetCamSpeed', 30.0)
            readValue(self, data, 'backCamFov', 90.0)
            readValue(self, data, 'rearViewCamPos', Math.Vector3(0, 4.8, -22.6))
            readValue(self, data, 'rearViewCamDir', Math.Vector3(0, 22, -350))
            readValue(self, data, 'rearViewCamFov', 60.0)
            readValue(self, data, 'leftCamPos', Math.Vector3(0, 0, 0))
            readValue(self, data, 'leftCamDir', Math.Vector3(0, 0, 0))
            readValue(self, data, 'rightCamPos', Math.Vector3(0, 0, 0))
            readValue(self, data, 'rightCamDir', Math.Vector3(0, 0, 0))
            readValue(self, data, 'topCamPos', Math.Vector3(0, 0, 0))
            readValue(self, data, 'topCamDir', Math.Vector3(0, 0, 0))
            readValue(self, data, 'bottomCamPos', Math.Vector3(0, 0, 0))
            readValue(self, data, 'bottomCamDir', Math.Vector3(0, 0, 0))
            readValue(self, data, 'pivotDistMax', 150.0)
            readValue(self, data, 'pivotDistMin', 5.4)
            readValue(self, data, 'freeCamDistHalflife', 0.0)
            readValue(self, data, 'freeCamFovNear', 65.0)
            readValue(self, data, 'freeCamFovFar', 65.0)
            readValue(self, data, 'normalCamInterpolationTime', 0.0)
            readValue(self, data, 'freeCamInterpolationTime', 0.0)
            readValue(self, data, 'freeCamFovInterpolationTime', 0.0)
            readValue(self, data, 'freeCamZoomFactor', 0.0)
            readValue(self, data, 'backCamInterpolationTime', 0.0)
            readValue(self, data, 'bombCamInterpolationTime', 0.0)
            readValue(self, data, 'sniperStateInterpolationTime', 0.01)
            readValue(self, data, 'sideCamInterpolationTime', 0.0)
            readValue(self, data, 'sideCamJInterpolationStartTime', 0.0)
            readValue(self, data, 'sideCamJInterpolationEndTime', 0.0)
            readValue(self, data, 'sideCamJInterpolationTimeTransitionTerm', 0.0)
            readValue(self, data, 'spectatorCamInterpolationTime', 0.0)
            readValue(self, data, 'targetCamInterpolationTime', 0.0)
            readValue(self, data, 'freeFixableCamInterpolationTime', 0.0)
            readValue(self, data, 'freeFixableCamSpeed', 0.0)
            readValue(self, data, 'vibrationAmplitudes', Math.Vector3(0, 0, 0))
            zoomTable = findSection(data, 'zoomTable')
            if zoomTable is not None:
                self.zoomPresets = dict()
                for zoomPreset in zoomTable.values():
                    stateID = zoomPreset.readString('id', 'None')
                    self.zoomPresets[stateID] = ZoomPreset(normal=ZoomData(findSection(zoomPreset, 'normalZoomData'), self.defaultFov), sniper=ZoomData(findSection(zoomPreset, 'sniperZoomData'), self.defaultFov))

            gunnerStateSettingsData = findSection(data, 'gunnerStateData')
            if gunnerStateSettingsData is not None:
                self.gunnerStateSettings = GunnerStateSettings(gunnerStateSettingsData)
            vibrationTable = findSection(data, 'vibrationTable')
            if vibrationTable is not None:
                self.vibrationFrequencies = vibrationTable.readVector3s('frequency')
            destroyedFallStateData = findSection(data, 'destroyedFall')
            if destroyedFallStateData is not None:
                self.destroyedFall = DestroyedFallStateSettings(destroyedFallStateData)
            destroyedLandedStateData = findSection(data, 'destroyedLanded')
            if destroyedLandedStateData is not None:
                self.destroyedLanded = DestroyedLandedStateSettings(destroyedLandedStateData)
            self.__postLoadTransform()
        return