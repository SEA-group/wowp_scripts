# Embedded file name: scripts/common/BWUserTypesCommon/FastCommandRequestData.py


class FastCommandRequestData(object):
    """Wrapper for FIXED_DICT with plane data for FastCommandData
    """

    def __init__(self, id, distance, distanceToNearest):
        self.id = id
        self.distance = distance
        self.distanceToNearest = distanceToNearest

    def __str__(self):
        data = instance.getDictFromObj(self)
        return '<FastCommandRequestData: {0}'.format(data)


class FastCommandRequestDataConverter(object):

    def getDictFromObj(self, obj):
        """Convert to FIXED_DICT
        @type obj: FastCommandRequestData
        @rtype: dict
        """
        return {'id': obj.id,
         'distance': obj.distance,
         'distanceToNearest': obj.distanceToNearest}

    def createObjFromDict(self, dict_):
        """Convert FIXED_DICT to CrewMemberData
        @type dict_: dict
        @rtype: CrewMemberData
        """
        return FastCommandRequestData(**dict_)

    def isSameType(self, obj):
        return isinstance(obj, FastCommandRequestData)


instance = FastCommandRequestDataConverter()