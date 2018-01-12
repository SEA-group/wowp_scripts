# Embedded file name: scripts/client/BattleReplayPlayMode.py
import BigWorld
from debug_utils import *
from BattleReplayMode import ModeInterface, deferred
import GameEnvironment
from CameraStates import CameraState
from Event import Event, EventManager
from clientConsts import SPECTATOR_TYPE
import BWLogging
logger = BWLogging.getLogger('BattleReplay')

def patchPickle():
    import cPickle
    import SafeUnpickler
    unpickler = SafeUnpickler.SafeUnpickler()
    cPickle.loads = unpickler.loads
    import wgPickle
    reload(wgPickle)
    logger.trace('patchPickle')


def startPlayback(replayCtrl, fileName):
    mode = PlayMode(replayCtrl)
    if not replayCtrl.startPlayback(fileName):
        logger.error('startPlayback failed {0}'.format(fileName))
        mode.destroy()
        return None
    else:
        logger.info('startPlayback {0}'.format(fileName))
        patchPickle()
        return mode


class PlayMode(ModeInterface):
    isTimeWarpInProgress = property(lambda self: self.__replayCtrl.isTimeWarpInProgress)
    isClientReady = property(lambda self: self.__replayCtrl.isClientReady)
    replayTime = property(lambda self: self.__replayCtrl.getTimeMark(self.REPLAY_TIME_MARK_CURRENT_TIME))
    replayTimeArenaLoaded = property(lambda self: self.__replayCtrl.getTimeMark(self.REPLAY_TIME_MARK_ARENA_LOADED))

    def isNormalSpeed(self):
        return abs(self.__replayCtrl.playbackSpeed - 1.0) <= 0.0001

    def __init__(self, replayCtrl):
        self.__replayCtrl = replayCtrl
        self.__replayCtrl.timeMarkerCallback = self._timeMarkerCallback
        self.__replayCtrl.replayFinishedCallback = self._replayFinishedCallback
        self.__replayCtrl.warpFinishedCallback = self._warpFinishedCallback
        self.__replayCtrl.applyInputAxisCallback = self._applyInputAxisCallback
        em = self.__eventMgr = EventManager()
        self.eFinish = Event(em)

    def destroy(self):
        self.__replayCtrl.applyInputAxisCallback = None
        self.__replayCtrl.replayFinishedCallback = None
        self.__replayCtrl.timeMarkerCallback = None
        self.__replayCtrl.warpFinishedCallback = None
        self.__replayCtrl = None
        return

    def setPlaybackSpeed(self, speed):
        if not self.isTimeWarpInProgress:
            logger.info('setPlaybackSpeed {0}'.format(speed))
            self.__replayCtrl.playbackSpeed = speed
            self._soundMute(not self.isNormalSpeed())

    @deferred
    def rewind(self, time):
        if not self.isTimeWarpInProgress:
            time = max(float(time), self.replayTimeArenaLoaded)
            if self.__replayCtrl.beginTimeWarp(time):
                logger.info('rewind to {0}'.format(time))
                self._soundMute(True)
            else:
                logger.error('rewind to {0} failed'.format(time))

    def onArenaLoaded(self):
        self.__replayCtrl.onSyncPoint1()
        self.__replayCtrl.onClientReady()
        if not self.isTimeWarpInProgress and self.replayTime < self.replayTimeArenaLoaded:
            logger.trace('onArenaLoaded')
            self.rewind(self.replayTimeArenaLoaded)

    def onLeaveWorld(self):
        logger.trace('onLeaveWorld')

    def _timeMarkerCallback(self, markType):
        if markType == self.REPLAY_TIME_MARK_ARENA_LOADED:
            logger.trace('onArenaLoaded callback')
            setFreeCamera()
            self.__replayCtrl.isControllingCamera = False

    def _replayFinishedCallback(self):
        logger.trace('onReplayFinished callback')
        BigWorld.quit()

    def _warpFinishedCallback(self):
        logger.trace('onWarpFinished callback')
        self._soundMute(not self.isNormalSpeed())

    def _applyInputAxisCallback(self, axis, value):
        BigWorld.player().applyInputAxis(axis, value, replayMode=True)

    def _soundMute(self, mute):
        from audio import GameSound
        GameSound().replayMute(mute)


def setSpectatorCamera():
    cam = GameEnvironment.getCamera()
    cam.setState(CameraState.DynamicSpectator, SPECTATOR_TYPE.CINEMATIC, replayMode=True)
    cam.getStateObject().updateTarget(BigWorld.player().id)


def cycleSpectatorMode():
    cam = GameEnvironment.getCamera()
    if cam.getState() != CameraState.DynamicSpectator:
        cam.setState(CameraState.DynamicSpectator, SPECTATOR_TYPE.CINEMATIC, replayMode=True)
        cam.getStateObject().updateTarget(BigWorld.player().id)
    cam.getStateObject().cycleSpectatorType()


def setFreeCamera():
    cam = GameEnvironment.getCamera()
    cam.setState(CameraState.ReplayFree, replayMode=True)