# Embedded file name: scripts/common/db/BDHUDPlaneScheme.py
from DBBaseClass import DBBaseClass
from DBHelpers import readValue, findSection

class _PartData(object):

    def __init__(self, partData):
        readValue(self, partData, 'normalState', '')
        readValue(self, partData, 'damageState', '')
        readValue(self, partData, 'critState', '')


class _GroupData(_PartData):

    def __init__(self, groupData):
        _PartData.__init__(self, groupData)
        self.dependency = []
        dependency = findSection(groupData, 'dependency')
        if dependency is not None:
            self.dependency = dependency.readStrings('part')
        return


class PlaneScheme(DBBaseClass):

    def __init__(self, typeID, fileName, data):
        DBBaseClass.__init__(self, typeID, fileName)
        readValue(self, data, 'planeScheme', '')
        self.__parts = {}
        self._readPartsData(data)
        self.__groups = {}
        self._readGroupsData(data)

    @property
    def parts(self):
        return self.__parts

    @property
    def groups(self):
        return self.__groups

    def _readPartsData(self, data):
        for partData in findSection(data, 'parts').values():
            name = partData.readString('name')
            self.__parts[name] = _PartData(partData)

    def _readGroupsData(self, data):
        groups = findSection(data, 'groups')
        if groups is not None:
            for groupData in groups.values():
                name = groupData.readString('name')
                self.__groups[name] = _GroupData(groupData)

        return