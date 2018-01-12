# Embedded file name: scripts/common/turrets/DirectStrategy.py
from turrets.BaseShootStratery import BaseShootStrategy

class DirectStrategy(BaseShootStrategy):

    def updateAttackPoint(self):
        pass

    def shoot(self):
        pass

    def calculateTimeToLive(self, dy, bulletDir, bulletSpeed):
        return super(DirectStrategy, self).calculateTimeToLive(dy, bulletDir, bulletSpeed) * 5

    def calculateBulletsCount(self):
        return 1