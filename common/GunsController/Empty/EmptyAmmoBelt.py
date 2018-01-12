# Embedded file name: scripts/common/GunsController/Empty/EmptyAmmoBelt.py


class EmptyAmmoBelt(object):

    class DummyAmmo(object):

        def __init__(self):
            pass

        @property
        def id(self):
            return -1

        @property
        def beltType(self):
            return 'empty'

    def __init__(self, description, gunProfile):
        self.__gunDescription = description
        self.__gunProfile = gunProfile
        self.__shotData = []

    def addBullet(self, ammoName):
        return None

    def restart(self):
        pass

    def extract(self):
        return None

    @property
    def ammoBelt(self):
        return EmptyAmmoBelt.DummyAmmo()

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
        pass