# Embedded file name: scripts/common/Achievements/AvatarAchievementsInterfaceClient.py
from Event import Event

class AvatarAchievementsInterfaceClient(object):
    unlockedAchievements = []

    def __init__(self):
        """
        @type self: Avatar.Avatar
        """
        self.eAchievementUnlocked = Event()

    def onLeaveWorld(self):
        self.eAchievementUnlocked.clear()

    def onAchievementUnlocked(self, achievementID):
        self.unlockedAchievements.append(achievementID)
        self.eAchievementUnlocked(achievementID)