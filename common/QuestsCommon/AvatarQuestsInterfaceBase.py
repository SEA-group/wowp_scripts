# Embedded file name: scripts/common/QuestsCommon/AvatarQuestsInterfaceBase.py


class AvatarQuestsInterfaceBase(object):

    def onQuestCompleted(self, questID):
        """
        @type self: Avatar.Avatar
        @type questID: int
        @param isChild: if true, its only a part of composite quest completed
        @type isChild: bool
        """
        self.client.onQuestCompleted(questID)