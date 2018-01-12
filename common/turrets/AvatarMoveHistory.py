# Embedded file name: scripts/common/turrets/AvatarMoveHistory.py
import BigWorld
import Math
from Math import Vector3

class AvatarMoveHistory(object):

    def _makeLocalProperties(self):
        self.moveHistoryStepsCount = 4
        self.moveHistory = [ Vector3() for _ in xrange(self.moveHistoryStepsCount) ]
        self._updateMoveHistoryTime = 0.35
        self._updateMoveHistoryLast = 0

    def update(self, position):
        self.updateMoveHistory(position)

    def updateMoveHistory(self, position):
        if BigWorld.time() - self._updateMoveHistoryLast >= self._updateMoveHistoryTime:
            self._updateMoveHistoryLast = BigWorld.time()
            count = self.moveHistoryStepsCount
            for i in xrange(count - 1):
                self.moveHistory[i] = self.moveHistory[i + 1]

            self.moveHistory[-1] = Vector3(position)