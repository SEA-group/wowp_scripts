# Embedded file name: scripts/client/gui/HudElements/CenterPointVariants.py
import GUI
import Math
import GameEnvironment

class CenterPoint(object):

    def __init__(self):
        self.__dataProvider = None
        self.__ui = None
        self.__movie = None
        self.__matrixProvider = None
        mtx = Math.MatrixProduct()
        mtx.a = GameEnvironment.getHUD().offsetMtx.reduction
        mtx.b = Math.Matrix()
        mtx.b.setIdentity()
        self.__targetMtx = mtx
        return

    def init(self, ui, movie):
        self.__ui = ui
        self.__movie = movie
        self.__createScaleformMatrix(self.__matrixProvider)
        self.__matrixProvider = None
        return

    def __createScaleformMatrix(self, matrix):
        if matrix is not None:
            self.__targetMtx.b = matrix
            worldToClipMtxProvider = GUI.WorldToClipMP()
            worldToClipMtxProvider.target = self.__targetMtx
            worldToClipMtxProvider.onlyInScreen = False
            self.__dataProvider = GUI.ScaleformDataProvider(worldToClipMtxProvider, self.__movie, 'hud.centerPointUpdate', 'x;y;z;yaw;pitch;roll', '')
            self.__dataProvider.updateInterval = 1
        return

    def setMatrixProvider(self, matrixProvider):
        if self.__movie is not None:
            self.__createScaleformMatrix(matrixProvider)
        else:
            self.__matrixProvider = matrixProvider
        return

    def getTargetMatrix(self):
        return self.__targetMtx

    def setTargetVisible(self, flag):
        pass

    def removeMatrixProvider(self):
        if self.__ui:
            self.__ui.call_1('hud.centerPointUpdate', 0, 0, 1, 0, 0, 0)
        self.__dataProvider = None
        self.__matrixProvider = None
        return