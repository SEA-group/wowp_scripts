# Embedded file name: scripts/client/Avatar.py
import BigWorld
import Math
from BWLogging import getLogger
from Math import Vector3
import CompoundSystem
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from MathExt import clamp
from _airplanesConfigurations_db import airplanesConfigurations, getAirplaneConfiguration
import _preparedBattleData_db
import db.DBLogic
from consts import *
from gui.HUDconsts import *
import updatable.UpdatableManager
from EntityHelpers import EntityStates, movementAbsToSpeed, isAvatar, getPartEnum, DummyPartBase, canAimToEnemyEntity, TurretsStateHandler
from Helpers.ActionMatcher import ActionMatcher, isUpdateAvatarAnimation
from Helpers.i18n import localizeAirplane
from debug_utils import *
import debug_observable
import functools
import EffectManager
import MapEffectsSettings
from db.DBEffects import Effects
import GameEnvironment
from ControllerManager import ControllerManager
import StaticModels
from CollidableObject import CollidableObject
from Event import Event, EventManager
from HelperFunctions import enumToString
from _performanceCharacteristics_db import airplanes as airplanes_PC
from clientConsts import BULLET_PARAM, EFFECT_COLLISION_RANGE, TURRET_TRACKER_AXIS, ALTITUDE_DX, EFFECTS_NAMES
import clientConsts
from SyncedRandom import SyncedRandom
import random
from ArenaHelpers.GameModes.AreaConquest.AvatarComponents import TacticalRespawnAvatarMixin, pauseInTacticalRespawn
from Achievements.AvatarAchievementsInterfaceClient import AvatarAchievementsInterfaceClient
from QuestsCommon.AvatarQuestsInterfaceClient import AvatarQuestsInterfaceClient
from audio import GameSound
from audio.SoundObjects.HitSound import HitSFXFactory
from audio.SoundObjects.ExplosionSound import ExplosionSFXFactory
from turrets.AvatarMoveHistory import AvatarMoveHistory
from modelManipulator.PartAnimatorControllers.BombHatchAnimator import BombHatchAnimator
from modelManipulator.PartAnimatorControllers.TurretAnimator.TurretsLogicAnimatorAdapter import TurretsLogicAnimatorAdapter, TURRET_ANIMATOR_ADAPTER_CONTROLLER_NAME
EFFECT_CHECK_FREQUENCY = 0.5

class AvatarDummyPart(DummyPartBase):

    def __init__(self, partsSettings, partID, stateID, authorID = 0, damageReason = 0):
        super(AvatarDummyPart, self).__init__(partsSettings, partID, stateID)
        self.name = partsSettings.getPartByID(partID).name
        self.logicalState = getPartLogicalState(stateID)
        self.authorID = authorID
        self.damageReason = damageReason
        self.enumName = getPartEnum(self.partTypeData)
        self.isAlive = self.logicalState != OBJ_STATES.DESTROYED


def isEntityInWorld(fn):

    @functools.wraps(fn)
    def wrapped(*args, **kw):
        if args[0].inWorld:
            return fn(*args, **kw)

    return wrapped


def onBulletExplosion(effectId, isPlayer, effectPosition, bulletDir = None, victim = None):
    MAX_DIST_TO_CAMERA = 500
    distToCamera = BigWorld.camera().position.distTo(effectPosition)
    if distToCamera < MAX_DIST_TO_CAMERA:
        params = {'variant': 'OWN' if isPlayer else 'OTHER'}
        if victim and isAvatar(victim):
            params['entity'] = victim
        if bulletDir:
            params['rotation'] = Math.Vector3(bulletDir.yaw, bulletDir.pitch, 0)
        if victim:
            player = BigWorld.player()
            if victim == player:
                params['sfx'] = HitSFXFactory.AVATAR_EFFECT_HIT
            elif player.curVehicleID == victim.id:
                params['sfx'] = HitSFXFactory.NPC_EFFECT_HIT
        EffectManager.g_instance.createWorldEffect(effectId, effectPosition, params)


class ControllersNames(object):
    """Avatar controllers names enum
    """
    WEAPONS = 'weapons'
    TURRETS_LOGIC = 'turretsLogic'
    SHELLS_CONTROLLER = 'shellController'
    MODEL_MANIPULATOR = 'modelManipulator'
    SOUND_CONTROLLER = 'soundController'


class Avatar(BigWorld.Entity, ControllerManager, CollidableObject, AvatarMoveHistory, TacticalRespawnAvatarMixin, AvatarAchievementsInterfaceClient, AvatarQuestsInterfaceClient):

    def __init__(self):
        ControllerManager.__init__(self)
        CollidableObject.__init__(self)
        TacticalRespawnAvatarMixin.__init__(self)
        AvatarAchievementsInterfaceClient.__init__(self)
        AvatarQuestsInterfaceClient.__init__(self)
        self.className = self.__class__.__name__
        self.filter = self.createFilter()
        self.filter.airplaneFilter = False
        self.filter.speedCalculateEnable = True
        self._settings = None
        self.actionMatcher = None
        self.targetMatrix = None
        self.clientIsReady = False
        self.__destroyCallback = None
        self.__hideModelCallback = None
        self.lastArmamentStates = 0
        self._leaveGame = False
        self.arenaVscriptStarted = False
        self.syncedRandom = SyncedRandom()
        self.turretsState = TurretsStateHandler()
        self.__lastPartStates = {}
        self._autoStartEffects = []
        EffectManager.Init()
        self.__lastPlaneAngles_forGFXs = (0, 0, 0)
        self.__lastPlaneRotation_forGFXs = None
        return

    @property
    def stallSpeed(self):
        return airplanes_PC[self.globalID].stallSpeed / 3.6

    @property
    def reductionPoint(self):
        return self._settings.airplane.flightModel.weaponOptions.reductionPoint * WORLD_SCALING

    @property
    def settings(self):
        """Plane static settings
        """
        return self._settings

    @settings.setter
    def settings(self, value):
        """Plane static settings setter.
        """
        if self._settings != value:
            self._settings = value
            self._onPlaneSettingsChanged()

    @property
    def engineSettings(self):
        engineId = self.logicalParts[LOGICAL_PART.ENGINE]
        return self.settings.airplane.flightModel.engine[engineId]

    def _onPlaneSettingsChanged(self):
        """Updates collision model if plane settings was changed
        """
        if self.settings:
            self.initPartsMap(self._settings.airplane.partsSettings)
            self.prepareMatrices()

    def updatePlaneConfiguration(self):
        config = airplanesConfigurations[self.globalID]
        self.planeID = config.planeID
        self.logicalParts = config.logicalParts
        self.weaponSlots = config.weaponSlots
        self._updateHeightLevels()
        self.loadPlaneSettings()
        self.aircraftClass = self._settings.airplane.planeType
        self.planeConfigurationChanged()

    def _updateHeightLevels(self):
        pbd = _preparedBattleData_db.preparedBattleData[self.globalID]
        self.heightOptimal = pbd.altimeter[4] * pbd.altimeter[-1]
        self.heightCritical = pbd.altimeter[5] * pbd.altimeter[-1]
        self.heightMax = pbd.altimeter[-1]

    def set_globalID(self, oldValue):
        if self.globalID != oldValue:
            self.updatePlaneConfiguration()

    def loadPlaneSettings(self):
        """Update plane settings from db
        """
        self.settings = db.DBLogic.g_instance.getAircraftData(self.planeID)

    def _createEvents(self):
        if hasattr(self, '_eventManager'):
            return False
        self._eventManager = EventManager()
        self.ePartStateChanged = Event(self._eventManager)
        self.eHealthChanged = Event(self._eventManager)
        self.eTeamIndexChanged = Event(self._eventManager)
        self.eOnEntityStateChanged = Event(self._eventManager)
        self.eCurrentSectorChanged = Event(self._eventManager)
        self.eRepair = Event(self._eventManager)
        self.eUnderRepairZoneInfluence = Event(self._eventManager)
        self.eUpdateConsumables = Event(self._eventManager)
        self.eLeaveWorldEvent = Event(self._eventManager)
        self.eSetBombTargetVisible = Event(self._eventManager)
        self.eUpdateHUDAmmo = Event(self._eventManager)
        self.eOnGunGroupFire = Event(self._eventManager)
        self.ePartFlagSwitchedNotification = Event(self._eventManager)
        self.eOnAvatarStateChanged = Event(self._eventManager)
        self.eTurretSetTarget = Event(self._eventManager)
        self.eTurretSetFireFlag = Event(self._eventManager)
        self.shellLaunched = Event(self._eventManager)
        self.planeConfigurationChanged = Event(self._eventManager)
        return True

    def debugViewer_addNewKey(self, dvKey, str_data):
        raise

    def debugViewer_removeKey(self, dvKey):
        raise

    def debugViewer_pushToView(self, str_data):
        raise

    def receiveOperationTimeout(self, invocationId):
        pass

    def clientReceiveResponse(self, responseType, sequenceId, invocationId, operationCode, argStr):
        pass

    def updateArena(self, functionIndex, updateFunctionID, argStr):
        pass

    def onStreamComplete(self, dataId, data):
        pass

    def getSettings(self):
        return self.settings

    def updateLocalizedName(self):
        self.localizedName = localizeAirplane(self.settings.airplane.name)

    @property
    def partTypes(self):
        return airplanesConfigurations[self.globalID].partTypes

    def _preStateChangeInit(self):
        pass

    def onEnterWorld(self, prereqs):
        self.setGameTeamIndex(self.teamIndex)
        self._createEvents()
        self._lastIsFire = False
        self.updatePlaneConfiguration()
        self.__updateEffectsCallback = None
        self.__engineDeltaPosList = None
        self.groundParticleName = {}
        self._groundParticles = {}
        self._killingInfo = None
        self.__prereqsHolder = prereqs
        self.extUpgrades = {LOGICAL_PART.PILOT: self.pilotBodyType}
        LOG_TRACE('Avatar: onEnterWorld', self.id, self.extUpgrades)
        self.updateLocalizedName()
        self.prepareMatrices()
        self.__createControllers()
        self._preStateChangeInit()
        self._setCrossHeirMatrix()
        self._checkStateSettings(EntityStates.UNDEFINED, self.state, False)
        if EntityStates.inState(self, EntityStates.GAME | EntityStates.WAIT_START | EntityStates.PRE_START_INTRO):
            self.__addToArena()
        self.updatePartStates()
        self.startCollisionDetection()
        player = BigWorld.player()
        if self is not player:
            player.onAvatarEnterWorld(self)
        self._createPersistentEffecs()
        self._updateEffects()
        self._notifyModelManipulatorOwnerChanged(self)
        self._bha = BombHatchAnimator(self)
        AvatarMoveHistory._makeLocalProperties(self)
        self._updateMoveHistoryID = BigWorld.callback(0.35, self._updateMoveHistory)
        self._subscribe()
        debug_observable.startObserv(self)
        arena = GameEnvironment.getClientArena()
        arena.onAvatarEnterWorld(self)
        self.updatePartStates(True)
        self.__updatePartFlags()
        return

    def _updateMoveHistory(self):
        self._updateMoveHistoryID = BigWorld.callback(0.35, self._updateMoveHistory)
        AvatarMoveHistory.updateMoveHistory(self, Vector3(self.position))

    def getSuperiorityPointsByGroupPartId(self, groupID):
        return 0

    def useCollisionModel(self):
        return False

    def useAutoAimMode(self):
        return 1

    @property
    def mouseDirection(self):
        return None

    def syncUpdatableState(self, updatableID, stateID, time):
        if updatable.UpdatableManager.g_instance:
            updatable.UpdatableManager.g_instance.setUpdatableState(updatableID, stateID, time)

    def createUpdatable(self, updatableTypeId, resourceID, args):
        if updatable.UpdatableManager.g_instance:
            updatable.UpdatableManager.g_instance.createUpdatable(updatableTypeId, resourceID, args)
            if updatableTypeId == UPDATABLE_TYPE.BOMB:
                settings = self.controllers['shellController'].getShellCommonData(SHELL_INDEX.TYPE2)
                launch_time = settings['portionTempo'] * max(0, settings['portion'] - 1)
                self._bha.launchBombsHatchAnimation(launch_time)

    def _applyFakeRotationMtx(self, rawRealMtx):
        return rawRealMtx

    def _setCrossHeirMatrix(self):
        pass

    def prepareMatrices(self):
        self.realMatrix = self.matrix
        self.realMatrix.notModel = True
        self.fakeRealMatrix = self._applyFakeRotationMtx(self.realMatrix)
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale((AIRCRAFT_MODEL_SCALING, AIRCRAFT_MODEL_SCALING, AIRCRAFT_MODEL_SCALING))
        scaleProduct = Math.MatrixProduct()
        scaleProduct.a = Math.Matrix()
        scaleProduct.b = scaleMatrix
        self.resMatrix = Math.MatrixProduct()
        HPMassOffset = Math.Matrix()
        if self.settings.hpmass.mass:
            HPMassOffset.translation = -Math.Vector3(self.settings.hpmass.mass.position)
        else:
            HPMassOffset.translation = Math.Vector3(0, 0, 0)
        HPMassShiftedMatrix = Math.MatrixProduct()
        HPMassShiftedMatrix.a = HPMassOffset
        HPMassShiftedMatrix.b = self.fakeRealMatrix
        self.resMatrix.a = scaleProduct
        self.resMatrix.b = HPMassShiftedMatrix
        offsetMatrix = Math.Matrix()
        offsetMatrix.translation = CUR_TARGET_INFO_WORLD_OFFSET
        self.targetMatrix = Math.MatrixProduct()
        self.targetMatrix.a = self.fakeRealMatrix
        self.targetMatrix.b = offsetMatrix
        self.mapMatrix = Math.MatrixProduct()
        self.mapMatrix.a = self.fakeRealMatrix

    def createFilter(self):
        return BigWorld.PredictionFilter()

    def movementFilter(self):
        return self.filter.__class__ == BigWorld.PredictionFilter

    def getWorldVector(self):
        if self.movementFilter():
            return self.filter.velocity
        else:
            return Math.Vector3(0.0, 0.0, 0.0)

    def getRotationSpeed(self):
        rs = Math.Vector3(0, 0, 0)
        if self.movementFilter():
            rs = self.filter.rotationSpeed
        return rs

    def getSpeed(self):
        if self.movementFilter():
            return movementAbsToSpeed(self.filter.velocity.length / WORLD_SCALING)
        else:
            return 0.0

    def __addToArena(self):
        GameEnvironment.g_instance.eAvatarAdded(self)

    def __clearFromArena(self, isLeaveWorld):
        GameEnvironment.g_instance.eAvatarRemoved(self, isLeaveWorld)
        if self.actionMatcher != None:
            self.actionMatcher.destroy()
            self.actionMatcher = None
        return

    def getRotation(self):
        quatRotation = Math.Quaternion()
        quatRotation.fromEuler(self.roll, self.pitch, self.yaw)
        return quatRotation

    def unregisterModelManipulator(self):
        modelManipulator = self.controllers.get('modelManipulator', None)
        self.model = None
        if modelManipulator is not None:
            if modelManipulator.entityId == self.id:
                modelManipulator.setMatrixProvider(None)
            self._unregisterController('modelManipulator')
        return

    def _unregisterControllers(self):
        self.unregisterModelManipulator()
        weapons = self.controllers['weapons']
        weapons.setOwner(None)
        self.ePartStateChanged -= weapons.onPartStateChanged
        self._unregisterController('weapons')
        t = self.controllers.get(TURRET_ANIMATOR_ADAPTER_CONTROLLER_NAME, None)
        if t:
            self._unregisterController(TURRET_ANIMATOR_ADAPTER_CONTROLLER_NAME)
            t.destroy()
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.setOwner(None)
            self._unregisterController('turretsLogic')
        self._unregisterController('soundController')
        self._destroyControllers()
        return

    def onLeaveWorld(self):
        self.eLeaveWorldEvent()
        self._unsubscribe()
        self._notifyModelManipulatorOwnerChanged(None)
        LOG_TRACE('Avatar: onLeaveWorld', self.id)
        player = BigWorld.player()
        if self is not player:
            player.onAvatarLeaveWorld(self)
        self.__clearFromArena(True)
        self._unregisterControllers()
        self.stopCollisionDetection()
        if self.__updateEffectsCallback is not None:
            BigWorld.cancelCallback(self.__updateEffectsCallback)
        if self.__destroyCallback:
            BigWorld.cancelCallback(self.__destroyCallback)
        if self.__hideModelCallback:
            BigWorld.cancelCallback(self.__hideModelCallback)
        if self._updateMoveHistoryID:
            BigWorld.cancelCallback(self._updateMoveHistoryID)
        self._bha.dispose()
        for engineParticles in self._groundParticles.itervalues():
            for particle in engineParticles.itervalues():
                map(lambda eff: eff.destroy(), particle)

        self._groundParticles = {}
        TacticalRespawnAvatarMixin.onLeaveWorld(self)
        AvatarAchievementsInterfaceClient.onLeaveWorld(self)
        AvatarQuestsInterfaceClient.onLeaveWorld(self)
        debug_observable.endObserv(self)
        arena = GameEnvironment.getClientArena()
        arena.onAvatarLeaveWorld(self)
        self._eventManager.clear()
        return

    def onLeaveSpace(self):
        pass

    def updateDebugHUD(self, args):
        pass

    def reportBattleResult(self, battleResult):
        pass

    def set_force(self, oldData):
        pass

    def set_nitroPrc(self, oldValue):
        pass

    def set_bullets(self, oldData):
        pass

    @pauseInTacticalRespawn
    def set_consumables(self, oldData):
        self.controllers['modelManipulator'].updateConsumablesEffects(self.consumables)
        self.eUpdateConsumables(self.consumables)

    def reportDestruction(self, killingInfo):
        player = BigWorld.player()
        if killingInfo['killerID'] == player.id and killingInfo['victimID'] == self.id:
            if self.state & EntityStates.DEAD:
                dist = (self.position - BigWorld.player().position).length
                EffectManager.g_instance.enemyKillEffect(killingInfo, dist)
                self._killingInfo = None
            else:
                self._killingInfo = killingInfo
        return

    def reportGainAward(self, awardInfo):
        pass

    def __updateDamagedSounds(self, hpLostNorm):
        pass

    def _updateDamageEffects(self, effectPosition, effectForce):
        if self.isPlayer():
            sfx = HitSFXFactory.AVATAR_EFFECT_HIT
        else:
            sfx = HitSFXFactory.NPC_EFFECT_HIT
        damageEffects = self.settings.airplane.visualSettings.damageEffects
        if self.damagedByGunID:
            gunDescription = db.DBLogic.g_instance.getComponentByIndex(COMPONENT_TYPE.GUNS, self.damagedByGunID)
            gunProfile = db.DBLogic.g_instance.getGunProfileData(gunDescription.gunProfileName)
            damageEffects = gunProfile
        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.receive_damage_other_1), effectPosition, {'force': effectForce,
         'sfx': sfx})
        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.receive_damage_other_2), effectPosition, {'sfx': sfx})

    def __getLastDamagePosition(self):
        partId = self.lastDamagedPartID
        if partId == -1:
            partName = random.choice(clientConsts.DAMAGED_PARTS_NAMES)
            part = self.settings.airplane.partsSettings.getPartByName(partName)
            partId = part.partId if part else 1
        matrix = Math.Matrix(self.resMatrix)
        size = self.getPartBBoxSize(partId)
        rndOffset = (-size + Math.Vector3(random.random() * size.x, random.random() * size.y, random.random() * size.z)) * 0.5
        pos = self.getPartBBoxPos(partId) + rndOffset
        damagedModelPosition = matrix.applyPoint(pos * (1.0 / WORLD_SCALING))
        return damagedModelPosition

    def set_teamIndex(self, oldTeamIndex):
        self.eTeamIndexChanged(self.teamIndex)
        self.setGameTeamIndex(self.teamIndex)

    def set_health(self, oldValue):
        if oldValue > self.health:
            hpLostNorm = (oldValue - self.health) / self.maxHealth
            parCount = clamp(1.0, hpLostNorm * 10.0, 40.0)
            self._updateDamageEffects(self.__getLastDamagePosition(), parCount)
            hitSFXManager = GameSound().hitSFXManager
            if hitSFXManager and HitSFXFactory.canPlay(self.id, self.health, oldValue, self.lastDamagerID, self.lastDamageReason):
                if self.isPlayer():
                    hitSoundEvent = HitSFXFactory.AVATAR_LOGIC_HIT
                    if self.damagedByGunID:
                        gunDescription = db.DBLogic.g_instance.getComponentByIndex(COMPONENT_TYPE.GUNS, self.damagedByGunID)
                        gunProfile = db.DBLogic.g_instance.getGunProfileData(gunDescription.gunProfileName)
                        hitSoundEvent = gunProfile.sounds.playerAvatarGotHitEvent
                    hitSFXManager.play(self.id, None, hitSoundEvent, self.lastDamageReason, enemyID=self.lastDamagerID)
                else:
                    player = BigWorld.player()
                    if self.teamIndex != player.teamIndex:
                        hitSFXManager.play(self.id, None, HitSFXFactory.NPC_LOGIC_HIT, self.lastDamageReason)
            GameEnvironment.g_instance.eAvatarHealthChange(self, oldValue)
            self._checkDamagerAccessibility(self.lastDamagerID)
        self.eHealthChanged(self.id, self.health, self.lastDamagerID, oldValue, self.maxHealth)
        return

    def _checkDamagerAccessibility(self, damagerID):
        isLocalPlayer = BigWorld.player() == self
        if not isLocalPlayer or damagerID <= 0 or damagerID == self.id:
            return
        e = BigWorld.entities.get(damagerID)
        if not e:
            LOG_ERROR('Damaged by inaccessible entity {iD}'.format(iD=damagerID))

    @isEntityInWorld
    def setNested_partStates(self, path, value):
        item = self.partStates[path[0]]
        LOG_DEBUG(self.id, 'setNested_partStates', item)
        partTypeData = self.presentPartsMap[item[0]]
        self.set_partStates(None)
        return

    def set_partStates(self, oldPartStates):
        LOG_DEBUG(self.id, 'set_partStates', [ (partID, state) for partID, state in self.partStates ])
        self.updatePartStates(True)
        self.onPartStatesUpdated()

    def set_lastDamagerID(self, prevLastDamagerID):
        GameEnvironment.g_instance.eAvatarChangeLastDamagerID(self)

    def updatePartStates(self, curTimeAction = False):
        modelManipulator = self.controllers.get('modelManipulator')
        if modelManipulator:
            modelManipulator.velocity = self.getWorldVector()
            if EntityStates.inState(self, EntityStates.DESTROYED):
                modelManipulator.velocity *= 0.1
            modelManipulator.updateStatesNet(self.partStates, curTimeAction)
            if EntityStates.inState(self, EntityStates.DESTROYED_FALL):
                for _, partState in self.partStates:
                    if partState == PART_STATS_STATE.CRIT:
                        modelManipulator.criticalDamage()

            elif EntityStates.inState(self, EntityStates.GAME_CONTROLLED):
                if curTimeAction:
                    self.startCollisionDetection()
                if not self.isPlayer():
                    player = BigWorld.player()
                    if self.lastDamagerID == player.id and self.teamIndex != player.teamIndex:
                        for partID, partState in self.partStates:
                            if partID == self.lastDamagedPartID:
                                if partState >= 2:
                                    reportedIDs = player.reportedDamagedPartsByEntity.get(self.id, None)
                                    if reportedIDs:
                                        if self.lastDamagedPartID in reportedIDs and reportedIDs[self.lastDamagedPartID] == partState:
                                            break
                                        else:
                                            reportedIDs[self.lastDamagedPartID] = partState
                                    else:
                                        player.reportedDamagedPartsByEntity[self.id] = {self.lastDamagedPartID: partState}
                                break

            for partID, stateID in self.partStates:
                lastState = self.__lastPartStates.get(partID)
                if lastState is None or lastState != stateID:
                    part = AvatarDummyPart(self.settings.airplane, partID, stateID)
                    self.__lastPartStates[partID] = stateID
                    self.ePartStateChanged(part)
                    if PART_STATS_STATE.CRIT == stateID:
                        self.onVictimInformAboutCrit(partID, self.id, stateID)

        return

    def onVictimInformAboutCrit(self, partID, victimID, partState):
        player = BigWorld.player()
        if self.lastDamagerID == player.id and canAimToEnemyEntity(player, self) and EffectManager.g_instance:
            EffectManager.g_instance.enemyCritEffect()

    def __getTerrainPointAndMaterial(self):
        toPos = self.position + self.getRotation().rotateVec(Math.Vector3(0, 0, EFFECT_COLLISION_RANGE))
        heightCollide = BigWorld.hm_collideSimple(self.spaceID, self.position, toPos)
        if heightCollide is not None:
            try:
                materialName = None
                materialName = db.DBLogic.g_instance.getMaterialName(heightCollide[1])
            except:
                pass

            return (heightCollide[0], materialName)
        else:
            return (self.position, None)
            return

    def __floodModel(self):
        matrix = BigWorld.DropMatrixProvider()
        matrix.velocity = Math.Vector3(0, -0.2, 0) * WORLD_SCALING
        matrix.acceleration = Math.Vector3(0, -0.5, 0) * WORLD_SCALING
        matrix.rotationSpeed = Math.Quaternion(0, 0, 0, 1)
        matrix.setMatrix(self.resMatrix)
        modelManipulator = self.controllers['modelManipulator']
        modelManipulator.setMatrixProvider(matrix)

    def __landModel(self, startPosition):
        crashMatrix = Math.Matrix(self.resMatrix)
        crashMatrix.translation = startPosition
        modelManipulator = self.controllers['modelManipulator']
        modelManipulator.setMatrixProvider(crashMatrix)

    def __fallModel(self):
        LOG_TRACE('Avatar: __fallModel', self.id)
        matrix = BigWorld.DropMatrixProvider()
        matrix.velocity = Math.Vector3(0, -10, 0) * WORLD_SCALING
        matrix.acceleration = Math.Vector3(0, -5, 0) * WORLD_SCALING
        matrix.rotationSpeed = Math.Quaternion(-random.random() - 1, 0, random.random() - 0.5, 1)
        matrix.setMatrix(self.resMatrix)
        modelManipulator = self.controllers['modelManipulator']
        modelManipulator.setMatrixProvider(matrix)
        import BattleReplay
        if BattleReplay.isPlaying():
            self.__hideModelCallback = BattleReplay.callback(10, self.__hideModel)
        else:
            self.__hideModelCallback = BigWorld.callback(10, self.__hideModel)

    def __hideModel(self):
        LOG_TRACE('Avatar: __hideModel', self.id)
        self.__hideModelCallback = None
        StaticModels.popModel(self.id)
        modelManipulator = self.controllers.get('modelManipulator', None)
        modelManipulator.setMatrixProvider(None)
        self.model = None
        return

    def __getExplosionSoundEvent(self):
        event = None
        if self.isPlayer():
            event = ExplosionSFXFactory.AVATAR_EXPLOSION
        elif self.lastDamagerID == BigWorld.player().id:
            event = ExplosionSFXFactory.NPC_EXPOSION_FRAG
        elif self.lastDamageReason:
            event = ExplosionSFXFactory.NPC_EXPLOSION
        return event

    def crashPlane(self, thisMomentAction, pos, oldState):
        LOG_TRACE('Avatar: crashPlane', self.id, self.lastDamageReason)
        self.__destroyCallback = None
        self.stopCollisionDetection()
        if StaticModels.isInStaticModelsList(self.id):
            LOG_TRACE('Avatar: crashPlane, isInStaticModelsList', self.id)
            return
        else:
            if not EntityStates.inState(self, EntityStates.DESTROYED):
                LOG_ERROR('Avatar not in DESTROYED state')
            terrainPoint, materialName = self.__getTerrainPointAndMaterial()
            destroyedOnWater = materialName == 'water'
            overTerrain = materialName is None
            if thisMomentAction:
                damageEffects = self.settings.airplane.visualSettings.damageEffects
                effectProps = {'variant': 'OWN' if self.isPlayer() else 'OTHER'}
                if overTerrain:
                    if oldState != EntityStates.DESTROYED_FALL:
                        effectProps['exp'] = self.__getExplosionSoundEvent()
                    EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.destroy_air), pos, effectProps)
                else:
                    effectPropsSFX = effectProps.copy()
                    if destroyedOnWater:
                        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.destroy_terrain if self.lastDamageReason == DAMAGE_REASON.TERRAIN else damageEffects.destroy_water), terrainPoint, effectPropsSFX)
                    else:
                        if oldState != EntityStates.DESTROYED_FALL:
                            effectPropsSFX['exp'] = self.__getExplosionSoundEvent()
                        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.destroy_terrain), terrainPoint, effectPropsSFX)
                        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(damageEffects.crashed_fire), terrainPoint, effectProps)
            oldModel = self.model
            self._selectModel()
            if oldModel:
                oldModel.delMotor(oldModel.motors[0])
            if overTerrain:
                self.__fallModel()
            elif destroyedOnWater:
                self.__floodModel()
            else:
                self.__landModel(terrainPoint)
            StaticModels.addModel(self.id, oldModel)
            return

    def _selectModel(self, forceFake = False):
        if forceFake or EntityStates.inState(self, EntityStates.DESTROYED | EntityStates.OBSERVER):
            self.__setModel(BigWorld.Model('objects/fake_model.model'))
        else:
            modelManipulator = self.controllers['modelManipulator']
            if StaticModels.isInStaticModelsList(self.id):
                self.__setModel(StaticModels.popModel(self.id))
            else:
                self.__setModel(modelManipulator.getRootModel())
            modelManipulator.setMatrixProvider(self.resMatrix)

    def __setModel(self, model):
        self.model = None
        self.model = model
        self.model.delMotor(self.model.motors[0])
        self.model.addMotor(BigWorld.Servo(self.resMatrix))
        LOG_TRACE('Avatar: __setModel', self.id, model)
        return

    def onRespawn(self):
        if self.__hideModelCallback:
            BigWorld.cancelCallback(self.__hideModelCallback)
        LOG_TRACE('Avatar: onRespawn', self.id)
        self._selectModel()
        self.startCollisionDetection()

    def _checkStateSettings(self, oldState, state, transitionActions):
        self.setGameState(self.state)
        self.controllers['modelManipulator'].setState(state, transitionActions)
        GameSound().onStateChanged(self, oldState, state)
        self.eOnEntityStateChanged(self.id, oldState, state)
        if state & EntityStates.DESTROYED:
            latency = self.filter.latency if self.movementFilter() else SERVER_TICK_LENGTH
            LOG_TRACE('Avatar: onDESTROYED state', self.id, latency)
            if transitionActions:
                self.__destroyCallback = BigWorld.callback(latency, functools.partial(self.crashPlane, transitionActions, self.position, oldState))
        if state & EntityStates.DESTROYED_FALL:
            LOG_TRACE('Avatar: onDESTROYED_FALL state', self.id)
            if transitionActions:
                effectProps = {'variant': 'OWN' if self.isPlayer() else 'OTHER'}
                effectProps['exp'] = self.__getExplosionSoundEvent()
                EffectManager.g_instance.createWorldEffect(Effects.getEffectId(self.settings.airplane.visualSettings.damageEffects.destroy_air), self.position, effectProps)
        if state & EntityStates.GAME:
            self.__addToArena()
            if not self.actionMatcher:
                self.actionMatcher = ActionMatcher(self, self.isPlayer())
            self.eSetBombTargetVisible(True)
        elif not state & EntityStates.WAIT_START:
            self.eSetBombTargetVisible(False)
        if state & EntityStates.CREATED and transitionActions or not self.isPlayer() and (state & (EntityStates.WAIT_START | EntityStates.PRE_START_INTRO) or oldState == EntityStates.UNDEFINED and state & EntityStates.GAME_CONTROLLED):
            self.setModelVisible(True)
            self.onRespawn()
        if EntityStates.inState(self, EntityStates.DEAD):
            if oldState != EntityStates.UNDEFINED:
                self.__clearFromArena(False)
            if oldState & EntityStates.GAME_CONTROLLED:
                self._onPlaneDestroyed()
            if self._killingInfo is not None:
                dist = (self.position - BigWorld.player().position).length
                EffectManager.g_instance.enemyKillEffect(self._killingInfo, dist)
                self._killingInfo = None
        if EntityStates.inState(self, EntityStates.PRE_START_INTRO):
            mapEntry = GameEnvironment.getClientArena().getMapEntry(self.id)
            if mapEntry:
                self.mapMatrix.a = mapEntry.mapMatrix
            else:
                self.mapMatrix.a = Math.Matrix(self.realMatrix)
        else:
            self.mapMatrix.a = self.realMatrix
        if EntityStates.inState(self, EntityStates.OBSERVER):
            self.setModelVisible(False)
        if self is BigWorld.player():
            if EntityStates.inState(self, EntityStates.GAME) and not self.arenaVscriptStarted:
                self.arenaVscriptStarted = True
                BigWorld.startArenaScripts()
            if self.arenaVscriptStarted and EntityStates.inState(self, EntityStates.END_GAME):
                self.arenaVscriptStarted = False
                BigWorld.stopArenaScripts()
        return

    def onMapEntryCreated(self, mapEntry):
        if EntityStates.inState(self, EntityStates.PRE_START_INTRO):
            self.mapMatrix.a = mapEntry.mapMatrix

    @isEntityInWorld
    def set_state(self, oldValue):
        curState = int(self.state)
        self._checkStateSettings(oldValue, curState, True)

    def set_arenaStartTime(self, oldValue):
        pass

    def updateAmmo(self):
        self.eUpdateHUDAmmo()

    def set_isArenaFreezed(self, oldValue):
        pass

    def _addBulletEffects(self, gunID, gun, delay):
        shellEffect = gun.shellPath != ''
        if shellEffect:
            tm = BigWorld.time()
            if tm - gun.shellSyncTime < gun.shellOutInterval:
                shellEffect = False
            else:
                gun.shellSyncTime = tm
        self.controllers['modelManipulator'].onAddBullet(gunID, delay, shellEffect)

    def addBullet(self, startPos, endPos, bulletSpeed, time, gun, explosionEffect, delay = 0, gunID = 0, dPos = None):
        gunID = gunID or gun.uniqueId
        explosionF = functools.partial(onBulletExplosion, explosionEffect, self.isPlayer()) if explosionEffect else None
        self._addBulletEffects(gunID, gun, delay)
        if dPos:
            return BigWorld.addBullet(startPos, endPos, bulletSpeed, time, gun.shootInfo.bulletRenderType, BULLET_PARAM.OWN if self.isPlayer() else BULLET_PARAM.FOREIGN, explosionF, self.id, dPos)
        else:
            return BigWorld.addBullet(startPos, endPos, bulletSpeed, time, gun.shootInfo.bulletRenderType, BULLET_PARAM.OWN if self.isPlayer() else BULLET_PARAM.FOREIGN, explosionF)
            return

    def addInvisibleBullet(self, startPos, endPos, bulletSpeed, time, gun, explosionEffect):
        if explosionEffect:
            explosionF = functools.partial(onBulletExplosion, explosionEffect, self.isPlayer())
            return BigWorld.addBullet(startPos, endPos, bulletSpeed, time, gun.shootInfo.bulletRenderType, BULLET_PARAM.INVISIBLE, explosionF)

    def getShootingControllerPosition(self):
        return self.position

    def getShootingControllerRotation(self):
        res = Math.Quaternion()
        res.fromEuler(self.roll, self.pitch, self.yaw)
        return self.filter.shootCorrection(float(self.fmTimeOffset) / 255).mul(res)

    def updateTurretsRotations(self, gunners):
        modelManipulator = self.controllers.get('modelManipulator', None)
        if modelManipulator:
            modelManipulator.setAxisValue(TURRET_TRACKER_AXIS, gunners)
        return

    def dynamicalDispersionCfc(self):
        return (self.reduction, self.reductionMod)

    def updateSpawnTimer(self, timeLeft):
        pass

    def set_curVehicleID(self, lastValue):
        pass

    def onVehicleChanged(self):
        modelManipulator = self.controllers.get('modelManipulator', None)
        if modelManipulator and self.vehicle is not None:
            modelManipulator.setVisible(False)
        return

    def onReceiveTextMessage(self, senderID, messageType, messageStringID, targetID, message, fromQueue):
        pass

    def onReceiveMarkerMessage(self, senderID, posX, posZ, fromQueue):
        pass

    def isPlayer(self):
        return self.__class__.__name__ == 'PlayerAvatar'

    def syncTurretTargetId(self, turretID, targetID, normAggro):
        self.turretsState.get(turretID).normAggro = normAggro
        self.turretsState.get(turretID).targetID = targetID
        self.eTurretSetTarget(turretID, targetID)

    def syncTurretFireFlag(self, turretID, isFire):
        self.turretsState.get(turretID).isFire = isFire
        self.eTurretSetFireFlag(turretID, isFire)

    def syncGuns(self, data):
        pass

    def deflectionTargetSet(self):
        pass

    def singleShot(self, groups):
        pass

    def singleShotReady(self, groups):
        pass

    def getMapTexture(self):
        return HUD_MINIMAP_ENTITY_TYPE_AVATAR

    def set_shellsCount(self, arrayShellsCount):
        self.controllers['modelManipulator'].setShelsCount(self.shellsCount)
        self.updateAmmo()

    def set_armamentStates(self, oldValue):
        if self.armamentStates != 0:
            self.lastArmamentStates = self.armamentStates

    def set_lockedByTurretsCounter(self, oldValue):
        if oldValue > self.lockedByTurretsCounter and self.lockedByTurretsCounter == 0:
            LOG_DEBUG('lockedByTurretsCounter ON', self.lockedByTurretsCounter, oldValue)
        if oldValue < self.lockedByTurretsCounter and oldValue == 0:
            LOG_DEBUG('lockedByTurretsCounter OFF', self.lockedByTurretsCounter, oldValue)

    def set_isTurretFiring(self, oldValue):
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic:
            turretsLogic.onChangeFiring(self.isTurretFiring)
        return

    def set_shootingSync(self, state):
        self.syncedRandom.state = self.shootingSync
        if COLLISION_RECORDER:
            self.markPosition(3, self.position, 'set_shootingSync({0}), was {1}'.format(self.shootingSync, state))
        weapons = self.controllers.get('weapons', None)
        if weapons:
            weapons.syncGunsRandom()
        return

    def set_turretTargetID(self, oldData):
        turretsLogic = self.controllers.get('turretsLogic', None)
        if turretsLogic is not None:
            turretsLogic.onTargetChanged()
        return

    def __createControllers(self):
        self._createControllers()
        self._onControllersCreation()

    def _createControllers(self):
        LOG_DEBUG('_createControllers', self.id)
        pilotUpgradeId = self.extUpgrades[LOGICAL_PART.PILOT]
        if pilotUpgradeId is 0:
            pilotUpgradeId = 1
        controllersData = GameEnvironment.getClientArena().createControllers(self.id, self.globalID, self.partStates, pilotUpgradeId=pilotUpgradeId)
        self.registerControllers(controllersData)

    def _onControllersCreation(self):
        self.ePartStateChanged += self.controllers['weapons'].onPartStateChanged

    def registerControllers(self, controllersData):
        self.settings = controllersData['settings']
        if ControllersNames.MODEL_MANIPULATOR in self.controllers:
            self._unregisterController(ControllersNames.MODEL_MANIPULATOR)
        modelManipulator = controllersData[ControllersNames.MODEL_MANIPULATOR]
        self._registerController(ControllersNames.MODEL_MANIPULATOR, modelManipulator)
        shellController = controllersData[ControllersNames.SHELLS_CONTROLLER]
        shellController.setOwner(self)
        modelManipulator.setShelsCount(self.shellsCount)
        modelManipulator.updateConsumablesEffects(self.consumables)
        if ControllersNames.SHELLS_CONTROLLER in self.controllers:
            self._unregisterController(ControllersNames.SHELLS_CONTROLLER)
        self._registerController(ControllersNames.SHELLS_CONTROLLER, shellController)
        weapons = controllersData[ControllersNames.WEAPONS]
        weapons.setOwner(self)
        if ControllersNames.WEAPONS in self.controllers:
            self.ePartStateChanged -= self.controllers[ControllersNames.WEAPONS].onPartStateChanged
            self._unregisterController(ControllersNames.WEAPONS)
        self._registerController(ControllersNames.WEAPONS, weapons)
        if ControllersNames.SOUND_CONTROLLER in self.controllers:
            self.controllers[ControllersNames.SOUND_CONTROLLER].destroy()
            self._unregisterController(ControllersNames.SOUND_CONTROLLER)
        soundController = controllersData[ControllersNames.SOUND_CONTROLLER]
        soundController.setOwner(self)
        self._registerController(ControllersNames.SOUND_CONTROLLER, soundController)
        self._unregisterTurretsController()
        turretsLogic = controllersData.get(ControllersNames.TURRETS_LOGIC, None)
        if turretsLogic:
            turretsLogic.setOwner(self)
            self._registerController(ControllersNames.TURRETS_LOGIC, turretsLogic)
            self.ePartStateChanged += turretsLogic.onPartStateChanged
        self._selectModel()
        return

    def _unregisterTurretsController(self):
        """Unregister turret controller if it was registered for this avatar
        """
        if ControllersNames.TURRETS_LOGIC in self.controllers:
            controller = self.controllers[ControllersNames.TURRETS_LOGIC]
            controller.setOwner(None)
            self.ePartStateChanged -= controller.onPartStateChanged
            self._unregisterController(ControllersNames.TURRETS_LOGIC)
        return

    def respondCommand(self, requestID, resultID, data):
        pass

    @isEntityInWorld
    def set_partFlags(self, changesData):
        self.__updatePartFlags()
        isFire = next((True for _, v in self.partFlags if v & PART_FLAGS.FIRE != 0), False)
        if self._lastIsFire != isFire:
            GameEnvironment.g_instance.eFireStateChange(self.id, isFire)
            self._lastIsFire = isFire

    def __updatePartFlags(self):
        if self.controllers and self.controllers.get('modelManipulator', None):
            changesMap = self.controllers['modelManipulator'].updatePartsFlags(self.partFlags)
            self.controllers['soundController'].updatePartsFlags(self.partFlags)
            for partID, flagID, flagValue in changesMap:
                self.ePartFlagSwitchedNotification(partID, flagID, flagValue)

        return

    def createWorldEffect(self, serverEffectID, serverParams):
        params = {}
        position = self.position
        if serverParams & FROM_SERVER_TO_CLIENT_EFFECT_PARAM.ROTATION:
            params['rotation'] = (self.yaw, self.pitch, 0)
        if serverParams & FROM_SERVER_TO_CLIENT_EFFECT_PARAM.GROUNDED:
            position, _ = self.__getTerrainPointAndMaterial()
        EffectManager.g_instance.createWorldEffect(Effects.getEffectId(EFFECTS_NAMES[serverEffectID]), position, params)

    def onPartFlagSwitchedOn(self, partId, flagID, authorID):
        pass

    def onPartStateChanging(self, partId, stateID, authorID, damageReason):
        pass

    def onKickedFromServer(self, reason, isBan, expiryTime):
        pass

    def messenger_onActionByServer(self, actionID, reqID, args):
        pass

    def sendInitialData(self, strData):
        pass

    def onResponseFromServer(self, cellRequest, cellResponse):
        pass

    def onShellLaunched(self, shellIndex):
        self.shellLaunched(shellIndex)

    def __getAltitude4Point(self, position):
        res = None
        heightCollide = BigWorld.hm_collideSimple(self.spaceID, position, position - Math.Vector3(0, 1500, 0))
        if heightCollide is not None:
            res = ((position - heightCollide[0]) / WORLD_SCALING).y
        return res

    def getAltitudeAboveWaterLevel(self):
        waterLevel = GameEnvironment.getClientArena().getWaterLevel()
        return (round(self.position.y, 3) - waterLevel) / WORLD_SCALING

    def __getDeltaPoint(self, l):
        dx = abs(l) * math.cos(self.yaw)
        dz = abs(l) * math.sin(self.yaw)
        sign = math.copysign(1, l)
        return Math.Vector3(self.position.x + sign * dx, self.position.y, self.position.z + sign * dz)

    def getAltitudeAboveObstacle(self):
        points = [self.position, self.__getDeltaPoint(ALTITUDE_DX), self.__getDeltaPoint(-ALTITUDE_DX)]
        s = 0.0
        n = 0
        for point in points:
            alt = self.__getAltitude4Point(point)
            if alt != None:
                s += alt
                n += 1

        if n > 0:
            return s / n
        else:
            return self.position.y

    def getDebugInfo(self):
        data = [('ID', self.id),
         ('Name', self.objectName),
         ('State', enumToString(EntityStates, self.state)),
         ('Class', self.__class__.__name__),
         ('HP', self.health)]
        compoundID = self.controllers.get('modelManipulator', None).compoundID
        if self.model is not None:
            data.append(('LOD', CompoundSystem.getCompoundLOD(compoundID)))
            if hasattr(self.model, 'visuals'):
                data.append(('Vis/Prim', '{0}/{1}'.format(self.model.visuals, self.model.primitives)))
        return data

    def sendCustomEventToCell(self, eventName, planName, paramList):
        self.cell.customEventFromClient(eventName, planName, paramList)

    def sendGlobalEventToCell(self, eventName, channelList, paramList, aspectsList):
        self.cell.globalEventFromClient(eventName, channelList, paramList, aspectsList)

    def customEventFromCell(self, eventName, planName, paramList):
        BigWorld.passEventToVisualScript(None, eventName, planName, paramList)
        return

    def globalEventFromCell(self, eventName, channelList, paramList, aspectsList):
        BigWorld.postRemoteEvent(eventName, channelList, paramList, aspectsList)

    def getDebugMarkerCaption(self):
        healthText = '{health}/{maxHealth}'.format(health=int(self.health), maxHealth=int(self.maxHealth))
        if self.teamIndex == BigWorld.player().teamIndex:
            return '\\c0000FFCC; Friendly\n {id}\n{health}'.format(id=self.id, health=healthText)
        elif self.teamIndex == TEAM_ID.TEAM_2:
            return '\\cAA9900CC; Neutral\n {id}\n{health}'.format(id=self.id, health=healthText)
        else:
            return '\\cFF0000CC; Enemy\n {id}\n{health}'.format(id=self.id, health=healthText)

    def onTokenReceived(self, requestID, tokenType, data):
        pass

    def voipClientStatus(self, channelType, channelName, status):
        pass

    def voipSquadStatus(self, squadID, status):
        pass

    def voipMuteClient(self, dbid, mute):
        pass

    def voipReceiveSquadChannel(self, channel, clients_list):
        pass

    def voipServerStatus(self, status, args):
        pass

    def requestClientStats(self):
        pass

    def cantSwitchVehicleResponse(self):
        pass

    def autoAlightFromDestroyedTransport(self):
        BigWorld.player().eAutoAlightFromDestroyedTransport()

    def set_isWarEmergencyPower(self, oldValue):
        self.controllers['modelManipulator'].updateForsageEffects(self.isWarEmergencyPower > 0)

    def set_armamentFreeUse(self, oldValue):
        self.controllers['weapons'].onArmamentFreeUseChanged(self.armamentFreeUse)

    def isPartStateAimable(self, presentPartsMap, partID, state):
        return state != PART_STATS_STATE.DESTROYED

    def victimInformAboutCrit(self, partID, victimID, damageReason):
        pass

    def _createPersistentEffecs(self):
        persistentEffects = self._autoStartEffects
        isPlayer = BigWorld.player() == self
        for effect in persistentEffects:
            params = {'variant': 'OWN' if isPlayer else 'OTHER',
             'entity': self}
            effects = EffectManager.g_instance.createWorldEffect(Effects.getEffectId(effect), Math.Vector3(0.0, 0.0, 0.0), params)

    def _updateEffects(self):
        self.__updateEffectsCallback = BigWorld.callback(EFFECT_CHECK_FREQUENCY, self._updateEffects)
        if EffectManager.g_instance:
            self._updateGroundEffects()

    def _notifyModelManipulatorOwnerChanged(self, owner):
        modelManipulator = self.controllers.get('modelManipulator')
        if modelManipulator:
            modelManipulator.onOwnerChanged(owner)

    def _updateGroundEffects(self):

        def getEnginesPos(parts_only_list):
            engines_pos = []
            if self.settings.airplane.name not in MapEffectsSettings.EXCLUDED_PLANES_WITH_2_ENGINES:
                curr_part = lambda p_: p_.getFirstPartType().componentType in ('Engine',)
                available_parts = [ part for part in parts_only_list if curr_part(part) ]
                for part in available_parts:
                    for upgrade in part.upgrades.values():
                        pl = upgrade.bboxes.getList()
                        if len(pl):
                            engines_pos.append(pl[-1].pos)

            else:
                engines_pos = [Math.Vector3(0, 0, 0)]
            return engines_pos

        angles = (self.roll, self.pitch, self.yaw)
        reassignRotation = False
        for angleIndex in range(0, 2):
            if abs(self.__lastPlaneAngles_forGFXs[angleIndex] - angles[angleIndex]) >= 0.174:
                reassignRotation = True

        if self.__lastPlaneRotation_forGFXs is None or reassignRotation:
            self.__lastPlaneRotation_forGFXs = self.getRotation()
            self.__lastPlaneAngles_forGFXs = angles
        if self.__engineDeltaPosList is None:
            self.__engineDeltaPosList = getEnginesPos(self.settings.airplane.partsSettings.getPartsOnlyList())
        gameState = EntityStates.inState(self, EntityStates.GAME)
        arenaData = db.DBLogic.g_instance.getArenaData(self.arenaType)
        for engine_index, localDeltaPos in enumerate(self.__engineDeltaPosList):
            effectData = None
            collisionPos = None
            materialName = MapEffectsSettings.Material.WATER
            if gameState and isUpdateAvatarAnimation(self.position):
                startPos = self.position + self.__lastPlaneRotation_forGFXs.rotateVec(localDeltaPos)
                collider = BigWorld.hm_collideSimple(self.spaceID, startPos, startPos - Math.Vector3(0, MapEffectsSettings.MAX_DIST_TO_TERRAIN, 0))
                if collider:
                    landscapeEffects = MapEffectsSettings.EFFECTS.get(arenaData.geometryName, {})
                    if landscapeEffects:
                        landscapeEffects = landscapeEffects[MapEffectsSettings.Groups.GROUND]
                    collisionPos, collisionMaterial = collider[0], collider[1]
                    collisionDist = (startPos - collisionPos).length
                    if collisionMaterial == COLLISION_TYPE_WATER:
                        effectData = landscapeEffects.get(MapEffectsSettings.Material.WATER)
                    elif collisionMaterial == COLLISION_TYPE_GROUND:
                        textureIndex = BigWorld.hm_terrainMaterialId(self.spaceID, collisionPos.x, collisionPos.z)
                        materialID = arenaData.getTextureMaterialID(textureIndex)
                        materialName = db.DBLogic.g_instance.getLandscapeMaterialName(materialID)
                        effectData = landscapeEffects.get(materialName)
                    if effectData is not None and collisionDist > effectData.maxDistance * WORLD_SCALING:
                        effectData = None
            self._doUpgradeGroundEffects(materialName, collisionPos, engine_index, localDeltaPos, effectData)

        return

    def _doUpgradeGroundEffects(self, materialName, collisionPos, engine_index, deltaPos, effectData):
        isActive = effectData is not None
        isGroundParticleActive = isActive and effectData.groundParticle

        def matrix(base_matrix, dp):
            om = Math.Matrix()
            om.translation = dp
            m = Math.MatrixProduct()
            m.a = om
            m.b = base_matrix
            return m

        if self.groundParticleName.get(engine_index) is None:
            if isGroundParticleActive:
                self.groundParticleName[engine_index] = effectData.groundParticle
                if effectData.groundParticle not in self._groundParticles.get(engine_index, {}):
                    groundParticle = EffectManager.g_instance.createModelGroundedEffect(Effects.getEffectId(effectData.groundParticle), {'variant': 'OWN' if BigWorld.player() == self else 'OTHER',
                     'matrix': matrix(self.realMatrix, deltaPos)})
                    self._groundParticles.setdefault(engine_index, {}).setdefault(effectData.groundParticle, []).append(groundParticle)
                map(lambda eff: eff.setVisible(True), self._groundParticles[engine_index].get(effectData.groundParticle, []))
        elif not isGroundParticleActive or self.groundParticleName[engine_index] != effectData.groundParticle:
            for particles in self._groundParticles.get(engine_index).itervalues():
                map(lambda eff: eff.setVisible(False), particles)

            del self.groundParticleName[engine_index]
        return

    def onGunGroupFire(self, group):
        self.eOnGunGroupFire(group)

    def onSingleShot(self, groups):
        pass

    def shootingGroups(self):
        return self.armamentStates

    def popSingleShotGroups(self, groups):
        return 0

    def set_currentSector(self, oldValue):
        """BigWorld callback for Avatar.currentSector property
        """
        self.eCurrentSectorChanged(self, oldValue, self.currentSector)

    def _onAvatarChangedPlane(self, avatarID, *args, **kwargs):
        if self.id == avatarID:
            self.onArenaAvatarInfoUpdated()

    def _subscribe(self):
        clientArena = GameEnvironment.getClientArena()
        clientArena.onAvatarChangedPlane += self._onAvatarChangedPlane
        clientArena.onVehicleKilled += self.reportDestruction

    def _unsubscribe(self):
        clientArena = GameEnvironment.getClientArena()
        clientArena.onAvatarChangedPlane -= self._onAvatarChangedPlane
        clientArena.onVehicleKilled -= self.reportDestruction

    def _onPlaneDestroyed(self):
        pass

    def setModelVisible(self, isVisible):
        self.controllers['modelManipulator'].setVisible(isVisible)

    def receivePlaneBattleTooltipData(self, planeID, planeBattleTooltipData):
        """Called from baseApp for PlayerAvatar only
        """
        pass

    def receivePlaneBattleCrewData(self, planeID, crewData):
        """Called from baseApp for PlayerAvatar only
        """
        pass

    def responseFastCommand(self, authorID, commandType, notificationType, targetID):
        """Called from baseApp for PlayerAvatar only
        """
        raise False or AssertionError

    def _onTacticalRespawnEndInternal(self):
        TacticalRespawnAvatarMixin._onTacticalRespawnEndInternal(self)
        self._notifyModelManipulatorOwnerChanged(self)

    @isEntityInWorld
    def set_isUnderRepairZoneInfluence(self, oldValue):
        self.eUnderRepairZoneInfluence(self.isUnderRepairZoneInfluence)

    @isEntityInWorld
    def set_repair(self, oldValue):
        self.eRepair(self.repair)

    def getShellController(self):
        return self.controllers[ControllersNames.SHELLS_CONTROLLER]

    def getWeaponController(self):
        return self.controllers[ControllersNames.WEAPONS]

    def hasGunner(self):
        for partID, _ in self.partStates:
            partSettings = self.settings.airplane.getPartByID(partID)
            if partSettings:
                for i, partTypeData in partSettings.upgrades.items():
                    if partTypeData.componentType == 'Gunner1':
                        return True

        return False

    def getAmmoBeltsInitialInfo(self):
        ammoInitialInfo = self.controllers['weapons'].getGunGroupsInitialInfo()
        return ammoInitialInfo

    def getBeltsAmmoCountByGroup(self):
        counters = self.controllers['weapons'].getGunGroupCounters()
        return counters

    def getShellsInitialInfo(self):
        shellsInitialInfo = self.controllers['shellController'].getShellGroupsInitialInfo()
        return shellsInitialInfo

    def receivePlaneTypeObjectives(self, objectives):
        pass

    def onObjectiveProgressChanged(self, objectiveID, progress):
        pass

    def onObjectiveProgressRawValueChanged(self, objectiveID, progressRawValue):
        pass

    def onGameplayHint(self, hintID, hintName, hintType, force):
        pass


from PlayerAvatar import PlayerAvatar