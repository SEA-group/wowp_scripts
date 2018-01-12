# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/ACSectorClient.py
from ACSector import ACSector
from consts import TEAM_ID, SECTOR_STATE
from GameModeSettings import ACSettings as SETTINGS

class ACSectorClient(object):
    """Sector data holder
    """

    def __init__(self, settings, entity):
        self._settings = settings
        self._capturePointsByTeams = (0, 0)
        self._entity = entity
        self.eNextBonusTickChanged = self._entity.eNextBonusTickChanged
        self.eStateChanged = self._entity.eStateChanged
        self.eStateChanged += self.resetCapturePoints
        self.eRocketV2TargetSectorIDChanged = self._entity.eRocketV2TargetSectorIDChanged
        self.resetCapturePoints()

    @property
    def ident(self):
        """Sector unique identifier
        @rtype: basestring
        """
        return self.settings.ident

    @property
    def entity(self):
        """Sector entity
        @rtype: ACSector
        """
        return self._entity

    @property
    def settings(self):
        """Sector settings
        @rtype: db.DBAreaConquest.SectorModel.SectorModel
        """
        return self._settings

    @property
    def state(self):
        """Sector state
        @rtype: basestring
        """
        return self._entity.stateContainer.state

    @property
    def teamIndex(self):
        """Owner team index
        @rtype: int
        """
        return self._entity.stateContainer.teamIndex

    @property
    def capturedAtTick(self):
        """Tick number when sector was captured last time
        @rtype: int
        """
        return self._entity.stateContainer.capturedAtTick

    @property
    def isCapturable(self):
        """Flag indicating that sector can or can't be captured by player
        @rtype: bool
        """
        return not (self.settings.isBase or self.settings.isFreeZone)

    @property
    def capturePointsTotal(self):
        """Points amount needed to capture sector
        @rtype: int
        """
        if SETTINGS.SECTOR.INDIVIDUAL_CAPTURE_POINTS:
            if self.teamIndex == TEAM_ID.TEAM_2:
                return self.settings.neutralCapturePoints
            else:
                return self.settings.ownedCapturePoints
        else:
            if self.teamIndex == TEAM_ID.TEAM_2:
                return SETTINGS.SECTOR.NEUTRAL_CAPTURE_POINTS
            return SETTINGS.SECTOR.OWNED_CAPTURE_POINTS

    @property
    def capturePointsByTeams(self):
        """Current capture points by teams in sector
        @rtype: (int, int)
        """
        return self._capturePointsByTeams

    @property
    def nextBonusTick(self):
        """Tick number when next bonus will be produced
        @rtype: int
        """
        return self._entity.nextBonusTick

    @property
    def rocketV2TargetSectorID(self):
        """Rocket V2 target sector id
        :rtype: str
        """
        return self._entity.rocketV2TargetSectorID

    def getPointsInTick(self, tickNumber):
        """Calculate points amount to be produced by sector in specified tick
        @param tickNumber: Current tick number
        @rtype: int
        """
        return self._settings.pointsProduction.getPointsInTick(self.capturedAtTick, tickNumber)

    def resetCapturePoints(self, *args, **kwargs):
        """Reset capture points by teams to default status
        """
        totalPoints = self.capturePointsTotal
        if self.teamIndex == TEAM_ID.TEAM_2:
            points = [int(totalPoints * 0.5), int(totalPoints * 0.5)]
        else:
            points = [0, 0]
            points[self.teamIndex] = totalPoints
        self._capturePointsByTeams = tuple(points)

    def addCapturePoints(self, teamIndex, points):
        """Add points amount for specified team in sector score
        @param teamIndex: Target team index
        @param points: Points amount
        """
        isCapturable = self.isCapturable and self.state != SECTOR_STATE.LOCKED
        playableTeamIndex = teamIndex in (TEAM_ID.TEAM_0, TEAM_ID.TEAM_1)
        if not (playableTeamIndex and isCapturable):
            return
        enemyTeamIndex = 1 - teamIndex
        capturePoints = list(self.capturePointsByTeams)
        capturePoints[enemyTeamIndex] = max(0, self.capturePointsByTeams[enemyTeamIndex] - points)
        capturePoints[teamIndex] = min(self.capturePointsTotal, self.capturePointsByTeams[teamIndex] + points)
        self._capturePointsByTeams = tuple(capturePoints)