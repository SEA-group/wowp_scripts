# Embedded file name: scripts/client/GameActionsManager.py
import BigWorld
import BWLogging
import GameEnvironment
from Event import Event, EventManager

class GameActionsManager(BigWorld.Entity):
    """Common game activities manager. Includes managing of:
        - Air Strike waves
        - Rocket V2 launches
    """
    activeASWaves = None

    def __init__(self):
        BigWorld.Entity.__init__(self)
        self.logger = BWLogging.getLogger(self)
        self._lastWaveIDs = set()
        self._eManager = EventManager()
        self.eWaveAdded = Event(self._eManager)
        self.eWaveRemoved = Event(self._eManager)
        self.eWaveStateChanged = Event(self._eManager)
        self.eBomberStateChanged = Event(self._eManager)

    def onEnterWorld(self, prereqs):
        proxy = GameEnvironment.getClientArena().gameActionsManager
        proxy.onManagerEnterWorld(self)
        self._processWavesUpdate()
        self.logger.info('Entered world, id = {0}'.format(self.id))

    def onLeaveWorld(self):
        proxy = GameEnvironment.getClientArena().gameActionsManager
        proxy.onManagerLeaveWorld(self)
        self._eManager.clear()
        self.logger.info('Left world, id = {0}'.format(self.id))

    def set_activeASWaves(self, oldValue):
        """Internal BW callback for activeASWaves property change
        """
        self._processWavesUpdate()

    def setNested_activeASWaves(self, changePath, oldValue):
        """Internal BW callback for activeASWaves property change
        """
        if len(changePath) == 2 and changePath[1] == 'state':
            index = changePath[0]
            record = self.activeASWaves[index]
            self.eWaveStateChanged(record, oldValue, record['state'])
        elif len(changePath) == 4 and changePath[1] == 'bomberIDsStates':
            index = changePath[0]
            record = self.activeASWaves[index]
            bomberID = record['bomberIDsStates'][changePath[2]]['id']
            state = record['bomberIDsStates'][changePath[2]]['state']
            self.eBomberStateChanged(record, bomberID, oldValue, state)

    def _processWavesUpdate(self):
        """Process update for activeASWaves field to 
        find added and removed waves and trigger corresponding events
        """
        currentWaveIDs = [ r['waveID'] for r in self.activeASWaves ]
        addedWaves = [ waveID for waveID in currentWaveIDs if waveID not in self._lastWaveIDs ]
        for record in self.activeASWaves:
            if record['waveID'] in addedWaves:
                self.eWaveAdded(record)

        removedWaves = (waveID for waveID in self._lastWaveIDs if waveID not in currentWaveIDs)
        for waveID in removedWaves:
            self.eWaveRemoved(waveID)

        self._lastWaveIDs = set(currentWaveIDs)