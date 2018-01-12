# Embedded file name: scripts/client/BattleReplayRecordMode.py
import BigWorld
from BattleReplayMode import ModeInterface
from debug_utils import *
import json
import datetime
import db.DBLogic
from EntityHelpers import extractGameMode
from gui.Version import Version

def startRecord(replayCtrl, fileName):
    mode = RecordMode(replayCtrl)
    if not replayCtrl.startRecording(fileName):
        LOG_ERROR('BattleReplay.startRecord failed')
        mode.destroy()
        return None
    else:
        return mode


class RecordMode(ModeInterface):

    def __init__(self, replayCtrl):
        self.__replayCtrl = replayCtrl

    def destroy(self):
        self.__replayCtrl = None
        return

    def onEnterWorld(self):
        self.__replayCtrl.onSyncPoint1()
        self.__replayCtrl.onClientReady()
        player = BigWorld.player()
        arenaData = db.DBLogic.g_instance.getArenaData(player.arenaType)
        vehicle = db.DBLogic.g_instance.getAircraftData(player.planeID).airplane
        nowT = datetime.datetime.now()
        now = '%02d.%02d.%04d %02d:%02d:%02d' % (nowT.day,
         nowT.month,
         nowT.year,
         nowT.hour,
         nowT.minute,
         nowT.second)
        arenaInfo = {'dateTime': now,
         'playerName': player.objectName,
         'myID': player.id,
         'playerVehicle': vehicle.name,
         'mapName': arenaData.typeName,
         'mapDisplayName': arenaData.typeName,
         'gameplayID': extractGameMode(player.gameMode),
         'clientVersion': str(Version().getVersion()).strip()}
        self.__replayCtrl.recMapName = arenaData.typeName
        self.__replayCtrl.recPlayerVehicleName = vehicle.name
        self.__replayCtrl.setArenaInfoStr(json.dumps(arenaInfo))

    def onLeaveWorld(self):
        pass

    def onArenaLoaded(self):
        self.__replayCtrl.onTimeMarker(self.REPLAY_TIME_MARK_ARENA_LOADED)

    def onBattleResultsReceived(self, results):

        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        self.__replayCtrl.setArenaStatisticsStr(json.dumps(results, default=set_default))

    def notifyAxisValues(self, axis, value):
        self.__replayCtrl.onApplyInputAxis(axis, value)