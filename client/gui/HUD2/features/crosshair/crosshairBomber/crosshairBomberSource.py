# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairBomber/crosshairBomberSource.py
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from Math import Vector3
from MathExt import sign
import math

class CrosshairBomberSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).crosshair.bomber
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._camera = features.require(Feature.CAMERA)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._timer.eUpdate += self._update
        self._camera.eSniperMode += self._onSniperMod
        self._gameEnvironment.eSetBombMarkerPos += self._onSetMarkerPos
        self._gameEnvironment.eSetBombRolled += self._onSetRolledState

    def _onSniperMod(self, value):
        self._model.zoomIndex = 4 * int(value)

    def _onSetMarkerPos(self, screen):
        markerPosition = dict(x=0.0, y=0.0)
        if screen is not None:
            markerPosition = dict(x=2.0 * screen.x / self._bigWorld.screenWidth() - 1.0, y=1.0 - 2.0 * screen.y / self._bigWorld.screenHeight())
        self._model.markerPosition = markerPosition
        return

    def _onSetRolledState(self, v):
        self._model.isLock = v

    def _update(self):
        planeDir = Vector3(self._player.getRotation().getAxisZ())
        planeDir.y = 0
        self._model.sightAngle = -math.degrees(self._player.roll)
        self._model.compassAngle = -sign(planeDir.dot(Vector3(1, 0, 0))) * math.degrees(planeDir.angle(Vector3(0, 0, 1)))

    def dispose(self):
        self._gameEnvironment.eSetBombMarkerPos -= self._onSetMarkerPos
        self._gameEnvironment.eSetBombRolled -= self._onSetRolledState
        self._camera.eSniperMode -= self._onSniperMod
        self._timer.eUpdate -= self._update
        self._gameEnvironment = None
        self._bigWorld = None
        self._camera = None
        self._player = None
        self._timer = None
        self._model = None
        return