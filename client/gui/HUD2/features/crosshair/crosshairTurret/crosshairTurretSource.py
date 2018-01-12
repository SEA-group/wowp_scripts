# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairTurret/crosshairTurretSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from ..CrosshairHelper import AimingTypes
from MathExt import clamp
import clientConsts
import Math
import BigWorld

def withTurret(foo):

    def wrapper(*args, **kwargs):
        self = args[0]
        if self.turret is not None and self.turret.isClientInAction:
            return foo(*args, **kwargs)
        else:
            return

    return wrapper


class CrosshairTurretSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).crosshair.turret
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._camera = features.require(Feature.CAMERA)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._model.sightMinSize = 50
        self._onTurretChanged(None, 0)
        self._gameEnvironment.ePlayerGunnerChangedTurret += self._onTurretChanged
        self._timer.eUpdate += self._update
        self._camera.eSniperMode += self._onSniperMod
        self._onEndCritTimeUpdate(BigWorld.serverTime())
        self._gameEnvironment.eTurretEndCritTimeChange += self._onEndCritTimeUpdate
        return

    def _onSniperMod(self, value):
        self._model.isZoomed = value

    def _onEndCritTimeUpdate(self, endTime):
        arenaStartTime = self._player.arenaStartTime
        self._model.critEndTime = int(endTime - arenaStartTime) if endTime else 0

    @property
    def turret(self):
        return self._player.controlledGunner

    @withTurret
    def _update(self):
        self.__gunnerCrosshairUpdate()
        self.__gunnerTargetUpdate()

    def __gunnerTargetUpdate(self):
        strategy = self._camera.getStateObject().strategy
        direction = getattr(strategy, 'cameraDirection', None)
        crossRadius = 0
        rect = Math.Vector2(0, 0)
        if direction is not None:
            crossRadius = self.turret.getScopeRadius(direction)
            rect = self.turret.getTurretZoneRectangle(direction)
        self._model.crossRadius = int(crossRadius)
        self._model.shadePosition = dict(x=rect.x, y=rect.y)
        return

    def __gunnerCrosshairUpdate(self):
        turret = self.turret
        self._model.onTarget = turret.isOnTarget()
        self._model.isFiring = turret.isClientFiring
        self._model.sightAccuracy = turret.getReduction()

    def _onTurretChanged(self, aimType, RPM):
        self._model.crossImage = AimingTypes.get(aimType, AimingTypes[0])
        self._model.rpm = RPM
        mul = 1.0 - clamp(clientConsts.PULSATION_MIN, RPM / clientConsts.NORMAL_GUNS_RPM, clientConsts.PULSATION_MAX)
        self._model.pulsStrength = clientConsts.MAX_PULSATION_LENGTH * mul

    def dispose(self):
        self._gameEnvironment.ePlayerGunnerChangedTurret -= self._onTurretChanged
        self._gameEnvironment.eTurretEndCritTimeChange -= self._onEndCritTimeUpdate
        self._camera.eSniperMode -= self._onSniperMod
        self._timer.eUpdate -= self._update
        self._camera = None
        self._player = None
        self._timer = None
        self._model = None
        return