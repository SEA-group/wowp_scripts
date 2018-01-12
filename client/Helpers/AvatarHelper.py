# Embedded file name: scripts/client/Helpers/AvatarHelper.py
import BigWorld
from consts import BOMB_TARGET_VIEW_HEIGHT_RANGE, DEFAULT_MIN_FLIGHT_HEIGHT, DEFAULT_MAX_FLIGHT_HEIGHT

def getAvatarSkillsList(avatarEntity):
    if len(avatarEntity.crewSkills) == 0:
        return []
    return map(lambda e: e['key'], avatarEntity.crewSkills[0]['skills'])


def isSpectating(entityID):
    return entityID == BigWorld.player().curVehicleID


def altitudeBombingZone(entity):
    minHeight, maxHeight = BOMB_TARGET_VIEW_HEIGHT_RANGE.get(entity.planeType, (DEFAULT_MIN_FLIGHT_HEIGHT, DEFAULT_MAX_FLIGHT_HEIGHT))
    altitude = entity.getAltitudeAboveObstacle()
    if altitude > maxHeight:
        return 1
    if altitude < minHeight:
        return -1
    return 0