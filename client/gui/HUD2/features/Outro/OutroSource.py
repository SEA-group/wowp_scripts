# Embedded file name: scripts/client/gui/HUD2/features/Outro/OutroSource.py
import BigWorld
import BWLogging
from consts import GAME_RESULT, OUTRO_TIME_QUIT_DELAY, OUTRO_TIME, ARENA_WAIT4DRAW_DELAY
from clientConsts import PREBATTLE_PLANE_TYPE_NAME
from EventHelpers import CompositeSubscription, EventSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from Helpers.i18n import localizeAirplane, localizeLobby
from GameEvents.features.coach.model import RankModel
logger = BWLogging.getLogger('HUD.Outro')
GAME_RESULT_LOC_IDS = {GAME_RESULT.DRAW_TIME_IS_RUNNING_OUT: ['HUD_DRAW_TIME', 'HUD_DRAW_TIME', 'HUD_DRAW_TIME'],
 GAME_RESULT.AREA_CONQUEST_SUCCESS: ['HUD_WIN_SUPERIORITY_STR', 'HUD_LOOSE_SUPERIORITY_STR', ''],
 GAME_RESULT.ELIMINATION: ['HUD_ENEMIES_ELIMINATION_STR', 'HUD_OWN_ELIMINATION_STR', ''],
 GAME_RESULT.DRAW_ELIMINATION: ['', '', 'HUD_DRAW_PLAYERS'],
 GAME_RESULT.DRAW_ELIMINATION_NO_PLAYERS: ['', '', 'HUD_PVE_NO_PLAYERS'],
 GAME_RESULT.DRAW_SUPERIORITY: ['', '', 'HUD_DRAW_SUPERIORITY_STR'],
 GAME_RESULT.DRAW_AREA_CONQUEST: ['', '', 'HUD_DRAW_SUPERIORITY_STR'],
 GAME_RESULT.MAIN_TIME_RUNNING_OUT: ['HUD_WIN_TIME_OVER_STR', 'HUD_LOOSE_TIME_OVER_STR', ''],
 GAME_RESULT.CAPTURE_ALL_SECTORS: ['HUD_WIN_SECTORS_STR', 'HUD_LOOSE_SECTORS_STR', ''],
 GAME_RESULT.DYNAMIC_TIME_RUNNING_OUT: ['HUD_WIN_TIME_OVER_STR', 'HUD_LOOSE_TIME_OVER_STR', ''],
 GAME_RESULT.ATTRITION_SUCCESS: ['HUD_WIN_ATTRITION_STR', 'HUD_LOOSE_ATTRITION_STR', ''],
 GAME_RESULT.ATTRITION_DRAW: ['', '', 'HUD_LOOSE_ATTRITION_STR']}

class OutroSource(DataSource):

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).outro
        self._db = features.require(Feature.DB_LOGIC)
        self._bigWorld = features.require(Feature.BIG_WORLD)
        self._economics = features.require(Feature.CLIENT_ECONOMICS)
        self._player = features.require(Feature.REAL_PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._clientArena.onGameResultChanged += self._update
        self._economics.onUpdateBattlePoints += self._updatePlayerEconomics
        self._cachedTeammates = []
        self._updateRateSubscription = None
        self._isFirstBattleResultUpdate = True
        return

    def _update(self, gameResult, winState):
        playerTeamIndex = self._player.teamIndex
        enemyTeamIndex = 1 - self._player.teamIndex
        logger.debug('RESULT::::: {0}'.format(gameResult))
        if gameResult in GAME_RESULT_LOC_IDS:
            resIndex = 2 if winState == 2 else int(playerTeamIndex != winState)
            reason = GAME_RESULT_LOC_IDS[gameResult][resIndex]
            self._model.reason = reason
            logger.debug('Update: {0}, {1}, {2}, {3}'.format(gameResult, winState, playerTeamIndex, reason))
        self._model.winnerTeamIndex = winState
        self._updateBattleTime()
        scoreGlobal = self._clientArena.gameMode.scoreGlobal
        self._model.allyPoints = scoreGlobal[playerTeamIndex]
        self._model.enemyPoints = scoreGlobal[enemyTeamIndex]
        self._updatePlayerTeamRate()
        self._updatePlayerEconomics()
        if not self._updateRateSubscription:
            self._updateRateSubscription = CompositeSubscription(EventSubscription(self._clientArena.onEconomicEvents, self._updatePlayerTeamRate), EventSubscription(self._clientArena.onEconomicPlayersPoints, self._updatePlayerTeamRate))
            self._updateRateSubscription.subscribe()
        self._updateBestRankData()

    def _updateBattleTime(self):
        if self._isFirstBattleResultUpdate:
            battleTimeRaw = self._bigWorld.serverTime() - self._bigWorld.player().arenaStartTime + ARENA_WAIT4DRAW_DELAY
            self._model.goToHangarTime = int(battleTimeRaw + OUTRO_TIME + OUTRO_TIME_QUIT_DELAY + 0.5)
            self._model.battleTime = int(battleTimeRaw + 0.5)
        self._isFirstBattleResultUpdate = False

    def _updatePlayerTeamRate(self, *args, **kwargs):
        """Update model.playerLevel based player's on battle points
        """
        places = {}
        teammatesArray = self._getTeammatesArray()
        for avatarID in teammatesArray:
            avatarInfo = self._clientArena.avatarInfos[avatarID]
            battlePoints = avatarInfo['economics']['totalBattlePoints']
            planeType = self._db.getAircraftData(avatarInfo['bestRankPlaneID']).airplane.planeType
            rankID = avatarInfo['planeTypeRank'][planeType]
            bestRankOrderIndex = 0
            if rankID != RankModel.EMPTY_RANK_ID:
                bestRankOrderIndex = RankModel.getRankByID(rankID).orderIndex
            places.setdefault((bestRankOrderIndex, battlePoints), []).append(avatarID)

        places = sorted(places.iteritems(), key=lambda item: item[0], reverse=True)
        playerPointsRate = None
        for place, (data, players) in enumerate(places, start=1):
            if self._player.id in players:
                playerPointsRate = place
                break

        raise playerPointsRate or AssertionError('Sorting error, data: {}'.format(places))
        logger.debug('Update player points rate: {0}'.format(playerPointsRate))
        self._model.playerLevel = playerPointsRate
        return

    def _getTeammatesArray(self):
        """Return list with teammates avatarIDs
        :rtype: list[int]
        """
        if not self._cachedTeammates:
            self._cachedTeammates = []
            for avatarID, avatarInfo in self._clientArena.avatarInfos.iteritems():
                if not avatarInfo['isNPC'] and self._player.teamIndex == avatarInfo['teamIndex']:
                    self._cachedTeammates.append(avatarID)

        return self._cachedTeammates

    def _updateBestRankData(self):
        avatarInfo = self._clientArena.avatarInfos[self._player.id]
        bestPlaneID = avatarInfo['bestRankPlaneID']
        planeData = self._db.getAircraftData(bestPlaneID)
        planeType = planeData.airplane.planeType
        bestRankID = avatarInfo['planeTypeRank'][planeType]
        logger.debug('Best rank id = {0}, planeID = {1}'.format(bestRankID, bestPlaneID))
        self._model.bestPlane = localizeAirplane(planeData.airplane.name)
        self._model.bestClass = localizeLobby(PREBATTLE_PLANE_TYPE_NAME[planeType])
        self._model.bestPlaneType = planeType
        self._model.bestRank = bestRankID
        self._model.bestTasks.clean()
        for objective in self._player.coachManager.getPlaneTypeObjectives(planeType):
            self._model.bestTasks.append(id=objective.id, title=objective.model.client.name.locale, description=objective.model.client.description.locale, progress=objective.progressCurrent, maxProgress=objective.progressMax, value=objective.progressRawValue, requiredValue=objective.getNextProgressBound())

    def _updatePlayerEconomics(self, *args, **kwargs):
        """Update outro economics data
        """
        self._model.battlePoints = self._economics.battlePoints
        self._model.masteryPoints = self._economics.experience

    def dispose(self):
        if self._updateRateSubscription:
            self._updateRateSubscription.unsubscribe()
            self._updateRateSubscription = None
        self._economics.onUpdateBattlePoints -= self._updatePlayerEconomics
        self._clientArena.onGameResultChanged -= self._update
        self._model = None
        self._bigWorld = None
        return