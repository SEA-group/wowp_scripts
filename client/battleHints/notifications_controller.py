# Embedded file name: scripts/client/battleHints/notifications_controller.py
import BigWorld
import battleHints
import db.DBLogic
import GameModeSettings.ACSettings as SETTINGS
from EntityHelpers import EntityStates
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from consts import TEAM_ID
SCORE_BORDER = 75

class Dummy(object):
    pass


class NotificationsController(object):

    def __init__(self, gameEnv, messenger):
        self._gameEnv = gameEnv
        self._messenger = messenger
        self._score = [0] * 2
        self._sectors = {}
        self._linked = False
        self._teamSuperiority = -1

    def dispose(self):
        self.unlinkEvents()
        self._gameEnv = None
        self._messenger = None
        return

    def update(self, dt):
        if self._canPerformUpdate():
            self._updateBattleEnd()
            self._updateBattleEvents()

    def onInitGameMode(self):
        self._setSectorData()
        self.linkEvents()

    @property
    def _getArena(self):
        return self._gameEnv.service('ClientArena')

    @property
    def _gameMode(self):
        return self._getArena.gameMode

    @property
    def _player(self):
        return BigWorld.player()

    def _setSectorData(self):
        arenaTypeData = db.DBLogic.g_instance.getArenaData(self._player.arenaType)
        for sectorData in arenaTypeData.sectors.sectors.values():
            if not sectorData.isFreeZone:
                if not sectorData.isBase:
                    sector = Dummy()
                    sector.name = sectorData.hudSettings.localizationID.split('_')[-1]
                    sector.icon = sectorData.hudSettings.battleHintIcon
                    self._sectors[sectorData.ident] = sector

    def linkEvents(self):
        if self._gameMode is not None and not self._linked:
            self._gameMode.addEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self._onGlobalScoreUpdate)
            self._gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorChangeState)
            self._gameMode.addEventHandler(AC_EVENTS.BOMBERS_LAUNCHED, self._onBomberWaveStarted)
            self._gameMode.lastPlayerManager.eUpdateLastPlayer += self.__onUpdateLastPlayer
            self._linked = True
        return

    def unlinkEvents(self):
        if self._gameMode is not None and self._linked:
            self._gameMode.removeEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self._onGlobalScoreUpdate)
            self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorChangeState)
            self._gameMode.removeEventHandler(AC_EVENTS.BOMBERS_LAUNCHED, self._onBomberWaveStarted)
            self._gameMode.lastPlayerManager.eUpdateLastPlayer -= self.__onUpdateLastPlayer
            self._linked = False
        return

    def __onUpdateLastPlayer(self, isEnemy, *args, **kwargs):
        if isEnemy:
            self._messenger.pushMessage(battleHints.NOTIFICATION_LAST_ENEMY)
        else:
            self._messenger.pushMessage(battleHints.NOTIFICATION_LAST_ALLY)

    def _onGlobalScoreUpdate(self, scoreGlobal):
        pointsToWin = self._gameMode.arenaTypeData._gameModeSettings.pointsToWin
        ownerTeamIndex = self._player.teamIndex
        enemyTeamIndex = 1 - ownerTeamIndex
        percent = lambda points: 100.0 * points / pointsToWin
        newScore = map(percent, scoreGlobal)
        if newScore[ownerTeamIndex] >= SCORE_BORDER and self._score[ownerTeamIndex] < SCORE_BORDER:
            self._messenger.pushMessage(battleHints.NOTIFICATION_VICTORY_IS_COM)
        if newScore[enemyTeamIndex] >= SCORE_BORDER and self._score[enemyTeamIndex] < SCORE_BORDER:
            self._messenger.pushMessage(battleHints.NOTIFICATION_DEFEAT_IS_COM)
        self._score = newScore
        self._updateSuperiority()

    def _updateSuperiority(self):
        ownerTeamIndex = self._player.teamIndex
        enemyTeamIndex = 1 - ownerTeamIndex
        teamSuperiority = ownerTeamIndex if self._gameMode.teamSuperiority(ownerTeamIndex) else (enemyTeamIndex if self._gameMode.teamSuperiority(enemyTeamIndex) else -1)
        if teamSuperiority != -1:
            if self._teamSuperiority != teamSuperiority:
                self._teamSuperiority = teamSuperiority
                notification = battleHints.NOTIFICATION_SUPERIORITY_ALLY if self._teamSuperiority == ownerTeamIndex else battleHints.NOTIFICATION_SUPERIORITY_ENEMY
                self._messenger.pushMessage(notification)

    def _onSectorChangeState(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp):
        ownerTeamIndex = self._player.teamIndex
        enemyTeamIndex = 1 - ownerTeamIndex
        if oldTeamIndex != teamIndex:
            hints = {ownerTeamIndex: battleHints.NOTIFICATION_ALLY_TEAM_CAPTURED_SECTOR,
             enemyTeamIndex: battleHints.NOTIFICATION_ENEMY_TEAM_CAPTURED_SECTOR}
            sector = self._sectors[sectorId]
            self._messenger.pushMessage(hints.get(teamIndex, -1), localData=dict(postfix=sector.name, icon=sector.icon))

    def _onBomberWaveStarted(self, sectorIdent, currentTargetSectorIdent, teamIndex, waveID, bombersIdsStates, startTime):
        hint = battleHints.NOTIFICATION_ALLY_BOMBERS_WAVE_LAUNCHED if self._player.teamIndex == teamIndex else battleHints.NOTIFICATION_ENEMY_BOMBERS_WAVE_LAUNCHED
        self._messenger.pushMessage(hint)

    def _updateBattleEnd(self):
        hint = battleHints.NOTIFICATION_X_TIME_TO_BATTLE_END
        hintData = db.DBLogic.g_instance.getBattleNotificationHintByID(hint)
        if self._gameMode.arenaTimeRemaining <= hintData.timer:
            self._messenger.pushMessage(hint)

    def _updateBattleEvents(self):
        triggers = self._gameMode.arenaTypeData.gameModeSettings.battleEvents.triggers
        eventRDTrigger = next((x for x in triggers if x.battleEvent == SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE))
        if eventRDTrigger is not None:
            csTriggerTime = eventRDTrigger.predicate.options['duration']
            arenaTimePassed = BigWorld.serverTime() - self._player.arenaStartTime
            timeToNRCountdown = csTriggerTime - arenaTimePassed
            hint_2 = battleHints.NOTIFICATION_STORM_FRONT_2
            hint_1 = battleHints.NOTIFICATION_STORM_FRONT_1
            hint_0 = battleHints.NOTIFICATION_STORM_FRONT_0
            hintData_2 = db.DBLogic.g_instance.getBattleNotificationHintByID(hint_2)
            hintData_1 = db.DBLogic.g_instance.getBattleNotificationHintByID(hint_1)
            if timeToNRCountdown <= hintData_2.addValue:
                secToMin = lambda v: int(v / 60.0)
                self._messenger.pushMessage(hint_2, localData=dict(addValue=secToMin(hintData_2.addValue)))
            if timeToNRCountdown <= hintData_1.addValue:
                self._messenger.pushMessage(hint_1, {'lifeTime': timeToNRCountdown,
                 'timer': timeToNRCountdown})
            if timeToNRCountdown <= 0:
                self._messenger.pushMessage(hint_0)
        return

    def _canPerformUpdate(self):
        if not (self._player and self._player.inWorld and EntityStates.inState(self._player, EntityStates.GAME)):
            return False
        if not (self._getArena and self._gameMode and self._gameMode.isReady):
            return False
        return True