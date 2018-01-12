# Embedded file name: scripts/client/gui/HudElements/BombTarget.py
import BigWorld
import GameEnvironment
import GUI
from ICMultiUpdate import ICMultiUpdate
from EntityHelpers import getBombGravityAcceleration, getAirResistance
import db.DBLogic
from consts import *
from gui.HUDconsts import *

class BombTarget(ICMultiUpdate):

    def __init__(self):
        self._inited = False
        self._visible = False
        self._player = GameEnvironment.g_instance.playerAvatarProxy
        ICMultiFunction = lambda : (self._update() if self._visible else None)
        ICMultiUpdate.__init__(self, (0.01666667, ICMultiFunction))
        self._matrixProvider = None
        return

    def _update(self):
        self._matrixProvider.dispersionAngle = self._player.getShellController().getBombDispersionAngle()

    def dispose(self):
        self._player = None
        ICMultiUpdate.dispose(self)
        return

    def restart(self):
        pass

    def __createTarget(self):
        self._createTargetMatrixProvider()
        self._createTargetHud()
        self._initHud()

    def _getMinMaxTargetSize(self):
        return (MIN_BOMB_TARGET_SIZE, MAX_BOMB_TARGET_SIZE)

    def _createTargetMatrixProvider(self):
        minTs, maxTs = self._getMinMaxTargetSize()
        self._matrixProvider = GUI.BombTargetMp()
        self._matrixProvider.target = self._player.realMatrix
        self._matrixProvider.acceleration = getBombGravityAcceleration(self._player.planeType).y
        self._matrixProvider.worldScalingCfc = WORLD_SCALING
        self._matrixProvider.speedScalingCfc = SPEED_SCALING
        self._matrixProvider.minTargetSize = minTs
        self._matrixProvider.maxTargetSize = maxTs
        self._matrixProvider.airResistance = getAirResistance(self._player.planeType)
        self._matrixProvider.minBombFlightHeight, self._matrixProvider.maxBombFlightHeight = BOMB_TARGET_VIEW_HEIGHT_RANGE.get(self._player.planeType, (DEFAULT_MIN_FLIGHT_HEIGHT, DEFAULT_MAX_FLIGHT_HEIGHT))

    def _createTargetHud(self):
        self._hud = GUI.BombSignHud()
        self._hud.signModelName = BOMB_SIGN_VISUAL
        self._hud.signDisabledModelName = BOMB_SIGN_DISABLED_VISUAL
        self._hud.bombMP = self._matrixProvider

    def _initHud(self):
        self._hud.init()
        self._signEnabled = True
        self._inited = True
        self._hud.visible = True
        GUI.addRoot(self._hud)

    def setBombDispersionParams(self, dispaersionAngle):
        self._matrixProvider.dispersionAngle = dispaersionAngle
        self._matrixProvider.pitchSpeedCfc = BOMB_Z_SCATTER_SCALING

    def destroy(self):
        self.setVisible(False)
        if self._inited:
            GUI.delRoot(self._hud)
            self._hud.bombMP = None
        self._inited = False
        self._visible = False
        self._hud = None
        self._cachedTexture = None
        self.dispose()
        return

    def setBombTargetEnable(self, signEnabled):
        if self._signEnabled != signEnabled:
            if signEnabled:
                self._hud.disabled = False
            else:
                self._hud.disabled = True
            self._signEnabled = signEnabled

    def getBombTargetEnable(self):
        return self._signEnabled

    def setVisible(self, visible):
        if visible != self._visible:
            self._visible = visible
            if visible and not self._inited:
                self.__createTarget()
            if self._inited:
                self._hud.visible = visible

    def isVisible(self):
        return self._visible

    @property
    def matrixProvider(self):
        return self._matrixProvider

    def disableUpdate(self, value):
        if self._matrixProvider is not None:
            self._matrixProvider.updateDisabled = value
        return