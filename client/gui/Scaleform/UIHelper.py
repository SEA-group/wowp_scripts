# Embedded file name: scripts/client/gui/Scaleform/UIHelper.py
import BigWorld
import GameEnvironment
import InputMapping

class SQUAD_TYPES:
    WITHOUT_SQUAD = 0
    OTHER = 1
    OWN = 2

    @staticmethod
    def getSquadType(squadNumber, avatarID):
        if not squadNumber:
            return SQUAD_TYPES.WITHOUT_SQUAD
        owner = BigWorld.player()
        if avatarID == owner.id:
            return SQUAD_TYPES.OWN
        clientArena = GameEnvironment.getClientArena()
        ownerInfo = clientArena.getAvatarInfo(owner.id)
        avatarInfo = clientArena.getAvatarInfo(avatarID)
        if ownerInfo is not None and avatarInfo is not None:
            if owner.teamIndex == avatarInfo['teamIndex'] and ownerInfo['squadID'] == squadNumber:
                return SQUAD_TYPES.OWN
            return SQUAD_TYPES.OTHER
        else:
            return

    @staticmethod
    def playerSquadID():
        return SQUAD_TYPES.getSquadIDbyAvatarID(BigWorld.player().id)

    @staticmethod
    def getSquadIDbyAvatarID(avatarID):
        avatarInfo = GameEnvironment.getClientArena().getAvatarInfo(avatarID)
        if avatarInfo is not None and 'squadID' in avatarInfo:
            return avatarInfo['squadID']
        else:
            return 0


def getKeyLocalization(cmdID, keyIndex = 0):
    keyName = ''
    keysControls = InputMapping.g_instance.getKeyControlsHelp([cmdID])
    keysData = keysControls.get(cmdID, None)
    if keysData is not None and keysData['keys']:
        keyName = InputMapping.getKeyLocalization(keysData['keys'][keyIndex])
        if keysData['isFireAxis'][keyIndex]:
            if keysData['axisSign'][keyIndex] == 1:
                keyName += '+'
            else:
                keyName += '-'
    return keyName