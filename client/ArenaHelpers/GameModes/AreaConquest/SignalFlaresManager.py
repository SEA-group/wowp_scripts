# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/SignalFlaresManager.py
import weakref
import BigWorld
import consts
import db.DBLogic
import EffectManager
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from db.DBEffects import Effects
from GameModeSettings import ACSettings as SETTINGS

class SignalFlaresManager(object):

    def __init__(self, gameMode):
        self._gameModeRef = weakref.ref(gameMode)
        self._sectorPositions = {}
        self._sectorsTeamIndices = {}
        self._subscribe()

    @property
    def gameMode(self):
        if self._gameModeRef:
            return self._gameModeRef()
        else:
            return None

    def initSectorsData(self, *args, **kwargs):
        arenaData = db.DBLogic.g_instance.getArenaData(BigWorld.player().arenaType)
        for sectorId, sector in arenaData.sectors.sectors.iteritems():
            self._sectorsTeamIndices[sectorId] = sector.teamIndex
            self._sectorPositions[sectorId] = sector.positionPoint

    def onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, *args, **kwargs):
        oldTeamIndex, self._sectorsTeamIndices[sectorId] = self._sectorsTeamIndices[sectorId], teamIndex
        if oldTeamIndex != teamIndex:
            self.spawnFlaresInSector(sectorId, teamIndex)

    def spawnFlaresInSector(self, sectorId, teamIndex):
        if teamIndex == consts.TEAM_ID.TEAM_2:
            flareType = SETTINGS.SIGNAL_FLARE_TYPE.NEUTRAL
        elif teamIndex == BigWorld.player().teamIndex:
            flareType = SETTINGS.SIGNAL_FLARE_TYPE.ALLY
        else:
            flareType = SETTINGS.SIGNAL_FLARE_TYPE.ENEMY
        self.spawnFlaresInPosition(self._sectorPositions[sectorId], flareType)

    def spawnFlaresInPosition(self, position, flareType):
        effectName = SETTINGS.SIGNAL_FLARE_EFFECTS[flareType]
        effectId = Effects.getEffectId(effectName)
        EffectManager.g_instance.createWorldEffect(effectId, position, {})

    def _subscribe(self):
        self.gameMode.eGameModeReady += self.initSectorsData
        self.gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self.onSectorStateChanged)

    def _unsubscribe(self):
        self.gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self.onSectorStateChanged)
        self.gameMode.eGameModeReady -= self.initSectorsData

    def destroy(self):
        self._unsubscribe()
        self._gameModeRef = None
        return