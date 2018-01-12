# Embedded file name: scripts/common/db/DBAreaConquest/Sectors.py
from Math import Vector2
from SectorModel import SectorModel

class Sectors(object):

    def __init__(self):
        self._sectors = {}
        self._distances = {}

    @property
    def sectors(self):
        """Sectors container
        @rtype: dict[basestring, Sector]
        """
        return self._sectors

    def getSector(self, ident):
        return self._sectors[ident]

    def getDistance(self, source, target):
        """Return distance between two sectors
        @param source: Source sector ident
        @param target: Target sector ident
        @return: Distance
        @rtype: float
        """
        return self._distances[source][target]

    def getSectorIdByPosition(self, position):
        pos2D = Vector2(position.x, position.z)
        sectors = sorted(self._sectors.values(), key=lambda s: (float('+inf') if s.isFreeZone else (Vector2(s.positionPoint.x, s.positionPoint.z) - pos2D).length))
        for sector in sectors:
            if sector.geometry.isInside(position):
                return sector.ident

    def fillSectorData(self, data):
        sectors = self._sectors
        for sectorId, sectorData in data.items():
            sectors[sectorId] = SectorModel()
            sectors[sectorId].ident = sectorId
            sectors[sectorId].read(sectorData)

    def convertPoints(self, getPointPosition):
        for sector in self._sectors.itervalues():
            sector.convertPoints(getPointPosition)

        self._calculateDistances()

    def _calculateDistances(self):
        for sourceIdent, source in self._sectors.iteritems():
            for destinationIdent, destination in self._sectors.iteritems():
                distance = (source.geometry.position - destination.geometry.position).length
                self._distances.setdefault(sourceIdent, {})[destinationIdent] = distance