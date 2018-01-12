# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/ACGameModeClient.py
import BigWorld
import Math
from ACSector import ACSector
from ArenaHelpers.GameModes import GameModeClient
from ArenaHelpers.GameModes.AreaConquest import ACSectorClient
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from ArenaHelpers.GameModes.AreaConquest import RocketV2Manager
from ArenaHelpers.GameModes.AreaConquest import SignalFlaresManager
from ArenaHelpers.GameModes.AreaConquest.LastPlayerManager import LastPlayerManager
from ArenaHelpers.GameModes.AreaConquest.WaveInfoManager import WaveInfoManager
from Event import eventHandler, Event, EventManager
from EventHelpers import CompositeSubscription, EventSubscription
from GameModeSettings import ACSettings as SETTINGS
from consts import ARENA_UPDATE, TEAM_ID, AIR_STRIKE_WAVE_STATE

class AC_ARENA_UPDATE_EVENTS:
    """Events for update arena calls.
    You should not use them outside ACGameModeClient, use AC_EVENT instead
    """
    UPDATE_AC_POINTS = 'update_ac_points'
    AC_ACTION_MESSAGE = 'ac_action_message'
    AC_GAME_TICK = 'ac_game_tick'
    AC_BATTLE_EVENT = 'ac_battle_event'
    AC_ROCKET_V2_LAUNCHED = 'ac_rocket_v2_launched'
    AC_ROCKET_V2_HIT_TARGET = 'ac_rocket_v2_hit_target'
    AC_ROCKET_V2_TARGET_OBJECT_CHANGED = 'ac_rocket_v2_target_object_changed'
    AC_BOMBER_IN_WAVE_DIED = 'ac_bomber_in_wave_died'
    AC_BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED = 'ac_bomber_dispatcher_target_sector_changed'


class ACGameModeClient(GameModeClient.GameModeClient):
    updateEventsMap = {ARENA_UPDATE.UPDATE_AC_POINTS: AC_ARENA_UPDATE_EVENTS.UPDATE_AC_POINTS,
     ARENA_UPDATE.AC_ACTION_MESSAGE: AC_ARENA_UPDATE_EVENTS.AC_ACTION_MESSAGE,
     ARENA_UPDATE.AC_GAME_TICK: AC_ARENA_UPDATE_EVENTS.AC_GAME_TICK,
     ARENA_UPDATE.AC_BATTLE_EVENT: AC_ARENA_UPDATE_EVENTS.AC_BATTLE_EVENT,
     ARENA_UPDATE.AC_ROCKET_V2_LAUNCHED: AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_LAUNCHED,
     ARENA_UPDATE.AC_ROCKET_V2_HIT_TARGET: AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_HIT_TARGET,
     ARENA_UPDATE.AC_ROCKET_V2_TARGET_OBJECT_CHANGED: AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_TARGET_OBJECT_CHANGED,
     ARENA_UPDATE.AC_BOMBER_IN_WAVE_DIED: AC_ARENA_UPDATE_EVENTS.AC_BOMBER_IN_WAVE_DIED,
     ARENA_UPDATE.AC_BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED: AC_ARENA_UPDATE_EVENTS.AC_BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED}

    def __init__(self, clientArena):
        super(ACGameModeClient, self).__init__(clientArena)
        self._scoreGlobal = (0, 0)
        self._sectors = {}
        self._currentTick = 0
        self._currentTickStartedAt = self.player.arenaStartTime
        self._isReady = False
        self._eManager = EventManager()
        self.eGameModeReady = Event(self._eManager)
        self._rocketV2Manager = RocketV2Manager.RocketV2Manager(self)
        self._signalFlaresManager = SignalFlaresManager.SignalFlaresManager(self)
        self._waveInfoManager = WaveInfoManager(self)
        self._lastPlayerManager = LastPlayerManager(self)
        self._pendingEvents = []
        self.createSectorsData()
        self.registerArenaUpdateEvents(self.updateEventsMap)
        gameActionsManager = self.clientArena.gameActionsManager
        self._subscription = CompositeSubscription(EventSubscription(gameActionsManager.eWaveAdded, self._onASWaveAdded), EventSubscription(gameActionsManager.eWaveRemoved, self._onASWaveRemoved), EventSubscription(gameActionsManager.eWaveStateChanged, self._onASWaveStateChanged), EventSubscription(gameActionsManager.eBomberStateChanged, self._onASBomberStateChanged))
        self._subscription.subscribe()

    @property
    def isReady(self):
        return self._isReady

    @property
    def rocketV2Manager(self):
        """
        @rtype: RocketV2Manager.RocketV2Manager
        """
        return self._rocketV2Manager

    @property
    def scoreGlobal(self):
        """Global game score
        @rtype: (int, int)
        """
        return self._scoreGlobal

    @property
    def sectors(self):
        """Sectors dict
        @rtype: dict[basestring, ACSectorClient.ACSectorClient]
        """
        raise self.isReady or AssertionError('Attempt to get sectors data while GameMode is not ready')
        return self._sectors

    @property
    def currentTick(self):
        """Current game tick number
        @rtype: int
        """
        return self._currentTick

    @property
    def currentTickStartedAt(self):
        """Time when current tick started by BigWorld.serverTime()
        @rtype: float
        """
        return self._currentTickStartedAt

    @property
    def arenaTimeRemaining(self):
        """battle time remaining
        @rtype: float
        """
        return self.player.arenaStartTime + self.arenaTypeData.gameModeSettings.battleDuration - BigWorld.serverTime()

    @property
    def waveInfoManager(self):
        """
        @rtype: WaveInfoManager.WaveInfoManager
        """
        return self._waveInfoManager

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_BATTLE_EVENT)
    def onBattleEvent(self, payload, *args, **kwargs):
        self._logDebug(':onUpdateACSBattleEvent: onBattleEvent'.format(payload))
        battleEventId = payload
        self.dispatch(AC_EVENTS.BATTLE_EVENT, battleEventId)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.UPDATE_AC_POINTS)
    def onUpdateACPoints(self, payload, *args, **kwargs):
        points = tuple(payload)
        self._logDebug(':onUpdateACPoints: points={0}'.format(points))
        self._scoreGlobal = points
        self.dispatch(AC_EVENTS.GLOBAL_SCORE_UPDATED, self.scoreGlobal)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_ACTION_MESSAGE)
    def onACActionMessage(self, payload, *args, **kwargs):
        self._logDebug(':onACActionMessage: payload={0}'.format(payload))
        action, teamIndex, avatarId, sectorId, tickNumber, points = payload
        settings = SETTINGS.ACTION_SETTINGS.get(action)
        if not settings:
            self._logError(':onACActionMessage: Unknown action got, id={0}'.format(action))
            return
        self.dispatch(AC_EVENTS.SECTOR_ACTION, sectorId, teamIndex, settings)
        if settings['sectorScore']:
            sector = self.sectors[sectorId]
            sector.addCapturePoints(teamIndex, points)
            self._logDebug(':onACActionMessage: updated sector capture points: {0}'.format(sector.capturePointsByTeams))
            self.dispatch(AC_EVENTS.SECTOR_CAPTURE_POINTS_CHANGED, sector.ident, sector.capturePointsByTeams)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_GAME_TICK)
    def onACGameTick(self, payload, *args, **kwargs):
        self._logDebug(':onACGameTick: payload={0}'.format(payload))
        tickNumber = payload
        self.dispatch(AC_EVENTS.GAME_MODE_TICK, tickNumber)
        self._currentTick = tickNumber + 1
        self._currentTickStartedAt = BigWorld.serverTime()

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_LAUNCHED)
    def onRocketV2Launched(self, payload, *args, **kwargs):
        launchPosition, targetPosition = Math.Vector3(), Math.Vector3()
        sectorIdent, launchPosition.x, launchPosition.y, launchPosition.z, targetID, targetPosition.x, targetPosition.y, targetPosition.z, flyingTime = payload
        self.dispatch(AC_EVENTS.ROCKET_V2_LAUNCHED, sectorIdent, launchPosition, targetPosition, flyingTime)

    def onRocketV2TargetSectorChanged(self, sectorID, oldTargetID, newTargetID, *args, **kwargs):
        self.dispatch(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, sectorID, newTargetID)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_TARGET_OBJECT_CHANGED)
    def onRocketV2TargetObjectChanged(self, payload, *args, **kwargs):
        sectorIdent, sectorTeamIndex, newTargetObjId = payload
        self.dispatch(AC_EVENTS.ROCKET_V2_TARGET_OBJECT_CHANGED, sectorIdent, sectorTeamIndex, newTargetObjId)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_HIT_TARGET)
    def onRocketV2HitTarget(self, payload, *args, **kwargs):
        sectorIdent, teamIndex, targetTeamObjectId, targetPositionX, targetPositionY, targetPositionZ, targetTeamIndex = payload
        self.dispatch(AC_EVENTS.ROCKET_V2_HIT_TARGET, sectorIdent, teamIndex, targetTeamObjectId)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_BOMBER_IN_WAVE_DIED)
    def onBomberInWaveDied(self, payload):
        sectorIdent, waveID, bomberID = payload
        self.dispatch(AC_EVENTS.BOMBER_IN_WAVE_DIED, sectorIdent, waveID, bomberID)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED)
    def onBombersChangeTarget(self, payload):
        sectorIdent, newTargetSectorIdent = payload
        self.dispatch(AC_EVENTS.BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED, sectorIdent, newTargetSectorIdent)

    def createSectorsData(self):
        """Create sectors data using arena settings
        """
        for sectorId, settings in self.arenaTypeData.sectors.sectors.iteritems():
            entity = next((sector for sector in ACSector.entities if sector.ident == sectorId), None)
            if entity:
                self._sectors[sectorId] = sector = ACSectorClient.ACSectorClient(settings, entity)
                sector.eStateChanged += self.onSectorStateChanged
                sector.eRocketV2TargetSectorIDChanged += self.onRocketV2TargetSectorChanged

        self._checkIsReady()
        return

    def getPointsInTick(self, tickNumber = None):
        """Return Points in tick
        @param tickNumber: tick number
        """
        tickNumber = tickNumber or self.currentTick
        score = [0, 0]
        for sector in self.sectors.itervalues():
            if sector.teamIndex in (TEAM_ID.TEAM_0, TEAM_ID.TEAM_1):
                score[sector.teamIndex] += sector.getPointsInTick(tickNumber)

        return score

    def getTickPeriod(self):
        """Return tick period
        """
        period = self.arenaTypeData.gameModeSettings.globalTickPeriod
        if self.teamSuperiority(TEAM_ID.TEAM_0) or self.teamSuperiority(TEAM_ID.TEAM_1):
            period = self.arenaTypeData.gameModeSettings.superiorityGlobalTickPeriod
        return period

    def teamSuperiority(self, teamIndex):
        """Check capture sectors by team
        """
        sectors = 0
        capturedSectors = 0
        for sector in self._sectors.itervalues():
            if not sector.isCapturable:
                continue
            sectors += 1
            if sector.teamIndex == teamIndex:
                capturedSectors += 1

        return sectors == capturedSectors

    def onSectorStateChanged(self, ident, oldState, state, *args, **kwargs):
        """Event handler for state changed event
        @param ident: Sector identifier
        @type state: BWUserTypesCommon.ACSectorState.ACSectorState
        @type oldState: BWUserTypesCommon.ACSectorState.ACSectorState
        """
        self.dispatch(AC_EVENTS.SECTOR_STATE_CHANGED, ident, oldState.state, oldState.teamIndex, state.state, state.teamIndex, state.nextStateTimestamp)

    def _checkIsReady(self):
        if self._isReady:
            return
        self._isReady = all((ident in self._sectors for ident in self.arenaTypeData.sectors.sectors))
        if self._isReady:
            self._processSuspendedEvents()
            self.eGameModeReady()

    def onACSectorCreated(self, entity):
        """Callback from sector entity on enter world event
        @type entity: ACSector
        """
        raise entity.ident in self.arenaTypeData.sectors.sectors or AssertionError("Unexpected sector created: '{0}', arena: {1}".format(entity.ident, self.arenaTypeData.typeName))
        settings = self.arenaTypeData.sectors.sectors[entity.ident]
        self._sectors[entity.ident] = sector = ACSectorClient.ACSectorClient(settings, entity)
        sector.eStateChanged += self.onSectorStateChanged
        self._checkIsReady()

    @property
    def lastPlayerManager(self):
        return self._lastPlayerManager

    def dispatch(self, event, *args, **kwargs):
        if not self.isReady:
            self._suspendEvent(event, args, kwargs)
            self._logDebug("Suspended event processing while game mode is not ready: event = '{0}', args = {1}, kwargs = {2}".format(event, args, kwargs))
            return
        super(ACGameModeClient, self).dispatch(event, *args, **kwargs)

    def destroy(self):
        self._subscription.unsubscribe()
        self._subscription = None
        self._waveInfoManager.destroy()
        self._lastPlayerManager.destroy()
        self._eManager.clear()
        self._rocketV2Manager.destroy()
        self._signalFlaresManager.destroy()
        self.clear()
        super(ACGameModeClient, self).destroy()
        return

    def _suspendEvent(self, event, args, kwargs):
        self._pendingEvents.append((event, args, kwargs))

    def _processSuspendedEvents(self):
        for event, args, kwargs in self._pendingEvents:
            self.dispatch(event, *args, **kwargs)

        self._pendingEvents[:] = []

    def _onASWaveAdded(self, record, *args, **kwargs):
        """Handler for GameActionsManager.eWaveAdded event
        :param record: AIR_STRIKE_WAVE_RECORD
        """
        self.dispatch(AC_EVENTS.BOMBERS_LAUNCHED, record['sectorID'], record['targetID'], record['teamIndex'], record['waveID'], record['bomberIDsStates'], record['startTime'])

    def _onASWaveRemoved(self, waveID, *args, **kwargs):
        """Handler for GameActionsManager.eWaveRemoved event
        :param waveID: Unique wave identifier 
        """
        self.dispatch(AC_EVENTS.BOMBERS_DIED, waveID)

    def _onASWaveStateChanged(self, record, stateOld, state, *args, **kwargs):
        """Handler for GameActionsManager.eWaveStateChanged event
        :param record: AIR_STRIKE_WAVE_RECORD
        :param stateOld: Old state value
        :param state: New state value
        """
        if state == AIR_STRIKE_WAVE_STATE.ATTACK_IN_PROGRESS and stateOld == AIR_STRIKE_WAVE_STATE.BOMBS_DROPPED:
            self.dispatch(AC_EVENTS.BOMBERS_ATTACK_STARTED, record['sectorID'], record['waveID'], record['size'], len(record['bomberIDsStates']))

    def _onASBomberStateChanged(self, record, bomberID, stateOld, state, *args, **kwargs):
        """Handler for GameActionsManager.eBomberStateChanged event
        :param record: AIR_STRIKE_WAVE_RECORD
        :param bomberID: Unique bomber id
        :param stateOld: Old state value
        :param state: New state value
        """
        if state == AIR_STRIKE_WAVE_STATE.ATTACK_NOTIFIED and stateOld == AIR_STRIKE_WAVE_STATE.INTRO_FLIGHT:
            self.dispatch(AC_EVENTS.BOMBER_ATTACK_NOTIFIED, record['sectorID'], record['waveID'], bomberID, record['size'], len(record['bomberIDsStates']))
        elif state == AIR_STRIKE_WAVE_STATE.BOMBS_DROPPED and stateOld == AIR_STRIKE_WAVE_STATE.ATTACK_NOTIFIED:
            self.dispatch(AC_EVENTS.BOMBER_BOMBS_DROPPED, record['sectorID'], record['waveID'], bomberID, record['size'], len(record['bomberIDsStates']))