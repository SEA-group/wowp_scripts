# Embedded file name: scripts/client/Coach/CoachManager.py
import weakref
import BWLogging
from consts import PLANE_TYPE
from GameEvents.features.coach.model import RankModel
from Event import Event, EventManager
logger = BWLogging.getLogger(__name__)

class CoachManager(object):
    """Coach client logic
    """

    def __init__(self, player):
        self._player = weakref.proxy(player)
        self._objectives = {}
        self._objectivesByPlaneType = {pType:dict() for pType in PLANE_TYPE.ALL}
        self._eManager = EventManager()
        self.eObjectivesChanged = Event(self._eManager)
        self.eObjectiveProgressChanged = Event(self._eManager)
        self.eObjectiveProgressRawValueChanged = Event(self._eManager)
        self._requestPlaneTypeObjectives()
        logger.info('CoachManager created')

    def onPlaneTypeObjectivesReceived(self, objectives):
        """Plane type objectives received from server
        :param objectives: Objectives container. Format: {planeType: {objectiveID: progress, ...}, ...}
        """
        logger.debug('Received plane type objectives: {0}'.format(objectives))
        self._clearAllObjectives()
        for planeType, pTypeObjectives in objectives.iteritems():
            self._objectivesByPlaneType[planeType] = []
            for id_, progress in pTypeObjectives.iteritems():
                progressCurrent, progressMax, progressRaw, progressRawRanges = progress
                data = _ObjectiveData(id_, planeType, progressCurrent, progressMax, progressRaw, progressRawRanges)
                self._objectives[id_] = data
                self._objectivesByPlaneType[planeType].append(data)

            self._objectivesByPlaneType[planeType].sort(key=lambda x: x.model.client.order)

        self.eObjectivesChanged()

    def onObjectiveProgressChanged(self, objectiveID, progress):
        """Plane type objective progress updated. Is called from server through Avatar
        :param objectiveID: Objective subscriber id
        :param progress: Updated progress
        """
        logger.debug('Received plane type objective progress: {0}, {1}'.format(objectiveID, progress))
        objective = self._objectives[objectiveID]
        objective.progressCurrent = progress
        self.eObjectiveProgressChanged(objective.planeType, objectiveID, progress)

    def onObjectiveProgressRawValueChanged(self, objectiveID, progressRawValue):
        """Plane type objective raw progress value updated. Is called from server through Avatar
        :param objectiveID: Objective subscriber id
        :param progressRawValue: Updated progress
        """
        logger.debug('Received plane type objective raw progress: {0}, {1}'.format(objectiveID, progressRawValue))
        objective = self._objectives[objectiveID]
        objective.progressRawValue = progressRawValue
        self.eObjectiveProgressRawValueChanged(objective.planeType, objectiveID, progressRawValue)

    def getPlaneTypeObjectives(self, planeType):
        """Return objectives container for specified plane type
        :param planeType: One of PLANE_TYPE.*
        :rtype: list[_ObjectiveData]
        """
        return self._objectivesByPlaneType[planeType]

    def getCurrentPlaneObjectives(self):
        """Return objectives container for current plane type
        :rtype: list[_ObjectiveData]
        """
        return self.getPlaneTypeObjectives(self._player.planeType)

    def getObjectiveByID(self, id_):
        """Return objective data by it's id
        :param id_: Objective identifier
        :rtype: _ObjectiveData
        """
        return self._objectives[id_]

    def destroy(self):
        self._clearAllObjectives()
        self._eManager.clear()
        self._player = None
        logger.info('CoachManager destroyed')
        return

    def _requestPlaneTypeObjectives(self):
        self._player.base.requestPlaneTypeObjectives()

    def _clearAllObjectives(self):
        self._objectives = {}
        self._objectivesByPlaneType = {pType:dict() for pType in PLANE_TYPE.ALL}


class _ObjectiveData(object):
    """Plane type objective data holder
    """

    def __init__(self, id_, planeType, progressCurrent, progressMax, progressRawValue, progressRawRanges):
        self.id = id_
        self.planeType = planeType
        self.progressCurrent, self.progressMax = progressCurrent, progressMax
        self.progressRawValue = progressRawValue
        self.progressRawRanges = progressRawRanges
        self.model = RankModel.get(id=self.id)

    def getNextProgressBound(self):
        """Return required raw progress for next level
        :rtype: int
        """
        if self.progressCurrent < len(self.progressRawRanges):
            return self.progressRawRanges[self.progressCurrent]
        return self.progressRawRanges[-1]