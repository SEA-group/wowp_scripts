# Embedded file name: scripts/client/audio/SoundUpdateManager.py
import BigWorld
import weakref
from WeakMethod import WeakMethod

class SoundUpdateQueue:

    def __init__(self, queueID, updatesPerTick):
        self._updatesPerTick = updatesPerTick
        self.__queueID = queueID
        self.__callbacksList = {}
        self.__callbacksQueue = []
        self.__removedInCurrentUpdateCycle = set()

    def append(self, cb):
        method = WeakMethod(cb)
        self.__callbacksList[WeakMethod.generateID(cb)] = method
        self.__callbacksQueue.append(method)

    def remove(self, cb):
        id = WeakMethod.generateID(cb)
        if id not in self.__callbacksList:
            return
        del self.__callbacksList[id]
        self.__removedInCurrentUpdateCycle.add(id)
        if not self.__callbacksList:
            SoundUpdateManager.instance().removeQueue(self.__queueID)

    def updateQueue(self):
        for i in range(min(self._updatesPerTick, len(self.__callbacksQueue))):
            weakMethod = self.__callbacksQueue.pop()
            if weakMethod.id not in self.__removedInCurrentUpdateCycle:
                weakMethod()

        if not len(self.__callbacksQueue):
            self.__removedInCurrentUpdateCycle.clear()
            self.__callbacksQueue.extend(self.__callbacksList.values())


g_instance = None

class SoundUpdateManager:

    def __init__(self):
        self.__queues = {}
        self.__updateCB = None
        return

    @staticmethod
    def instance():
        global g_instance
        if not g_instance:
            g_instance = SoundUpdateManager()
        return g_instance

    def start(self):
        self.__soundMainUpdate()

    def stop(self):
        if self.__updateCB:
            BigWorld.cancelCallback(self.__updateCB)

    def __soundMainUpdate(self):
        for queueID, queue in self.__queues.items():
            queue.updateQueue()

        self.__updateCB = BigWorld.callback(0, self.__soundMainUpdate)

    def registerQueue(self, queueID, queue):
        self.__queues[queueID] = queue

    def isQueueRegistred(self, queueID):
        return queueID in self.__queues

    def getQueue(self, queueID):
        if queueID not in self.__queues:
            return None
        else:
            return self.__queues[queueID]

    def removeQueue(self, queueID):
        if queueID in self.__queues:
            del self.__queues[queueID]

    def clear(self):
        self.__queues.clear()