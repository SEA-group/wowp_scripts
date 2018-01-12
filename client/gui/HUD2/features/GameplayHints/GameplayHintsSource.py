# Embedded file name: scripts/client/gui/HUD2/features/GameplayHints/GameplayHintsSource.py
import BigWorld
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
import BWLogging
from consts import HINTS_TYPE, SECTOR_LEVEL_TYPE_TO_SECTOR_GAMEPLAY_TYPE as SECTOR_GT

class GameplayHintsSource(DataSource):
    DISABLED_TIME = -1000
    SECTOR_HINTS_END_ID = 106
    DELAY_BEFORE_HINT = 2
    DEFAULT_POINTS_LABELS = 'default'
    SECTORS_BY_HINTID = {101: ('military_base', 0),
     102: ('airfield', 0),
     103: ('airfield', 2),
     104: ('factory', 2),
     105: ('radar', 1),
     106: ('military_base', 1)}

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._model = features.require(Feature.GAME_MODEL).gameplayHints
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._gameEnvironment = features.require(Feature.GAME_ENVIRONMENT)
        self._gameMode = self._clientArena.gameMode
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gamePlayHints = features.require(Feature.GAME_PLAY_HINTS)
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._playerAvatar.eOnGameplayHint += self.onGameplayHint
        self._playerAvatar.eCloseGamePlayHint += self.onCloseGamePlayHint
        self._gameEnvironment.eShowHint += self.onShowHint
        self._gameEnvironment.eDisableStartHint += self.onDisableStartHint
        for hintType in HINTS_TYPE.ALL:
            self._playerAvatar.tryToShowHint(hintType)

        self._hintCallbacks = {HINTS_TYPE.START: self._setStartHintActive,
         HINTS_TYPE.SHOOTING: self._setShootingHintActive}

    def dispose(self):
        self._playerAvatar.eOnGameplayHint -= self.onGameplayHint
        self._playerAvatar.eCloseGamePlayHint -= self.onCloseGamePlayHint
        self._gameEnvironment.eShowHint -= self.onShowHint
        self._gameEnvironment.eDisableStartHint -= self.onDisableStartHint
        self._timer.eUpdate -= self._onUpdate

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def __getPointsInTick(self, sector):
        pointsProduction = sector.settings.pointsProduction
        return sum((p.points for p in pointsProduction.filterProducers(labels=self.DEFAULT_POINTS_LABELS)))

    def onGameplayHint(self, hintID, hintName, hintType, force):
        self._logger.info('>>>> onGameplayHint: {0} {1}'.format(hintID, hintName))
        if hintID <= self.SECTOR_HINTS_END_ID:
            gamePlaySector = SECTOR_GT[hintName]
            sectorData = dict(gamePlayType=gamePlaySector['gamePlayType'], gamePlayLevel=gamePlaySector['gamePlayLevel'])
            self._model.sectorData = sectorData
        if hintType == HINTS_TYPE.START:
            self._model.startHintID = hintID
            self._model.startHintTime = self.DISABLED_TIME
        elif hintType == HINTS_TYPE.SHOOTING:
            self._model.shootingHintID = hintID
            self._model.shootingHintTime = self.DISABLED_TIME
        self.__tryToShowForce(hintType, force)

    def __tryToShowForce(self, hintType, force):
        if not force:
            return
        if self._gamePlayHints.hintVisible:
            return
        self._hintCallbacks[hintType](True)

    def onShowHint(self, hintType):
        self._hintCallbacks[hintType](True)

    def onCloseGamePlayHint(self, hintType):
        self._hintCallbacks[hintType](False)

    def onDisableStartHint(self):
        self._model.startHintTime = self.DISABLED_TIME

    def _onUpdate(self):
        if self._model.startHintTime.get() == self.DISABLED_TIME:
            return
        currentTime = self._getCurrentTime()
        if currentTime >= self._model.startHintTime.get():
            self._gamePlayHints.setHintVisibility(True)
            self._timer.eUpdate -= self._onUpdate

    def _setStartHintActive(self, active):
        if active:
            if self._model.startHintTime.get() != self.DISABLED_TIME or not self._playerAvatar.startHintAvailable:
                return
            self._model.startHintTime = self._getCurrentTime() + self.DELAY_BEFORE_HINT
            self._timer.eUpdate += self._onUpdate
        else:
            self._model.startHintID = 0
            self._model.sectorData = {}
            self._model.startHintTime = self.DISABLED_TIME

    def _setShootingHintActive(self, active):
        if active:
            if self._model.shootingHintTime.get() != self.DISABLED_TIME or self._playerAvatar.startHintAvailable or not self._playerAvatar.shootingHintAvailable:
                return
            self._model.shootingHintTime = self._getCurrentTime() + self.DELAY_BEFORE_HINT
        else:
            self._model.shootingHintID = 0
            self._model.shootingHintTime = self.DISABLED_TIME

    def _getCurrentTime(self):
        serverTime = self._bigWorld.serverTime()
        arenaStartTime = self._playerAvatar.arenaStartTime
        return int(round(serverTime - arenaStartTime))