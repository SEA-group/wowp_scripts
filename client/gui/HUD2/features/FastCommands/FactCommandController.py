# Embedded file name: scripts/client/gui/HUD2/features/FastCommands/FactCommandController.py
from math import sqrt
import Math
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataController
from gui.HUD2.core.MessageRouter import message
from gui.HUD2.hudFeatures import Feature
from BWUserTypesCommon.FastCommandRequestData import FastCommandRequestData
POINT_ID = 'centerPoint'
BOMBER_ID = 'sector'

class TargetData(object):

    def __init__(self, value):
        value = value.split('=')
        itemPosition = value[1].split('x')
        self.id = str(value[0])
        self.position = Math.Vector2(int(itemPosition[0]), int(itemPosition[1]))
        self.distance = 0
        self.distanceToNearest = 0

    def toFCRequestData(self):
        return FastCommandRequestData(self.id, int(self.distance), int(self.distanceToNearest))

    def __repr__(self):
        return 'TargetData: id:%s,%s ,dist:%s' % (self.id, self.position, self.distance)

    def __str__(self):
        return 'TargetData: id:%s,%s ,dist:%s' % (self.id, self.position, self.distance)


class FactCommandController(DataController):

    def __init__(self, features):
        self.gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameMode = self._clientArena.gameMode
        self._waveInfoManager = self._gameMode.waveInfoManager

    @message('fastCommand.selectPlane')
    def selectPlane(self, targetsData):
        callID = self._getCallID(targetsData)
        targetsList = self._getNearestItems(targetsData)
        self.gameEnvironment.eGetTargetsFromFlash(targetsList, callID)

    @message('fastCommand.selectSector')
    def selectSector(self, targetsData):
        callID = self._getCallID(targetsData)
        targetsList = self._getNearestItems(targetsData)
        self.gameEnvironment.eGetTargetsFromFlash(targetsList, callID)

    def _getNearestItems(self, targetsData):
        targetsList, point = self._parseData(targetsData)
        for targetData in targetsList:
            targetData.distance = self._getDistance(point, targetData)

        targetsList.sort(key=lambda x: x.distance)
        targetsList = targetsList[0:2]
        for targetData in targetsList:
            targetData.distance = self._getDistance(point, targetData)

        for i in range(targetsList.__len__()):
            targetData = targetsList[i]
            prevTargetData = targetsList[i - 1] if i > 0 else targetsList[i]
            targetData.distanceToNearest = self._getDistance(prevTargetData, targetData)

        return targetsList

    def _getCallID(self, _data):
        params = _data.split('/')
        callID = params[1].split('=')[1]
        return int(callID)

    def _parseData(self, _data):
        result = []
        params = _data.split('/')
        data = params[0].split('|')
        point = None
        for targetData in data:
            targetData = TargetData(targetData)
            if targetData.id != POINT_ID:
                if self._waveInfoManager.checkIsAirStrike(targetData.id):
                    waveId = targetData.id
                    targetData.id = self._waveInfoManager.getRandomPlaneInWave(waveId)
                result.append(targetData)
            else:
                point = targetData

        return (result, point)

    def _getDistance(self, point1, point2):
        result = point1.position - point2.position
        return result.length

    def dispose(self):
        self.gameEnvironment = None
        self._clientArena = None
        self._waveInfoManager = None
        self._gameMode = None
        return