# Embedded file name: scripts/client/audio/SoundObjects/UI.py
from WwiseGameObject import WwiseGameObject, GS
import BigWorld
import db.DBLogic
import WWISE_
import GlobalEvents
from gui.HUDconsts import HUD_MODULE_DESTROYED
from consts import OBJ_STATES
from EntityHelpers import EntityStates
from audio.AKConsts import SOUND_UI_EVENTS

class UI(WwiseGameObject):

    def __init__(self):
        self.__bpTime = {}
        self.__battleResultsPlayed = True
        WwiseGameObject.__init__(self, 'UI')
        self.__update1secCallBack = None
        self.__registerGlobalEvents()
        return

    def __registerGlobalEvents(self):
        GlobalEvents.onMovieLoaded += self.__onMovieLoaded

    def __onMovieLoaded(self, movieName, movieInstance):
        from gui.Scaleform import main_interfaces
        if movieName == main_interfaces.GUI_SCREEN_UI:
            self.update1sec()
            BigWorld.player().eLeaveWorldEvent += self.__onPlayerLeaveWorld
        from gui.Scaleform.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.eOnVehicleLoaded += self.__onVehicleLoaded

    def onPartStateChanging(self, data):
        if BigWorld.player().state != EntityStates.GAME:
            return
        if data.logicalState != OBJ_STATES.DESTROYED:
            self.postEvent('Play_crit_red_fixed')
        elif data.partTypeData.componentType == 'Pilot' or data.partTypeData.componentType == 'Gunner1':
            self.postEvent('Play_crit_pilot')
        else:
            self.postEvent('Play_crit_red_start')

    def update1sec(self):
        serverTime = BigWorld.serverTime()
        arenaStartTime = BigWorld.player().arenaStartTime
        if arenaStartTime > 0:
            curTime = int(round(arenaStartTime - serverTime))
            if curTime > 0:
                WWISE_.postGlobalEvent(SOUND_UI_EVENTS.TIMER)
        self.__update1secCallBack = BigWorld.callback(1.0, self.update1sec)

    def __clear1secCallaback(self):
        if self.__update1secCallBack:
            BigWorld.cancelCallback(self.__update1secCallBack)
            self.__update1secCallBack = None
        return

    def __onPlayerLeaveWorld(self):
        self.__clear1secCallaback()
        self.__clearBattleEvents()

    def onBattleStart(self):
        self.__battleResultsPlayed = False
        WWISE_.postGlobalEvent(SOUND_UI_EVENTS.TIMER_LAST)
        self.__clear1secCallaback()
        self.__registerBattleEvents()

    def __registerBattleEvents(self):
        player = BigWorld.player()
        player.eReportNoShell += self.__reportNoShell
        player.eRespawn += self.__onRespawn
        player.eUpdateSpectator += self.__onSpectator

    def __clearBattleEvents(self):
        player = BigWorld.player()
        player.eReportNoShell -= self.__reportNoShell
        player.eRespawn -= self.__onRespawn
        player.eUpdateSpectator -= self.__onSpectator

    def onVictimInformAboutCrit(self, partID, victimID, partState):
        if victimID != BigWorld.player().id and partState == HUD_MODULE_DESTROYED:
            self.postEvent('Play_crit_red_NPC')

    def __reportNoShell(self, shellID, result):
        WWISE_.postGlobalEvent(SOUND_UI_EVENTS.UNABLE_ROCKET_BOMB)

    def onReceiveMarkerMessage(self, senderID, posX, posZ, messageStringID, fromQueue):
        WWISE_.postGlobalEvent(SOUND_UI_EVENTS.MINIMAP_CLICK)

    def __onRespawn(self):
        if BigWorld.player().state == EntityStates.WAIT_START:
            WWISE_.postGlobalEvent(SOUND_UI_EVENTS.RESPAWN)

    def __onSpectator(self, avatarID):
        WWISE_.postGlobalEvent(SOUND_UI_EVENTS.CAMERA_SWITCH)

    def onPlaneBlocked(self, aircraftID):
        self.__bpTime[aircraftID] = BigWorld.time()

    def onPlaneUnlocked(self, aircraftID):
        if aircraftID not in self.__bpTime:
            return
        if BigWorld.time() - self.__bpTime[aircraftID] < 2.0:
            self.__bpTime.pop(aircraftID)

    def onPLaneReturnFromBattle(self, aircraftID):
        if aircraftID not in self.__bpTime:
            return
        self.play('UISoundVehicleBack')
        self.__bpTime.pop(aircraftID)

    def __onVehicleLoaded(self):
        pass

    def toggleInGameMenu(self, visible):
        WWISE_.setState('STATE_GUI_Screen_Appear', 'GUI_Screen_On' if visible else 'GUI_Screen_Off')

    def play(self, tag):
        events = db.DBLogic.g_instance.getUI()
        if tag not in events:
            return
        self.postEvent(events[tag])

    def playLobbyResults(self):
        played = self.__battleResultsPlayed
        self.__battleResultsPlayed = True
        if played:
            return

    def setHoverButtonRadius(self, r):
        self.setRTPC('RTPC_UI_Hover_Battle_Volume', min(100.0, max(0.0, r)), 100.0)