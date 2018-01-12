# Embedded file name: scripts/client/gui/HudElements/CrosshairVariants.py
import math
import BigWorld
from MathExt import clamp
from clientConsts import MIN_TARGET_SIZE, CLAMP_MIN_TARGET_SIZE, CLAMP_MAX_TARGET_SIZE, TARGET_DISP_IDENTITY_CFC
import GUI
from gui.HUDconsts import HUD_REDUCTION_POINT_SCALE
from gui.WindowsManager import g_windowsManager
import GameEnvironment

class _MovingTargetSizeUpdater(object):

    def __init__(self):
        self.__active = False
        self.__valuesQueue = [0] * 10
        self.__valuesQueueIndex = 0
        self.__targetValue = 0
        self.__prevValue = 0
        self.__prevFov = 0
        self.__prevActive = 0
        self.__smoothStep = 0
        self.__minTargetSize = math.radians(MIN_TARGET_SIZE)
        self.__clampMaxTargetSize = math.radians(CLAMP_MAX_TARGET_SIZE)
        self.__clampMinTargetSize = math.radians(CLAMP_MIN_TARGET_SIZE)

    def updateSize(self, fov, size):
        self.__valuesQueue[self.__valuesQueueIndex] = size
        self.__valuesQueueIndex = (self.__valuesQueueIndex + 1) % 10
        newValue = sum(self.__valuesQueue) / 10
        if newValue != 0:
            newValue += self.__minTargetSize
        deltaValue = newValue - self.__prevValue
        if newValue != self.__targetValue:
            self.__targetValue = newValue
            self.__smoothStep = deltaValue / 10
        if self.__prevValue != newValue or self.__prevFov != fov or self.__prevActive != self.__active:
            if abs(deltaValue) > 0.0001:
                newValue = self.__prevValue + self.__smoothStep
            self.__prevValue = newValue
            self.__prevFov = fov
            self.__prevActive = self.__active
            if GameEnvironment.g_instance:
                value = clamp(self.__clampMinTargetSize, TARGET_DISP_IDENTITY_CFC * newValue, self.__clampMaxTargetSize)
                GameEnvironment.g_instance.eOnCrossSizeChanged(value / fov * 2.0 * BigWorld.screenHeight())

    def setIsActive(self, value):
        self.__active = value


class MovingTarget(object):

    def __init__(self):
        self.__targetMatrix = GameEnvironment.getHUD().offsetMtx
        self.__targetMatrix.source = BigWorld.player().fakeRealMatrix
        self.__targetMatrix.defaultLength = BigWorld.player().reductionPoint
        self.__dataProvider = None
        self.__movie = None
        self._sizeUpdater = _MovingTargetSizeUpdater()
        return

    def getTargetMatrix(self):
        return self.__targetMatrix

    def setTargetMatrix(self, matrix):
        self.__targetMatrix.source = matrix
        if self.__movie is not None:
            self.init(self.__movie)
        return

    def init(self, movie):
        self.__movie = movie
        worldToClipMtxProvider = GUI.WorldToClipMP()
        worldToClipMtxProvider.target = self.__targetMatrix
        self.__dataProvider = GUI.ScaleformDataProvider(worldToClipMtxProvider, movie, 'hud.crosshairUpdate', 'x;y;z;yaw;pitch;roll', '')
        self.__dataProvider.updateInterval = 1

    def setSize(self, fov, size):
        self._sizeUpdater.updateSize(fov, size)

    def setTargetVisible(self, flag):
        self._sizeUpdater.setIsActive(flag)
        ui = g_windowsManager.getBattleUI()
        if ui:
            ui.movingTargetVisibility(flag)

    def removeProviders(self):
        self.__dataProvider = None
        return

    def destroy(self):
        self.__dataProvider = None
        return