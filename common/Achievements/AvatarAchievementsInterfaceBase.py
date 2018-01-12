# Embedded file name: scripts/common/Achievements/AvatarAchievementsInterfaceBase.py


class AvatarAchievementsInterfaceBase(object):
    unlockedAchievements = []

    def onAchievementUnlocked(self, achievementID):
        """
        @type self: Avatar.Avatar
        @type achievementID: int
        """
        self.unlockedAchievements.append(achievementID)
        self.client.onAchievementUnlocked(achievementID)