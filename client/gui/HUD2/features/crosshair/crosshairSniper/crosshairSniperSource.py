# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairSniper/crosshairSniperSource.py
import math
import clientConsts
from MathExt import clamp
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class CrosshairSniperSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).crosshair.sniper
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._camera = features.require(Feature.CAMERA)
        self._pulsationChangeTrigger = False
        self._timer.eUpdate += self._update
        self._playerAvatar.eOnForsageStateChanged += self.__onForsageChanged
        self._playerAvatar.eOnGunGroupFire += self._onGunGroupFire
        self._model.toggleForsage = False
        self._model.scopeMaxSize = clientConsts.SNIPER_SCOPE_MAX_SIZE
        self._model.scopeShakeLength = clientConsts.SNIPER_SHAKE_LENGTH
        self._model.scopeSize = 0.0

    def __onForsageChanged(self, state):
        self._model.toggleForsage = state

    def dispose(self):
        self._playerAvatar.eOnForsageStateChanged -= self.__onForsageChanged
        self._timer.eUpdate -= self._update
        self._playerAvatar.eOnGunGroupFire -= self._onGunGroupFire

    def _update(self):
        sniperFov = math.radians(self._camera.context.cameraSettings.defaultFov) * self._camera.curZoomData.fovPercent
        self._model.scopeSize = clamp(0.0, float(clientConsts.SNIPER_SCOPE_COEF) * (1.0 - self._camera.getFOV() / sniperFov), 1.0)

    def _onGunGroupFire(self, group):
        rpm = group.gunDescription.RPM
        pulse = 1.0 - clamp(clientConsts.PULSATION_MIN, rpm / clientConsts.NORMAL_GUNS_RPM, clientConsts.PULSATION_MAX)
        pulseTriggered = (9999.0 * pulse + (1.0 if self._pulsationChangeTrigger else 0.0)) / 10000.0
        self._model.pulsation = pulseTriggered
        self._pulsationChangeTrigger = not self._pulsationChangeTrigger