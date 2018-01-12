# Embedded file name: scripts/client/ArenaHelpers/GameModes/GameModeClient.py
import weakref
import BigWorld
from Event import EventDispatcher
from debug_utils import LOG_DEBUG, LOG_ERROR

class GameModeClient(EventDispatcher):
    """Client game mode controller
    """

    def __init__(self, clientArena):
        """Creates new game mode instance
        @type clientArena: ClientArena.ClientArena
        """
        super(GameModeClient, self).__init__()
        self._clientArenaRef = weakref.ref(clientArena)
        self._updateArenaEventsMap = {}
        self._arenaTypeData = None
        self.loadArenaTypeData()
        self._logDebug(':__init__: {0}'.format(clientArena))
        return

    @property
    def clientArena(self):
        """Client arena reference
        @rtype: ClientArena.ClientArena
        """
        return self._clientArenaRef()

    @property
    def player(self):
        """Player avatar instance
        @rtype: PlayerAvatar.PlayerAvatar
        """
        return BigWorld.player()

    @property
    def arenaTypeData(self):
        """Arena type data
        @rtype: db.DBArenaType.ArenaType
        """
        return self._arenaTypeData

    def onArenaUpdate(self, functionID, payload):
        """Handle arena update from server
        @param functionID: ARENA_UPDATE.* identifier
        @param payload: Update data received from server
        """
        event = self._updateArenaEventsMap.get(functionID)
        if event:
            self.dispatch(event, payload)
        return bool(event)

    def registerArenaUpdateEvent(self, functionID, event):
        """Register event to be fired on arena update with specified functionID
        @param functionID: ARENA_UPDATE.* identifier
        @param event: Event identifier to be fired
        """
        self._updateArenaEventsMap[functionID] = event

    def registerArenaUpdateEvents(self, mapping):
        """Register events to be fired on arena update from mapping: functionID -> event
        @param mapping: Mapping from functionID to event
        @type mapping: dict
        """
        self._updateArenaEventsMap.update(mapping)

    def destroy(self):
        """Destruction logic
        """
        self._logDebug(':destroy')

    def loadArenaTypeData(self):
        """Load arena type data from db
        """
        from db.DBLogic import g_instance as db
        self._arenaTypeData = db.getArenaData(self.player.arenaType)

    def _logDebug(self, message):
        """Wrapper around LOG_DEBUG methods
        @param message: Log message
        """
        LOG_DEBUG('{0}:{1}'.format(self.__class__.__name__, message))

    def _logError(self, message):
        """Wrapper around LOG_ERROR methods
        @param message: Log message
        """
        LOG_ERROR('{0}:{1}'.format(self.__class__.__name__, message))