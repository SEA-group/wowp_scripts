# Embedded file name: scripts/client/gui/HUD2/features/Ranks/RanksDataSource.py
import BWLogging
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from GameEvents.features.coach.model import RankModel
logger = BWLogging.getLogger('HUD.Ranks')

class RanksDataSource(DataSource):
    """Data source for RanksModel
    """
    _PROGRESS_REQUIRED_VALUES = [4,
     7,
     9,
     11,
     13]

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).ranks
        self._initModel()
        logger.debug('Ranks data source initialized')

    def _initModel(self):
        """Fill model with ranks static data
        """
        maxOrderIndex = len(self._PROGRESS_REQUIRED_VALUES) - 1
        for rank in RankModel.getAllRanks():
            requiredProgress = self._PROGRESS_REQUIRED_VALUES[min(rank.orderIndex, maxOrderIndex)]
            self._model.ranks.append(id=rank.rankID, title=rank.title, description=rank.description, iconPath=rank.iconPath, orderIndex=rank.orderIndex, requiredProgress=requiredProgress)

    def dispose(self):
        self._model = None
        return