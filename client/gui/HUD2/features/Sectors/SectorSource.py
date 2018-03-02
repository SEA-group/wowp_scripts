# Embedded file name: scripts/client/gui/HUD2/features/Sectors/SectorSource.py
import Math
import BigWorld
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from GameModeSettings.ACSettings import SECTOR_BONUS_TYPE, USE_SECTOR_RADIUS_TABLE
from HelperFunctions import findIf, findSuitableIndex
from consts import SECTOR_STATE, GAME_MODE
from db.DBAreaConquest.SectorGeometry import SectorGeometryCircle
from BWLogging import getLogger
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
ATTACK_TYPE_BOMBER = 0
ATTACK_TYPE_ROCKET = 1
ALLY = 'ally'
ENEMY = 'enemy'
BASE_SECTORS_LOCALE = {ALLY: 'HUD_MAP_LOADING_SPAWN_ALL',
 ENEMY: 'HUD_MAP_LOADING_SPAWN_ENEMY'}
FEATURE_DISABLE = 'feature_disable'
FEATURE_DISABLE_SETTINGS = {GAME_MODE.NAMES[GAME_MODE.OFFENSE_DEFENCE]: [SECTOR_BONUS_TYPE.ROCKET_LAUNCH, SECTOR_BONUS_TYPE.AIR_STRIKE]}

class TargetItem(object):

    def __init__(self, sectorId, targetID, attackTypeValue):
        self.sectorIdent = sectorId
        self.targetIdent = targetID
        self.attackType = attackTypeValue


class SectorSource(DataSource):
    BONUS_POINTS_LABELS = ('bonus',)
    DEFAULT_POINTS_LABELS = ('default',)

    def __init__(self, features):
        self._sectors = features.require(Feature.GAME_MODEL).domination.sectors
        self._bases = features.require(Feature.GAME_MODEL).domination.bases
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._db = features.require(Feature.DB_LOGIC)
        self._gameMode = self._clientArena.gameMode
        self._enemyTeamIndex = -1
        self._playerTeamIndex = -1
        self._log = getLogger(self)
        self._targetList = []
        self._updateZOrderCallback = None
        self._setBaseData()
        if self.gameMode.isReady:
            self._setupModel()
        else:
            self.gameMode.eGameModeReady += self._setupModel
        return

    def _setBaseData(self):
        self._arenaTypeData = self._db.getArenaData(BigWorld.player().arenaType)
        for sectorData in self._arenaTypeData.sectors.sectors.values():
            if not sectorData.isFreeZone:
                if sectorData.isBase:
                    self._appendBase(sectorData)
                else:
                    self._appendEmptySector(sectorData)

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def _setupModel(self, *args, **kwargs):
        self._playerTeamIndex = self._playerAvatar.teamIndex
        self._enemyTeamIndex = 1 - self._playerTeamIndex
        self._subscribe()
        self._updateSectorProperty()
        self._updateSectorsZOrder()

    def _subscribe(self):
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_CAPTURE_POINTS_CHANGED, self._onCapturePointsChanged)
        self._gameMode.addEventHandler(AC_EVENTS.GAME_MODE_TICK, self._onGameModeTick)
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        self._gameMode.addEventHandler(AC_EVENTS.BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED, self._onSectorBombersChangeTarget)
        self._gameMode.addEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self._onSectorRocketsChangeTarget)
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_PERMANENT_LOCK, self._onSectorpermanentLock)

    def _onSectorRocketsChangeTarget(self, sectorId, targetID):
        self._updateSectorTarget(sectorId, targetID, ATTACK_TYPE_ROCKET)
        self._updateTargetStrc()

    def _onSectorBombersChangeTarget(self, sectorId, targetID):
        self._updateSectorTarget(sectorId, targetID, ATTACK_TYPE_BOMBER)
        self._updateTargetStrc()

    def _updateSectorTarget(self, sectorId, targetID, attackType):
        targetItem = findIf(self._targetList, lambda var: var.sectorIdent == sectorId)
        if targetItem:
            targetItem.targetIdent = targetID
            targetItem.attackType = ATTACK_TYPE_BOMBER
        else:
            targetItem = TargetItem(sectorId, targetID, attackType)
            self._targetList.append(targetItem)

    def _updateTargetAfterCapture(self, sectorId):
        targetItem = findIf(self._targetList, lambda var: var.targetIdent == sectorId)
        if targetItem:
            targetSector = self._getSectorByID(sectorId)
            curSetorSector = self._getSectorByID(targetItem.sectorIdent)
            if curSetorSector.teamIndex == targetSector.teamIndex:
                targetItem.targetIdent = ''
                targetItem.attackType = -1
                sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == sectorId)
                sectorStructure.isAttack = targetItem.attackType
                self._updateTargetAfterCapture(sectorId)

    def _onSectorpermanentLock(self, sectorId, *args, **kwargs):
        sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == sectorId)
        if sectorStructure:
            sectorStructure.isPermanentLock = True

    def _updateTargetStrc(self):
        return
        for sectorStructure in self._sectors:
            targetItem = findIf(self._targetList, lambda var: var.targetIdent == sectorStructure.sectorID.get())
            if targetItem:
                sectorStructure.isAttack = targetItem.attackType
            else:
                sectorStructure.isAttack = -1

    def _onCapturePointsChanged(self, sectorId, capturePointsByTeams, *args, **kwargs):
        sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == sectorId)
        if sectorStructure:
            sectorStructure.currentPoints = int(capturePointsByTeams[self._playerTeamIndex])
            sectorStructure.maxPoints = int(sum(list(capturePointsByTeams)))

    def _onGameModeTick(self, tickNumber, *args, **kwargs):
        self._log.debug(' SECTORS_2 _onGameModeTick :')
        for sector in self._sectors:
            sectorID = sector.sectorID.get()
            sector.pointsInTick = self._getPointsInTick(sectorID, tickNumber)
            self._log.debug(' SECTORS_2 _onGameModeTick sector : %s, tickNumber %s, %s, %s', sectorID, tickNumber, self._getNextBonusTime(sectorID), self._getPointsInTick(sectorID, tickNumber))

    def _getPointsInTick(self, sectorID, tickNumber):
        sector = self._getSectorByID(sectorID)
        if sector.settings.bonusType == SECTOR_BONUS_TYPE.POINTS:
            nextTick = sector.nextBonusTick
        else:
            nextTick = tickNumber + 1
        self._log.debug(' _getPointsInTick : %s %s %s %s', sectorID, tickNumber, nextTick, sector.getPointsInTick(nextTick))
        return self._getPointsInTinck(sector, nextTick)

    def _getPointsInTinck(self, sector, tick):
        pointsProduction = sector.settings.pointsProduction
        return sum((p.points for p in pointsProduction.filterProducers(labels=self.DEFAULT_POINTS_LABELS)))

    def _onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
        sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == sectorId)
        sectorData = self._getSectorByID(sectorId)
        if sectorStructure:
            isLock = state == SECTOR_STATE.LOCKED
            lockEndTime = nextStateTimestamp - self._playerAvatar.arenaStartTime if isLock else 0.0
            sectorStructure.lockEndTime = int(lockEndTime)
            sectorStructure.teamIndex = teamIndex
            sectorStructure.pointsInTick = self._getPointsInTick(sectorData.ident, self.gameMode.currentTick)
            sectorStructure.currentPoints = int(sectorData.capturePointsByTeams[self._playerTeamIndex])
            sectorStructure.maxPoints = int(sum(list(sectorData.capturePointsByTeams)))
            sectorStructure.isFeatureDisable = self._isFeatureDisable(sectorData.ident)
        self._updateTargetAfterCapture(sectorId)

    def _appendBase(self, sectorData):
        radius = sectorData.geometry.radius if isinstance(sectorData.geometry, SectorGeometryCircle) else 0
        base = self._bases.append(sectorName='HUD_MAP_LOADING_SPAWN', entityID=-1, sectorID=sectorData.ident, radius=float(radius), teamIndex=sectorData.teamIndex, descriptionList={'array': []}, gameplayType=sectorData.gameplayType)

    def _appendEmptySector(self, sectorData):
        sectorRadius = self._playerAvatar.sectorRadius if USE_SECTOR_RADIUS_TABLE else sectorData.geometry.radius
        radius = sectorRadius if isinstance(sectorData.geometry, SectorGeometryCircle) else 0
        sectorFeatureName = sectorData.hudSettings.featuresName if not sectorData.hudSettings.isHideFeaturesName else ''
        newSector = self._sectors.append(entityID=-1, description=sectorData.hudSettings.description, sectorID=sectorData.ident, radius=float(radius), currentPoints=1, maxPoints=2, sectorTypeIconPath=sectorData.hudSettings.sectorIconPath, featuresIconPath=sectorData.hudSettings.featuresIconPath, miniMapSectorIconPath=sectorData.hudSettings.miniMapSectorIconPath, miniMapFeaturesIconPath=sectorData.hudSettings.miniMapFeaturesIconPath, isNeedToShowTimer=sectorData.hudSettings.isNeedToShowTimer, isBig=sectorData.hudSettings.isBig, isMulticolorInPermanentLockState=sectorData.hudSettings.isMulticolorInPermanentLockState, sectorName=sectorData.hudSettings.localizationID, featureName=sectorFeatureName, lockEndTime=0, bonusEndTime=0, teamIndex=sectorData.teamIndex, isAttack=-1, pointsInTick=0, playerSpawnEnabled=sectorData.playerSpawnEnabled, gameplayType=sectorData.gameplayType, sectorItems={'array': sectorData.hudSettings.sectorObjects}, descriptionList={'array': sectorData.hudSettings.descriptionList}, zOrder=0)
        planesEffectiveness = sectorData.hudSettings.planesEffectiveness
        for effectData in planesEffectiveness:
            newSector.planeEffectiveness.appendSilently(planeType=effectData['planeType'], effectiveness=effectData['effectivness'])
            newSector.planeEffectiveness.finishAppending()

    def _updateSectorProperty(self):
        for sector in self._sectors:
            sectorId = sector.sectorID.get()
            sectorData = self._getSectorByID(sectorId)
            entity = sectorData.entity
            sectorData.eNextBonusTickChanged += self._onNextBonusTickChanged
            if sector:
                sector.entityID = entity.id
                sector.entityPosition = self._makePosition(entity.position)
                self._log.debug(' SECTORS : updateSectorProperty: %s %s', entity.id, self._makePosition(entity.position))
                sector.currentPoints = int(sectorData.capturePointsByTeams[self._playerTeamIndex])
                sector.maxPoints = int(sum(list(sectorData.capturePointsByTeams)))
                self._updateBonusEndTime(sectorId)
                sector.teamIndex = sectorData.teamIndex
                sector.isPermanentLock = bool(sectorData.isLockForBattle)
                sector.pointsInTick = self._getPointsInTick(sectorId, self.gameMode.currentTick)
                sector.isFeatureDisable = self._isFeatureDisable(sectorId)

        for base in self._bases:
            baseID = base.sectorID.get()
            baseData = self._getSectorByID(baseID)
            base.entityID = baseData.entity.id
            baseTeamIndex = base.teamIndex.get()
            key = ALLY if baseTeamIndex == self._playerTeamIndex else ENEMY
            base.descriptionList = {'array': [BASE_SECTORS_LOCALE[key]]}

    def _updateSectorsZOrder(self):
        sectorsDists = []
        playerPos = BigWorld.player().position
        for sector in self._sectors:
            sectorId = sector.sectorID.get()
            sectorData = self._getSectorByID(sectorId)
            playerToSectorDist = (sectorData.entity.position - playerPos).length
            sectorsDists.append((sectorId, playerToSectorDist))

        orderedSectors = sorted(sectorsDists, None, lambda e: e[1], True)
        for sector in self._sectors:
            sector.zOrder = findSuitableIndex(orderedSectors, lambda e: e[0] == sector.sectorID.get())

        self._updateZOrderCallback = BigWorld.callback(1, self._updateSectorsZOrder)
        return

    def _makePosition(self, position):
        testPosition = self.__getAltitude4Point(position)
        return {'x': position.x,
         'y': testPosition.y,
         'z': position.z}

    def __getAltitude4Point(self, position):
        res = None
        basePosition = Math.Vector3(position.x, 0, position.z)
        heightCollide = BigWorld.hm_collideSimple(BigWorld.player().spaceID, position, basePosition)
        if heightCollide is not None:
            res = heightCollide[0]
        else:
            res = basePosition
        return res

    def _getNextBonusTime(self, sectorId):
        sectorData = self._getSectorByID(sectorId)
        tickCount = sectorData.nextBonusTick - self.gameMode.currentTick
        bonusTime = self.gameMode.getTickPeriod() * tickCount
        bonusTimeLeft = self.gameMode.currentTickStartedAt - BigWorld.player().arenaStartTime + bonusTime
        return int(round(bonusTimeLeft))

    def _getSectorByID(self, sectorId):
        """ACSectorClient instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACSectorClient.ACSectorClient
        """
        return self.gameMode.sectors[sectorId]

    def _onNextBonusTickChanged(self, ident, *args, **kwargs):
        sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == ident)
        self._updateBonusEndTime(ident)
        sectorStructure.pointsInTick = self._getPointsInTick(ident, self.gameMode.currentTick)

    def _updateBonusEndTime(self, ident):
        sectorStructure = self._sectors.first(lambda e: e.sectorID.get() == ident)
        bonusEndTime = self._getNextBonusTime(ident)
        if sectorStructure.bonusEndTime.get() != bonusEndTime:
            if bonusEndTime + BigWorld.player().arenaStartTime > BigWorld.serverTime():
                sectorStructure.bonusEndTime = bonusEndTime
                self._log.debug(' SECTORS LOG sectorStructure.bonusEndTime : %s', bonusEndTime)

    def _isFeatureDisable(self, sectorID):
        sector = self._getSectorByID(sectorID)
        _bonus = sector.settings.bonusType
        if sector.teamIndex == 0:
            if _bonus in FEATURE_DISABLE_SETTINGS.get(self._clientArena.gameModeName, []):
                return True
        return False

    def dispose(self):
        if self._updateZOrderCallback:
            BigWorld.cancelCallback(self._updateZOrderCallback)
            self._updateZOrderCallback = None
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_CAPTURE_POINTS_CHANGED, self._onCapturePointsChanged)
        self._gameMode.removeEventHandler(AC_EVENTS.GAME_MODE_TICK, self._onGameModeTick)
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        self._gameMode.removeEventHandler(AC_EVENTS.BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED, self._onSectorBombersChangeTarget)
        self._gameMode.removeEventHandler(AC_EVENTS.ROCKET_V2_TARGET_SECTOR_CHANGED, self._onSectorRocketsChangeTarget)
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_PERMANENT_LOCK, self._onSectorpermanentLock)
        self.gameMode.eGameModeReady -= self._setupModel
        self._sectors = None
        self._targetList = None
        self._clientArena = None
        self._playerAvatar = None
        self._gameMode = None
        return