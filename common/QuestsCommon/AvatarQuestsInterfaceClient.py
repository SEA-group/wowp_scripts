# Embedded file name: scripts/common/QuestsCommon/AvatarQuestsInterfaceClient.py
from Event import Event

class AvatarQuestsInterfaceClient(object):

    def __init__(self):
        """
        @type self: Avatar.Avatar
        """
        self.eQuestCompleted = Event()

    def onLeaveWorld(self):
        self.eQuestCompleted.clear()

    def onQuestCompleted(self, questID):
        self.eQuestCompleted(questID)