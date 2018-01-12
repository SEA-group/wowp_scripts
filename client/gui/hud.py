# Embedded file name: scripts/client/gui/hud.py
import EffectManager
from GameServiceBase import GameServiceBase
from HUDconsts import *
from debug_utils import *
import Cursor
import InputMapping
from HudElements.ForestallingPoint import ForestallingPoint
import _awards_data
import Settings
import GUI

class HUD(GameServiceBase):

    def __init__(self):
        super(HUD, self).__init__()
        self.__denyHideCursor = False
        self.__offsetMtx = GUI.OffsetMp()
        self.__forestallingPoint = ForestallingPoint(self.__offsetMtx)
        self.getActiveQuest()

    @property
    def forestallingPoint(self):
        return self.__forestallingPoint

    def afterLinking(self):
        super(HUD, self).afterLinking()

    def destroy(self):
        self.__forestallingPoint.destroy()
        self.__forestallingPoint = None
        super(self.__class__, self).destroy()
        return

    def restartHUD_QA(self):
        self.doLeaveWorld()
        self.destroy()
        self.__init__()
        self.afterLinking()

    def doLeaveWorld(self):
        self.__entityList = dict()
        GameServiceBase.doLeaveWorld(self)

    def onDenyCursorHideChanged(self, deny):
        self.__denyHideCursor = deny

    def onVisibilityCursor(self, visibleFlag):
        if not visibleFlag and self.__denyHideCursor:
            return
        Cursor.forceShowCursor(visibleFlag)
        entity = BigWorld.player()
        entity.setFlyMouseInputAllowed(not visibleFlag)

    def __visibilityMouseCursor(self, fired):
        LOG_DEBUG('Mouse cursor visibility %r' % fired)
        if fired:
            BigWorld.player().onFireChange(0)
        self.onVisibilityCursor(fired)

    def addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_SHOW_CURSOR, None, None, lambda fired: self.__visibilityMouseCursor(fired))
        processor.addListeners(InputMapping.CMD_REPLAY_SHOW_CURSOR, None, None, lambda fired: self.__visibilityMouseCursor(fired))
        processor.addListeners(InputMapping.CMD_CHAT_ON_OFF, None, None, lambda fired: Settings.g_instance.setGameUIValue('isChatEnabled', not Settings.g_instance.getGameUI()['isChatEnabled']))
        return

    @property
    def offsetMtx(self):
        return self.__offsetMtx

    def getActiveQuest(self):
        LOG_ERROR('getActiveQuest')

    def reportGainAward(self, awardInfo):
        LOG_ERROR('reportGainAward')