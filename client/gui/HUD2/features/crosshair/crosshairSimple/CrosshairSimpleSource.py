# Embedded file name: scripts/client/gui/HUD2/features/crosshair/crosshairSimple/CrosshairSimpleSource.py
import clientConsts
from MathExt import clamp
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from consts import GUN_OVERHEATING_TEMPERATURE
from BWLogging import getLogger
from ..CrosshairHelper import AimingTypes, WEAPON_AIM_TYPE, NORMAL_CROSSHAIR_SIZE

class CrosshairSimpleSource(DataSource):

    def __init__(self, features):
        self._modelCrosshair = features.require(Feature.GAME_MODEL).crosshair
        self._model = features.require(Feature.GAME_MODEL).crosshair.simple
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._input = features.require(Feature.INPUT)
        self._camera = features.require(Feature.CAMERA)
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._model.heatShowLimit = clientConsts.WEAPON_OVERHEAT_DELTA
        self._model.maxPulsationLength = clientConsts.MAX_PULSATION_LENGTH
        self._log = getLogger(self)
        self._pulsationChangeTrigger = False
        self._updateEnabled = True
        self._timer.eUpdate += self._update
        self._playerAvatar.eOnGunGroupFire += self._onGunGroupFire
        self._updateCrossImage(None)
        self._playerAvatar.eTacticalRespawnEnd += self._updateCrossImage
        self._playerAvatar.eTacticalSpectator += self._updateCrossImage
        self._gameEnvironment.eOnCrossSizeChanged += self.setCrossSize
        self._camera.eSetCrosshairVisible += self.__setCrosshairVisible
        return

    def _update(self):
        mainGroup = self._playerAvatar.getWeaponController().guns.groups[0]
        currentTemperature = float(min(max(0.0, mainGroup.temperature), GUN_OVERHEATING_TEMPERATURE))
        self._model.heatLevel = currentTemperature / GUN_OVERHEATING_TEMPERATURE

    def setCrossSize(self, size):
        if not self._updateEnabled:
            return
        self._model.crossSize = int(size * 2.0)

    def _onGunGroupFire(self, group):
        rpm = group.gunDescription.RPM
        pulse = 1.0 - clamp(clientConsts.PULSATION_MIN, rpm / clientConsts.NORMAL_GUNS_RPM, clientConsts.PULSATION_MAX)
        pulseTriggered = (9999.0 * pulse + (1.0 if self._pulsationChangeTrigger else 0.0)) / 10000.0
        self._model.pulsation = pulseTriggered
        self._pulsationChangeTrigger = not self._pulsationChangeTrigger

    def dispose(self):
        self._camera.eSetCrosshairVisible -= self.__setCrosshairVisible
        self._timer.eUpdate -= self._update
        self._gameEnvironment.eOnCrossSizeChanged -= self.setCrossSize
        self._playerAvatar.eOnGunGroupFire -= self._onGunGroupFire
        self._playerAvatar.eTacticalRespawnEnd -= self._updateCrossImage
        self._playerAvatar.eTacticalSpectator -= self._updateCrossImage
        self._model = None
        self._input = None
        self._camera = None
        self._playerAvatar = None
        self._modelCrosshair = None
        return

    def _updateCrossImage(self, *args, **kwargs):
        aimType = self._playerAvatar.getWeaponController().getMainWeaponGroupAimType()
        self._model.crossImage = AimingTypes.get(aimType, AimingTypes[0])
        if aimType is WEAPON_AIM_TYPE.empty:
            self.setCrossSize(NORMAL_CROSSHAIR_SIZE)
            self._updateEnabled = False
        else:
            self._updateEnabled = True

    def __setCrosshairVisible(self, state):
        self._model.isHidden = not state