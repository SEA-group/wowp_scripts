# Embedded file name: scripts/client/OrientationMarkers/OrientationMarkersSettings.py
import ResMgr
import GameEnvironment
import db.DBLogic
from consts import PLANE_TYPE, BATTLE_MODE
VISION_SETTINGS_XML_PATH = 'gui/flash/xml/visionSettings.xml'
AIM_DISTANCE_BY_PLANE_TYPE_BY_LEVEL = {}
VERY_FAR_DISTANCE_BY_LEVEL = {}
CIRCLE_RADIUS = 10.0
NAME_TO_PLANE_TYPE = {'Fighter': PLANE_TYPE.FIGHTER,
 'Heavy': PLANE_TYPE.HFIGHTER,
 'Assault': PLANE_TYPE.ASSAULT,
 'Navy': PLANE_TYPE.NAVY,
 'Bomber': PLANE_TYPE.BOMBER}

def getDistancesForPlayer(playerAvatar, battleMode):
    global VERY_FAR_DISTANCE_BY_LEVEL
    global AIM_DISTANCE_BY_PLANE_TYPE_BY_LEVEL
    clientArena = GameEnvironment.getClientArena()
    avatarInfo = clientArena.getAvatarInfo(playerAvatar.id)
    if avatarInfo is None:
        return
    else:
        settings = avatarInfo['settings']
        effectiveShootingDistance = _getGunnerShootingDistance(playerAvatar) if battleMode == BATTLE_MODE.GUNNER_MODE else _getMainArmamentShootingDistance(playerAvatar)
        planeLevel = settings.airplane.level
        planeType = settings.airplane.planeType
        aimDistance = AIM_DISTANCE_BY_PLANE_TYPE_BY_LEVEL[planeType][planeLevel]
        veryFarDistance = VERY_FAR_DISTANCE_BY_LEVEL[planeLevel]
        return (('Shooting', effectiveShootingDistance), ('Aiming', aimDistance), ('Far', veryFarDistance))


def _getMainArmamentShootingDistance(avatar):
    playerGlobalID = avatar.globalID
    return db.DBLogic.g_instance.getShootingDistanceEffective(playerGlobalID)


def _getGunnerShootingDistance(avatar):
    """
    @type avatar: PlayerAvatar.PlayerAvatar
    """
    gunner = avatar.controlledGunner
    return gunner.shootDistance


def _readSettingsFromVisionSettingsXml():
    visionSettingsRoot = ResMgr.openSection(VISION_SETTINGS_XML_PATH)
    for rootChildName, rootChild in visionSettingsRoot.items():
        if rootChildName == 'planeType':
            _parseAimDistance(rootChild)
        elif rootChildName == 'veryFar':
            _parseVeryFarDistance(rootChild)
        elif rootChildName == 'radius':
            _parseCircleRadius(rootChild)


def _parseAimDistance(planeTypeNode):
    planeTypeName = planeTypeNode['type'].asString
    planeType = NAME_TO_PLANE_TYPE[planeTypeName]
    for childName, child in planeTypeNode.items():
        if childName == 'aimDistance':
            level = child['level'].asInt
            value = child['value'].asFloat
            AIM_DISTANCE_BY_PLANE_TYPE_BY_LEVEL.setdefault(planeType, {})[level] = value


def _parseVeryFarDistance(varyFarNode):
    for child in varyFarNode.values():
        level = child['level'].asInt
        value = child['value'].asFloat
        VERY_FAR_DISTANCE_BY_LEVEL[level] = value


def _parseCircleRadius(radiusNode):
    global CIRCLE_RADIUS
    CIRCLE_RADIUS = radiusNode['value'].asFloat


_readSettingsFromVisionSettingsXml()