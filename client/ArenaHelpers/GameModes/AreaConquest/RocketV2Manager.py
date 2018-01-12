# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/RocketV2Manager.py
"""Client manager for Rocket Launch feature
"""
import collections
import weakref
import BigWorld
import BWLogging
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from Event import EventDispatcher
from consts import UPDATABLE_TYPE
from GameModeSettings import ACSettings as DEFAULT_SETTINGS
from ScenarioClient.ClientScenarioActions import getTerrainPointAndMaterial
logger = BWLogging.getLogger('RocketV2')

class RocketAdapter(object):

    def __init__(self, ballistic, teamIndex, targetSectorID):
        self.id = ballistic.getID()
        self.ballistic = ballistic
        self.teamIndex = teamIndex
        self.targetSectorID = targetSectorID

    def forceExplode(self):
        self.ballistic.doExplosion()


class RocketV2Manager(EventDispatcher):

    def __init__(self, gameMode):
        super(RocketV2Manager, self).__init__()
        self._gameModeRef = weakref.ref(gameMode)
        self._activeRockets = collections.defaultdict(list)
        self._subscribe()

    @property
    def gameMode(self):
        """Reference to game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        if self._gameModeRef:
            return self._gameModeRef()
        else:
            return None

    def onRocketV2TargetSectorChanged(self, sectorId, newTargetId):
        if DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.ENABLED:
            self._debugDrawInfluenceLine(sectorId, newTargetId)

    def onRocketV2Launched(self, sectorIdent, launchPosition, targetPosition, flyingTime, *args, **kwargs):
        if not self.gameMode.isReady:
            logger.info('Rocket launched while game mode is not ready. Launch skipped')
            return
        settings = self.gameMode.arenaTypeData.sectors.sectors[sectorIdent].rocketV2Settings
        self._launchRocketVisual(sectorIdent, launchPosition, targetPosition, settings.shotHeight, settings.ballisticProfileName, flyingTime)
        if DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.ENABLED:
            self._debugDrawRocketTarget(sectorIdent, launchPosition, targetPosition)

    def destroy(self):
        self._unsubscribe()
        self._gameModeRef = None
        return

    def _subscribe(self):
        self.gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_LAUNCHED, self.onRocketV2Launched)
        self.gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self.onRocketV2TargetSectorChanged)
        self.gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)

    def _unsubscribe(self):
        self.gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        self.gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self.onRocketV2TargetSectorChanged)
        self.gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_LAUNCHED, self.onRocketV2Launched)

    def _launchRocketVisual(self, sectorIdent, startPosition, endPosition, height, profileName, flyingTime):
        ballistic = launchRocketVisual(startPosition, endPosition, height, profileName)
        ballistic.onExplosion += self._onRocketExplosion
        sourceTeamIndex = self.gameMode.sectors[sectorIdent].teamIndex
        targetSectorIdent = self._getTargetSectorID(sectorIdent)
        adapter = RocketAdapter(ballistic, sourceTeamIndex, targetSectorIdent)
        self._activeRockets[adapter.id] = adapter
        self.dispatch(AC_EVENTS.ROCKET_V2_EFFECT_STARTED, adapter.id, sectorIdent, targetSectorIdent, startPosition, endPosition, sourceTeamIndex, flyingTime)

    def _getTargetSectorID(self, sectorID):
        return self.gameMode.sectors[sectorID].rocketV2TargetSectorID

    def _onRocketExplosion(self, instance):
        id = instance.getID()
        self._activeRockets.pop(id)
        self.dispatch(AC_EVENTS.ROCKET_V2_EFFECT_ENDED, id)

    def _onSectorStateChanged(self, sectorID, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
        for rocket in self._activeRockets.values():
            if rocket.targetSectorID == sectorID:
                if rocket.teamIndex == teamIndex:
                    rocket.forceExplode()

    def _debugDrawInfluenceLine(self, sectorId, targetId):
        name = DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.SECTOR_LINE_GROUP_NAME.format(sectorId=sectorId)
        sectors = self.gameMode.arenaTypeData.sectors
        sector, target = sectors.sectors[sectorId], sectors.sectors.get(targetId)
        BigWorld.clearGroup(name)
        if target:
            colour = DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.SECTOR_LINE_COLOUR
            BigWorld.addDrawLine(name, sector.positionPoint, target.positionPoint, colour, True)

    def _debugDrawRocketTarget(self, sectorId, launchPosition, targetPosition):
        name = DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.LINE_GROUP_NAME.format(sectorId=sectorId)
        BigWorld.clearGroup(name)
        colour = DEFAULT_SETTINGS.ROCKET_V2_SETTINGS.DEBUG.LINE_COLOUR
        BigWorld.addDrawLine(name, launchPosition, targetPosition, colour, True)

    def _debugExplodeActiveRockets(self):
        for rocket in self._activeRockets.values():
            rocket.forceExplode()


def launchRocketVisual(startPosition, endPosition, height, profileName):
    """Launch rocket visual effect from start position to end position
    @type startPosition: Math.Vector3
    @type endPosition: Math.Vector3
    @type height: int
    @type profileName: basestring
    @rtype: Ballistic.BallisticUpdatable
    """
    from db.DBLogic import g_instance as db
    from updatable.UpdatableManager import g_instance as updatableManager
    profile = db.getScenarioShotBallisticProfile(profileName)
    endPosition, material = getTerrainPointAndMaterial(BigWorld.player().spaceID, endPosition)
    effect = profile.explosionParticles.__dict__.get(material, profile.explosionParticles.default)
    startVector = endPosition - startPosition
    startVector.normalise()
    return updatableManager.createUpdatableLocal(UPDATABLE_TYPE.BALLISTIC, profileName, startPosition, startVector, startVector, endPosition, height, effect)