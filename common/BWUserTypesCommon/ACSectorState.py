# Embedded file name: scripts/common/BWUserTypesCommon/ACSectorState.py
"""ACSectorState definition file
"""

class ACSectorState(object):
    """Wrapper for FIXED_DICT representing ACSector state
    """

    def __init__(self, state, teamIndex, nextStateTimestamp, capturedAtTick):
        self.state = state
        self.teamIndex = teamIndex
        self.nextStateTimestamp = nextStateTimestamp
        self.capturedAtTick = capturedAtTick

    def __str__(self):
        return '<ACSectorState: state={0}, teamIndex={1}, nextStateTimestamp={2}, capturedAtTick={3}>'.format(self.state, self.teamIndex, self.nextStateTimestamp, self.capturedAtTick)


class ACSectorStateConverter(object):
    """ACSectorState converter to/from FIXED_DICT
    """

    def getDictFromObj(self, obj):
        """Convert to FIXED_DICT
        @type obj: ACSectorState
        @rtype: dict
        """
        return {'state': obj.state,
         'teamIndex': obj.teamIndex,
         'nextStateTimestamp': obj.nextStateTimestamp,
         'capturedAtTick': obj.capturedAtTick}

    def createObjFromDict(self, dict_):
        """Convert FIXED_DICT to ACSectorState
        @type dict_: dict
        @rtype: ACSectorState
        """
        return ACSectorState(**dict_)

    def isSameType(self, obj):
        return isinstance(obj, ACSectorState)


instance = ACSectorStateConverter()