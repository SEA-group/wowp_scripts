# Embedded file name: scripts/client/gui/HUD2/features/Respawn/RespawnSource.py
import BWLogging
from _airplanesConfigurations_db import getAirplaneConfiguration
from _skills_data import SkillDB
import BigWorld
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from GameModeSettings import ACSettings as SETTINGS
from Helpers.i18n import localizeAirplane
from clientConsts import PLANE_TYPE_ICO_PATH
from consts import PLANE_CLASS, TEAM_ID, COMPONENT_TYPE, UPGRADE_TYPE, UPGRADE_TYPE_TO_COMPONENT_TYPE
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature

class RespawnSource(DataSource):

    def __init__(self, features):
        self._logger = BWLogging.getLogger(self.__class__.__name__)
        self._model = features.require(Feature.GAME_MODEL).respawn
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._db = features.require(Feature.DB_LOGIC)
        self._gameMode = self._clientArena.gameMode
        self._sectors = {}
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._clientArena.onUpdatePlayerStats += self._onUpdatePlayerStats
        self._playerAvatar.ePlaneBattleHintDataReceived += self._ePlaneBattleHintDataReceived
        self._gameMode.addEventHandler(AC_EVENTS.BATTLE_EVENT, self._onBattleEvent)
        self._isNoRespawn = False
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        if self.gameMode.isReady:
            self._setBaseTeamIndex()
        else:
            self.gameMode.eGameModeReady += self._setBaseTeamIndex
        return

    def _onBattleEvent(self, batleEventID):
        self._model.respawnUnlimited = False
        self._isNoRespawn = True

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eRescueTimeChanged -= self._updateRespawnTime
        self._playerAvatar.eRescueTimeChanged += self._updateRespawnTime
        self._gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        arenaTypeData = self._db.getArenaData(BigWorld.player().arenaType)
        avatarInfo = self._clientArena.getAvatarInfo(self._playerAvatar.id)
        self._onUpdatePlayerStats(avatarInfo)
        endTime = int(round(self._playerAvatar.rescueTime - BigWorld.player().arenaStartTime))
        self._model.timeToRespawnPossibility = endTime
        self._model.timeToAutoRespawn = endTime + SETTINGS.RESPAWN.AUTO_RESPAWN_TIME
        self._model.respawnUnlimited = arenaTypeData.gameModeSettings.respawn.unlimited
        self._model.selectedPlaneID = self._playerAvatar.objTypeID
        self._model.spawnSectorID = self._findInitialSpawnSectorID()
        self.setPlanes()
        self._updateRespawnTime()

    def _onUpdatePlayerStats(self, avatarInfo):
        if avatarInfo['avatarID'] == self._playerAvatar.id:
            stats = avatarInfo['stats']
            avatarLives = stats['lifes']
            if avatarLives == -1:
                self._model.respawnAmount = 10
                self._model.respawnUnlimited = True
            else:
                self._model.respawnUnlimited = False
                self._model.respawnAmount = avatarLives

    def _setBaseTeamIndex(self, *args, **kwargs):
        for sectorData in self.gameMode.sectors.values():
            if sectorData.teamIndex != TEAM_ID.TEAM_2:
                self._sectors[sectorData.ident] = sectorData.teamIndex

        self._updateSectors()

    def _findInitialSpawnSectorID(self):
        self._arenaTypeData = self._db.getArenaData(self._playerAvatar.arenaType)
        for sectorData in self._arenaTypeData.sectors.sectors.values():
            if sectorData.isBase and sectorData.teamIndex == self._playerAvatar.teamIndex:
                return sectorData.ident

    def _onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
        self._sectors[sectorId] = teamIndex
        self._updateSectors()
        self._checkPoint(sectorId, teamIndex)
        sector = self._getSectorByID(sectorId)
        if self._model.timeToRespawnPossibility.get() < 2:
            return
        if sector.settings.respawnCooldownReduceEnabled:
            if oldTeamIndex != TEAM_ID.TEAM_2:
                if self._playerAvatar.teamIndex == teamIndex:
                    localID = 'UI_MESSAGE_EVENT_AIRFIELD_CAP'
                else:
                    localID = 'UI_MESSAGE_EVENT_AIRFIELD_LOST'
                endTime = int(self._playerAvatar.rescueTime)
                if endTime > BigWorld.serverTime():
                    reduceData = {'teamIndex': teamIndex,
                     'time': self.gameMode.arenaTypeData.gameModeSettings.respawn.respawnStrategySettings.cooldownReduceStep,
                     'localID': localID}
                    self._model.changeRespawnTimeData = reduceData
                    self._model.changeRespawnTimeData = {}

    def _checkPoint(self, sectorId, teamIndex):
        if self._model.spawnSectorID.get() == sectorId:
            if self._playerAvatar.teamIndex != teamIndex:
                self._model.spawnSectorID = self._findInitialSpawnSectorID()

    def _updateSectors(self):
        isEnableRespawnBySector = False
        for sector in self._sectors:
            if self._playerAvatar.teamIndex == self._sectors[sector]:
                from db.DBLogic import g_instance as db
                self._arenaTypeData = db.getArenaData(BigWorld.player().arenaType)
                if self._arenaTypeData.sectors.getSector(sector).tacticalRespawnEnabled:
                    isEnableRespawnBySector = True

        if self._model.respawnIsAvailableBySector.get() != isEnableRespawnBySector:
            self._model.respawnIsAvailableBySector = isEnableRespawnBySector

    def setPlanes(self):
        for planeID in self._playerAvatar.availablePlanes:
            data = self._db.getAircraftData(planeID).airplane
            isPremium = self._db.isPlanePremium(planeID)
            isElite = planeID in self._playerAvatar.elitePlanes
            isPrimary = planeID in self._playerAvatar.primaryPlanes
            planeStatus = PLANE_CLASS.PREMIUM if isPremium else isElite * PLANE_CLASS.ELITE or PLANE_CLASS.REGULAR
            self._model.planes.append(planeID=planeID, planeNameShort=localizeAirplane(data.name), planeLevel=data.level, iconPath=data.iconPath, planeType=data.planeType, nation=self._db.getNationIDbyName(data.country), planeStatus=planeStatus, isPrimary=isPrimary, typeIconPath=PLANE_TYPE_ICO_PATH.iconHud(data.planeType, planeStatus))

    def _ePlaneBattleHintDataReceived(self, data):
        globalId = data.globalID
        planeId = self._db.getPlaneIDByGlobalID(globalId)
        planeStrc = self._model.planes.first(lambda a: a.planeID.get() == planeId)
        self.updateSkills(data.crewSkills, planeStrc)
        self.updateEquipment(data.equipment, planeStrc)
        self.updateConsumable(data.consumables, planeStrc)
        self.updateAmmobelts(data.ammoBelts, planeStrc, planeId)
        self.updateAmmunition(data.shellsCount, planeStrc, globalId, planeId)

    def updateAmmunition(self, ammunitionData, modelPlaneStrc, globalId, planeId):
        modelPlaneStrc.ammunitions.clean()
        for slotID, confID in getAirplaneConfiguration(globalId).weaponSlots:
            weaponInfo = self._db.getWeaponInfo(planeId, slotID, confID)
            if not weaponInfo:
                continue
            wType, wName, _ = weaponInfo
            if wType in (UPGRADE_TYPE.BOMB, UPGRADE_TYPE.ROCKET):
                component = self._db.getComponentByName(UPGRADE_TYPE_TO_COMPONENT_TYPE[wType], wName)
                ammunitionStrc = modelPlaneStrc.ammunitions.first(lambda a: a.id.get() == slotID)
                if not ammunitionStrc:
                    modelPlaneStrc.ammunitions.append(id=slotID, iconPath=component.iconPathSmall, ammoName='WEAPON_NAME_' + component.caliber, isInstalled=True)

        for data_ in ammunitionData:
            id_ = data_.key
            ammunitonStrc = modelPlaneStrc.ammunitions.first(lambda a: a.id.get() == id_)
            if ammunitonStrc:
                ammunitonStrc.amount = data_.value

    def updateAmmobelts(self, ammobeltData, modelPlaneStrc, planeId):
        modelPlaneStrc.ammoBelts.clean()
        for data_ in ammobeltData:
            id_ = data_.key
            beltId = data_.value
            gun = self._db.getComponentByName(COMPONENT_TYPE.GUNS, id_)
            gunCount = self._db.getGunsCount(planeId, gun.name)
            belt = self._db.getComponentByID(COMPONENT_TYPE.AMMOBELT, beltId)
            beltStrc = modelPlaneStrc.ammoBelts.first(lambda a: a.id.get() == id_)
            if not beltStrc:
                modelPlaneStrc.ammoBelts.append(id=beltId, iconPath=belt.lobbyIconPath, caliber=gun.caliber, count=gunCount)

    def updateEquipment(self, equipmentData, modelPlaneStrc):
        modelPlaneStrc.equipments.clean()
        for id_ in equipmentData:
            equipment = self._db.getEquipmentByID(id_)
            if equipment:
                equipmentStrc = modelPlaneStrc.equipments.first(lambda a: a.id.get() == id_)
                if not equipmentStrc:
                    modelPlaneStrc.equipments.append(id=id_, iconPath=equipment.icoPathSmall)

    def updateConsumable(self, consumablesData, modelPlaneStrc):
        modelPlaneStrc.consumables.clean()
        for data_ in consumablesData:
            id_ = data_.key
            consumable = self._db.getConsumableByID(id_)
            if consumable:
                consumableStrc = modelPlaneStrc.consumables.first(lambda a: a.id.get() == id_)
                if not consumableStrc:
                    modelPlaneStrc.consumables.append(id=id_, iconPath=consumable.icoPathSmall)

    def updateSkills(self, crewSkills, modelPlaneStrc):
        modelPlaneStrc.crews.clean()
        for data_ in crewSkills:
            specializationID = data_.specializationID
            crewMemberStrc = modelPlaneStrc.crews.first(lambda a: a.specialization.get() == specializationID)
            if not crewMemberStrc:
                crewMemberStrc = modelPlaneStrc.crews.append(specialization=specializationID, specializationResearchPercent=0)
                for skillIndex, skillData_ in enumerate(data_.skills):
                    id_ = getattr(skillData_, 'key')
                    skill = SkillDB[id_]
                    mainForSpecialization = getattr(skill, 'mainForSpecialization', -1)
                    if mainForSpecialization == -1:
                        crewMemberStrc.skills.appendSilently(id=id_, iconPath=skill.smallIcoPath)
                    else:
                        crewMemberStrc.specializationResearchPercent = getattr(skillData_, 'value')

                crewMemberStrc.skills.finishAppending()

    def _updateRespawnTime(self, *args, **kwargs):
        endTime = int(round(self._playerAvatar.rescueTime - BigWorld.player().arenaStartTime))
        deathTime = int(round(BigWorld.serverTime() - BigWorld.player().arenaStartTime))
        self._model.deathTime = deathTime
        self._model.timeToRespawnPossibility = endTime
        self._model.timeToAutoRespawn = endTime + SETTINGS.RESPAWN.AUTO_RESPAWN_TIME
        if self._isNoRespawn:
            self._model.respawnAmount = 0
            self._model.respawnUnlimited = False

    @property
    def gameMode(self):
        """Game mode instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        return self._gameMode

    def _getSectorByID(self, sectorId):
        """ACSectorClient instance
        @rtype: ArenaHelpers.GameModes.AreaConquest.ACSectorClient.ACSectorClient
        """
        return self.gameMode.sectors[sectorId]

    def dispose(self):
        self._gameMode.removeEventHandler(AC_EVENTS.BATTLE_EVENT, self._onBattleEvent)
        self._gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self._onSectorStateChanged)
        self._playerAvatar.eRescueTimeChanged -= self._updateRespawnTime
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self.gameMode.eGameModeReady -= self._setBaseTeamIndex
        self._clientArena.onUpdatePlayerStats -= self._onUpdatePlayerStats
        self._playerAvatar.ePlaneBattleHintDataReceived -= self._ePlaneBattleHintDataReceived
        self._model = None
        self._playerAvatar = None
        self._clientArena = None
        self._gameMode = None
        self._sectors = {}
        return