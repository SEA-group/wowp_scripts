# Embedded file name: scripts/client/gui/Scaleform/GameOptions/vo/GameSettingsVO.py
from config_consts import IS_DEVELOPMENT
from gui.Scaleform.GameOptions.vo.AttitudeIndicatorSettingsVO import AttitudeIndicatorSettingsVO
from gui.Scaleform.GameOptions.vo.RadarSettingsVO import RadarSettingsVO
__author__ = 's_karchavets'
from gui.Scaleform.GameOptions.utils import ArrayIndex

class LobbySettingsVO:

    def __init__(self):
        self.isEnabled = False
        self.hangar = ArrayIndex()
        self.previewImg = []


class GameSettingsVO:

    def __init__(self):
        self.isLazy = False
        self.measurementSystem = ArrayIndex()
        self.heightMode = ArrayIndex()
        self.invitationsOnlyFromContactList = False
        self.messageCensureActive = False
        self.messageDateVisible = False
        self.messagesOnlyFromContactList = False
        self.ingnoreListVisible = False
        self.onlineListVisible = False
        self.saveBattleReplays = True
        self.removeBattleReplays = True
        self.daysForRemoveBattleReplays = 30
        self.pathSaveBattleReplays = ''
        self.pathSaveScreenshots = ''
        self.isChatEnabled = True
        self.lobbySettings = LobbySettingsVO()
        self.radarSettings = RadarSettingsVO()
        self.attitudeIndicatorSettings = AttitudeIndicatorSettingsVO()
        self.cameraEffectsEnabled = False
        self.blockWinButton = False
        self.blockAltTAB = False
        self.collisionWarningSystem = False
        self.preIntroEnabled = False
        self.hintsEnabled = True
        self.advancedSettingsEnable = IS_DEVELOPMENT