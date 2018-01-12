# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/ACClientArenaHelper.py
from collections import defaultdict
from EntityHelpers import AvatarFlags

def countAliveOrRespawnablePlayersByTeam(clientArena):
    """
    Players are meant to be players and player bots (stand ins), ignoring map elements: defenders and airstrike bombers
    @type clientArena: ClientArena.ClientArena
    @return: defaultdict[TEAM_ID, count]
    @rtype: defaultdict[int: int]
    """
    aliveOrRespawnableByTeam = defaultdict(int)
    for avatarInfo in clientArena.avatarInfos.itervalues():
        if isAvatarDefender(avatarInfo) or isAvatarAirstrikeBomber(avatarInfo):
            continue
        if isAvatarRespawnable(avatarInfo) or isAvatarAlive(avatarInfo):
            aliveOrRespawnableByTeam[getAvatarTeamIndex(avatarInfo)] += 1

    return aliveOrRespawnableByTeam


def getAvatarTeamIndex(avatarInfo):
    return avatarInfo['teamIndex']


def isDeadForEver(avatarInfo):
    return not isAvatarRespawnable(avatarInfo) and not isAvatarAlive(avatarInfo)


def isAvatarInRespawn(avatarInfo):
    return isAvatarRespawnable(avatarInfo) and not isAvatarAlive(avatarInfo)


def isAvatarRespawnable(avatarInfo):
    lifes = avatarInfo['stats']['lifes']
    return lifes > 0 or lifes == -1


def isAvatarAlive(avatarInfo):
    flags = avatarInfo['stats']['flags']
    return flags & AvatarFlags.DEAD == 0


def isAvatarLost(avatarInfo):
    flags = avatarInfo['stats']['flags']
    return flags & AvatarFlags.LOST != 0


def isAvatarDefender(avatarInfo):
    return bool(avatarInfo['defendSector'])


def isAvatarAirstrikeBomber(avatarInfo):
    return avatarInfo['isBomber']