# Embedded file name: scripts/client/OrientationMarkers/OrientationMarkersDebug.py
from AvatarControllerBase import AvatarControllerBase
import GameEnvironment
from consts import BATTLE_MODE
from OrientationMarkersDebugInterface import OrientationMarkersDebugInterface
from OrientationMarkersSettings import getDistancesForPlayer, CIRCLE_RADIUS

class OrientationMarkersDebug(AvatarControllerBase, OrientationMarkersDebugInterface):
    """
    @type _interface: OrientationMarkersDebugInterface
    """

    def __init__(self, owner):
        super(OrientationMarkersDebug, self).__init__(owner)
        self._interface = None
        return

    def _init(self, interface):
        self._interface = interface
        self._battleMode = BATTLE_MODE.COMBAT_MODE
        self._owner.eTacticalRespawnEnd += self._onTacticalRespawn
        GameEnvironment.getInput().eBattleModeChange += self._onBattleModeChange
        self._updateCategoryDistances()
        self._updateCircleRadius()

    def _onBattleModeChange(self, bState):
        if self._battleMode == BATTLE_MODE.GUNNER_MODE or bState == BATTLE_MODE.GUNNER_MODE:
            self._battleMode = bState
            self._updateCategoryDistances()

    def _destroy(self):
        self._interface = None
        self._owner.eTacticalRespawnEnd -= self._onTacticalRespawn
        GameEnvironment.getInput().eBattleModeChange -= self._onBattleModeChange
        return

    def _updateCircleRadius(self):
        self._interface.setCircleRadius(CIRCLE_RADIUS)

    def _updateCategoryDistances(self):
        categoryDistances = getDistancesForPlayer(self._owner, self._battleMode)
        names, distances = zip(*categoryDistances)
        self._interface.setCategoryDistances(list(names) + ['Very Far'], list(distances))

    def _onTacticalRespawn(self, *args, **kwargs):
        self._updateCategoryDistances()