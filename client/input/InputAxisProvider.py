# Embedded file name: scripts/client/input/InputAxisProvider.py
import BigWorld
import GameEnvironment
from ICMultiUpdate import ICMultiUpdate
import InputMapping
from consts import *
from Event import Event
from debug_utils import LOG_INFO
from input.Profile.MouseProfile import MouseProfile
from input.Profile.GamepadProfile import GamepadProfile
from input.Profile.JoystickProfile import JoystickProfile
from input.Profile.KeyboarProfile import KeyboardProfile
from time import time
from clientConsts import NOT_CONTROLLED_MOD, AXIS_MUTE_MOD

class InputAxisProvider(object):
    """
    InputAxisProvider aggregates a profile that allows switching between profiles and storage of
    global states - which must be retained on reboot profile
    """

    def __init__(self):
        self.__inputSystemState = None
        self.__suspended = False
        self.__profile = None
        self.__notControlledByUser = NOT_CONTROLLED_MOD.CONTROLLED
        self.__timeSNTP = 0
        self.__currentBattleMode = BATTLE_MODE.COMBAT_MODE
        self.__commandProcessor = None
        self.__lastDirection = None
        self.__muted = AXIS_MUTE_MOD.NO_MUTE
        InputMapping.g_instance.onProfileLoaded += self.__loadSubSystems
        BigWorld.player().eRestartInput += self.restart
        return

    def init(self, commandProcessor):
        self.__commandProcessor = commandProcessor
        self.__commandProcessor.addListeners(InputMapping.CMD_AUTOPILOT, lambda : self.notControlledByUser(True, NOT_CONTROLLED_MOD.PLANE_ALIGN), lambda : self.notControlledByUser(False, NOT_CONTROLLED_MOD.PLANE_ALIGN))
        self.__loadSubSystems()

    def dispose(self):
        if self.__profile:
            self.__profile.dispose()
            self.__profile = None
        InputMapping.g_instance.onProfileLoaded -= self.__loadSubSystems
        BigWorld.player().eRestartInput -= self.restart
        if self.__commandProcessor:
            self.__commandProcessor.removeListeners(InputMapping.CMD_AUTOPILOT, lambda : self.notControlledByUser(True, NOT_CONTROLLED_MOD.PLANE_ALIGN), lambda : self.notControlledByUser(False, NOT_CONTROLLED_MOD.PLANE_ALIGN))
        return

    def setBattleState(self, state):
        self.__currentBattleMode = state
        GameEnvironment.getInput().eBattleModeChange(self.__currentBattleMode)

    def __sendInputSystemState(self, state):
        if state != self.__inputSystemState:
            self.__inputSystemState = state
            BigWorld.player().cell.sendInputSystemState(state)
            self.request()

    def request(self):
        self.__timeSNTP = time()
        BigWorld.player().cell.inputProviderRequest()

    def response(self, T2, T3):
        T4 = time()
        self.__timeSNTP = 0.5 * (T2 - self.__timeSNTP + (T3 - T4))

    @property
    def serverTime(self):
        return BigWorld.serverTime() - BigWorld.player().filter.latency

    def __setNewProfile(self, inputState):
        GameEnvironment.getInput().eInputProfileChange(inputState)
        if self.__profile:
            self.__profile.removeCommandListeners(self.__commandProcessor)
            self.__profile.dispose()
            self.__lastDirection = None
        if inputState == INPUT_SYSTEM_STATE.MOUSE:
            self.__profile = MouseProfile(self, self.__notControlledByUser, self.__currentBattleMode)
        elif inputState == INPUT_SYSTEM_STATE.KEYBOARD:
            self.__profile = KeyboardProfile(self, self.__notControlledByUser)
        elif inputState == INPUT_SYSTEM_STATE.JOYSTICK:
            self.__profile = JoystickProfile(self, self.__notControlledByUser)
        elif inputState == INPUT_SYSTEM_STATE.GAMEPAD_DIRECT_CONTROL:
            self.__profile = GamepadProfile(self, self.__notControlledByUser, self.__currentBattleMode)
        else:
            LOG_INFO('::__setNewProfile: input State [%s] ignored' % (inputState,))
        self.__profile.addCommandListeners(self.__commandProcessor)
        return

    def resetKeyboardInput(self, sousce):
        if self.__profile:
            self.__profile.resetKeyboardInput(sousce)

    def __loadSubSystems(self):
        inputState = InputMapping.g_instance.currentProfileType
        if inputState:
            self.__sendInputSystemState(inputState)
            self.__setNewProfile(inputState)

    def restart(self):
        if self.__profile:
            self.__profile.restart()
            self.__lastDirection = None
        return

    def processMouseEvent(self, event):
        if self.__profile:
            self.__profile.processMouseEvent(event)

    def processJoystickEvent(self, event):
        if self.__profile:
            self.__profile.processJoystickEvent(event)

    def getCurrentForce(self):
        if self.__profile:
            return self.__profile.getCurrentForce()
        else:
            return 0

    def notControlledByUser(self, value, mod):
        if value != bool(self.__notControlledByUser & mod):
            self.__notControlledByUser = self.__notControlledByUser ^ mod
            if mod is not NOT_CONTROLLED_MOD.AUTOPILOT:
                switch_NCBUStrategy = self.__notControlledByUser & NOT_CONTROLLED_MOD.NCBU_STRATEGY_ACTIVATE
                BigWorld.player().cell.sendNotControlledByUser(bool(switch_NCBUStrategy))
            if self.__profile:
                self.__profile.notControlledByUser(self.__notControlledByUser)

    @property
    def controlledByUser(self):
        return not self.__notControlledByUser

    @property
    def currentBattleMode(self):
        return self.__currentBattleMode

    @property
    def currentProfileType(self):
        return self.__inputSystemState

    @property
    def battleDirection(self):
        if self.__lastDirection is None:
            return BigWorld.player().getRotation().getAxisZ()
        else:
            return self.__lastDirection

    @battleDirection.setter
    def battleDirection(self, v):
        self.__lastDirection = v

    def mute(self, value, mod):
        if value != bool(self.__muted & mod):
            self.__muted = self.__muted ^ mod
            if self.__profile:
                self.__profile.mute(self.__muted)