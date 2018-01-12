# Embedded file name: scripts/client/gui/HUD2/features/battleEvent/BattleLogSource.py
from EventHelpers import CompositeSubscription, EventSubscription
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from BattleEventsHelper import createQuestCompletedEventModel, createAchievementUnlockedEventModel, createRankGainedEventModel

class BattleLogSource(DataSource):
    """
    @type _model: gui.HUD2.features.battleEvent.BattleLogModel.BattleLogModel
    @type _economics: clientEconomics.ClientEconomic.ClientEconomic
    @type _player: PlayerAvatar.PlayerAvatar
    """

    def __init__(self, features):
        self._model = features.require(Feature.GAME_MODEL).battlePoints
        self._economics = features.require(Feature.CLIENT_ECONOMICS)
        self._player = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._subscription = CompositeSubscription(EventSubscription(self._player.eAchievementUnlocked, self._onAchievementUnlocked), EventSubscription(self._player.eQuestCompleted, self._onQuestCompleted), EventSubscription(self._clientArena.onAvatarPlaneTypeRankChanged, self._onPlayerPlaneTypeRankUpdated))
        self._subscription.subscribe()
        self._economics.assignModelView(self)

    def dispose(self):
        self._subscription.unsubscribe()
        self._subscription = None
        self._economics.assignModelView(None)
        self._economics = None
        self._model = None
        self._player = None
        return

    def refresh(self, totalPoints, totalExp, newEvents):
        """
        @param totalPoints: int
        @param newEvents: list()
        look ClientEconomics.onEconomicEvents() for parameters of each event
        """
        from debug_utils import LOG_DEBUG
        LOG_DEBUG('ECOVIEW: BattleLogSource: new events {0}, bp {1}, mp {2}'.format(len(newEvents), totalPoints, totalExp))
        for event in newEvents:
            self._model.battleEvent = event

        self._model.totalPoints = totalPoints
        self._model.totalExp = totalExp

    def _onQuestCompleted(self, questID):
        e = createQuestCompletedEventModel(questID)
        self._model.battleEvent = e

    def _onAchievementUnlocked(self, achievementID):
        e = createAchievementUnlockedEventModel(achievementID)
        self._model.battleEvent = e

    def _onPlayerPlaneTypeRankUpdated(self, avatarID, planeType, oldRankID, rankID, *args, **kwargs):
        if avatarID == self._player.id and planeType == self._player.planeType:
            e = createRankGainedEventModel(rankID)
            self._model.battleEvent = e