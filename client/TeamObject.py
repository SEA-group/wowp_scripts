# Embedded file name: scripts/client/TeamObject.py
import BigWorld
import BWLogging
import GameEnvironment
import db.DBLogic
import Math
import CompoundSystem
from consts import *
from debug_utils import *
import debug_utils
from gui.HUDconsts import *
import gui.hud
import EffectManager
from db.DBEffects import Effects
from Helpers.i18n import localizeObject
from EntityHelpers import *
from ControllerManager import ControllerManager
from CollidableObject import CollidableObject
from SyncedRandom import SyncedRandom
from functools import partial
import MathExt
from clientConsts import BULLET_PARAM, TURRET_TRACKER_AXIS
from ScenarioClient.TeamObjectScenarioController import TeamObjectScenarioController
from Event import Event, EventManager
from consts import TEAM_ID
from GameModeSettings import ACSettings as SETTINGS
from Event import Event
import debug_observable

class TODummyPart(DummyPartBase):

    def __init__(self, partSettings, partID, partState):
        super(TODummyPart, self).__init__(partSettings, partID, partState)
        self.isAlive = self.partTypeData.states[partState].stateHelthCfc != 0


from audio import GameSound

def onBulletExplosion(effectId, startPos, end):
    MAX_DIST_TO_CAMERA = 300
    distToCamera = BigWorld.camera().position.distTo(end)
    if distToCamera < MAX_DIST_TO_CAMERA:
        bulletDir = end - startPos
        EffectManager.g_instance.createWorldEffect(effectId, end, {'variant': 'OTHER',
         'rotation': Math.Vector3(bulletDir.yaw, bulletDir.pitch, 0)})


class TeamObject(BigWorld.Entity, ControllerManager, CollidableObject):

    def __init__(self):
        ControllerManager.__init__(self)
        CollidableObject.__init__(self)
        self._logger = BWLogging.getLogger(self)
        self.filter = BigWorld.AvatarFilter()
        self._settings = None
        self.alignToGround = False
        self.__addedToArena = False
        self.__teamObjectArenaData = None
        self.vscriptStarted = False
        self.syncedRandom = SyncedRandom()
        return

    def updateLocalizedName(self):
        self.localizedName = localizeObject(self._settings.name)

    def onMapEntryCreated(self, mapEntry):
        pass

    @property
    def mapMatrix(self):
        return self.matrix

    def onEnterWorld(self, prereqs):
        self.setGameTeamIndex(self.teamIndex)
        self._initDBSettings()
        self.prepareMatrices()
        self.__createEvents()
        self._createControllers()
        movementStrategy = self.controllers.get('movementStrategy', None)
        if hasattr(self._settings, 'alignToGround'):
            self.alignToGround = self._settings.alignToGround
        if movementStrategy and movementStrategy.matrixProvider:
            self.filter = movementStrategy.createFilter()
        elif self.alignToGround:
            self.filter = BigWorld.AvatarDropFilter()
            self.filter.alignToGround = True
        elif self.filter.__class__ != BigWorld.PredictionFilter:
            self.filter = BigWorld.PredictionFilter()
        self.updateLocalizedName()
        self._checkStateSettings()
        self._notifyModelManipulatorOwnerChanged(self)
        self.controllers['modelManipulator'].updatePartsFlags(self.partFlags)
        self.controllers['modelManipulator'].updateStatesNet(self.partStates, True)
        self.eTeamIndexChanged += self.updateCompoundColour
        self.controllers['modelManipulator'].eCompoundLoaded += self.updateCompoundColour
        self.updateCompoundColour()
        self.eOnTeamObjectEnterWorld(self)
        debug_observable.startObserv(self)
        return

    def _notifyModelManipulatorOwnerChanged(self, owner):
        modelManipulator = self.controllers.get('modelManipulator')
        if modelManipulator:
            modelManipulator.onOwnerChanged(owner)

    def __createEvents(self):
        self._eventManager = EventManager()
        self.ePartStateChanged = Event(self._eventManager)
        self.eHealthChanged = Event(self._eventManager)
        self.eTeamIndexChanged = Event(self._eventManager)
        self.eOnEntityStateChanged = Event(self._eventManager)
        self.eOnTeamObjectEnterWorld = Event(self._eventManager)
        self.eOnTeamObjectLeaveWorld = Event(self._eventManager)

    def _createControllers(self):
        controllersData = GameEnvironment.getClientArena().createTeamObjectControllers(self.id, self._settings, self, self.partTypes, self.partStates)
        modelManipulator = controllersData['modelManipulator']
        self._registerController('modelManipulator', modelManipulator)
        self.model = modelManipulator.getRootModel()
        self.model.delMotor(self.model.motors[0])
        self.model.addMotor(BigWorld.Servo(self.resMatrix))
        modelManipulator.setMatrixProvider(self.resMatrix)
        turretsLogic = controllersData.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.setOwner(self)
            self._registerController('turretsLogic', turretsLogic)
            self.ePartStateChanged += turretsLogic.onPartStateChanged
        if self.scenarioName != '':
            if not self.scenarioName.endswith('.xml') and not self.scenarioName.endswith('.plan'):
                scenarioData = db.DBLogic.g_instance.getScenario(self.scenarioName)
                if scenarioData:
                    scenarioController = TeamObjectScenarioController(self, scenarioData)
                    self._registerController('scenarioController', scenarioController)
                else:
                    LOG_ERROR("Can't find scenario", self.scenarioName)
        soundController = controllersData['soundController']
        self._registerController('soundController', soundController)
        return

    def isPlayer(self):
        return False

    def getSuperiorityPointsByGroupPartId(self, groupID):
        return getattr(self._settings, 'superiorityPointsGroup%d' % groupID, 0)

    def set_partFlags(self, changesData):
        self.controllers['modelManipulator'].updatePartsFlags(self.partFlags)
        self.controllers['soundController'].updatePartsFlags(self.partFlags)

    def setNested_partStates(self, path, value):
        item = self.partStates[path[0]]
        part = TODummyPart(self._settings.partsSettings, item[0], item[1])
        self.ePartStateChanged(part)
        if self.__addedToArena:
            isDead = self.__isPartDead(part.partTypeData, item[1])
            GameEnvironment.g_instance.eTOPartChanged(self.id, item[0], isDead)
        self.set_partStates(None)
        return

    def set_partStates(self, oldPartStates):
        modelManipulator = self.controllers.get('modelManipulator', None)
        if modelManipulator:
            modelManipulator.velocity = self.getWorldVector()
            modelManipulator.updateStatesNet(self.partStates, True)
        if EntityStates.inState(self, EntityStates.GAME_CONTROLLED):
            player = BigWorld.player()
            if self.lastDamagerID == player.id and self.teamIndex != player.teamIndex and self.teamIndex <= 1:
                for partID, partState in self.partStates:
                    if partID == self.lastDamagedPartID:
                        if partState >= 4:
                            reportedIDs = player.reportedDamagedPartsByEntity.get(self.id, None)
                            if reportedIDs:
                                if self.lastDamagedPartID in reportedIDs and reportedIDs[self.lastDamagedPartID] == partState:
                                    break
                                else:
                                    reportedIDs[self.lastDamagedPartID] = partState
                            else:
                                player.reportedDamagedPartsByEntity[self.id] = {self.lastDamagedPartID: partState}
                        break

        self.__collisionStateUpdate(True)
        if oldPartStates is not None:
            for partID, partState in self.partStates:
                GameEnvironment.g_instance.eTOPartChanged(self.id, partID, False)

        return

    def _checkStateSettings(self, transtitionActions = False):
        if self.inWorld:
            self.setGameState(self.state)
            self.controllers['modelManipulator'].setState(self.state, transtitionActions)
            if EntityStates.inState(self, EntityStates.CREATED):
                self.onRespawn()
            elif EntityStates.inState(self, EntityStates.DESTROYED):
                if transtitionActions:
                    LOG_DEBUG('TeamObject::_checkStateSettings - For object %s set effects %s to self.position' % (self._settings.name, self._settings.damageEffects.destroy))
                    EffectManager.g_instance.createWorldEffect(Effects.getEffectId(self._settings.damageEffects.destroy), self.position, {})
                self._clearFromArena(False)
        if EntityStates.inState(self, EntityStates.GAME | EntityStates.WAIT_START):
            self._addToArena()
            self.controllers['modelManipulator'].setVisible(True)
        self.__collisionStateUpdate(True)
        if EntityStates.inState(self, EntityStates.GAME) and not self.vscriptStarted:
            self.vscriptStarted = True
            BigWorld.startEntityScripts(self)
        if self.vscriptStarted and not EntityStates.inState(self, EntityStates.GAME):
            self.vscriptStarted = False
            BigWorld.stopEntityScripts(self)

    def __collisionStateUpdate(self, inWorld):
        needCollision = not EntityStates.inState(self, EntityStates.CREATED) and self.inWorld and inWorld
        if needCollision:
            self.startCollisionDetection()
        else:
            self.stopCollisionDetection()

    def onRespawn(self):
        LOG_TRACE('TeamObject: onRespawn', self.id)
        self.controllers['modelManipulator'].setVisible(False)
        self._clearFromArena(False)

    def set_state(self, oldValue):
        self._checkStateSettings(True)
        self.eOnEntityStateChanged(self.id, oldValue, self.state)

    def getWorldVector(self):
        return Math.Vector3()

    def getSpeed(self):
        return 0.0

    def prepareMatrices(self):
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale((self._settings.modelScaling, self._settings.modelScaling, self._settings.modelScaling))
        self.modelTranslationsMatrix = Math.Matrix()
        productMatrix = Math.MatrixProduct()
        productMatrix.a = scaleMatrix
        productMatrix.b = None
        self.resMatrix = productMatrix
        self.targetMatrix = productMatrix
        return

    def setupMP(self, mp):
        self.resMatrix.b = mp

    def onLeaveWorld(self):
        self.eTeamIndexChanged -= self.updateCompoundColour
        self.controllers['modelManipulator'].eCompoundLoaded -= self.updateCompoundColour
        self._notifyModelManipulatorOwnerChanged(None)
        self._eventManager.clear()
        self._clearFromArena(True)
        modelManipulator = self.controllers.get('modelManipulator', None)
        modelManipulator.setMatrixProvider(None)
        self._unregisterController('modelManipulator')
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.setOwner(None)
            self._unregisterController('turretsLogic')
        self._unregisterController('soundController')
        self._destroyControllers()
        self.model = None
        debug_observable.endObserv(self)
        self.__collisionStateUpdate(False)
        self.eOnTeamObjectLeaveWorld(BigWorld.player(), self.id, self)
        return

    def _addToArena(self):
        if not self.__addedToArena:
            self.__addedToArena = True
        GameEnvironment.g_instance.eAvatarAdded(self)

    def _clearFromArena(self, isLeaveWorld):
        if self.__addedToArena:
            self.__addedToArena = False
        GameEnvironment.g_instance.eAvatarRemoved(self, isLeaveWorld)

    def _directionOnCurrentEnemy(self):
        entity = BigWorld.entities.get(self.lastDamagerID, None)
        if entity:
            vector = entity.position - self.position
            vector.normalise()
            return vector
        else:
            return Math.Vector3(0, 1, 0)
            return

    def set_health(self, oldValue):
        if oldValue > self.health:
            GameEnvironment.g_instance.eAvatarHealthChange(self, oldValue)
        self.eHealthChanged(self.id, self.health, self.lastDamagerID, oldValue, self.maxHealth)

    def getMapTexture(self):
        if self._settings.turretName:
            return HUD_MINIMAP_ENTITY_TYPE_TURRET
        if self._settings.type == TYPE_TEAM_OBJECT.BIG:
            return HUD_MINIMAP_ENTITY_TYPE_TEAM_OBJECT_BASE
        return self._settings.type == TYPE_TEAM_OBJECT.TURRET and HUD_MINIMAP_ENTITY_TYPE_TURRET or HUD_MINIMAP_ENTITY_TYPE_TEAM_OBJECT

    def _initDBSettings(self):
        arenaSettings = db.DBLogic.g_instance.getArenaData(BigWorld.player().arenaType)
        self.__teamObjectArenaData = arenaSettings.getTeamObjectData(self.arenaObjID)
        if self.__teamObjectArenaData:
            modelStrID = self.__teamObjectArenaData['modelID']
            self._settings = db.DBLogic.g_instance.getEntityDataByName(db.DBLogic.DBEntities.BASES, modelStrID)
            if self._settings:
                self.initPartsMap(self.settings.partsSettings)
            else:
                LOG_ERROR("Can't find settings for teamObject", modelStrID)
        else:
            LOG_ERROR("Can't find data for object", self.arenaObjID)

    @property
    def settings(self):
        return self._settings

    def set_isTurretFiring(self, oldValue):
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.onChangeFiring(self.isTurretFiring)
        return

    def set_turretShootSync(self, oldValue):
        LOG_DEBUG(' set_turretTest TO')
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.onChangeShootingSync(self.turretShootSync)
        return

    def addBullet(self, startPos, endPos, bulletSpeed, time, gun, explosionEffect, delay = 0, gunID = 0, dPos = None):
        explosionF = None
        if explosionEffect:
            explosionF = partial(onBulletExplosion, explosionEffect, startPos)
        shellEffect = gun.shellPath != ''
        if shellEffect:
            tm = BigWorld.time()
            if tm - gun.shellSyncTime < gun.shellOutInterval:
                shellEffect = False
            else:
                gun.shellSyncTime = tm
        turretShotStartPos = self.controllers['modelManipulator'].onAddBullet(gunID, delay, shellEffect)
        bulletId = BigWorld.addBullet(startPos if turretShotStartPos is None else turretShotStartPos, endPos, bulletSpeed, time, gun.shootInfo.bulletRenderType, BULLET_PARAM.FOREIGN, explosionF)
        return bulletId

    def addInvisibleBullet(self, startPos, endPos, bulletSpeed, time, gun, explosionEffect):
        if explosionEffect:
            explosionF = partial(onBulletExplosion, explosionEffect, startPos)
            return BigWorld.addBullet(startPos, endPos, bulletSpeed, time, gun.shootInfo.bulletRenderType, BULLET_PARAM.INVISIBLE, explosionF)

    def updateTurretsRotations(self, gunners):
        modelManipulator = self.controllers.get('modelManipulator', None)
        if modelManipulator:
            modelManipulator.setAxisValue(TURRET_TRACKER_AXIS, gunners)
        return

    def set_turretTargetID(self, oldData):
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic is not None:
            turretsLogic.eTurretTargetChanged(self.turretTargetID)
        soundController = self.controllers.get('soundController', None)
        if soundController:
            for gunnerId, _ in turretsLogic.gunners.iteritems():
                soundController.onTurretTargetChanged(gunnerId, self.turretTargetID)

        return

    def set_timelinesTime(self, oldValue):
        """transfer timeLines state from Cell ScenarioControllerMaster to Client ScenarioControllerSlave"""
        scenarioController = self.controllers.get('scenarioController', None)
        if scenarioController:
            scenarioController.refreshTimelines(self.timelinesTime)
        return

    def set_curStrategyStartTime(self, prevValue):
        movementStrategy = self.controllers.get('movementStrategy', None)
        if movementStrategy:
            movementStrategy.setStartTime(self.curStrategyStartTime)
        return

    def set_curStrategyPausedAt(self, prevValue):
        movementStrategy = self.controllers.get('movementStrategy', None)
        if movementStrategy:
            movementStrategy.setPauseTime(self.curStrategyPausedAt)
        return

    def getDebugInfo(self):
        matrix = Math.Matrix(self.matrix)
        compoundID = self.controllers.get('modelManipulator', None).compoundID
        data = [('ID', self.id),
         ('Name', self.objectName),
         ('arenaObjID', self.arenaObjID),
         ('HP', str(self.health) + '/' + str(self.maxHealth)),
         ('typeName', self._settings.typeName),
         ('LOD', CompoundSystem.getCompoundLOD(compoundID)),
         ('Vis/Prim', '{0}/{1}'.format(self.model.visuals, self.model.primitives)),
         ('DistanceBW', (BigWorld.camera().position - Math.Matrix(self.matrix).translation).length),
         ('Class', self.__class__.__name__),
         ('Parts', '{0}|{1}'.format(len(self.partStates), ','.join([ '{0}:{1}'.format(pID, pValue) for pID, pValue in self.partStates ]))),
         ('State', EntityStates.getStateName(self.state)),
         ('YPR,S', '({0:.2},{1:.2},{2:.2}),{3:.3}'.format(math.degrees(matrix.yaw), math.degrees(matrix.pitch), math.degrees(matrix.roll), math.pow(matrix.determinant, 1.0 / 3.0))),
         ('ACType', SETTINGS.GROUND_OBJECT_TYPE.getName(self.areaConquestType))]
        if self.__teamObjectArenaData['DsName']:
            data.append(('DsName', self.__teamObjectArenaData['DsName']))
        if self.scenarioName:
            timeLineData = '{0}[{1}]'.format(self.scenarioName, ','.join([ '{0}:{1}'.format(i, int(BigWorld.serverTime() - time) if time != -1 else 'N') for i, time in enumerate(self.timelinesTime) ]))
            data.append(('scenarioName', timeLineData))
        return data

    def getDebugMarkerCaption(self):
        if not hasattr(self, 'teamIndex'):
            return '\\cFFFFFFCC; BAD OBJECT:\n NOT TEAM INDEX\n {id}'.format(id=self.id)
        healthText = '{health}/{maxHealth}'.format(health=int(self.health), maxHealth=int(self.maxHealth))
        if self.teamIndex == BigWorld.player().teamIndex:
            return '\\c0000FFCC; Friendly ground\n {id}\n{health}'.format(id=self.id, health=healthText)
        elif self.teamIndex == TEAM_ID.TEAM_2:
            return '\\cAA9900CC; Neutral ground\n {id}\n{health}'.format(id=self.id, health=healthText)
        else:
            return '\\cFF0000CC; Enemy ground\n {id}\n{health}'.format(id=self.id, health=healthText)

    def useCollisionModel(self):
        return False

    def getPartsTypeData(self, pID = None, isConsiderDead = False):
        partsData = list()
        if self.settings is not None:
            partStates = dict(self.partStates)
            for partTuple in self.settings.partsSettings.getPartsList():
                upgrade = None
                partID = partTuple[0]
                if pID is not None and pID != partID:
                    continue
                partDB = partTuple[1]
                for it in self.partTypes:
                    if it['key'] == partID:
                        upgrade = partDB.getPartType(it['value'])
                        break

                if not upgrade:
                    upgrade = partDB.getFirstPartType()
                if upgrade.bboxes.list:
                    isArmored = False
                    for bbox in upgrade.bboxes.list:
                        if bbox.absorption < 1:
                            isArmored = True
                            break

                    partState = partStates.get(partID, 1)
                    if partState in upgrade.states:
                        isDead = self.__isPartDead(upgrade, partState)
                        if not isDead or isConsiderDead:
                            partsData.append({'isDead': isDead,
                             'partId': partID,
                             'isFiring': upgrade.componentType == 'Gunner',
                             'isArmored': isArmored})
                    else:
                        LOG_WARNING('getPartsTypeData - partState not in states', partID, partState, upgrade.states, partStates)

        else:
            LOG_ERROR('getPartsTypeData - settings is not loaded', self.id)
        return partsData

    def useAutoAimMode(self):
        return TEAM_OBJECT_AUTO_AIMING_ENABLED

    def __isPartDead(self, upgrade, partState):
        return upgrade.states[partState].stateHelthCfc == 0

    def isPartStateAimable(self, presentPartsMap, partID, state):
        return presentPartsMap[partID].states[state].stateHelthCfc > 0

    def sendCustomEventToCell(self, eventName, planName, paramList):
        self.cell.customEventFromClient(eventName, planName, paramList)

    def customEventFromCell(self, eventName, planName, paramList):
        BigWorld.passEventToVisualScript(self, eventName, planName, paramList)

    def globalEventFromCell(self, eventName, channelList, paramList, aspectsList):
        pass

    def updateCompoundColour(self, *args, **kwargs):
        """Update compound colour based on team index. Called on enter world,
        on ModelManipulator3.eCompoundLoaded and on TeamObject.eTeamIndexChanged events
        """
        self._logger.debug('updateCompoundColour: teamIndex={0}'.format(self.teamIndex))
        modelManipulator = self.controllers.get('modelManipulator')
        if not modelManipulator:
            self._logger.warning('updateCompoundColour: modelManipulator not found')
            return
        compoundID = modelManipulator.compoundID
        if not CompoundSystem.isHandleValid(compoundID):
            self._logger.debug('updateCompoundColour: invalid compoundID'.format(self.teamIndex))
            return
        if self.teamIndex == TEAM_ID.TEAM_2:
            pick = SETTINGS.TEAM_OBJECTS_PAINTING.NEUTRAL_INDEX
        else:
            player = BigWorld.player()
            if self.teamIndex == player.teamIndex:
                pick = SETTINGS.TEAM_OBJECTS_PAINTING.ALLY_INDEX
            else:
                pick = SETTINGS.TEAM_OBJECTS_PAINTING.ENEMY_INDEX
        tilesCount = SETTINGS.TEAM_OBJECTS_PAINTING.TILES_COUNT
        CompoundSystem.setCompoundPick(compoundID, tilesCount, pick)

    def set_teamIndex(self, oldValue):
        self.eTeamIndexChanged(self.teamIndex)
        self.setGameTeamIndex(self.teamIndex)