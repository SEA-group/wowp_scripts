# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/WaveInfoManager.py
from itertools import ifilter
from random import randint
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from debug_utils import LOG_DEBUG

class WaveData(object):

    def __init__(self, waveID, bomberIDsStates):
        self.waveId = waveID
        self.bomberIds = [ bomber['id'] for bomber in bomberIDsStates ]


class WaveInfoManager(object):

    def __init__(self, gameMode):
        self._gameMode = gameMode
        self._allWavesData = {}
        if self._gameMode.isReady:
            self._setupModel()
        else:
            self._gameMode.eGameModeReady += self._setupModel

    def _setupModel(self, *args, **kwargs):
        for record in self._gameMode.clientArena.gameActionsManager.activeASWaves:
            self._onBombersLaunched(record['sectorID'], record['targetID'], record['teamIndex'], record['waveID'], record['bomberIDsStates'], record['startTime'])

        self._gameMode.addEventHandler(AC_EVENTS.BOMBERS_LAUNCHED, self._onBombersLaunched)
        self._gameMode.addEventHandler(AC_EVENTS.BOMBERS_DIED, self._onBombersDied)

    def _onBombersLaunched(self, sectorIdent, targetSectorIdent, teamIndex, waveID, bomberIDsStates, startTime, *args, **kwargs):
        self._allWavesData[waveID] = WaveData(waveID, bomberIDsStates)

    def _onBombersDied(self, waveID, *args, **kwargs):
        del self._allWavesData[waveID]

    def getRandomPlaneInWave(self, waveID):
        planeList = self._allWavesData[waveID].bomberIds
        index = randint(0, planeList.__len__() - 1)
        return str(planeList[index])

    def getWaveByPlaneID(self, planeID):
        for key, waveData in self._allWavesData.items():
            value = next(ifilter(lambda o: o == int(planeID), waveData.bomberIds), None)
            if value:
                return key

        return -1

    def _getItem(pred, items):
        return next(ifilter(pred, items), None)

    def checkIsAirStrike(self, itemId):
        return itemId in self._allWavesData.keys()

    def destroy(self):
        self._gameMode.removeEventHandler(AC_EVENTS.BOMBERS_LAUNCHED, self._onBombersLaunched)
        self._gameMode.removeEventHandler(AC_EVENTS.BOMBERS_DIED, self._onBombersDied)
        self._gameMode.eGameModeReady -= self._setupModel
        self._allWavesData = None
        self._gameMode = None
        return