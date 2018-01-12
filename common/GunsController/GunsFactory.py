# Embedded file name: scripts/common/GunsController/GunsFactory.py
import db.DBLogic
from debug_utils import LOG_ERROR
from consts import COMPONENT_TYPE
from Empty.EmptyGunGroup import EmptyGunGroup
from .GunGroup import WeaponGroup
from .GunsController import GunsController

def getGunInfo(weaponsInfo):
    gunInfos = {}
    for gunInfo in weaponsInfo:
        gunDescription = db.DBLogic.g_instance.getGunData(gunInfo.name)
        if gunDescription:
            gunInfos.setdefault(gunInfo.weaponGroup, []).append(gunInfo)

    return gunInfos


def generateWeaponGroups(gunInfos, planeID, pivots, ammoBeltsMap):
    groupID = 0
    for weaponGroup, infos in gunInfos.iteritems():
        gunName = infos[0].name
        gunDescription = db.DBLogic.g_instance.getGunData(gunName)
        belt = None
        if ammoBeltsMap:
            if gunName in ammoBeltsMap:
                beltID = ammoBeltsMap[gunName]
                belt = db.DBLogic.g_instance.getComponentByID(COMPONENT_TYPE.AMMOBELT, beltID)
            else:
                LOG_ERROR("Can't find belt for gun", gunName, 'in', ammoBeltsMap)
        else:
            belt = db.DBLogic.g_instance.getComponentByID(COMPONENT_TYPE.AMMOBELT, gunDescription.defaultBelt)
        yield WeaponGroup(groupID, pivots, gunDescription, infos, belt, planeID)
        groupID += 1

    return


class GunsFactory(object):

    def __init__(self, isDebug = False):
        pass

    def __createEmptyGunGroup(self, gunInfo, planeID, pivots, beltsMap):
        return [EmptyGunGroup(pivots, gunInfo, planeID, beltsMap)]

    def __createGunGroups(self, gunInfo, planeID, pivots, beltsMap):
        return list(generateWeaponGroups(gunInfo, planeID, pivots, beltsMap))

    def create(self, weaponsInfo, planeID, pivots, beltsMap):
        gunInfo = getGunInfo(weaponsInfo)
        if gunInfo:
            groups = self.__createGunGroups(gunInfo, planeID, pivots, beltsMap)
        else:
            groups = self.__createEmptyGunGroup(gunInfo, planeID, pivots, beltsMap)
        return GunsController(groups)