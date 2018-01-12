# Embedded file name: scripts/client/gui/HUD2/features/AmmoBelts/AmmoBeltsSource.py
import consts
from EntityHelpers import EntityStates
from consts import COMPONENT_TYPE, AMMOBELT_SPECS, BULLET_FLY_DIST_CORRECTION
from gui.HUD2.core.DataPrims import DataSource
from gui.HUD2.hudFeatures import Feature
from Helpers.iconPathHelper import get24ModuleIconPath
BELT_TYPE_DESCRIPTION = {'standartbelt': 'TOOLTIP_STANDARTBELT_WEP',
 'armourpiercingbelt': 'TOOLTIP_ARMOURPIERCINGBELT_EFF_ALL_WEP',
 'ap_incinerating': 'TOOLTIP_AP-INCINERATINGBELT_EFF_RAPID-FIRE_WEP',
 'armourpiercingbelt2': 'TOOLTIP_FRAGBELT_EFF_BIG_WEP',
 'fugasbelt': 'TOOLTIP_GENERALPURPOSEBELT_EFF_ALL_WEP'}

class AmmoBeltsSource(DataSource):

    def __init__(self, features):
        self._LOG_TAG = '  AMMOBELTS : '
        self._model = features.require(Feature.GAME_MODEL).ammoBelts
        self._clientArena = features.require(Feature.CLIENT_ARENA)
        self._ms = features.require(Feature.MEASUREMENT_SYSTEM)
        self._playerAvatar = features.require(Feature.PLAYER_AVATAR)
        self._db = features.require(Feature.DB_LOGIC)
        self._clientArena.onNewAvatarsInfo += self._setupModel
        self._weaponGroup = {}
        if self._clientArena.isAllServerDataReceived():
            self._setupModel(None)
        return

    def _setupModel(self, newInfos):
        self._clientArena.onNewAvatarsInfo -= self._setupModel
        self._playerAvatar.eUpdateHUDAmmo += self._updateBelts
        self._playerAvatar.eTacticalSpectator += self._onTacticalSpectator
        self._addBaseBelts()

    def _onTacticalSpectator(self, *args, **kwargs):
        self._model.ammoBelts.clean()
        self._addBaseBelts()

    def _addBaseBelts(self):
        weaponGroups = self._playerAvatar.getAmmoBeltsInitialInfo()
        from consts import MAX_WEAPON_GROUP
        groups = [0] + [1] * MAX_WEAPON_GROUP
        for groupID in weaponGroups.iterkeys():
            groups[groupID] = 0

        for groupID, weaponData in weaponGroups.items():
            if weaponData.get('description', None) is not None:
                self._addAmmunition(weaponData, groupID)

        return

    def _updateBelts(self):
        if EntityStates.inState(self._playerAvatar, EntityStates.WAIT_START):
            self._model.ammoBelts.clean()
            self._addBaseBelts()
        else:
            ammoGroups = self._playerAvatar.getBeltsAmmoCountByGroup()
            for groupID in ammoGroups:
                beltStructure = self._model.ammoBelts.first(lambda e: e.id.get() == groupID)
                if beltStructure:
                    status = ammoGroups[groupID]
                    if status != beltStructure.status.get():
                        beltStructure.status = status

    def _addAmmunition(self, weaponData, groupID):
        beltId = weaponData.get('id')
        beltData = self._db.getComponentByID(COMPONENT_TYPE.AMMOBELT, beltId)
        if beltData is None:
            return
        else:
            weapName = weaponData.get('weaponName')
            gunData = self._db.getGunData(weapName)
            beltIcon = beltData.hudIconPath
            beltType = beltData.beltType
            beltIconSmall = get24ModuleIconPath(beltData.lobbyIconPath)
            effectiveDistance = self._ms.getMeters(BULLET_FLY_DIST_CORRECTION * gunData.bulletFlyDist / consts.WORLD_SCALING)
            gunName = 'WEAPON_NAME_' + weaponData.get('description').weapName.upper()
            beltName = 'WEAPON_NAME_' + beltData.ui_name.upper()
            propsList = []
            if gunData is not None and hasattr(gunData, 'tag'):
                for x in gunData.tag:
                    data = {'tagName': x.name,
                     'tagType': x.type}
                    propsList.append(data)

            newBelt = self._model.ammoBelts.append(id=groupID, iconPath=beltIcon, count=weaponData.get('objCount'), status=0, caliber=weaponData.get('description').caliber, dps=int(weaponData.get('description').DPS), rpm=int(weaponData.get('description').RPM), effectiveDistance=int(round(effectiveDistance)), gunName=gunName, beltName=beltName, beltType=beltType, beltIconSmall=beltIconSmall, propsList=propsList)
            for spec in AMMOBELT_SPECS.SPEC_LIST:
                value, flag = self._db.calculateBeltSpec(gunData, beltData, spec)
                newBelt.specs.appendSilently(specName=spec.locTag, specType=int(round(flag)), value=round(value))

            newBelt.specs.finishAppending()
            return

    def dispose(self):
        self._playerAvatar.eUpdateHUDAmmo -= self._updateBelts
        self._playerAvatar.eTacticalSpectator -= self._onTacticalSpectator
        self._model = None
        self._clientArena = None
        self._playerAvatar = None
        self._weaponGroup = None
        self._ms = None
        return