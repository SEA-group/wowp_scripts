# Embedded file name: scripts/common/GunsController/AmmoBelt.py
import BigWorld
import db.DBLogic
from debug_utils import LOG_ERROR

class AmmoBelt:

    def __init__(self, gunDescription, ammoBelt, gunProfile):
        self.__ammoBelt = ammoBelt
        self.__gunDescription = gunDescription
        self.__gunProfile = gunProfile
        self.__shotData = []
        self.__index = 0
        for ammoName in db.DBLogic.g_instance.getAmmoNames(gunDescription, ammoBelt):
            self.addBullet(ammoName)

        if len(self.__shotData) == 0:
            if len(gunDescription.ammunition) > 0:
                ammoName = gunDescription.ammunition[0].name
                self.addBullet(ammoName)
                LOG_ERROR('ShootData empty fo gun id: {0}. Setup ammo: {1}'.format(gunDescription.id, ammoName))
            else:
                LOG_ERROR('Gun id: {0} does not have any ammunition!'.format(gunDescription.id))
        self.restart()

    def addBullet(self, ammoName):
        shot = db.DBLogic.g_instance.getAmmoData(ammoName)
        if shot:
            shot.bulletRenderType = -1
            self.__shotData.append(shot)
        else:
            LOG_ERROR('Unknown ammunition in gunDescription', self.__gunDescription.name, ammoName)
        return shot

    def restart(self):
        self.__index = 0

    def extract(self):
        index = self.__index
        self.__index += 1
        if self.__index >= len(self.__shotData):
            self.__index = 0
        return self.__shotData[index]

    @property
    def ammoBelt(self):
        return self.__ammoBelt

    @property
    def gunProfile(self):
        return self.__gunProfile

    @property
    def gunDescription(self):
        return self.__gunDescription

    @gunDescription.setter
    def gunDescription(self, description):
        self.__gunDescription = description

    @property
    def shotData(self):
        return self.__shotData

    @shotData.setter
    def shotData(self, data):
        self.__shotData = data

    def registerShotRender(self, nameID = None):
        for shot in self.__shotData:
            if shot.bulletRenderType == -1 or nameID is not None:
                name = str(id(shot))
                if nameID is not None:
                    name = str(nameID)
                shot.bulletRenderType = BigWorld.registerBulletType(name, (self.__gunProfile.bulletThinkness, self.__gunProfile.bulletLen, self.__gunProfile.bulletLenExpand), self.__gunProfile.bulletThicknessExpand, (self.__gunProfile.smokeSizeX, self.__gunProfile.smokeSizeY), self.__gunProfile.smokeTillingLength, self.__gunProfile.smokeRadiusScale, (shot.bulletColour, shot.smokeColour), self.__gunProfile.textureIndex, self.__gunDescription.passbySound)

        return