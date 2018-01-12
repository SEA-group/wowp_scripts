# Embedded file name: scripts/client/Helpers/TeamObjectHelper.py
from clientConsts import TEAM_OBJECTS_PARTS_TYPES, TARGET_PARTS_TYPES
from debug_utils import LOG_DEBUG, LOG_WARNING
import BigWorld

def getTeamObjectTypeByParts(id, partsData = None):
    """
    :param id: <int>
    :param partsData: <list>
    :rtype int
    """
    partsData = __getTeamObjectPartsData(id, partsData)
    if partsData is None:
        LOG_DEBUG('getTeamObjectTypeByParts - partsData is None', id)
        return TEAM_OBJECTS_PARTS_TYPES.SIMPLE
    elif not partsData:
        LOG_DEBUG('getTeamObjectTypeByParts - object has no live parts', id)
        return TEAM_OBJECTS_PARTS_TYPES.ERROR
    else:
        hasArmored, hasFiring, hasSimple = False, False, False
        for part in partsData:
            if part['isArmored']:
                hasArmored = True
            else:
                hasSimple = True
            if part['isFiring']:
                hasFiring = True

        if not hasSimple:
            if hasFiring:
                return TEAM_OBJECTS_PARTS_TYPES.FIRING_ARMORED
            return TEAM_OBJECTS_PARTS_TYPES.ARMORED
        elif hasFiring:
            if hasArmored:
                return TEAM_OBJECTS_PARTS_TYPES.SIMPLE_FIRING_ARMORED
            return TEAM_OBJECTS_PARTS_TYPES.SIMPLE_FIRING
        elif hasArmored:
            return TEAM_OBJECTS_PARTS_TYPES.SIMPLE_ARMORED
        return TEAM_OBJECTS_PARTS_TYPES.SIMPLE
        return


def getTeamObjectPartsTypes(id, partsData = None, isConsiderDead = False):
    """
    :param id: <int>
    :param partsData: <list>
    :return: <dict>
    """
    partsData = __getTeamObjectPartsData(id, partsData, isConsiderDead)
    partsInfo = dict()
    for part in partsData:
        partsInfo[part['partId']] = dict()
        partsInfo[part['partId']]['isDead'] = part['isDead']
        partsInfo[part['partId']]['type'] = getPartTypeIndex(part['isFiring'], part['isArmored'])

    return partsInfo


def getPartTypeIndex(isFiring, isArmored, isHigh):
    if isFiring:
        if isArmored:
            if isHigh:
                return TARGET_PARTS_TYPES.ARMORED_FIRING_HIGH
            return TARGET_PARTS_TYPES.ARMORED_FIRING
        elif isHigh:
            return TARGET_PARTS_TYPES.NOT_ARMORED_FIRING_HIGH
        else:
            return TARGET_PARTS_TYPES.NOT_ARMORED_FIRING
    else:
        if isArmored:
            return TARGET_PARTS_TYPES.ARMORED_STATIC
        return TARGET_PARTS_TYPES.NOT_ARMORED_STATIC


def __getTeamObjectPartsData(id, partsData = None, isConsiderDead = False):
    if partsData is None:
        en = BigWorld.entities.get(id, None)
        if en is None:
            LOG_WARNING('getTeamObjectTypesByParts - team object live the world', id)
            return
        partsData = en.getPartsTypeData(None, isConsiderDead)
    return partsData