# Embedded file name: scripts/client/gui/HUD2/features/Sectors/SectorsGameEffectsSource.py
import BigWorld
import BWLogging
import _performanceCharacteristics_db
from gui.HUD2.core.DataModel import Structure
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from EntityHelpers import speedToMovement
from EventHelpers import CompositeSubscription, EDSubscription, EventSubscription
from consts import WORLD_SCALING, AIR_STRIKE_WAVE_STATE
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.HUD2.features.Entities import getClientTeamIndex

class BOMBERS_WAVE_STATE:
    INTRO_FLIGHT = 0
    BOMBING = 1
    OUTRO_FLIGHT = 2


WAVE_STATE_TO_HUD_STATE = {AIR_STRIKE_WAVE_STATE.INTRO_FLIGHT: BOMBERS_WAVE_STATE.INTRO_FLIGHT,
 AIR_STRIKE_WAVE_STATE.ATTACK_NOTIFIED: BOMBERS_WAVE_STATE.BOMBING,
 AIR_STRIKE_WAVE_STATE.BOMBS_DROPPED: BOMBERS_WAVE_STATE.OUTRO_FLIGHT,
 AIR_STRIKE_WAVE_STATE.OUTRO_FLIGHT: BOMBERS_WAVE_STATE.OUTRO_FLIGHT}

class SectorsGameEffectsSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).domination.sectorsGameEffects
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._db = features.require(Feature.DB_LOGIC)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._gameMode = self._clientArena.gameMode
        self._disableBomberCallbacks = {}
        self._subscription = CompositeSubscription(EDSubscription(self.gameMode, AC_EVENTS.BOMBERS_LAUNCHED, self._onBombersLaunched), EDSubscription(self.gameMode, AC_EVENTS.BOMBER_ATTACK_NOTIFIED, self._onBomberAttackNotified), EDSubscription(self.gameMode, AC_EVENTS.BOMBER_BOMBS_DROPPED, self._onBomberBombsDropped), EDSubscription(self.gameMode, AC_EVENTS.BOMBERS_DIED, self._onBombersDied), EDSubscription(self.gameMode, AC_EVENTS.BOMBER_IN_WAVE_DIED, self._onBomberInWaveDied), EDSubscription(self.gameMode.rocketV2Manager, AC_EVENTS.ROCKET_V2_EFFECT_STARTED, self._onRocketEffectStarted), EDSubscription(self.gameMode.rocketV2Manager, AC_EVENTS.ROCKET_V2_EFFECT_ENDED, self._onRocketEffectEnded), EventSubscription(self._clientArena.onReceiveMarkerMessage, self._onReceiveMarkerMessage))
        self.gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self._onRocketEffectSectorChanged)
        if self.gameMode.isReady:
            self._setupModel()
        else:
            self.gameMode.eGameModeReady += self._setupModel

    def _setupModel(self, *args, **kwargs):
        for record in self._clientArena.gameActionsManager.activeASWaves:
            state = WAVE_STATE_TO_HUD_STATE[record['state']]
            self._processASWave(record['sectorID'], record['targetID'], record['teamIndex'], record['waveID'], record['bomberIDsStates'], record['startTime'], state)

        self._subscription.subscribe()

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def _onBombersLaunched(self, sectorIdent, targetSectorIdent, teamIndex, waveID, bomberIDsStates, startTime, *args, **kwargs):
        bomberIDs = [ bomber['id'] for bomber in bomberIDsStates ]
        self._logger.debug("onBombersLaunched: sectorID = '{0}', targetID = '{1}', teamIndex = {2}, waveID = '{3}', bomberIDs = {4}, startTime = {5}".format(sectorIdent, targetSectorIdent, teamIndex, waveID, bomberIDs, startTime))
        self._processASWave(sectorIdent, targetSectorIdent, teamIndex, waveID, bomberIDsStates, startTime, BOMBERS_WAVE_STATE.INTRO_FLIGHT)

    def _processASWave(self, sectorIdent, targetSectorIdent, teamIndex, waveID, bomberIDsStates, startTime, state):
        arenaTypeData = self._gameMode.arenaTypeData
        sector = arenaTypeData.sectors.sectors[sectorIdent]
        influenceSettings = sector.bomberDispatcher.influenceBySectors[targetSectorIdent]
        splineSettings = influenceSettings.splinesByTeams[teamIndex]
        spline = self._db.getSpline(splineSettings.name)
        points = spline.getBasePoints()
        startPoint = self._makePos(points[0].x, points[0].z)
        endPoint = self._makePos(points[-1].x, points[-1].z)
        actionPointIndex = splineSettings.actionPointIndex
        globalID = arenaTypeData.gameModeSettings.airStrike.globalIDByLevel[self._playerAvatar.battleLevel]
        maxSpeed = _performanceCharacteristics_db.airplanes[globalID].maxSpeed
        curSpeed = speedToMovement(maxSpeed) * WORLD_SCALING / 3.6
        dist = points[0].distTo(points[actionPointIndex])
        startDelay = 2
        flyingTime = dist / curSpeed
        arenaTime = startTime - self._playerAvatar.arenaStartTime
        strikeTime = int(arenaTime + flyingTime + startDelay)
        self._logger.debug('Bombing time estimation: arenaTime = {0}, startDelay = {1}, flyingTime = {2}'.format(arenaTime, startDelay, flyingTime))
        waveTeamIndex = getClientTeamIndex(teamIndex, self._playerAvatar.teamIndex)
        self._appendASWave(sectorIdent, targetSectorIdent, waveTeamIndex, waveID, startPoint, endPoint, strikeTime, state, bomberIDsStates)

    def _onBomberInWaveDied(self, sectorIdent, waveID, bomberID):
        bomberEffect = self._model.airStrikes.first(lambda a: a.waveID.get() == waveID)
        if bomberEffect:
            bomberIDStruct = bomberEffect.bomberIDsStates.first(lambda d: d.id.get() == bomberID)
            if bomberIDStruct:
                bomberEffect.bomberIDsStates.splice(bomberIDStruct)

    def _onBomberAttackNotified(self, sectorID, waveID, bomberID, waveSize, aliveBombers, *args, **kwargs):
        self._logger.debug("_onBombersAttackNotified: sectorID = '{0}', waveID = '{1}', waveSize = {2}, aliveBombers = {3}".format(sectorID, waveID, waveSize, aliveBombers))
        waveModel = self._model.airStrikes.first(lambda a: a.waveID.get() == waveID)
        if waveModel:
            waveModel.strikeState = BOMBERS_WAVE_STATE.BOMBING
            bomberModel = waveModel.bomberIDsStates.first(lambda a: a.id.get() == bomberID)
            if bomberModel:
                bomberModel.state = BOMBERS_WAVE_STATE.BOMBING

    def _onBomberBombsDropped(self, sectorID, waveID, bomberID, waveSize, aliveBombers, *args, **kwargs):
        arenaTypeData = self._gameMode.arenaTypeData
        delay = arenaTypeData.gameModeSettings.airStrike.markersDelayByLevel[self._playerAvatar.battleLevel]
        model = self._model.airStrikes.first(lambda a: a.waveID.get() == waveID)
        self._disableBomberCallbacks[bomberID] = BigWorld.callback(delay, lambda : self.disableBomber(model, bomberID))

    def disableBomber(self, model, bomberID):

        def checkIfReadyToSplice(list):
            for item in list:
                if item.state.get() is not BOMBERS_WAVE_STATE.OUTRO_FLIGHT:
                    return False

            return True

        def checkIfSomebodyIsBombing(list):
            for item in list:
                if item.state.get() is BOMBERS_WAVE_STATE.BOMBING:
                    return True

            return False

        if model:
            bomberModel = model.bomberIDsStates.first(lambda a: a.id.get() == bomberID)
            if bomberModel:
                bomberModel.state = BOMBERS_WAVE_STATE.OUTRO_FLIGHT
            if checkIfReadyToSplice(model.bomberIDsStates):
                model.strikeState = BOMBERS_WAVE_STATE.OUTRO_FLIGHT
                waveID = model.waveID.get()
                if self._model.airStrikes.first(lambda a: a.waveID.get() == waveID):
                    self._model.airStrikes.splice(model)
            elif checkIfSomebodyIsBombing(model.bomberIDsStates):
                model.strikeState = BOMBERS_WAVE_STATE.BOMBING
            else:
                model.strikeState = BOMBERS_WAVE_STATE.INTRO_FLIGHT

    def _onBombersDied(self, waveID, *args, **kwargs):
        self._logger.debug("onBombersDied: waveID = '{0}'".format(waveID))
        model = self._model.airStrikes.first(lambda a: a.waveID.get() == waveID)
        if model:
            for bomber in model.bomberIDsStates:
                bomber.state = BOMBERS_WAVE_STATE.OUTRO_FLIGHT

            model.strikeState = BOMBERS_WAVE_STATE.OUTRO_FLIGHT
            self._model.airStrikes.splice(model)

    def _onRocketEffectStarted(self, id, sectorIdent, targetSectorIdent, startPosition, endPosition, teamIndex, flyingTime):
        startTime = BigWorld.serverTime() - BigWorld.player().arenaStartTime
        startSectorPosition = self._getPosBySectorId(sectorIdent)
        endSectorPosition = self._getPosBySectorId(targetSectorIdent)
        self._model.rockets.append(id=id, sectorID=sectorIdent, targetSectorID=targetSectorIdent, startPoint=self._makePos(startSectorPosition.x, startSectorPosition.z), endPoint=self._makePos(endSectorPosition.x, endSectorPosition.z), teamIndex=teamIndex, flyingTime=flyingTime, startTime=startTime)

    def _onRocketEffectSectorChanged(self, id, newTargetSectorIdent):
        startSectorPosition = self._getPosBySectorId(id)
        endSectorPosition = self._getPosBySectorId(newTargetSectorIdent)
        for rocketEffect in self._model.rockets:
            if rocketEffect.sectorID.get() == id:
                rocketEffect.startPoint = self._makePos(startSectorPosition.x, startSectorPosition.z)
                rocketEffect.endPoint = self._makePos(endSectorPosition.x, endSectorPosition.z)
                rocketEffect.targetSectorID = newTargetSectorIdent
                break

    def _onReceiveMarkerMessage(self, senderID, posX, posZ, messageStringID, fromQueue):
        self._model.selectedPoint = self._makePos(posX, posZ)

    def _onRocketEffectEnded(self, id):
        model = self._model.rockets.first(lambda a: a.id.get() == id)
        if model:
            self._model.rockets.splice(model)

    def _makePos(self, x, y):
        return {'x': x,
         'y': y}

    def _getPosBySectorId(self, sectorId):
        sectorData = self._getSectorByID(sectorId)
        return sectorData.entity.position

    def _checkSectorInSectors(self, sectorId):
        return sectorId in self.gameMode.sectors

    def _getSectorByID(self, sectorId):
        """ACSectorClient instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACSectorClient.ACSectorClient
        """
        return self.gameMode.sectors[sectorId]

    def _appendASWave(self, sectorID, targetID, teamIndex, waveID, startPoint, endPoint, strikeTime, state, bomberIDsStates):
        item = self._model.airStrikes.append(sectorID=sectorID, targetSectorID=targetID, teamIndex=teamIndex, waveID=waveID, startPoint=startPoint, endPoint=endPoint, strikeTime=strikeTime, strikeState=state)
        for bomber in bomberIDsStates:
            item.bomberIDsStates.appendSilently(id=bomber['id'], state=state)

        item.bomberIDsStates.finishAppending()

    def dispose(self):
        for item in self._disableBomberCallbacks.itervalues():
            BigWorld.cancelCallback(item)

        self._disableBomberCallbacks.clear()
        self.gameMode.eGameModeReady -= self._setupModel
        self.gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self._onRocketEffectSectorChanged)
        self._subscription.unsubscribe()
        self._logger = None
        self._model = None
        self._clientArena = None
        self._db = None
        self._playerAvatar = None
        self._gameMode = None
        self._subscription = None
        return