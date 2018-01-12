# Embedded file name: scripts/client/gui/HUD2/features/Ammunitions/AmmunitionSource.py
import math
import BigWorld
import InputMapping
import consts
from EntityHelpers import isCorrectBombingAngle, LOG_DEBUG, EntityStates
from Helpers.i18n import localizeLobby
from consts import UPDATABLE_TYPE, SHELL_INDEX
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from gui.Scaleform.UIHelper import getKeyLocalization

class AmmunitionSource(DataSource):

    def __init__(self, features):
        self._LOG_TAG = '  AMMUNITION : '
        self._model = features.require(Feature.GAME_MODEL).ammunitions
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._timer = features.require(Feature.TIMER_SERVICE)
        self._db = features.require(Feature.DB_LOGIC)
        self._ms = features.require(Feature.MEASUREMENT_SYSTEM)
        self._playerAvatar.eUpdateHUDAmmo += self._onPlayerLaunchShell
        self._playerAvatar.eTacticalRespawnEnd += self._onRespawn
        self._playerAvatar.eTacticalSpectator += self._onRespawn
        self._playerAvatar.eUpdateShellsRechargeInfo += self._onPlayerUpdateShellsInfo
        self._modelSetted = False
        self._playerAvatar.onStateChanged += self._onStateChanged
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._isCorrectBombAngel = True
        self._weaponDataDict = {}
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    @property
    def shellsController(self):
        """Shells controller assigned to entity
        @rtype: ShellController.ShellController
        """
        return self._playerAvatar.getShellController()

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._timer.eUpdate1Sec += self._onUpdateTimer
        self.addBaseAmmunition()
        self._modelSetted = True

    def _onStateChanged(self, oldState, state):
        if state & (EntityStates.DESTROYED | EntityStates.DESTROYED_FALL):
            if oldState & EntityStates.GAME_CONTROLLED:
                weaponGroups = self._playerAvatar.getShellsInitialInfo()
                for groupID, weaponData in weaponGroups.items():
                    if weaponData.get('description', None) is not None:
                        shellIndex = weaponData.get('shellIndex')
                        sectorStructure = self._model.ammunitions.first(lambda e: e.id.get() == shellIndex)
                        sectorStructure.amount = weaponData.get('initialCount')

        return

    def addBaseAmmunition(self):
        weaponGroups = self._playerAvatar.getShellsInitialInfo()
        for groupID, weaponData in weaponGroups.items():
            if weaponData.get('description', None) is not None:
                self._addAmmunition(weaponData)

        self._onPlayerUpdateShellsInfo()
        return

    def _onUpdateTimer(self):
        for key in self._weaponDataDict:
            if self._weaponDataDict[key].get('shellID') == UPDATABLE_TYPE.BOMB:
                ammunitionStructure = self._model.ammunitions.first(lambda e: e.id.get() == key)
                if ammunitionStructure:
                    isAvailable = isCorrectBombingAngle(BigWorld.player(), BigWorld.player().getRotation())
                    if isAvailable != self._isCorrectBombAngel:
                        ammunitionStructure.isAvailable = isAvailable
                    self._isCorrectBombAngel = isAvailable

    def _onRespawn(self, *args, **kwargs):
        LOG_DEBUG(self._LOG_TAG, '_onRespawn: ')
        self._model.ammunitions.clean()
        self.addBaseAmmunition()

    def _onPlayerLaunchShell(self):
        for ammunitionStructure in self._model.ammunitions:
            shellTypeID = ammunitionStructure.id.get()
            ammount = self._getCount(shellTypeID)
            if ammunitionStructure.amount.get() != ammount:
                if ammount != -1:
                    LOG_DEBUG(self._LOG_TAG, 'updateCount')
                    ammunitionStructure.amount = self._getCount(shellTypeID)

    def _onPlayerUpdateShellsInfo(self):
        for shellData in self._playerAvatar.shellsRechargeInfo:
            ammunitionStructure = self._model.ammunitions.first(lambda e: e.id.get() == shellData.shellIndex)
            if ammunitionStructure:
                endTime = shellData['rechargeTime'] + shellData['startedAt']
                rechargeDuration = shellData['rechargeDuration']
                cooldownStartTime = int(endTime - rechargeDuration - BigWorld.player().arenaStartTime)
                if ammunitionStructure.cooldownStartTime.get() != cooldownStartTime:
                    ammunitionStructure.cooldownStartTime = cooldownStartTime
                coolDownEndTime = int(endTime - BigWorld.player().arenaStartTime)
                if ammunitionStructure.cooldownEndTime.get() != coolDownEndTime:
                    ammunitionStructure.cooldownEndTime = coolDownEndTime

    def _addAmmunition(self, weaponData):
        shellIndex = weaponData.get('shellIndex')
        wepDesciption = weaponData.get('description')
        componentType = weaponData.get('componentType')
        compData = self._db.getComponentByName(componentType, wepDesciption.name)
        propsList = []
        if compData is not None and hasattr(compData, 'tag'):
            for x in compData.tag:
                data = {'tagName': x.name,
                 'tagType': x.type}
                propsList.append(data)

        explosionRadius = int(self._ms.getMeters(round(wepDesciption.explosionRadius / consts.WORLD_SCALING)))
        explosionDamage = int(wepDesciption.explosionDamage)
        wepName = 'WEAPON_NAME_' + wepDesciption.name.upper()
        self._model.ammunitions.append(id=shellIndex, iconPath=wepDesciption.hudIcoPath, shellIcon=wepDesciption.shellIcon, amount=self._getCount(shellIndex), cluster=self._getPortion(shellIndex), amountMax=weaponData.get('initialCount'), key=self._getKeys(weaponData.get('shellID'), shellIndex), componentType=weaponData.get('componentType', -1), cooldownStartTime=-1, cooldownEndTime=-1, propsList=propsList, explosionRadius=explosionRadius, explosionDamage=explosionDamage, ammoName=wepName, isAvailable=True)
        self._weaponDataDict[shellIndex] = weaponData
        return

    def _getPortion(self, shellIndex):
        settings = self.shellsController.getShellCommonData(shellIndex)
        key = 'portion'
        if settings:
            if key in settings:
                return int(max(1, settings[key]))
        return -1

    def _getCount(self, shellIndex):
        return self.shellsController.getShellCount(shellIndex)

    def _getKeys(self, shellID, shellIndex):
        if shellID != -1:
            key = getKeyLocalization(InputMapping.CMD_LAUNCH_ROCKET) if shellIndex == SHELL_INDEX.TYPE1 else getKeyLocalization(InputMapping.CMD_LAUNCH_BOMB)
            return key

    def dispose(self):
        self._playerAvatar.eUpdateHUDAmmo -= self._onPlayerLaunchShell
        self._playerAvatar.eUpdateShellsRechargeInfo -= self._onPlayerUpdateShellsInfo
        self._playerAvatar.eTacticalRespawnEnd -= self._onRespawn
        self._playerAvatar.eTacticalSpectator -= self._onRespawn
        if self._modelSetted:
            self._timer.eUpdate1Sec -= self._onUpdateTimer
        else:
            self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.onStateChanged -= self._onStateChanged
        self._model = None
        self._playerAvatar = None
        self._clientArena = None
        self._timer = None
        self._ms = None
        self._weaponDataDict = None
        return