# Embedded file name: scripts/client/gui/HUD2/features/Spectator/SpectatorSource.py
import BigWorld
from EntityHelpers import EntityStates
from debug_utils import LOG_DEBUG
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
TAG = ' SpectatorSource ::: '

class SpectatorSource(DataSource):

    def __init__(self, features):
        LOG_DEBUG(TAG, '__init__')
        self._model = features.require(Feature.GAME_MODEL).spectator
        self._entitiesModel = features.require(Feature.GAME_MODEL).entities
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._playerAvatar.eUpdateSpectator += self.__onSpectator
        self._playerAvatar.eTacticalRespawnEnd += self._onTacticalRespawnEnd

    def __onSpectator(self, avatarID):
        LOG_DEBUG(TAG, ' onSpectator ', avatarID)
        self._model.selectedPlayerId = avatarID

    def _onTacticalRespawnEnd(self, *args, **kwargs):
        self._model.selectedPlayerId = 0

    def getAvatar(self):
        if not self._playerAvatar.inWorld:
            return None
        else:
            for avatar in self._entitiesModel.avatars:
                if avatar.id.get() != self._playerAvatar.id:
                    if avatar.teamIndex.get() == self._playerAvatar.teamIndex:
                        if avatar.health.get() > 0:
                            return avatar.id.get()

            return None

    def dispose(self):
        self._playerAvatar.eUpdateSpectator -= self.__onSpectator
        self._playerAvatar.eTacticalRespawnEnd -= self._onTacticalRespawnEnd
        self._model = None
        self._playerAvatar = None
        return