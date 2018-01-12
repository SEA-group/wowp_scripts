# Embedded file name: scripts/client/modelManipulator/PartAnimatorControllers/BombHatchAnimator.py
import BigWorld
import db.DBLogic
from consts import ANIMATION_TRIGGERS
from _airplanesConfigurations_db import getAirplaneConfiguration

class BombHatchAnimator(object):

    class Sorces:
        Cam = 0
        Key = 1

    class State:
        Close = 0
        Open = 1

    def __init__(self, owner):
        self._owner = owner
        self._timer = -1
        self._timer_callback = None
        self._cam_close_callback = None
        self._state = {BombHatchAnimator.Sorces.Cam: BombHatchAnimator.State.Close,
         BombHatchAnimator.Sorces.Key: BombHatchAnimator.State.Close}
        return

    def dispose(self):
        self._owner = None
        if self._timer_callback is not None:
            BigWorld.cancelCallback(self._timer_callback)
            self._timer_callback = None
        if self._cam_close_callback is not None:
            BigWorld.cancelCallback(self._cam_close_callback)
            self._cam_close_callback = None
        return

    def restart(self):
        self._state = {BombHatchAnimator.Sorces.Cam: BombHatchAnimator.State.Close,
         BombHatchAnimator.Sorces.Key: BombHatchAnimator.State.Close}
        self.__try_animate_bomb_hatch()

    def __get_bomb_hatch_close_offset(self):
        ac = getAirplaneConfiguration(self._owner.globalID)
        obj_db_data = db.DBLogic.g_instance.getAircraftData(ac.planeID).airplane
        return getattr(obj_db_data.visualSettings, 'bombHatchCloseOffset', 1)

    def __try_animate_bomb_hatch(self):
        is_open = bool(sum(self._state.values()))
        self._owner.controllers['modelManipulator'].triggerAnimation(ANIMATION_TRIGGERS.BOMB_HATCH_OPEN, is_open)

    def __close_on_live_state(self):
        self._cam_close_callback = None
        self._state[BombHatchAnimator.Sorces.Cam] = BombHatchAnimator.State.Close
        self.__try_animate_bomb_hatch()
        return

    def __start_launch_timer(self, d_time):
        self._state[BombHatchAnimator.Sorces.Key] = BombHatchAnimator.State.Open
        self.__try_animate_bomb_hatch()
        if self._timer_callback is not None:
            BigWorld.cancelCallback(self._timer_callback)
        self._timer_callback = BigWorld.callback(d_time, self.__stop_launch_timer)
        return

    def __stop_launch_timer(self):
        self._timer_callback = None
        self._state[BombHatchAnimator.Sorces.Key] = BombHatchAnimator.State.Close
        self.__try_animate_bomb_hatch()
        return

    def launchBombsHatchAnimation(self, launch_delta_time):
        bomb_hatch_close_offset = self.__get_bomb_hatch_close_offset()
        self.__start_launch_timer(launch_delta_time + bomb_hatch_close_offset)

    def onBombState(self, isBombState):
        self._state[BombHatchAnimator.Sorces.Cam] = BombHatchAnimator.State.Open if isBombState else BombHatchAnimator.State.Close
        if self._cam_close_callback is not None:
            BigWorld.cancelCallback(self._cam_close_callback)
        if self._state[BombHatchAnimator.Sorces.Cam] == BombHatchAnimator.State.Open:
            self.__try_animate_bomb_hatch()
        else:
            self._cam_close_callback = BigWorld.callback(self.__get_bomb_hatch_close_offset(), self.__close_on_live_state)
        return