# Embedded file name: scripts/client/battleHints/messenger.py
import BigWorld
import db.DBLogic
import InputMapping
from battleHints.alerts_controller import AlertsController
from battleHints.notifications_controller import NotificationsController
from ICMultiUpdate import ICMultiUpdate

class AlertUIData(object):

    def __init__(self, *args, **kwargs):
        self.title = kwargs.get('title', '')
        self.type = kwargs.get('type', -1)
        self.icon = kwargs.get('icon', '')
        self.lifeTime = kwargs.get('lifeTime', -1)
        self.priority = kwargs.get('priority', -1)
        self.description = kwargs.get('description', '')
        self.consumableDependency = kwargs.get('consumableDependency', '')
        self.data = kwargs.get('data', -1)


class NotificationUIData(object):

    def __init__(self, *args, **kwargs):
        self.title = kwargs.get('title', '')
        self.type = kwargs.get('type', -1)
        self.icon = kwargs.get('icon', '')
        self.lifeTime = kwargs.get('lifeTime', -1)
        self.priority = kwargs.get('priority', -1)
        self.description = kwargs.get('description', '')
        self.timer = kwargs.get('timer', -1)
        self.addValue = kwargs.get('addValue', -1)
        self.data = kwargs.get('data', -1)

    def addPostfix(self, value):
        self.title += value

    postfix = property(None, addPostfix)


class AlertMessage(object):

    def __init__(self, *args, **kwargs):
        self.ui = None
        self._planeValid = map(int, kwargs.get('validPlanes', []))
        self._spamInterval = kwargs.get('spamInterval', -1)
        self._lastPushTime = -10000000000.0
        self._initUI(*args, **kwargs)
        return

    def _initUI(self, *args, **kwargs):
        self.ui = AlertUIData(*args, **kwargs)

    def _coolDownValid(self):
        time = BigWorld.time()
        if time - self._lastPushTime >= self._spamInterval:
            self._lastPushTime = time
            return True
        return False

    def _planeTypeValid(self):
        if len(self._planeValid):
            return BigWorld.player().planeType in self._planeValid
        return True

    def reset(self):
        self._lastPushTime = 0

    def canPush(self):
        return self._coolDownValid() and self._planeTypeValid()

    def isGameModeAvailable(self, value):
        return True


class NotificationMessage(AlertMessage):

    def _initUI(self, *args, **kwargs):
        self.ui = NotificationUIData(*args, **kwargs)
        self._gameModes = kwargs.get('gameModes', [])

    def isGameModeAvailable(self, value):
        return value in self._gameModes


class ProxyMessage(AlertMessage):

    def canPush(self):
        return False


_StaticProxyMessage = ProxyMessage()

class BattleAlerts(object):

    def __init__(self):
        self._modelView = None
        self._messages = {}
        return

    def dispose(self):
        self._modelView = None
        self._messages = {}
        return

    def reset(self):
        for hint in self._messages.itervalues():
            hint.reset()

    def assignModelView(self, model):
        self._modelView = model

    def pushMessage(self, ID, localData = None):
        if self._modelView is not None:
            ms = self._messages.get(ID, _StaticProxyMessage)
            if ms.canPush():
                self._modelView.pushMessage(self.tryOverride(ms.ui, localData))
        return

    @staticmethod
    def tryOverride(uiData, localData):
        if localData is None:
            return uiData
        else:
            res = AlertUIData(**uiData.__dict__)
            for k, v in localData.iteritems():
                setattr(res, k, v)

            return res

    @staticmethod
    def localize(label):
        return label

    def loadMessages(self):
        data = db.DBLogic.g_instance.getBattleAlertHints()
        for ID, ms in data.iteritems():
            self._messages[ID] = AlertMessage(type=ms.type, title=self.localize(ms.title), icon=ms.icon, lifeTime=ms.lifeTime, priority=ms.priority, description=self.localize(ms.description), planeValid=[], spamInterval=ms.coolDown, consumableDependency=ms.consumableDependency, validPlanes=ms.validPlanes)


class BattleNotification(BattleAlerts):

    @staticmethod
    def tryOverride(uiData, overData):
        if overData is None:
            return uiData
        else:
            res = NotificationUIData(**uiData.__dict__)
            for k, v in overData.iteritems():
                setattr(res, k, v)

            return res

    @staticmethod
    def localize(label):
        return label

    def loadMessages(self):
        data = db.DBLogic.g_instance.getBattleNotificationHints()
        for ID, ms in data.iteritems():
            self._messages[ms.id] = NotificationMessage(type=ms.type, title=self.localize(ms.title), icon=ms.icon, lifeTime=ms.lifeTime, priority=ms.priority, description=self.localize(ms.description), planeValid=[], spamInterval=ms.coolDown, timer=ms.timer, addValue=ms.addValue, gameModes=ms.gameModes)

    def onInitGameMode(self, value):
        self._gameModeName = value

    def pushMessage(self, ID, localData = None):
        if self._modelView is not None:
            ms = self._messages.get(ID, _StaticProxyMessage)
            if ms.canPush() and ms.isGameModeAvailable(self._gameModeName):
                self._modelView.pushMessage(self.tryOverride(ms.ui, localData))
        return


_dt = 0.333

class Messenger(ICMultiUpdate):

    def __init__(self, gameEnv):
        self._gameEnv = gameEnv
        self._battleAlerts = BattleAlerts()
        self._alertsController = AlertsController(gameEnv, self._battleAlerts)
        self._battleNot = BattleNotification()
        self._notificationController = NotificationsController(gameEnv, self._battleNot)
        ICMultiUpdate.__init__(self, (_dt, self._update))

    @property
    def battleAlerts(self):
        return self._battleAlerts

    @property
    def battleNotification(self):
        return self._battleNot

    def init(self, *args, **kwargs):
        self._battleAlerts.loadMessages()
        self._battleNot.loadMessages()

    def onGameModeCreate(self):
        _gameModeName = self._gameEnv.service('ClientArena').gameModeName
        self._notificationController.onInitGameMode()
        self._battleNot.onInitGameMode(_gameModeName)

    def afterLinking(self, *args, **kwargs):
        pass

    def doLeaveWorld(self, *args, **kwargs):
        self._battleAlerts.reset()
        self._battleNot.reset()
        self._notificationController.unlinkEvents()

    def destroy(self, *args, **kwargs):
        ICMultiUpdate.dispose(self)
        self._alertsController.dispose()
        self._notificationController.dispose()
        self._battleAlerts.dispose()
        self._battleNot.dispose()

    def addInputListeners(self, processor):
        processor.addListeners(InputMapping.CMD_FLAPS_UP, None, None, self._alertsController.tryUseFlaps)
        return

    def onPartFlagSwitchedNotification(self, partID, flagID, flagValue):
        self._alertsController.onPartFlagSwitchedNotification(partID, flagID, flagValue)

    def reportEngineOverheat(self):
        self._alertsController.reportEngineOverheat()

    def onPartStateChanging(self, partData):
        self._alertsController.onPartStateChanging(partData)

    def onGunGroupFire(self, group):
        self._alertsController.onGunGroupFire(group)

    def applyArenaData(self, data):
        self._alertsController.applyArenaData(data)

    def autopilot(self, new, old):
        self._alertsController.autopilot(new, old)

    def reportNoShell(self, shellID, result):
        self._alertsController.reportNoShell(shellID, result)

    def _update(self):
        self._alertsController.update(_dt)
        self._notificationController.update(_dt)