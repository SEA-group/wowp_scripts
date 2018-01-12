# Embedded file name: scripts/client/LifetimeController.py
import GameEnvironment
from AvatarControllerBase import AvatarControllerBase
import BigWorld

class LifetimeController(AvatarControllerBase):

    def __init__(self, owner):
        super(LifetimeController, self).__init__(owner)
        self._playerAvatar.eEnterWorldEvent += self._onEnterWorld
        self._playerCallback = None
        return

    def _onEnterWorld(self):
        self._playerCallback = BigWorld.callback(0.5, self._checkLoadingTime)

    def _checkLoadingTime(self):
        arena = GameEnvironment.getClientArena()
        if arena is None:
            return
        else:
            vehiclesLoadStatusInfo = arena.vehiclesLoadStatus()
            vehiclesLoadStatus = 1.0
            if vehiclesLoadStatusInfo[1] > 0:
                vehiclesLoadStatus = float(vehiclesLoadStatusInfo[0]) / vehiclesLoadStatusInfo[1]
            spaceLoadStatus = BigWorld.spaceLoadStatus()
            loadLevel = int(50 * (spaceLoadStatus + vehiclesLoadStatus))
            if loadLevel >= 100.0:
                self._playerAvatar.onArenaLoaded()
                self._playerCallback = None
            else:
                GameEnvironment.g_instance.eLoadingProgress(loadLevel)
                self._playerCallback = BigWorld.callback(0.5, self._checkLoadingTime)
            return

    def destroy(self):
        if self._playerCallback is not None:
            BigWorld.cancelCallback(self._playerCallback)
        super(LifetimeController, self).destroy()
        return

    @property
    def _playerAvatar(self):
        """
        :return: client.PlayerAvatar.PlayerAvatar
        """
        return self._owner