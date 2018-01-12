# Embedded file name: scripts/client/gui/HUD2/core/MessageRouter.py
from collections import defaultdict

class MessageRouter:

    def __init__(self):
        self._messageHandlers = defaultdict(lambda : [])

    def setupHandlers(self, controllers):
        self._messageHandlers.clear()
        self._initHandlers(controllers)

    def _initHandlers(self, controllers):
        for controller in controllers:
            for attrName in dir(controller):
                callback = getattr(controller, attrName)
                if not hasattr(callback, 'isMessageHandler'):
                    continue
                self._messageHandlers[callback.route].append(callback)

    def processData(self, messageData):
        self._routeMessage(*self._parseMessage(messageData))

    def _parseMessage(self, messageData):
        tokens = filter(None, messageData.split(','))
        raise len(tokens) > 0 or AssertionError("Invalid message. Can't parse it: " + messageData)
        messageName, messageArgs = tokens[0], tokens[1:]
        return (messageName, messageArgs)

    def _routeMessage(self, messageName, args):
        for handler in self._messageHandlers.get(messageName, []):
            handler(*args)


def message(route):

    def decorator(func):
        func.isMessageHandler = True
        func.route = route
        return func

    return decorator