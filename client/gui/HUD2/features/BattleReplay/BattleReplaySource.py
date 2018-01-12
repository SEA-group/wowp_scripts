# Embedded file name: scripts/client/gui/HUD2/features/BattleReplay/BattleReplaySource.py
import BigWorld
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
import Keys
import InputMapping
import GlobalEvents
FAST_FORWARD_STEP = 20.0

class BattleReplaySource(DataSource):

    def __init__(self, features):
        self._battleReplay = features.require(Feature.BATTLE_REPLAY)
        self._playbackSpeedModifiers = (0.0, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)
        self._playbackSpeedModifiersStr = ('0', '1/8', '1/4', '1/2', '1', '2', '4', '8', '16')
        self._playbackSpeedIdx = self._playbackSpeedModifiers.index(1.0)
        self._playbackSpeedIdxSaved = self._playbackSpeedIdx
        self._model = features.require(Feature.GAME_MODEL).battleReplay
        self._model.source = self
        self._model.panelVisibility = False
        self._model.isPaused = False
        self._model.speed = self._playbackSpeedModifiersStr[self._playbackSpeedIdx]
        self._model.timeMax = self._battleReplay.getReplayLength()
        self._model.timeCurrent = self._battleReplay.getReplayTime()
        self._inited = self._battleReplay.isPlaying
        if self._inited:
            self._timer = features.require(Feature.TIMER_SERVICE)
            self._timer.eUpdate += self._onUpdate
            GlobalEvents.onMouseEvent += self._handleMouseEvent
            ctrlBtn = lambda : BigWorld.isKeyDown(Keys.KEY_LCONTROL, 0) or BigWorld.isKeyDown(Keys.KEY_RCONTROL, 0)
            shiftBtn = lambda : BigWorld.isKeyDown(Keys.KEY_LSHIFT, 0) or BigWorld.isKeyDown(Keys.KEY_RSHIFT, 0)
            cmdList = [InputMapping.CMD_REPLAY_PLAYPAUSE,
             InputMapping.CMD_REPLAY_CAMERA_SWITCH,
             InputMapping.CMD_REPLAY_SPEED_DEC,
             InputMapping.CMD_REPLAY_SPEED_INC,
             InputMapping.CMD_REPLAY_FORWARD,
             InputMapping.CMD_REPLAY_BACK,
             InputMapping.CMD_REPLAY_END]
            processor = features.require(Feature.INPUT).commandProcessor
            for cmd in cmdList:
                processor.addPredicate(cmd, lambda : not ctrlBtn() and not self._battleReplay.isTimeWarpInProgress)

            processor.addListeners(InputMapping.CMD_REPLAY_PLAYPAUSE, self.playPause)
            processor.addListeners(InputMapping.CMD_REPLAY_SPEED_DEC, self.speedDec)
            processor.addListeners(InputMapping.CMD_REPLAY_SPEED_INC, self.speedInc)
            processor.addListeners(InputMapping.CMD_REPLAY_FORWARD, self.rewindForward)
            processor.addListeners(InputMapping.CMD_REPLAY_BACK, self.rewindBack)
            processor.addListeners(InputMapping.CMD_REPLAY_BEGIN, self.rewindBegin)
            processor.addListeners(InputMapping.CMD_REPLAY_END, self.rewindEnd)
            processor.addListeners(InputMapping.CMD_REPLAY_SHOW_CURSOR, None, None, self.showPanel)
        return

    def dispose(self):
        if self._inited:
            GlobalEvents.onMouseEvent -= self._handleMouseEvent
            self._timer.eUpdate -= self._onUpdate
        self._model = None
        self._battleReplay = None
        return

    def speedInc(self):
        self._setPlaybackSpeedIdx(self._playbackSpeedIdx + 1)

    def speedDec(self):
        self._setPlaybackSpeedIdx(self._playbackSpeedIdx - 1)

    def playPause(self):
        if self._playbackSpeedIdx == 0:
            self._setPlaybackSpeedIdx(self._playbackSpeedIdxSaved)
        else:
            self._setPlaybackSpeedIdx(0)

    def rewindTo(self, time):
        self._battleReplay.rewind(time)

    def rewindBegin(self):
        self._battleReplay.rewind(0.0)

    def rewindEnd(self):
        self._battleReplay.rewind(self._battleReplay.getReplayLength())

    def rewindForward(self):
        self._battleReplay.rewind(self._battleReplay.getReplayTime() + FAST_FORWARD_STEP)

    def rewindBack(self):
        self._battleReplay.rewind(self._battleReplay.getReplayTime() - FAST_FORWARD_STEP)

    def showPanel(self, visible):
        self._model.panelVisibility = visible

    def _onUpdate(self):
        self._model.timeCurrent = self._battleReplay.getReplayTime()

    def _handleMouseEvent(self, event):
        if BigWorld.isKeyDown(Keys.KEY_LSHIFT, 0) or BigWorld.isKeyDown(Keys.KEY_RSHIFT, 0):
            if event.dz != 0:
                self.speedInc() if event.dz > 0 else self.speedDec()
                return True
        return False

    def _setPlaybackSpeedIdx(self, idx):
        lastIdx = self._playbackSpeedIdx
        if not self._battleReplay.isTimeWarpInProgress and idx != lastIdx and 0 <= idx < len(self._playbackSpeedModifiers):
            if idx == 0:
                self._playbackSpeedIdxSaved = lastIdx
                self._model.isPaused = True
            else:
                self._model.isPaused = False
            self._playbackSpeedIdx = idx
            newSpeed = self._playbackSpeedModifiers[self._playbackSpeedIdx]
            self._battleReplay.setPlaybackSpeed(newSpeed)
            self._model.speed = self._playbackSpeedModifiersStr[self._playbackSpeedIdx]
        return lastIdx