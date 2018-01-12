# Embedded file name: scripts/client/gui/HUD2/core/DataView.py


class ProxyView(object):

    def __init__(self, dataModel, protocol):
        """
        :type dataModel: DataModel.DataModel
        :type protocol: Protocol.Protocol
        """
        raise dataModel is not None or AssertionError
        raise protocol is not None or AssertionError
        self._dataModel = dataModel
        self._dataModel.registerProxyView(self)
        self._protocol = protocol
        self._subscribedFields = []
        return

    def subscribe(self, fieldFullName):
        try:
            self._dataModel.subscribeField(fieldFullName)
            self._protocol.updateField(self._dataModel.getFieldByName(fieldFullName))
        except AssertionError:
            raise Exception('Subscription Error %s' % fieldFullName)

    def unsubscribe(self, fieldFullName):
        self._dataModel.unsubscribeField(fieldFullName)

    def dispose(self):
        self._dataModel.unsubscribe(self)

    def onFieldChanged(self, changedField):
        self._protocol.updateField(changedField)

    def onItemAppended(self, changedField):
        self._protocol.appendItem(changedField)

    def onItemSpliced(self, field, index):
        self._protocol.spliceItem(field, index)

    def onListClean(self, field):
        self._protocol.listClean(field)