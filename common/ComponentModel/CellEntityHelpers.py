# Embedded file name: scripts/common/ComponentModel/CellEntityHelpers.py
import BigWorld
from consts import IS_CELLAPP
from ComponentLoggingHelpers import logEntityDoesNotExistError
if IS_CELLAPP:
    from EntityProviders import ArenaProvider, GameActionsManagerProvider

def getArena(component):
    entity = BigWorld.entities[component.planEntityId]
    arena = ArenaProvider().get(entity)
    if arena is None:
        logEntityDoesNotExistError('Arena', component)
    return arena


def getGameActionsManager(component):
    entity = BigWorld.entities[component.planEntityId]
    mgr = GameActionsManagerProvider().get(entity)
    if mgr is None:
        logEntityDoesNotExistError('GameActionsManager', component)
    return mgr