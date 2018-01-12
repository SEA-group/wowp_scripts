# Embedded file name: scripts/common/GunsController/GunsController.py
from consts import GUN_OVERHEATING_TEMPERATURE, GUN_STATE, IS_CELLAPP, SINGLE_SHOT_RPM_THRESHOLD
import Event
from WeaponsHelpers import isGunGroupShooting

class GunsController:

    def __init__(self, weaponGroups):
        self.__eventManager = Event.EventManager()
        if IS_CELLAPP:
            self.eTotalRecoilGunsThrust = Event.Event(self.__eventManager)
            self.__wasOverHeated = 0
        self.eGunOverHeat = Event.Event(self.__eventManager)
        self.__ammoStartWeight = 0
        self.__totalRecoilThrust = 0.0
        self.__weaponGroups = weaponGroups
        for group in self.__weaponGroups:
            if IS_CELLAPP:
                group.eGunOverHeat += self.__onGroupOverHeat
            else:
                group.eGunOverHeat += self.__onGroupOverHeatClient

        self.__weaponGroups.sort(key=lambda group: group.gunDescription.RPM)
        self.__weaponGroups.sort(key=lambda group: group.gunDescription.caliber, reverse=True)
        self.singleShotMask = 0
        for singleShotBit, group in enumerate(self.__weaponGroups):
            group.singleShotBit = 1 << singleShotBit if group.gunDescription.RPM <= SINGLE_SHOT_RPM_THRESHOLD else 0
            self.singleShotMask |= group.singleShotBit

    def destroy(self):
        for group in self.__weaponGroups:
            group.destroy()

        self.__eventManager.clear()

    def restart(self):
        for group in self.__weaponGroups:
            group.restart()

    def reload(self, groups):
        for bit, group in enumerate(self.__weaponGroups):
            if groups & 1 << bit:
                group.reload()

    def shoot(self, armamentStates):

        def generateList():
            for bit, group in enumerate(self.__weaponGroups):
                if armamentStates & 1 << bit and group.isReady():
                    group.shootInfo = group.ammoBelt.extract()
                    yield group

        return list(generateList())

    def cellUpdate(self, dt, fireFlags):
        armaments = 0
        for bit, group in enumerate(self.__weaponGroups):
            if isGunGroupShooting(fireFlags, bit):
                armaments |= 1 << bit

        self.commonUpdate(dt, armaments)
        self.eTotalRecoilGunsThrust(self.__totalRecoilThrust)
        return armaments

    def commonUpdate(self, dt, armaments):
        self.__totalRecoilThrust = 0.0
        for bit, group in enumerate(self.__weaponGroups):
            isGroupFiring = armaments & 1 << bit != 0
            group.update(dt, isGroupFiring)
            self.__totalRecoilThrust += group.recoilThrust

    def backup(self):
        return {'gunsBackup': [ group.backup() for group in self.__weaponGroups ],
         'wasOverheated': not self.__wasOverHeated}

    def restoreFromBackup(self, bp):
        for i, groupData in enumerate(bp['gunsBackup']):
            self.__weaponGroups[i].restoreFromBackup(groupData)

        self.__wasOverHeated = bp['wasOverheated']

    def calculateMiddleBulletSpeed(self):
        if self.__weaponGroups:
            return sum((group.gunDescription.bulletSpeed for group in self.__weaponGroups)) / len(self.__weaponGroups)
        return 1000

    def calculateBulletSpeedForMostLargeCaliberGroup(self):
        speed, caliber, dps = (0.0, 0.0, 0.0)
        for weaponGroup in self.__weaponGroups:
            if weaponGroup.gunDescription.caliber > caliber or 0.0 < caliber == weaponGroup.gunDescription.caliber and weaponGroup.dps > dps:
                caliber = weaponGroup.gunDescription.caliber
                speed = weaponGroup.gunDescription.bulletSpeed
                dps = weaponGroup.dps

        return speed

    def getGunGroupsInitialInfo(self):
        """return bullet counters for all group of guns"""

        def generateData():
            for i, group in enumerate(self.__weaponGroups):
                uiGroupID = i + 1
                yield (uiGroupID, {'initialCount': GUN_OVERHEATING_TEMPERATURE,
                  'description': group.gunDescription,
                  'isMain': not i,
                  'shellID': -1,
                  'weaponName': group.gunDescription.name,
                  'ammoBeltType': group.ammoBelt.ammoBelt.beltType,
                  'objCount': len(group.guns),
                  'id': group.ammoBelt.ammoBelt.id})

        return dict(generateData())

    def getGunGroupCounters(self):
        """return bullet counters for all group of guns"""

        def generateData():
            for i, group in enumerate(self.__weaponGroups):
                uiGroupID = i + 1
                yield (uiGroupID, int(min(group.temperature, GUN_OVERHEATING_TEMPERATURE)))

        return dict(generateData())

    def getGunGroupsStates(self):

        def generateData():
            for i, group in enumerate(self.__weaponGroups):
                uiGroupID = i + 1
                yield (uiGroupID, GUN_STATE.OVERHEATED if group.temperature == GUN_OVERHEATING_TEMPERATURE else GUN_STATE.READY)

        return dict(generateData())

    def getWeaponGroupsMaxAttackRange(self):
        """return - maxFlyDist by group"""
        if self.__weaponGroups:
            return max((group.gunDescription.bulletFlyDist for group in self.__weaponGroups))
        return 0

    def getSyncData(self):
        """This function used on cell side to sync bullets with client"""
        syncData = []
        for group in self.__weaponGroups:
            syncData.append(group.temperature)
            syncData.append(group.getReloadTimer())

        return syncData

    def syncGuns(self, data):
        for i, group in enumerate(self.__weaponGroups):
            temperature, reloadTimer = data[2 * i], data[2 * i + 1]
            group.sync(temperature, reloadTimer)

    def __onGroupOverHeat(self):
        self.__wasOverHeated += 1
        self.eGunOverHeat()

    def __onGroupOverHeatClient(self):
        self.eGunOverHeat()

    @property
    def wasOverHeated(self):
        return self.__wasOverHeated

    @property
    def groups(self):
        return self.__weaponGroups

    def getDps(self):
        if self.__weaponGroups:
            return sum((group.dps for group in self.__weaponGroups))
        return 0

    def getFullDPS(self):
        if self.__weaponGroups:
            return sum((group.fullDPS for group in self.__weaponGroups))
        return 0

    def damagePerPass(self, stallSpeed):
        if self.__weaponGroups:
            return sum((group.fullDPS * group.gunDescription.bulletFlyDist / stallSpeed for group in self.__weaponGroups))
        return 0

    def getMass(self):
        if self.__weaponGroups:
            return sum((group.gunDescription.mass * group.size for group in self.__weaponGroups))
        return 0