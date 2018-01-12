# Embedded file name: scripts/common/updatable/Ballistic.py
import BigWorld
from UpdatableObjectBase import *
import Math
import math
from consts import *
from consts import COMPONENT_TYPE
import db.DBLogic
import Event
from debug_utils import *
from UpdatableObjectSound import UpdatableObjectSound
if IS_CLIENT:
    import EffectManager
    from db.DBEffects import Effects

def testPoint(pos, color):
    matrix = Math.Matrix()
    matrix.translation = pos
    BigWorld.addPoint('Test', matrix, color, True)


class BallisticUpdatable(UpdatableObjectBase):

    def __init__(self, owner):
        UpdatableObjectBase.__init__(self, owner)
        self.model = None
        self.__maxFlightDist = 1000.0
        self.__tickMovement = 0.0
        self.__totalMovement = 0.0
        self.__direction = None
        self.__matrix = None
        self.position = Math.Vector3(0, 0, 0)
        self._startPosition = Math.Vector3(0, 0, 0)
        self._startVector = Math.Vector3(0, 0, 0)
        self._startRotation = Math.Vector3(0, 0, 0)
        self.__shellDescription = None
        self.__scaleMatrix = Math.Matrix()
        self.__scaleMatrix.setScale((AIRCRAFT_MODEL_SCALING, AIRCRAFT_MODEL_SCALING, AIRCRAFT_MODEL_SCALING))
        self.__attachedEffect = None
        self._eManager = Event.EventManager()
        self.onExplosion = Event.Event(self._eManager)
        return

    def getSyncType(self):
        return UPDATABLE_SYNK_TYPE.NONE

    def setState(self, state, timeShift = 0.0):
        UpdatableObjectBase.setState(self, state, timeShift)
        if IS_CLIENT and self._owner:
            if self.getState() == UPDATABLE_STATE.DESTROY:
                position = self.position
                EffectManager.g_instance.createWorldEffect(Effects.getEffectId(self.__effectName), position, {})
                if IS_CLIENT:
                    self.__updatableSound.stopSound()
                self.onExplosion(self)
                self.destroy()
            if self.getState() == UPDATABLE_STATE.CREATE:
                if self.model:
                    self.model.visible = True

    def destroy(self):
        self._eManager.clear()
        if self.__attachedEffect:
            self.__attachedEffect.destroy()
        UpdatableObjectBase.destroy(self)
        if self.model:
            BigWorld.delModel(self.model)
            self.model = None
            self.__matrix.scaleMatrix = None
            self.__matrix = None
        return

    def doExplosion(self):
        self.__doExplosion()

    def __doExplosion(self, timeShift = 0.0):
        self.setState(UPDATABLE_STATE.DESTROY, timeShift)

    def __getPositionForTime(self, t):
        return self._startPosition + self.__direction * self.__getDistForTime(t)

    def __getDistForTime(self, t):
        return self.__shellDescription.startSpeed * t + self.__shellDescription.acceleration * t * t / 2

    def _positionUpdate(self):
        t = self._getCurrentTime()
        if t >= 0.0:
            if self.__matrix is not None:
                self.__matrix.move = True
                if self.__matrix.totalMovement >= self.__distance or self.__matrix.tickMovement < 0:
                    self.__matrix.move = False
                    self.position = self._endPosition
                    self.__doExplosion()
                    return
                self.__updatableSound.updatePosition(self.__matrix.position)
        return

    def _onBaseCreate(self, args):
        UpdatableObjectBase.setUnpackArgs(self, (args[0], args[1]))
        self.__shellDescription = db.DBLogic.g_instance.getScenarioShotBallisticProfile(self._resourceID)
        self._startPosition = args[2]
        self._startVector = args[3]
        self._startRotation = args[4]
        self.position = self._startPosition
        self._endPosition = args[5]
        self.__direction = Math.Vector3(self._endPosition - self._startPosition)
        self.__direction.normalise()
        h = args[6]
        self.__effectName = args[7]
        self.__distance = (self._endPosition - self._startPosition).length
        if h > 0 and h < 89:
            height = self.__distance * math.tan(math.radians(h)) / 2
        else:
            height = math.fabs(h)
        self.__koefA = -4 * height / (self.__distance * self.__distance)
        self.__koefB = 4 * height / self.__distance
        self.__loadRocketModel()
        if IS_CLIENT:
            self.__updatableSound = UpdatableObjectSound('Ballistic', self.creatorOwnerID())

    def _onCreate(self, args):
        pass

    def __loadRocketModel(self):
        BigWorld.loadResourceListBG((self.__shellDescription.model,), self.__onRocketModelLoaded)

    def __onRocketModelLoaded(self, resourceRefs):
        if self._owner is not None:
            modelName = self.__shellDescription.model
            if modelName not in resourceRefs.failedIDs:
                self.model = resourceRefs[modelName]
                self.__setModel()
                if IS_CLIENT:
                    weaponSoundID = 'weapon_' + getattr(self.__shellDescription, 'name', '')
                    self.__updatableSound.startSound(weaponSoundID, self.position, self.getState())
            else:
                LOG_ERROR("Can't load ballistic model", modelName)
        return

    def __setModel(self):
        self.model.position = self.position
        self.__matrix = BigWorld.MatrixBalisticMoveProvider(self.position, self._endPosition, self._startVector)
        self.__matrix.scaleMatrix = self.__scaleMatrix
        self.__matrix.koefA = self.__koefA
        self.__matrix.koefB = self.__koefB
        self.__matrix.startSpeed = self.__shellDescription.startSpeed
        self.__matrix.acceleration = self.__shellDescription.acceleration
        servo = BigWorld.Servo(self.__matrix)
        self.model.addMotor(servo)
        BigWorld.addModel(self.model)
        self.model.visible = self.getState() == UPDATABLE_STATE.CREATE
        try:
            self.__attachedEffect = EffectManager.g_instance.createNodeAttachedEffect(Effects.getEffectId(self.__shellDescription.particleSmoke), self.model.node('HP_flame'), {'uniqueId': str(self._id)})
        except ValueError:
            LOG_ERROR('Ballistic: No node named HP_flame in model ', self.model.sources)