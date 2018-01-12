# Embedded file name: scripts/client/ACSector.py
import BigWorld
import BWLogging
import Event
import GameEnvironment
from BWUserTypesCommon.ACSectorState import ACSectorState
from debug_utils import LOG_WARNING

class ACSector(BigWorld.Entity):
    """Client AC sector entity
    """
    entities = []
    ident = ''
    nextBonusTick = 0
    stateContainer = None
    rocketV2TargetSectorID = None
    isWasEnterWorld = False

    def __init__(self):
        super(ACSector, self).__init__()
        self.logger = BWLogging.getLogger(self)
        self.logger.info("Created client sector entity for sector '{0}'".format(self.ident))
        self._eManager = Event.EventManager()
        self.eNextBonusTickChanged = Event.Event(self._eManager)
        self.eStateChanged = Event.EventOrdered(self._eManager)
        self.eRocketV2TargetSectorIDChanged = Event.Event(self._eManager)

    def onEnterWorld(self, prereqs):
        self.entities.append(self)
        self._notifyGameModeAboutCreation()
        self.isWasEnterWorld = True

    def onLeaveWorld(self):
        self._eManager.clear()
        self.entities.remove(self)

    def set_nextBonusTick(self, oldValue):
        """nextBonusTick property callback from BigWorld
        """
        if not self.isWasEnterWorld:
            LOG_WARNING(' SECTOR set_nextBonusTick before onEnterWorld')
        self.eNextBonusTickChanged(self.ident, oldValue, self.nextBonusTick)

    def set_stateContainer(self, oldValue):
        """C{stateContainer} property callback from BigWorld
        """
        self.eStateChanged(self.ident, oldValue, self.stateContainer)

    def set_rocketV2TargetSectorID(self, oldValue):
        """rocketV2TargetSectorID property callback from BigWorld
        """
        self.eRocketV2TargetSectorIDChanged(self.ident, oldValue, self.rocketV2TargetSectorID)

    def _notifyGameModeAboutCreation(self):
        clientArena = GameEnvironment.getClientArena()
        if clientArena.gameMode:
            clientArena.gameMode.onACSectorCreated(self)