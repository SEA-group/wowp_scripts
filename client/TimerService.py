# Embedded file name: scripts/client/TimerService.py
from Event import Event, EventManager
import BigWorld
from GameServiceBase import GameServiceBase

class TimerService(GameServiceBase):

    def __init__(self):
        super(TimerService, self).__init__()
        self.__manager = EventManager()
        self.eUpdate1Sec = Event(self.__manager)
        self.eUpdate = Event(self.__manager)
        self.__updateCallback = None
        self.__update1SecCallback = None
        return

    def afterLinking(self):
        self.__updateCallback = BigWorld.callback(0.1, self.__update)
        self.__update1SecCallback = BigWorld.callback(1.0, self.__update1Sec)

    def doLeaveWorld(self):
        BigWorld.cancelCallback(self.__update1SecCallback)
        BigWorld.cancelCallback(self.__updateCallback)

    def __update1Sec(self):
        self.eUpdate1Sec()
        self.__update1SecCallback = BigWorld.callback(1.0, self.__update1Sec)

    def __update(self):
        self.eUpdate()
        self.__updateCallback = BigWorld.callback(0.1, self.__update)

    def destroy(self):
        self.__manager.clear()