# Embedded file name: scripts/common/BWUserTypesCommon/PlaneBattleTooltipData.py
"""PlaneBattleTooltipData definition file
"""

class PlaneBattleTooltipData(object):
    """Wrapper for FIXED_DICT with plane data for HUD tooltip
    """

    def __init__(self, globalID, ammoBelts, shellsCount, equipment, consumables, crewSkills):
        self.globalID, self.ammoBelts, self.shellsCount, self.equipment, self.consumables, self.crewSkills = (globalID,
         ammoBelts,
         shellsCount,
         equipment,
         consumables,
         crewSkills)

    def __str__(self):
        data = instance.getDictFromObj(self)
        return '<PlaneBattleTooltipData: {0}>'.format(data)


class PlaneBattleTooltipDataConverter(object):
    """PlaneBattleTooltipData converter to/from FIXED_DICT
    """

    def getDictFromObj(self, obj):
        """Convert to FIXED_DICT
        @type obj: PlaneBattleTooltipData
        @rtype: dict
        """
        return {'globalID': obj.globalID,
         'ammoBelts': obj.ammoBelts,
         'shellsCount': obj.shellsCount,
         'equipment': obj.equipment,
         'consumables': obj.consumables,
         'crewSkills': obj.crewSkills}

    def createObjFromDict(self, dict_):
        """Convert FIXED_DICT to PlaneBattleTooltipData
        @type dict_: dict
        @rtype: PlaneBattleTooltipData
        """
        return PlaneBattleTooltipData(**dict_)

    def isSameType(self, obj):
        return isinstance(obj, PlaneBattleTooltipData)


instance = PlaneBattleTooltipDataConverter()