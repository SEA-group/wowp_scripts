# Embedded file name: scripts/client/OrientationMarkers/OrientationMarkersDebugInterface.py


class OrientationMarkersDebugInterface(object):

    def getDebugGroupIds(self):
        """
        @rtype: tuple[string]
        """
        return ()

    def setDebugGroupVisible(self, groupId, isVisible):
        """
        @type groupId: str
        @type isVisible: bool
        """
        pass

    def isDebugGroupVisible(self, groupId):
        """
        @type groupId: str
        @rtype: bool
        """
        return False

    def setCategoryDistances(self, categoryNames, categoryDistances):
        """
        @type categoryNames: list[str]
        @type categoryDistances: list[float]
        """
        pass

    def setCircleRadius(self, circleRadius):
        """
        @type circleRadius: float
        """
        pass