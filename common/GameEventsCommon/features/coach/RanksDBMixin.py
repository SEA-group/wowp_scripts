# Embedded file name: scripts/common/GameEventsCommon/features/coach/RanksDBMixin.py
import collections
import BWLogging
from consts import PLANE_TYPE
logger = BWLogging.getLogger('DB.Ranks')

class RanksDBMixin(object):
    EMPTY_RANK_ID = -1
    _RANK_EPS_GROUP = 'rank.level'
    _EMPTY_RANK_EPS_GROUP = 'rank.empty'
    _FE_EMPTY_RANK_ID = 0

    def __init__(self):
        self._ranks = {}
        self._ranksByPlaneType = collections.defaultdict(dict)

    def loadData(self):
        """Load ranks data from XML
        """
        if self._ranks:
            logger.warning('Plane type ranks already loaded, existing data will be overwritten')
            self._ranks = {}
            self._ranksByPlaneType = collections.defaultdict(dict)
        self._appendEmptyRankData()
        rankModels = list(self.filter(group=self._RANK_EPS_GROUP))
        rankModels.sort(key=lambda x: (x.relatedPlaneType, x.name))
        for id_, model in enumerate(rankModels, start=1):
            model.updateRankID(id_)
            self._ranks[id_] = model.id
            self._ranksByPlaneType[model.relatedPlaneType][model.localID] = model.id
            logger.debug('Loaded rank: id = {0}, local id = {1}, plane type = {2}'.format(id_, model.localID, PLANE_TYPE.getName(model.relatedPlaneType)))

        logger.info('Plane type ranks loaded: total count = {0}'.format(len(self._ranks)))

    @property
    def initialRankID(self):
        """Initial rank identifier. 
        This rank will be assigned as default rank for all players on arena start
        """
        return self.EMPTY_RANK_ID

    def getRankByID(self, id_):
        """Return rank by id
        :param id_: Unique rank id
        :rtype: PlaneTypeRankModel
        """
        return self.get(id=self._ranks[id_])

    def getRankByPlaneType(self, planeType, localID):
        """Return rank by planeType and local rank id
        :param planeType: One of PLANE_TYPE.*
        :param localID: EPS subscriber <name> value
        :rtype: PlaneTypeRankModel
        """
        return self.get(id=self._ranksByPlaneType[planeType][localID])

    def getAllRanks(self):
        """Return iterator over all ranks loaded from XML
        :rtype: collections.Iterable[PlaneTypeRankModel]
        """
        return (self.get(id=id_) for id_ in self._ranks.itervalues())

    def _appendEmptyRankData(self):
        """Add empty rank data to ranks storage
        """
        subscriber = self.get(group=self._EMPTY_RANK_EPS_GROUP)
        subscriber.updateRankID(self._FE_EMPTY_RANK_ID)
        self._ranks[self._FE_EMPTY_RANK_ID] = subscriber.id