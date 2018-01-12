# Embedded file name: scripts/client/gui/HUD2/features/PlaneTypeObjectives/PlaneTypeObjectivesDataSource.py
import BWLogging
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from EventHelpers import EventSubscription, CompositeSubscription
logger = BWLogging.getLogger('HUD.PlaneTypeObjectives')

class PlaneTypeObjectivesDataSource(DataSource):
    """Data source for PlaneTypeObjectives model
    """

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).classTasks
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        coachMgr = self._player.coachManager
        self._subscription = CompositeSubscription(EventSubscription(coachMgr.eObjectivesChanged, self._updateCurrentObjectives), EventSubscription(coachMgr.eObjectiveProgressChanged, self._updateObjectiveProgress), EventSubscription(coachMgr.eObjectiveProgressRawValueChanged, self._updateObjectiveRawProgressValue), EventSubscription(self._player.eTacticalRespawnEnd, self._updateCurrentObjectives))
        self._subscription.subscribe()
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        else:
            self._clientArena.onNewAvatarsInfo += self._setupModel
        logger.debug('Plane type objectives data source initialized')
        return

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._updateCurrentObjectives()

    def _updateCurrentObjectives(self, *args, **kwargs):
        """Update current plane objectives.
        Should be called when objectives received from server or
        when avatar changed plane and new objectives are active now
        """
        self._model.classTasks.clean()
        coachMgr = self._player.coachManager
        for objective in coachMgr.getCurrentPlaneObjectives():
            self._model.classTasks.append(id=objective.id, title=objective.model.client.name.locale, countDescription=objective.model.client.countDescription.locale, description=objective.model.client.description.locale, progress=objective.progressCurrent, maxProgress=objective.progressMax, value=objective.progressRawValue, requiredValue=objective.getNextProgressBound())

    def _updateObjectiveProgress(self, planeType, objectiveID, progress, *args, **kwargs):
        """Handle objective progress update on eObjectiveProgressChanged event
        """
        objectiveData = self._player.coachManager.getObjectiveByID(objectiveID)
        objectiveModel = self._model.classTasks.first(lambda e: e.id.get() == objectiveID)
        if objectiveModel:
            objectiveModel.progress = progress
            objectiveModel.requiredValue = objectiveData.getNextProgressBound()

    def _updateObjectiveRawProgressValue(self, planeType, objectiveID, progressRawValue, *args, **kwargs):
        """Handle objective progress update on eObjectiveProgressChanged event
        """
        objectiveModel = self._model.classTasks.first(lambda e: e.id.get() == objectiveID)
        if objectiveModel:
            objectiveModel.value = progressRawValue

    def dispose(self):
        self._subscription.unsubscribe()
        self._subscription = None
        self._player = None
        self._clientArena = None
        self._model = None
        return