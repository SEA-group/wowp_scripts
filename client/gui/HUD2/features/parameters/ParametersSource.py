# Embedded file name: scripts/client/gui/HUD2/features/parameters/ParametersSource.py
from EntityHelpers import EntityStates
from consts import METERS_PER_SEC_TO_KMH_FACTOR, WEP_ENABLE_TEMPERATURE, WEP_DISABLE_TEMPERATURE, SPEEDOMETER_LOGICAL_STATES
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from debug_utils import LOG_DEBUG
PART_CRIT = 3

class GEAR_STATES:
    NORMAL = 0
    ATTENTION = 1
    WARNING = 2


class SPEEDOMETER_VISUAL_STATES:
    WHITE = 0
    ORANGE = 1
    RED = 2
    ORANGE_ANIMATION = 3
    RED_ANIMATION = 4


SPEEDOMETER_LOGICAL_TO_VISUAL_STATES = {SPEEDOMETER_LOGICAL_STATES.STALL: SPEEDOMETER_VISUAL_STATES.RED_ANIMATION,
 SPEEDOMETER_LOGICAL_STATES.STALL_DANGER: SPEEDOMETER_VISUAL_STATES.ORANGE_ANIMATION,
 SPEEDOMETER_LOGICAL_STATES.TOO_SLOW: SPEEDOMETER_VISUAL_STATES.ORANGE,
 SPEEDOMETER_LOGICAL_STATES.OPTIMAL: SPEEDOMETER_VISUAL_STATES.WHITE,
 SPEEDOMETER_LOGICAL_STATES.TOO_FAST: SPEEDOMETER_VISUAL_STATES.ORANGE,
 SPEEDOMETER_LOGICAL_STATES.DIVE_DANGER: SPEEDOMETER_VISUAL_STATES.RED}

class ParametersSource(DataSource):

    def __init__(self, features):
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._model = features.require(Feature.GAME_MODEL).parameters
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._ms = features.require(Feature.MEASUREMENT_SYSTEM)
        self._preparedData = features.require(Feature.PREPARED_BATTLE_DATA)
        self._uiSettings = features.require(Feature.UI_SETTINGS)
        self._input = features.require(Feature.INPUT)
        self._processor = self._input.commandProcessor
        self._player.eUpdateForce += self._updateForce
        self._timer.eUpdate += self._update
        self._player.onReceiveServerData += self._update
        self._player.eTacticalSpectator += self._setupModel
        self._player.eUpdateEngineTemperature += self._onUpdateEngineTemperature
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._uiSettings.onMeasurementSystemChanged += self._onSetMeasurementSystem
        self._player.ePartStateChanged += self._updatePart
        self._player.onStateChanged += self._onAvatarStateChanged
        self._isCritEngine = False
        self._speedData = None
        self._altitudeData = [0] * 7
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    def _updateForce(self, value):
        if value >= 1.0:
            self._onShowForse()
        else:
            self._onHidePForse()

    def _setupModel(self, *args, **kwargs):
        self._setInitialData()

    def _onSetMeasurementSystem(self, *args, **kwargs):
        self._ms.onMeasurementSystemChanged()
        self._setInitialData()

    def _setInitialData(self):
        if not self._player.inWorld:
            return
        playerID = self._player.globalID
        playerData = self._preparedData[playerID]
        self._speedData = playerData.speedometer
        self._altitudeData = playerData.altimeter[:]
        self._model.speedMetric = self._ms.localizeHUD('ui_speed')
        self._model.speedState = GEAR_STATES.NORMAL
        self._model.speed = 0
        self._model.altitudeMetric = self._ms.localizeHUD('ui_vario')
        self._model.altitudeState = GEAR_STATES.NORMAL
        self._model.altitude = 0
        self._model.forceMax = self._calculateForceMax()
        self._model.force = self._calculateForce()
        self._model.speedMax = int(round(self._ms.getKmh(self._speedData.diveSpeed * METERS_PER_SEC_TO_KMH_FACTOR)))
        self._model.speedRanges.clean()
        for range, (start, end) in self._speedData.stateRanges.iteritems():
            self._model.speedRanges.appendSilently(start=start, end=end)

        self._model.speedRanges.finishAppending()
        self._model.stallSpeed = int(round(self._ms.getKmh(self._player.stallSpeed * METERS_PER_SEC_TO_KMH_FACTOR)))
        self._model.altitudeRanges.clean()
        i = 1
        maxIndex = len(self._altitudeData)
        while i < maxIndex - 1:
            self._model.altitudeRanges.appendSilently(start=self._altitudeData[i - 1], end=self._altitudeData[i])
            i += 1

        self._model.altitudeRanges.appendSilently(start=self._altitudeData[i - 1], end=1.0)
        self._model.altitudeRanges.finishAppending()
        self._model.altitudeMax = int(round(self._ms.getMeters(self._altitudeData[maxIndex - 1])))

    @staticmethod
    def _getState(data, value):
        xs, x1, _, _, x4, xf, norma = data
        x = value / norma if norma else 0
        if x > xf or x < xs:
            return GEAR_STATES.WARNING
        if x > x4 or x < x1:
            return GEAR_STATES.ATTENTION
        return GEAR_STATES.NORMAL

    @staticmethod
    def _getSpeedometerVisualState(speedometerData, value):
        """
        @type speedometerData: _preparedBattleData_db.SpeedometerData
        @type value: float
        @rtype: int
        """
        x = float(value) / speedometerData.diveSpeed
        for logicalState, (start, end) in speedometerData.stateRanges.iteritems():
            if start <= x < end:
                return SPEEDOMETER_LOGICAL_TO_VISUAL_STATES[logicalState]

        return SPEEDOMETER_VISUAL_STATES.RED

    def _onAvatarStateChanged(self, oldState, newState):
        if newState != EntityStates.GAME:
            self._onHidePForse()

    def _update(self):
        if not self._player.inWorld:
            return
        else:
            speed = self._player.getSpeed()
            self._model.speed = min(int(self._ms.getKmh(speed * METERS_PER_SEC_TO_KMH_FACTOR)), 5000)
            self._model.speedState = self._getSpeedometerVisualState(self._speedData, speed) if self._speedData is not None else SPEEDOMETER_VISUAL_STATES.WHITE
            altitude = self._player.getAltitudeAboveWaterLevel()
            self._model.altitude = int(self._ms.getMeters(altitude))
            self._model.altitudeState = self._getState(self._altitudeData, altitude)
            return

    def _onUpdateEngineTemperature(self, engineTemperature, wepWorkTime, isForceEngine):
        self._model.forceMax = self._calculateForceMax()
        self._model.force = self._calculateForce()

    def _calculateForceMax(self):
        if self._isCritEngine:
            return 0.0
        return self._player.wepWorkTime

    def _calculateForce(self):
        if self._isCritEngine:
            return 0.0
        k = (WEP_DISABLE_TEMPERATURE - WEP_ENABLE_TEMPERATURE) / self._player.wepWorkTime
        force = max(0.0, self._player.wepWorkTime - (self._player.engineTemperature - WEP_ENABLE_TEMPERATURE) / k)
        return force

    def _updatePart(self, partData):
        isAllDestroy = True
        for part in self._player.partStates:
            partId = part[0]
            partSettings = self._player.settings.airplane.getPartByID(partId)
            upgr = partSettings.upgrades
            for key in upgr:
                if upgr[key].componentType == 'Engine':
                    if part[1] != PART_CRIT:
                        isAllDestroy = False

        if isAllDestroy:
            self._isCritEngine = True
            self._model.force = 0.0
        else:
            self._isCritEngine = False
            self._model.force = self._calculateForce()
        self._model.forceMax = self._calculateForceMax()

    def _onShowForse(self):
        self._model.isForce = True

    def _onHidePForse(self):
        self._model.isForce = False

    def dispose(self):
        self._input = None
        self._processor = None
        self._player.ePartStateChanged -= self._updatePart
        self._player.eTacticalSpectator -= self._setupModel
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._timer.eUpdate -= self._update
        self._player.onReceiveServerData -= self._update
        self._player.eUpdateEngineTemperature -= self._onUpdateEngineTemperature
        self._uiSettings.onMeasurementSystemChanged -= self._onSetMeasurementSystem
        self._player.eUpdateForce -= self._updateForce
        self._player.onStateChanged -= self._onAvatarStateChanged
        self._clientArena = None
        self._timer = None
        self._player = None
        return