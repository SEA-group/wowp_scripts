# Embedded file name: scripts/client/BattleReplayMode.py
import BigWorld
import time
start_time = time.time()
import functools

def deferred(fn):

    @functools.wraps(fn)
    def decorated(*args, **kwargs):
        return BigWorld.callback(-1, lambda : fn(*args, **kwargs))

    return decorated


def traceFn(fn):

    @functools.wraps(fn)
    def decorated(*args, **kwargs):
        print '{0}: {1}'.format(time.time() - start_time, fn.__name__)
        return fn(*args, **kwargs)

    return decorated


class ModeInterface:
    REPLAY_TIME_MARK_ARENA_LOADED = 1
    REPLAY_TIME_MARK_CLIENT_READY = 2147483648L
    REPLAY_TIME_MARK_REPLAY_FINISHED = 2147483649L
    REPLAY_TIME_MARK_CURRENT_TIME = 2147483650L

    def rewind(self, time):
        pass

    def setPlaybackSpeed(self, speed):
        pass

    def onEnterWorld(self):
        pass

    def onLeaveWorld(self):
        pass

    def onArenaLoaded(self):
        pass

    def onFlyKeyBoardInputAllowed(self, flag, playerAvatar):
        pass

    def onBattleResultsReceived(self, results):
        pass

    def onExtendedBattleResultsReceived(self, results):
        pass

    def notifyAxisValues(self, axis, value):
        pass

    def notifyTargetEntity(self, entityId):
        pass

    def notifyZoomChange(self, zoomIdx, zoomPreset):
        pass

    def notifyCameraState(self, camState, isEnter):
        pass

    def notifySniperModeType(self, sniperModeType):
        pass