# Embedded file name: scripts/client/gui/HUD2/features/Entities/__init__.py
from ArenaHelpers.GameModes.AreaConquest.ACClientArenaHelper import isAvatarInRespawn, isAvatarLost, isAvatarAlive, isDeadForEver
from EntityHelpers import EntityStates
from consts import TEAM_ID

def getClientTeamIndex(pythonTeamIndex, playerIndex):
    if pythonTeamIndex in TEAM_ID.CHOSEN:
        if pythonTeamIndex == playerIndex:
            return 0
        else:
            return 1
    elif pythonTeamIndex == TEAM_ID.TEAM_2:
        return 2
    return 3


IS_WAITE_FOR_RESPAWN = 1024

def getLogicState(avatarInfo):
    logicState = EntityStates.UNDEFINED
    isInRespawn = isAvatarInRespawn(avatarInfo)
    isAlive = isAvatarAlive(avatarInfo)
    isDead = isDeadForEver(avatarInfo)
    if isAlive:
        logicState = EntityStates.GAME
    if isInRespawn:
        logicState = IS_WAITE_FOR_RESPAWN
    if isDead:
        logicState = EntityStates.DEAD
    return logicState


def checkLost(avatarInfo):
    return isAvatarLost(avatarInfo)