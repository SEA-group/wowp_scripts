# Embedded file name: scripts/common/db/DBBaseClass.py


class DBBaseClass(object):

    def __init__(self, typeID, fileName):
        self.typeID = typeID
        self.typeName = fileName.lower()