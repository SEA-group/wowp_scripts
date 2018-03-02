# Embedded file name: scripts/common/ShellController.py
import db.DBLogic
from consts import COMPONENT_TYPE
import Math
from random import random
from consts import *
from AvatarControllerBase import AvatarControllerBase
from EntityHelpers import EntityStates, isCorrectBombingAngle, movementAbsToSpeed, getRotation, getBombGravityAcceleration
from debug_utils import *
from MathExt import quat2Euler, repeatGauss, clamp, sign
from collections import namedtuple, deque
from _weapons import SHELL_TYPE
COMPONENTS_DB_TO_UPDATABLE_TYPE_MAP = {COMPONENT_TYPE.ROCKETS: UPDATABLE_TYPE.ROCKET,
 COMPONENT_TYPE.BOMBS: UPDATABLE_TYPE.BOMB}
SHELL_TYPE_TO_EFFECT_ID = {UPDATABLE_TYPE.BOMB: 'LAUNCH_BOMB',
 UPDATABLE_TYPE.ROCKET: 'LAUNCH_ROCKET'}
COMPONENTS_DB_TO_DBSHELL_TYPE_MAP = dict(((v, SHELL_TYPE.__dict__[k]) for k, v in COMPONENT_TYPE.__dict__.items() if isinstance(v, int) and k in SHELL_TYPE.__dict__))
ShellSettings = namedtuple('ShellSettings', 'portion portionTempo')

class ShellController(AvatarControllerBase):
    NO_ROCKETS_INDEX = -1

    def __init__(self, owner, weaponsInfo, pivots, initialCounters = None, isEmulation = False):
        AvatarControllerBase.__init__(self, owner)
        settings = {}
        shells = {}
        weaponGroups = []
        self.__shellGroups = []
        self.__shellsCommonData = []
        self.__rocketsMaxFlightRange = 0
        self.__isBombState = False
        for shellInfo in weaponsInfo:
            name = shellInfo.name.lower()
            shellComponentType, shellDescription = db.DBLogic.g_instance.getShellComponentsGroupIDAndDescription(name)
            if shellDescription:
                numAmmo = shellDescription.loadedAmmo if shellDescription.bracketOnly else 1
                if shellInfo.weaponGroup not in settings:
                    settings[shellInfo.weaponGroup] = {'resourceId': shellDescription.index,
                     'weaponGroup': shellInfo.weaponGroup,
                     'dispersionAngle': shellInfo.dispersionAngle,
                     'weaponName': shellInfo.name,
                     'shellDescription': shellDescription,
                     'initialCount': initialCounters and next((r['value'] for r in initialCounters if r['key'] == shellInfo.slotID), 0) or 0,
                     'maxCount': numAmmo,
                     'updatableType': COMPONENTS_DB_TO_UPDATABLE_TYPE_MAP[shellComponentType],
                     'componentType': shellComponentType,
                     'slotID': shellInfo.slotID,
                     'shellInfo': shellInfo}
                    settings[shellInfo.weaponGroup].update(self.getShellPortionSettings(shellComponentType, shellInfo))
                    shells[shellInfo.weaponGroup] = []
                    weaponGroups.append(shellInfo.weaponGroup)
                else:
                    settings[shellInfo.weaponGroup]['maxCount'] += numAmmo
                pivot = self.__getPivot(shellInfo.flamePath, pivots)
                if not pivot:
                    LOG_ERROR("Can't find pivot for globalID", owner.globalID)
                shells[shellInfo.weaponGroup].append(Shell(pivot.position, shellInfo.flamePath))

        if len(weaponGroups) > 2:
            LOG_DEBUG_DEV('Maximum 2 kind of shells supported at this moment', settings)
            LOG_CURRENT_EXCEPTION()
        elif len(weaponGroups) > 0:
            if len(weaponGroups) == 1:
                if settings[weaponGroups[0]]['updatableType'] == UPDATABLE_TYPE.BOMB:
                    weaponGroups.insert(0, self.NO_ROCKETS_INDEX)
                    shells[self.NO_ROCKETS_INDEX] = []
                    settings[self.NO_ROCKETS_INDEX] = {'updatableType': UPDATABLE_TYPE.ROCKET,
                     'shellDescription': None,
                     'initialCount': 0,
                     'maxCount': 0,
                     'slotID': 0,
                     'weaponGroup': self.NO_ROCKETS_INDEX,
                     'weaponName': '',
                     'componentType': COMPONENT_TYPE.BOMBS}
            elif settings[weaponGroups[0]]['updatableType'] != settings[weaponGroups[1]]['updatableType']:
                if settings[weaponGroups[0]]['updatableType'] == UPDATABLE_TYPE.BOMB:
                    weaponGroups[0], weaponGroups[1] = weaponGroups[1], weaponGroups[0]
            else:
                weaponGroups.sort()
            if IS_CELLAPP and not self._owner.shellsCount or isEmulation:
                counters = []
                for wg in weaponGroups:

                    def invalidateInitialCount():
                        if isEmulation:
                            initialCount = settings[wg]['maxCount']
                        else:
                            initialCount = min(settings[wg]['initialCount'], settings[wg]['maxCount'])
                        settings[wg]['initialCount'] = initialCount

                    invalidateInitialCount()
                    counters.append(settings[wg]['initialCount'])

                self._owner.shellsCount = counters
            for i, wg in enumerate(weaponGroups):
                settings[wg]['uiWeaponGroup'] = i + 4
                settings[wg]['shellIndex'] = i
                self.__shellGroups.append(shells[wg])
                self.__shellsCommonData.append(settings[wg])

        self.ammoRestorePoints = {}
        if IS_CELLAPP:
            self._launchSequence = [ deque() for _ in weaponGroups ]
        if IS_CLIENT:
            self.__shellsEnabled = set()
        return

    def backup(self):
        return {'isBombState': self.__isBombState,
         'launchSequence': self._launchSequence}

    def restore(self, backupContainer):
        self.__isBombState = backupContainer['isBombState']
        self._launchSequence = backupContainer['launchSequence']

    def __fillShellsEnabled(self):
        for weaponSlotSettings in self._owner.settings.components.weapons2.slots.itervalues():
            if weaponSlotSettings.name == 'PODVES':
                for weaponTypeSettings in weaponSlotSettings.types.itervalues():
                    for weaponSettings in weaponTypeSettings.weapons:
                        shellDBGroupID, shellDesc = db.DBLogic.g_instance.getShellComponentsGroupIDAndDescription(weaponSettings.name)
                        if shellDesc:
                            self.__shellsEnabled.add(COMPONENTS_DB_TO_UPDATABLE_TYPE_MAP[shellDBGroupID])

    def setOwner(self, owner):
        AvatarControllerBase.setOwner(self, owner)
        for settings in self.__shellsCommonData:
            if settings['maxCount']:
                settings.update(self.getShellPortionSettings(settings['componentType'], settings['shellInfo']))

        if IS_CLIENT and self._owner.id == BigWorld.player().id:
            self.__fillShellsEnabled()

    def getShellPortionSettings(self, shellComponentType, shellInfo):
        shellSettings = self.__getShellSettings(COMPONENTS_DB_TO_DBSHELL_TYPE_MAP[shellComponentType], shellInfo)
        return {'portion': shellSettings.portion,
         'portionTempo': shellSettings.portionTempo}

    def getShellCommonData(self, shellIndex):
        if shellIndex < len(self.__shellsCommonData):
            return self.__shellsCommonData[shellIndex]
        else:
            return None

    def isTypeOnBoard(self, updatableType):
        return next((True for settings in self.__shellsCommonData if settings['updatableType'] == updatableType and settings['shellDescription']), False)

    def getShellType(self, shellIndex):
        if IS_CLIENT:
            if not self.__shellsCommonData:
                if shellIndex == SHELL_INDEX.TYPE1:
                    return UPDATABLE_TYPE.ROCKET
                return UPDATABLE_TYPE.BOMB
            if shellIndex >= len(self.__shellsCommonData):
                return UPDATABLE_TYPE.BOMB
        return self.__shellsCommonData[shellIndex]['updatableType']

    def getShellCount(self, shellIndex, failResult = -1):
        if shellIndex < len(self._owner.shellsCount):
            return self._owner.shellsCount[shellIndex]
        return failResult

    def getShellCountForType(self, shellType):
        counters = [ count for shellIndex, count in enumerate(self._owner.shellsCount) if self.__shellsCommonData[shellIndex]['updatableType'] == shellType ]
        if counters:
            return sum(counters)
        return 0

    def getShellCountForSlotID(self, slotID):
        return next((count for shellIndex, count in enumerate(self._owner.shellsCount) if self.__shellsCommonData[shellIndex]['slotID'] == slotID), 0)

    def getShellsSlotMap(self):
        return dict(((self.__shellsCommonData[shellIndex]['slotID'], count) for shellIndex, count in enumerate(self._owner.shellsCount)))

    def getSlotsShellCount(self):
        return [ {'key': self.__shellsCommonData[shellIndex]['slotID'],
         'value': count} for shellIndex, count in enumerate(self._owner.shellsCount) ]

    def getShellCountersForSlots(self, slotsMap):
        return [ slotsMap.get(s['slotID'], 0) for s in self.__shellsCommonData ]

    def getMaxMassHingedArms(self):
        mass = 0
        for settings in self.__shellsCommonData:
            if settings['shellDescription']:
                mass += settings['shellDescription'].mass * settings['maxCount']

        return mass

    def getMassHingedArms(self):
        mass = 0
        for shellIndex, settings in enumerate(self.__shellsCommonData):
            if settings['shellDescription']:
                mass += settings['shellDescription'].mass * self._owner.shellsCount[shellIndex]

        return mass

    def __getShellSettings(self, shellTypeID, shellInfo):
        planeSettings = getattr(self._owner, 'settings', None)
        if planeSettings is None:
            return ShellSettings(None, None)
        else:
            planeType = planeSettings.airplane.planeType
            shellSettings = db.DBLogic.g_instance.getAircraftClassDescription(planeType).shellSettings
            classSettings = next((classSettings for classSettings in shellSettings.settings if classSettings.type == shellTypeID), None)

            def get(name):
                val = getattr(shellInfo, name, None)
                if val is not None:
                    return val
                else:
                    return getattr(classSettings, name)

            return ShellSettings(get('portion'), get('portionTempo'))

    def __getPivot(self, pivotName, pivots):
        if pivotName in pivots.mountPoints:
            return pivots.mountPoints[pivotName]
        else:
            LOG_WARNING('Unkown pivot for shell:' + pivotName)
            return None

    def _processLaunchPortion(self):
        for shellIndex, counter in enumerate(self._launchSequence):
            if counter:
                self.__launch(shellIndex)

    def update(self, dt):
        self._processLaunchPortion()

    def getShellGroupsInitialInfo(self):
        """return map of all loaded shells descriptions for hud initialization"""
        shellsCount = {}
        for settings in self.__shellsCommonData:
            shellsCount[settings['uiWeaponGroup']] = {'initialCount': settings['maxCount'],
             'objCount': settings['maxCount'],
             'description': settings['shellDescription'],
             'shellID': settings['updatableType'],
             'componentType': settings['componentType'],
             'weaponName': settings['weaponName'],
             'ammoBeltType': 'standartbelt',
             'shellIndex': settings['shellIndex']}

        return shellsCount

    def getShellsCountByGroup(self):
        shellsCount = {}
        for shellIndex, settings in enumerate(self.__shellsCommonData):
            shellsCount[settings['uiWeaponGroup']] = self._owner.shellsCount[shellIndex]

        return shellsCount

    def tryToLaunchShell(self, shellIndex):
        """return current shells count or: 0 - all was spended, -1 - no one was installed, -2 - invalid bomb angle"""
        shellCount = self.getShellCount(shellIndex)
        shellType = self.getShellType(shellIndex)
        if shellCount > 0:
            if shellType == UPDATABLE_TYPE.BOMB and not isCorrectBombingAngle(self._owner, getRotation(self._owner)):
                return -2
            self._owner.cell.askToLaunchShell(shellIndex)
            shellGroup = self.__shellGroups[shellIndex]
            shellGroupCommons = self.__shellsCommonData[shellIndex]
            shellStartIndex = shellGroupCommons['maxCount'] - shellCount
            shell = shellGroup[shellStartIndex]
            import BigWorld
            if BigWorld.player().id == self._owner.id:
                if shellType in SHELL_TYPE_TO_EFFECT_ID:
                    effectID = SHELL_TYPE_TO_EFFECT_ID[shellType]
                    import CameraEffect
                    if CameraEffect.g_instance:
                        effectDir = shell.posDelta
                        effectDir.y -= 0.5
                        CameraEffect.g_instance.onCameraEffect(effectID, True, 1.0, shell.posDelta)
        elif shellType not in self.__shellsEnabled:
            return -3
        return shellCount

    def getMaxRocketFlightRange(self):
        rockets = [ getattr(settings['shellDescription'], 'maxFlightRange', 0) for shellIndex, settings in enumerate(self.__shellsCommonData) if self._owner.shellsCount[shellIndex] and self.getShellType(shellIndex) == UPDATABLE_TYPE.ROCKET ]
        if rockets:
            return max(rockets)
        else:
            return 0

    def getShelsModels(self):
        singleShellsList = {}
        for shellIndex, shellGroup in enumerate(self.__shellGroups):
            shellGroupCommons = self.__shellsCommonData[shellIndex]
            groupDescription = shellGroupCommons['shellDescription']
            if groupDescription and not groupDescription.bracketOnly:
                shelList = [ (groupDescription.model, shell.hpName) for shell in shellGroup ]
                singleShellsList[shellIndex] = shelList

        return singleShellsList

    def getShellPosition(self, shellIndex, shellIdx = 0):
        currentShellsCount = self.getShellCount(shellIndex)
        if currentShellsCount > 0 and shellIdx < currentShellsCount:
            shellGroup = self.__shellGroups[shellIndex]
            shellGroupCommons = self.__shellsCommonData[shellIndex]
            shellStartIndex = shellGroupCommons['maxCount'] - currentShellsCount
            shell = shellGroup[shellStartIndex + shellIdx]
            return shell.posDelta
        else:
            return None
            return None

    def _getDispersionAngle(self, shellIndex):
        cfc = 1
        if self.__isBombState and self.getShellType(shellIndex) == UPDATABLE_TYPE.BOMB:
            cfc = BOMBER_BOMB_DISPERSION_CFC
        em = self._owner.controllers.get('externalModifiers')
        if em is not None:
            cfc /= em.modifiers.BOMB_MISSILE_FOCUS
        return cfc * self.__shellsCommonData[shellIndex]['dispersionAngle']

    def shoot(self, shellIndex, requestedShellInShoot = None):
        maxPossiblePortion = self.getShellCount(shellIndex) - len(self._launchSequence[shellIndex])
        if maxPossiblePortion > 0:
            settings = self.__shellsCommonData[shellIndex]
            requestedPortion = requestedShellInShoot or settings['portion']
            portion = min(requestedPortion, maxPossiblePortion)
            tempo = settings['portionTempo']
            sequence = self._launchSequence[shellIndex]
            if len(sequence) <= requestedPortion:
                ts = BigWorld.time() if not sequence else sequence[-1] + tempo
                for _ in range(portion):
                    sequence.append(ts)
                    ts += tempo

                return self.__launch(shellIndex)
        return 0

    def __launch(self, shellIndex):
        shellType = self.getShellType(shellIndex)
        shellSettings = self.__shellsCommonData[shellIndex]
        if shellType == UPDATABLE_TYPE.BOMB and not isCorrectBombingAngle(self._owner, self._owner.controllers['flightModel'].rotation):
            self._owner.shellsCount[shellIndex] = self._owner.shellsCount[shellIndex] / shellSettings['portion'] * shellSettings['portion']
            self._owner.onLaunchShell(shellIndex, 0)
            self._launchSequence[shellIndex].clear()
            return
        sequence = self._launchSequence[shellIndex]
        now = BigWorld.time()
        shellInShoot = 0
        while sequence and sequence[0] <= now:
            sequence.popleft()
            shellInShoot += 1

        updatableManager = self._owner.controllers['updatableManager']
        shellGroup = self.__shellGroups[shellIndex]
        shellStartIndex = shellSettings['maxCount'] - self.getShellCount(shellIndex)
        dispersionAngle = self._getDispersionAngle(shellIndex)
        resourceId = shellSettings['resourceId']
        for i in range(shellStartIndex, shellStartIndex + shellInShoot):
            if i < 0 or i >= len(shellGroup):
                LOG_ERROR('shoot error for airplane ', self._owner.globalID, 'with shellIndex = ', shellIndex, 'currShellCount = ', self.getShellCount(shellIndex), 'i = ', i, 'shellStartIndex = ', shellStartIndex, 'shellInShoot = ', shellInShoot, 'maxCount = ', shellSettings['maxCount'])
            shell = shellGroup[i]
            ownerRotation = Math.Quaternion(self._owner.rotation)
            startPosition = self._owner.position + ownerRotation.rotateVec(shell.posDelta)
            startVector = self._owner.vector * WORLD_SCALING
            if shellType == UPDATABLE_TYPE.ROCKET:
                axisAngle = random() * math.pi * 2.0
                dispersionAxis = Math.Vector3(sin(axisAngle), cos(axisAngle), 0)
                angle = math.pow(random(), 1.5) * dispersionAngle
                dispersionRotation = Math.Quaternion()
                dispersionRotation.fromAngleAxis(angle, dispersionAxis)
                ownerRotation = ownerRotation.mul(dispersionRotation)
                startVector = ownerRotation.rotateVec(self._owner.reductionPointVector)
                startVector.normalise()
                startVector *= self._owner.vector.length * WORLD_SCALING
                startRotation = quat2Euler(ownerRotation)
                updatableManager.createUpdatableLocal(shellType, resourceId, startPosition, startVector, startRotation)
            else:
                accelerationV = getBombGravityAcceleration(self._owner.settings.airplane.planeType)
                zScaling = 1.0 + BOMB_Z_SCATTER_SCALING * hypot(startVector.x, startVector.z) / (WORLD_SCALING * movementAbsToSpeed(VELLOCITY_OF_SOUND))
                delta = abs(accelerationV.y * math.tan(dispersionAngle / 2.0))
                probability = lambda x: sign(2.0 * x - 1.0) * pow(abs(2.0 * x - 1.0), 1.3)
                dispersionZ = probability(random()) * delta * zScaling
                dispersionX = probability(random()) * delta
                startRotation = quat2Euler(ownerRotation)
                updatableManager.createUpdatableLocal(shellType, resourceId, startPosition, startVector, startRotation, dispersionX, dispersionZ)

        self._owner.shellsCount[shellIndex] -= shellInShoot
        if shellInShoot > 0:
            self._owner.onLaunchShell(shellIndex, shellInShoot)
        return shellInShoot

    def getBombDispersionAngle(self):
        bombs = [ self._getDispersionAngle(shellIndex) for shellIndex, settings in enumerate(self.__shellsCommonData) if self.getShellType(shellIndex) == UPDATABLE_TYPE.BOMB ]
        if bombs:
            return max(bombs)
        else:
            return 0

    def getMaxBombExplosionRadius(self):
        bombs = [ settings['shellDescription'].explosionRadius for shellIndex, settings in enumerate(self.__shellsCommonData) if self.getShellType(shellIndex) == UPDATABLE_TYPE.BOMB ]
        if bombs:
            explosionRadius = max(bombs)
            em = self._owner.controllers.get('externalModifiers')
            if em is not None:
                explosionRadius *= em.modifiers.BOMB_SPLASH
            return explosionRadius
        else:
            return 0
            return

    def setIsBombState(self, v):
        self.__isBombState = v

    def restoreAmmoType(self, shellType):
        """
        Restores specific ammo initial count
        @type shellIndex: UPDATABLE_TYPE
        """
        for i, settings in enumerate(self.__shellsCommonData):
            if settings['updatableType'] == shellType:
                self._owner.shellsCount[i] = settings['initialCount']

    def restoreShellsByIndex(self, shellIndex):
        """Restore shells by shellIndex
        @param shellIndex: One of SHELL_INDEX.*
        """
        settings = self.__shellsCommonData[shellIndex]
        self._owner.shellsCount[shellIndex] = settings['initialCount']

    def restoreAmmo(self):
        """
        Restores all kind of shells initial count
        """
        initialShellsCount = {index:count for index, count in enumerate(self._owner.shellsCount)}
        self._owner.shellsCount = [ settings['initialCount'] for settings in self.__shellsCommonData ]
        return {index:count - initialShellsCount[index] for index, count in enumerate(self._owner.shellsCount)}

    def restoreAmmoAsRightAlong(self):
        RELOAD_POINT_DEF = {SHELL_INDEX.TYPE1: 100,
         SHELL_INDEX.TYPE2: 100}
        RELOAD_POINT_REGENERATION_SPEED = {SHELL_INDEX.TYPE1: 10,
         SHELL_INDEX.TYPE2: 10}

        def isFullAmmo():
            return all((self._owner.shellsCount[_] == self.__shellsCommonData[_]['initialCount'] for _, count in enumerate(self._owner.shellsCount)))

        if not isFullAmmo():
            for shellIndex, settings in enumerate(self.__shellsCommonData):
                initialCount = settings['initialCount']
                if initialCount != 0:
                    if shellIndex not in self.ammoRestorePoints:
                        self.ammoRestorePoints[shellIndex] = 0
                    restoreConditions = self._owner.shellsCount[shellIndex]
                    if restoreConditions < initialCount:
                        ammoPrice = RELOAD_POINT_DEF.get(shellIndex, 0) / initialCount
                        self.ammoRestorePoints[shellIndex] += RELOAD_POINT_REGENERATION_SPEED.get(shellIndex, 0)
                        if self.ammoRestorePoints[shellIndex] - ammoPrice >= 0 and self._owner.shellsCount[shellIndex] < initialCount:
                            self._owner.shellsCount[shellIndex] += 1
                            self.ammoRestorePoints[shellIndex] -= ammoPrice


class Shell():

    def __init__(self, position, hpName):
        self.posDelta = Math.Vector3(position)
        self.hpName = hpName