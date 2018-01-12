# Embedded file name: scripts/client/gui/HUD2/features/Achievements/AchievementsDataSource.py
import BWLogging
from EventHelpers import EventSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from Helpers.i18n import localizeAchievements
from GameEvents.features.achievements.model import AchievementModel
logger = BWLogging.getLogger('HUD.Achievements')

class AchievementsDataSource(DataSource):
    """Data source for achievements model
    """
    DIRECTION_LEFT = 'left'
    DIRECTION_RIGHT = 'right'

    def __init__(self, features):
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._model = features.require(Feature.GAME_MODEL).achievements
        self._subscription = EventSubscription(self._player.eAchievementUnlocked, self._onAchievementUnlocked)
        self._subscription.subscribe()
        for achievementID in self._player.unlockedAchievements:
            self._appendAchievement(achievementID)

    def _onAchievementUnlocked(self, achievementID, *args, **kwargs):
        self._appendAchievement(achievementID)

    def _appendAchievement(self, achievementID):
        model = AchievementModel.get(id=achievementID)
        direction = model.client.place
        if direction not in (self.DIRECTION_LEFT, self.DIRECTION_RIGHT):
            logger.error("Wrong direction '{0}' got for achievement {1}".format(direction, model))
            direction = self.DIRECTION_LEFT if achievementID < 0 else self.DIRECTION_RIGHT
        achievementsModel = self._model.achievements.first(lambda e: e.id.get() == achievementID)
        if achievementsModel is None:
            self._model.achievements.append(id=achievementID, iconPath=model.client.icon.big, title=model.localized.name, description=model.localized.descriptionWithProcessorData, direction=direction, priority=model.client.order)
        return

    def dispose(self):
        self._subscription.unsubscribe()
        self._subscription = None
        self._model = None
        self._player = None
        return