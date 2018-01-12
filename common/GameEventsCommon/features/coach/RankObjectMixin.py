# Embedded file name: scripts/common/GameEventsCommon/features/coach/RankObjectMixin.py


class RankObjectMixin(object):
    rankID = None

    @property
    def planeType(self):
        """Compatibility field
        """
        return self.relatedPlaneType

    @property
    def localID(self):
        """Rank id unique only inside plane type ranks
        :rtype: int
        """
        return int(self.name)

    @property
    def orderIndex(self):
        """Rank order index. Higher index - higher rank
        :rtype: int
        """
        return self.client.order

    def updateRankID(self, rankID):
        raise NotImplementedError