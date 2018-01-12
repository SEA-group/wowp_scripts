# Embedded file name: scripts/client/audio/AudioHelpers/AirStrikeDefeatedEventProvider.py
import BigWorld
from Event import Event
from EventHelpers import CompositeSubscription, EventSubscription, EDSubscription
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from functools import partial

class EventCandidate(object):

    def __init__(self, waveID, bomberIDs, targetID, teamIndex):
        self.waveID = waveID
        self.bomberIDs = bomberIDs
        self.targetID = targetID
        self.teamIndex = teamIndex
        self.isDamagedByPlayer = False


class AirStrikeDefeatedEventProvider(object):
    """
    Provides with event when air strike bombers are defeated with player participation before they started to attack
    
    @type _eventCandidates: dict[int, EventCandidate]
    """

    def __init__(self, gameEnvironment, gameMode):
        """
        @type gameEnvironment: GameEnvironment.GameEnvironment
        @type gameMode: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        self._gameEnvironment = gameEnvironment
        self._gameMode = gameMode
        self._eventCandidates = {}
        self.__waveDiedCallbacks = {}
        self.eAirStrikeDefeated = Event()
        self._subscribe()

    def destroy(self):
        self.__clearAllCallbacks()
        self._unsubscribe()
        self.eAirStrikeDefeated.clear()
        self._gameEnvironment = None
        self._gameMode = None
        return

    def _subscribe(self):
        self._subscription = CompositeSubscription(EventSubscription(self._gameEnvironment.eAvatarHealthChange, self._onAvatarHealthChanged), EDSubscription(self._gameMode, AC_EVENTS.BOMBERS_LAUNCHED, self._onACBombersWaveLaunched), EDSubscription(self._gameMode, AC_EVENTS.BOMBERS_DIED, self._onACBombersWaveDied), EDSubscription(self._gameMode, AC_EVENTS.BOMBERS_ATTACK_STARTED, self._onACBombersAttackStarted))
        self._subscription.subscribe()

    def _unsubscribe(self):
        self._subscription.unsubscribe()
        self._subscription = None
        return

    def __clearCB(self, waveID):
        if waveID in self.__waveDiedCallbacks:
            BigWorld.cancelCallback(self.__waveDiedCallbacks[waveID])
            del self.__waveDiedCallbacks[waveID]

    def __clearAllCallbacks(self):
        for waveID, callback in self.__waveDiedCallbacks.iteritems():
            BigWorld.cancelCallback(callback)

        self.__waveDiedCallbacks = {}

    def _onAvatarHealthChanged(self, entity, *args, **kwargs):
        if entity.lastDamagerID != BigWorld.player().id:
            return
        for waveID, candidate in self._eventCandidates.iteritems():
            if candidate.isDamagedByPlayer:
                continue
            if entity.id in candidate.bomberIDs:
                candidate.isDamagedByPlayer = True
                break

    def _onACBombersWaveLaunched(self, sectorID, targetID, teamIndex, waveID, bomberIDsStates, startTime, *args, **kwargs):
        if BigWorld.player().teamIndex == teamIndex:
            return
        bomberIDs = [ bomber['id'] for bomber in bomberIDsStates ]
        self._eventCandidates[waveID] = EventCandidate(waveID, bomberIDs, targetID, teamIndex)

    def _onACBombersAttackStarted(self, sectorID, waveID, waveSize, aliveBombers, *args, **kwargs):
        if waveID in self._eventCandidates:
            del self._eventCandidates[waveID]

    def _onACBombersWaveDied(self, waveID, *args, **kwargs):
        if waveID in self._eventCandidates:
            if self._eventCandidates[waveID].isDamagedByPlayer:
                if waveID not in self.__waveDiedCallbacks:
                    onACBombersWaveDiedCallback = partial(self._onACBombersWaveDied, waveID, *args, **kwargs)
                    self.__waveDiedCallbacks[waveID] = BigWorld.callback(0.5, onACBombersWaveDiedCallback)
                    return
                targetID = self._eventCandidates[waveID].targetID
                if not self._eventCandidates[waveID].teamIndex == self._gameMode.sectors[targetID].teamIndex:
                    self.eAirStrikeDefeated()
                self.__clearCB(waveID)
            del self._eventCandidates[waveID]