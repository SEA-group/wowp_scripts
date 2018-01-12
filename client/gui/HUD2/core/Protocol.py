# Embedded file name: scripts/client/gui/HUD2/core/Protocol.py
from DataModel import List, Structure

class ScaleformProtocol:

    def __init__(self, sender):
        self._sender = sender

    def updateState(self, state):
        """
        :type state: str
        """
        self._sender({'updateState': state})

    def toggleHUDVisibility(self):
        self._sender('toggleHUDVisibility')

    def openInter(self, id):
        self._sender({'openInter': id})

    def closeInter(self, id):
        self._sender({'closeInter': id})

    def closeInterForce(self):
        self._sender({'closeInter': 'ALL'})

    def updateField(self, field):
        """
        :type field: DataModel.ModelAttr
        """
        value = self._serialize(field)
        self._sender({'type': 'updateField',
         field.fullName: value})

    def appendItem(self, field):
        """
        :type field: DataModel.ModelAttr
        """
        item = self._serialize(field.items[-1])
        self._sender({'type': 'appendItem',
         field.fullName: item})

    def spliceItem(self, field, index):
        """
        :type field: DataModel.ModelAttr
        :type index: int
        """
        self._sender({'type': 'spliceItem',
         field.fullName: index})

    def listClean(self, field):
        """
        :type field: DataModel.ModelAttr
        """
        self._sender({'type': 'listClean',
         field.fullName: True})

    def _serialize(self, field):
        if isinstance(field.type, List):
            return map(lambda e: self._serialize(e), field.items)
        elif isinstance(field.type, Structure):
            return {key:self._serialize(model) for key, model in field.fields.items()}
        else:
            return field.get()