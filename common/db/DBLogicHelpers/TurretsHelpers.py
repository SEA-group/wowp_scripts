# Embedded file name: scripts/common/db/DBLogicHelpers/TurretsHelpers.py
from consts import UPGRADE_TYPE
from _airplanesConfigurations_db import getAirplaneConfiguration

def findSlotAndTurretIndexByTurretName(aircraftData, turretName):
    for slotIndex, slot in enumerate(aircraftData.airplane.flightModel.turretSlot):
        for turretIndex, turret in enumerate(slot.turret):
            if turret.name == turretName:
                return (slotIndex, turretIndex)

    return (-1, -1)


def findTurretSlotByTurretName(aircraftData, turretName):
    slotIndex, turretIndex = findSlotAndTurretIndexByTurretName(aircraftData, turretName)
    if slotIndex == -1 or turretIndex == -1:
        return None
    else:
        return aircraftData.airplane.flightModel.turretSlot[slotIndex]


def findAircraftTurretSettingsByTurretName(aircraftData, turretName):
    slotIndex, turretIndex = findSlotAndTurretIndexByTurretName(aircraftData, turretName)
    if slotIndex == -1 or turretIndex == -1:
        return None
    else:
        return aircraftData.airplane.flightModel.turretSlot[slotIndex].turret[turretIndex]


def findAircraftTurretsSettingsByGlobalID(db, globalID):
    """
    @type db: db.DBLogic.db
    """
    modules = getAirplaneConfiguration(globalID).modules
    aircraftData = db.getAircraftDataByGlobalID(globalID)
    for moduleName in modules:
        turretSettings = findAircraftTurretSettingsByTurretName(aircraftData, moduleName)
        if turretSettings is not None:
            yield turretSettings

    return


def findTurretNamesByGlobalID(db, globalID):
    """
    @type db: db.DBLogic.db
    """
    return db.findUpgradeNamesByGlobalIDAndType(globalID, UPGRADE_TYPE.TURRET)