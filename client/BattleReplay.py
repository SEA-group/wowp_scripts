# Embedded file name: scripts/client/BattleReplay.py
import BigWorld
import Settings
from debug_utils import *
from Helpers.cleaner import deleteOldFiles
from BattleReplayPlayMode import startPlayback
from BattleReplayRecordMode import startRecord
REPLAY_FILE_EXTENSION = '.wowpreplay'
AUTO_RECORD_TEMP_FILENAME = 'temp'
REPLAY_TIME_MARK_ARENA_LOADED = 1
REPLAY_TIME_MARK_CLIENT_READY = 2147483648L
REPLAY_TIME_MARK_REPLAY_FINISHED = 2147483649L
REPLAY_TIME_MARK_CURRENT_TIME = 2147483650L
g_replay = None

class BattleReplay:
    isPlaying = property(lambda self: self.__replayCtrl.isPlaying)
    isControllingCamera = property(lambda self: self.__replayCtrl.isControllingCamera)
    isTimeWarpInProgress = property(lambda self: self.__replayCtrl.isTimeWarpInProgress)

    def __init__(self):
        self.__replayCtrl = BigWorld.WGReplayController(BigWorld.getMinCompatibleClientVersion())
        self.__replayDir = BigWorld.getReplaysDirectory()
        self.__mode = None
        self._replayFileName = ''
        return

    def destroy(self):
        self.__stop()
        self.__replayCtrl = None
        return

    def __stop(self):
        self.__replayCtrl.stop()
        if self.__mode:
            self.__mode.destroy()
            self.__mode = None
            self._replayFileName = ''
        return

    @property
    def replayFileName(self):
        return self._replayFileName

    def startAutoPlay(self):
        self.__stop()
        fileName = self.__replayCtrl.getAutoStartFileName()
        if fileName != '':
            self.__mode = startPlayback(self.__replayCtrl, fileName)
            self._replayFileName = fileName
        return self.__mode != None

    def startAutoRecord(self):
        self.__stop()
        enableRecord = Settings.g_instance.getReplaySettings()['saveBattleReplays']
        if enableRecord:
            self.__prepareDir(self.__replayDir)
            fileName = os.path.join(self.__replayDir, AUTO_RECORD_TEMP_FILENAME + REPLAY_FILE_EXTENSION)
            self.__mode = startRecord(self.__replayCtrl, fileName)
            self._replayFileName = fileName
        return self.__mode != None

    def setPlaybackSpeed(self, speed):
        if self.__mode:
            self.__mode.setPlaybackSpeed(speed)

    def rewind(self, time):
        if self.__mode:
            self.__mode.rewind(time)

    def getReplayTime(self):
        return self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_CURRENT_TIME)

    def getReplayLength(self):
        return self.__replayCtrl.getTimeMark(REPLAY_TIME_MARK_REPLAY_FINISHED)

    def deleteOldReplays(self):
        rem = Settings.g_instance.getReplaySettings()['removeBattleReplays']
        days = Settings.g_instance.getReplaySettings()['daysForRemoveBattleReplays']
        if rem and days:
            deleteOldFiles(self.__replayDir, days, REPLAY_FILE_EXTENSION)

    def onEnterWorld(self):
        if self.__mode:
            self.__mode.onEnterWorld()

    def onLeaveWorld(self):
        if self.__mode:
            self.__mode.onLeaveWorld()

    def onArenaLoaded(self):
        if self.__mode:
            self.__mode.onArenaLoaded()

    def onFlyKeyBoardInputAllowed(self, flag, playerAvatar):
        if self.__mode:
            self.__mode.onFlyKeyBoardInputAllowed(flag, playerAvatar)

    def onBattleResultsReceived(self, results):
        if self.__mode:
            self.__mode.onBattleResultsReceived(results)

    def onExtendedBattleResultsReceived(self, results):
        if self.__mode:
            self.__mode.onExtendedBattleResultsReceived(results)

    def notifyAxisValues(self, axis, value):
        if self.__mode:
            self.__mode.notifyAxisValues(axis, value)

    def notifyTargetEntity(self, entityId):
        pass

    def notifyZoomChange(self, zoomIdx, zoomPreset):
        pass

    def notifyCameraState(self, camState, isEnter):
        pass

    def notifySniperModeType(self, sniperModeType):
        pass

    @staticmethod
    def __prepareDir(dir):
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except:
                LOG_ERROR('BattleReplay.prepareDir: Failed to create directory for replay files')


def isPlaying():
    if g_replay is None:
        return False
    else:
        return g_replay.isPlaying


def callback(delay, function):
    t = delay
    if isPlaying():
        if g_replay.isTimeWarpInProgress:
            function()
            return None
    return BigWorld.callback(t, function)