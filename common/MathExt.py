# Embedded file name: scripts/common/MathExt.py
import BigWorld
import Math
import math
from random import gauss, random
from bisect import bisect_right

def FloatToCInt8(value):
    return clamp(-100, int(value * 100), 100)


def CInt8ToFloat(value):
    return float(value) / 100.0


def FloatToUCInt8(value):
    return clamp(0, int(value * 200), 200)


def UCInt8ToFloat(value):
    return float(value) / 200.0


def FloatToCInt16(value):
    return clamp(-32767, int(value * 32767), 32767)


def CInt16ToFloat(value):
    return float(value) / 32767.0


def FloatArrayToTupleOfCInt8(array):
    return tuple([ FloatToCInt8(x) for x in tuple(array) ])


def TupleOfCInt8ToFloatArray(array, arrayObject):
    return arrayObject([ CInt8ToFloat(x) for x in array ])


def FloatArrayToTupleOfCInt16(array):
    return tuple([ FloatToCInt16(x) for x in tuple(array) ])


def TupleOfCInt16ToFloatArray(array, arrayObject):
    return arrayObject([ CInt16ToFloat(x) for x in array ])


def weightRandomGenerator(weights):
    rnd = random() * sum(weights)
    for i, w in enumerate(weights):
        rnd -= w
        if rnd < 0:
            return i


def weightRandomGeneratorN(weights, n):
    """to get N non-unique weights indices"""
    totals = []
    curTotal = 0
    for w in weights:
        curTotal += w
        totals.append(curTotal)

    return [ bisect_right(totals, random() * curTotal) for i in xrange(n) ]


def sampleListByWeights(a, weights, n = -1):
    """to get N non-repeat weights indices"""
    wLen = len(weights)
    if n < 0:
        n = wLen
    if n == 0 or wLen == 0:
        return []
    n = min(n, wLen)
    indices = [ i for i in xrange(wLen) ]
    maxSumWeight = sum(weights)
    curLen = wLen
    for i in xrange(n):
        wSum = random() * maxSumWeight
        curSum = 0
        for j in xrange(curLen):
            curSum += weights[indices[j]]
            if wSum <= curSum:
                curLen -= 1
                indices[j], indices[curLen] = indices[curLen], indices[j]
                maxSumWeight -= wSum
                break

    return [ a[indices[i]] for i in xrange(wLen - 1, wLen - 1 - n, -1) ]


def lerp(fromValue, toValue, norm):
    return fromValue * (1.0 - norm) + toValue * norm


def rangeLerp(fromValue, toValue, rangePoint, startRange, endRange):
    if startRange == endRange:
        return fromValue
    norm = float(rangePoint - startRange) / (endRange - startRange)
    return lerp(fromValue, toValue, clamp(0, norm, 1))


def quadraticEquation(a, b, c):
    """quadratic equation ,returned discriminant and roots"""
    if a == 0:
        if b == 0:
            return (-1, 0, 0)
        x = -c / b
        return (0, x, x)
    else:
        D = b * b - 4 * a * c
        if D >= 0:
            D = math.sqrt(D)
            x1 = (-b - D) / (2 * a)
            x2 = (-b + D) / (2 * a)
            return (D, x1, x2)
        return (D, 0, 0)


def sign(value):
    if value == 0.0:
        return 0.0
    elif value > 0:
        return 1.0
    else:
        return -1.0


def clampAngle(a):
    if a > math.pi:
        return a - math.pi * 2.0
    if a < -math.pi:
        return a + math.pi * 2.0
    return a


def clampAngle2Pi(a):
    if a < 0:
        return a + 2 * math.pi
    if a > 2 * math.pi:
        return a - 2 * math.pi
    return a


def ellipseCfc(x, y, a, b):
    return x * x / (a * a) + y * y / (b * b)


def mullVector3(a, b):
    return Math.Vector3(a.x * b.x, a.y * b.y, a.z * b.z)


def normalized(a):
    len = a.length
    if len == 0:
        return a
    return Math.Vector3(a.x / len, a.y / len, a.z / len)


def clamp(minimum, x, maximum):
    if x < minimum:
        return minimum
    if x > maximum:
        return maximum
    return x


def clamp01(x):
    return clamp(0, x, 1)


def quat2Euler(quat):
    matrix = Math.Matrix()
    forward = quat.getAxisZ()
    up = quat.getAxisY()
    matrix.lookAt((0, 0, 0), (forward.x, forward.y, forward.z), (up.x, up.y, up.z))
    matrix.invert()
    return (matrix.roll, matrix.pitch, matrix.yaw)


def getDirProjection(objPos, objRotation, targetPos, dirVector):
    norm = objPos - targetPos
    norm.normalise()
    return objRotation.rotateVec(dirVector).dot(norm)


def packRotationBy2AnglesToInt16(angle1, angle2):
    if angle1 < 0:
        angle1 += 2 * math.pi
    a = int(angle1 * 255 / (2 * math.pi))
    if angle2 < 0:
        angle2 += 2 * math.pi
    b = int(angle2 * 255 / (2 * math.pi))
    return a << 8 | b


def unpackInt16ToAngles(v):
    a = float(v >> 8) / 255 * 2 * math.pi
    b = float(v & 255) / 255 * 2 * math.pi
    return (a, b)


def toVec4(vec3):
    return Math.Vector4(vec3.x, vec3.y, vec3.z, 0)


def rotateDiscreteY(vec, a):
    invA = 1.0 - abs(a)
    return Math.Vector3(vec.x * invA + vec.z * a, vec.y, vec.z * invA + vec.x * a)


def rotateDiscreteX(vec, a):
    invA = 1.0 - abs(a)
    return Math.Vector3(vec.x, vec.y * invA + vec.z * a, vec.z * invA + vec.y * a)


def trancatedGauss(a, b):
    """return value in [a, b], where a < b and a > 0"""
    middle = (a + b) * 0.5
    v = gauss(middle, (b - middle) * 0.3)
    if v > b:
        return b
    if v < a:
        return a
    return v


def repeatGauss(a, b, mu = None, sigmaK = 0.3):
    """return value in [a, b], where a < b
    mu in [a, b] - mu for gauss function or (a + b)*0.5 if invalid or empty
    
    sigmaK - 0.3 - 99% values of gauss() function will be in [a, b]
    sigmaK < 0.3 - more values will be out of interval
    sigmaK > 0.3 - less values will be out of interval"""
    if not mu or mu > b or mu < a:
        from debug_utils import LOG_DEBUG
        LOG_DEBUG('invalid mu', mu, 'when interval is [', a, ',', b, '] - use middle value instead')
        mu = (a + b) * 0.5
    sigma = (b - a) * 0.5 * sigmaK
    v = gauss(mu, sigma)
    while v > b or v < a:
        v = gauss(mu, sigma)

    return v


def getRotationFromDirection(dir):
    return (0.0, math.atan2(dir.y, math.sqrt(dir.x ** 2 + dir.z ** 2)), math.atan2(dir.x, dir.z))


def insideConvex2DPolygon(point2D, points2D):
    RIGHT = 'right'
    LEFT = 'left'

    def getSide(a, b):
        x = a.x * b.y - a.y * b.x
        if x < 0:
            return LEFT
        elif x > 0:
            return RIGHT
        else:
            return None
            return None

    prevSide = None
    pointsCount = len(points2D)
    for n in xrange(pointsCount):
        a, b = points2D[n], points2D[(n + 1) % pointsCount]
        currSide = getSide(b - a, point2D - a)
        if currSide is None:
            return False
        if prevSide is None:
            prevSide = currSide
        elif prevSide != currSide:
            return False

    return True


def inside2DPolygon(point2D, points2D):
    RAY_LENGTH = 20000
    segment = (point2D, point2D + Math.Vector2(RAY_LENGTH, RAY_LENGTH))
    crossingCount = 0
    pointsCount = len(points2D)
    for n in xrange(pointsCount):
        currSegment = (points2D[n], points2D[(n + 1) % pointsCount])
        if segmentCrossing(segment, currSegment) is not None:
            crossingCount += 1

    return crossingCount % 2 == 1


def segmentCrossing(segment1, segment2):
    b1 = b2 = 0
    xCross = None
    xDiff1 = segment1[1].x - segment1[0].x
    yDiff1 = segment1[1].y - segment1[0].y
    if xDiff1 != 0:
        a1 = yDiff1 / xDiff1
        b1 = segment1[0].y - a1 * segment1[0].x
    else:
        a1 = float('inf')
        xCross = segment1[0].x
    xDiff2 = segment2[1].x - segment2[0].x
    yDiff2 = segment2[1].y - segment2[0].y
    if xDiff2 != 0:
        a2 = yDiff2 / xDiff2
        b2 = segment2[0].y - a2 * segment2[0].x
    else:
        a2 = float('inf')
        xCross = segment2[0].x
    if a1 == a2:
        return
    if xCross is None:
        xCross = (b2 - b1) / (a1 - a2)
    if a1 != float('inf'):
        yCross = a1 * xCross + b1
    else:
        yCross = a2 * xCross + b2
    if min(segment1[0].x, segment1[1].x) > xCross:
        return
    elif max(segment1[0].x, segment1[1].x) < xCross:
        return
    elif min(segment1[0].y, segment1[1].y) > yCross:
        return
    elif max(segment1[0].y, segment1[1].y) < yCross:
        return
    elif min(segment2[0].x, segment2[1].x) > xCross:
        return
    elif max(segment2[0].x, segment2[1].x) < xCross:
        return
    elif min(segment2[0].y, segment2[1].y) > yCross:
        return
    elif max(segment2[0].y, segment2[1].y) < yCross:
        return
    else:
        return (xCross, yCross)


def boundingCircle(points):
    """
    Fastest, low accuracy
    @type points: list[Math.Vector2]
    @return: center, radius
    @rtype: tuple[Math.Vector2, float]
    """
    xMin = yMin = float('+inf')
    xMax = yMax = float('-inf')
    for p in points:
        xMin = min(p.x, xMin)
        yMin = min(p.y, yMin)
        xMax = max(p.x, xMax)
        yMax = max(p.y, yMax)

    tx = (xMax - xMin) / 2
    ty = (yMax - yMin) / 2
    cx = xMin + tx
    cy = yMin + ty
    r = tx + ty - min(tx, ty) / 2
    return (Math.Vector2(cx, cy), r)


def isCircleCrossedBySegment(center, radius, segmentStart, segmentDelta):
    """
    @type center: Math.Vector2
    @type radius: float
    @type segmentStart: Math.Vector2
    @type segmentDelta: Math.Vector2
    @rtype: bool
    """
    vectorToCenter = center - segmentStart
    angle = math.atan2(vectorToCenter.y - segmentDelta.y, vectorToCenter.x - segmentDelta.x)
    segmentDir = segmentDelta
    segmentDir.normalise()
    segmentProjection = segmentStart + segmentDir * vectorToCenter.length * math.cos(angle)
    return (segmentProjection - center).length <= radius


def km_to_m(value):
    return value / 3.6


def m_to_km(value):
    return value * 3.6


def convGlobalToRelativeRotation(maxYaw, minYaw, maxPitch, minPitch):
    leftYaw = 0.0
    rightYaw = 0.0
    DEG = math.degrees(2 * math.pi)
    if maxYaw > DEG:
        rightYaw = maxYaw - DEG
        leftYaw = minYaw - DEG
    else:
        rightYaw = maxYaw - math.degrees(math.pi)
        leftYaw = minYaw - math.degrees(math.pi)
    upPitch = maxPitch
    downPitch = minPitch
    return (upPitch,
     downPitch,
     leftYaw,
     rightYaw)