# Embedded file name: scripts/client/ClientPlaneTurret/IGunnerPlayer.py
from Math import Vector2

class IGunnerPlayer(object):

    @property
    def shootDistance(self):
        return 0.0

    @property
    def isClientFiring(self):
        return False

    def destroy(self):
        pass

    def tryCatchTurret(self, turret):
        pass

    def isOnTarget(self):
        return False

    def getScopeRadius(self, direction):
        return 0

    def getReduction(self):
        return 0

    def getTurretZoneRectangle(self, direction):
        return Vector2(1, 1)

    @property
    def isClientInAction(self):
        return False

    def activate(self, active):
        pass

    def setControlMtx(self, mtx):
        pass

    def setDirection(self, direction):
        pass

    def isActiveGun(self, gunId):
        return False