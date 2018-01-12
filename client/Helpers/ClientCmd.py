# Embedded file name: scripts/client/Helpers/ClientCmd.py
from functools import partial
from itertools import cycle
import BigWorld
import wgPickle
from AccountCommands import REQUEST_ID_UNRESERVED_MAX as ID_MAX, REQUEST_ID_UNRESERVED_MIN as ID_MIN
from consts import QA_FUNCTIONS
from debug_utils import LOG_DEBUG, CRITICAL_ERROR
idGenerator = cycle(xrange(ID_MIN, ID_MAX))

class ClientCmd:

    def __init__(self, server, client, handler = None):
        self.server = server
        self.client = client
        self.handler = handler
        self.deferredRequests = {}

    def _ipcCommand(self, route, op, **kw):
        """
        Proxy calls to server.doCommand as QA_FUNCTIONS.TURBO
        Add callback as a Deferred callback
        """
        from twisted.internet.defer import Deferred
        d = Deferred()
        self.sendCmd(QA_FUNCTIONS.TURBO, lambda req, resp, args: (d.callback(args) if resp == 0 else d.errback(args)), -1, route, op, kw)
        return d

    def proxy(self, route):
        """
        Create remote proxy
        :param route: remote node identifier, 'base' or 'cell'
        """
        from testcore.ipc.proxy import Proxy
        return Proxy(partial(self._ipcCommand, route))

    def destroy(self):
        """
        Destroy/release
        """
        self.server = None
        self.client = None
        self.deferredRequests.clear()
        return

    def sendCmd(self, commandID, callback, targetID, *args):
        """
        Double pickle args (cPickle+msgpack) and send them to server
        :param commandID: command id (QA_FUNCTIONS)
        :param callback: callback(requestID, result, response),
                         called in onCmdResponse
        :param targetID:
        :param args: command parameters (unpickled)
        """
        requestID = next(idGenerator)
        if callback is None:
            callback = self.__onCmdCallback
        if targetID == -1:
            targetID = self.client.id
        self.deferredRequests[requestID] = callback
        argstr = wgPickle.dumps(wgPickle.FromServerToServer, args)
        arg = wgPickle.dumps(wgPickle.FromClientToServer, argstr)
        self.server.doCommand(requestID, commandID, targetID, arg)
        return

    def onCmdResponse(self, requestID, resultID, responseDataStr):
        """
        Unpack response and fire callback by requestID
        :param requestID: id passed in doCmd method.
        :param resultID: command result.
        :param responseDataStr: pickled response
        """
        callback = self.deferredRequests.pop(requestID, self.__onCmdCallback)
        args = wgPickle.loads(wgPickle.FromServerToClient, responseDataStr)
        callback(requestID, resultID, args)

    def __onCmdCallback(self, requestID, resultID, args):
        """
        Default response callback
        :param requestID: requestID from sendCmd
        :param resultID: returned result code
        :param args: returned data
        """
        LOG_DEBUG('Default respond callback:', 'requestID', requestID, 'resultID', resultID, 'data', args)