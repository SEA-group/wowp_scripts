# Embedded file name: scripts/common/db/DBAreaConquest/SectorGeometry.py
from abc import ABCMeta, abstractmethod, abstractproperty
from Math import Vector3, Vector2
from MathExt import inside2DPolygon, boundingCircle

class SectorGeometryBase(object):
    """Sector geometry base class
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def position(self):
        """Sector position point, actually is figure center
        @rtype: Math.Vector3
        """
        raise NotImplementedError()

    @abstractproperty
    def position2D(self):
        """Sector position point in 2D - (x, z)
        @rtype: Math.Vector2
        """
        raise NotImplementedError()

    @abstractproperty
    def boundingCircle(self):
        """
        @return: center, radius
        @rtype: tuple[Math.Vector2, float]
        """
        return NotImplementedError()

    @abstractmethod
    def isInside(self, point):
        """Check if point is inside figure
        @type point: Math.Vector3
        @rtype: bool
        """
        raise NotImplementedError()

    @abstractmethod
    def convertPoints(self, provider):
        """Convert points from string idents to Vector3
        @param provider: Point positions provider
        @type provider: (basestring) -> Math.Vector3
        """
        raise NotImplementedError()


class SectorGeometryPolygon(SectorGeometryBase):
    """Polygon sector geometry
    """

    def __init__(self, vertexes):
        self._position = None
        self._position2D = None
        self._vertexes = vertexes
        self._vertexes2D = None
        self._boundingCircle = (None, None)
        return

    @property
    def position(self):
        return self._position

    @property
    def position2D(self):
        return self._position2D

    @property
    def vertexes(self):
        return self._vertexes

    @property
    def boundingCircle(self):
        return self._boundingCircle

    def isInside(self, point):
        return inside2DPolygon(Vector2(point.x, point.z), self._vertexes2D)

    def convertPoints(self, provider):
        self._vertexes = map(provider, self._vertexes)
        self._vertexes2D = [ Vector2(v.x, v.z) for v in self._vertexes ]
        self._position = sum(self._vertexes, Vector3()) / len(self._vertexes)
        self._position2D = Vector2(self._position.x, self._position.z)
        self._boundingCircle = boundingCircle(self._vertexes2D)


class SectorGeometryCircle(SectorGeometryBase):
    """Circle sector geometry
    """

    def __init__(self, position, radius):
        self._position = position
        self._position2D = None
        self._radius = radius
        return

    @property
    def position(self):
        return self._position

    @property
    def position2D(self):
        return self._position2D

    @property
    def radius(self):
        """Sector radius
        @rtype: float
        """
        return self._radius

    @property
    def boundingCircle(self):
        return (self._position2D, self._radius)

    def isInside(self, point):
        return (Vector2(point.x, point.z) - self._position2D).length <= self.radius

    def convertPoints(self, provider):
        self._position = provider(self._position)
        self._position2D = Vector2(self._position.x, self._position.z)