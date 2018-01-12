# Embedded file name: scripts/common/DestructibleObjectFactory.py
import BigWorld
import GameEnvironment
import db.DBLogic
from modelManipulator.ModelManipulator3 import ModelManipulator3
from Weapons import Weapons
from ShellController import ShellController
from audio.SoundController import SoundController
from EntityHelpers import buildAndGetWeaponsInfo, filterPivots
from db.DBParts import buildPartsMapByPartName
from ClientGroundTurretLogic import ClientGroundTurretLogic
from debug_utils import LOG_DEBUG
from GunsController.GunsFactory import GunsFactory

class DestructibleObjectFactory(object):

    @staticmethod
    def createControllers(objID, settingsRoot, logicSettings, partTypes, partStates, weaponsSlot = None, owner = None, fullLoading = True, callback = None, turretsName = None, camouflage = None, decals = None):
        """
        create Weapons, ShellController and ModelManipulator controllers
        @param objID:
        @param settingsRoot: object settings (result of db.DBLogic.g_instance.getAircraftData() for Avatar for example)
        @param logicSettings: same with settingsRoot for TeamObjects but settingsRoot.airplane for Avatars
        @param partTypes:
        @param partStates:
        @param weaponsSlot: must be set for objects with MainWeaponController - like Avatar
        @param owner: entity inst.
        @return created controllers dictionary
        """
        player = BigWorld.player()
        isPlayer = player and objID == player.id
        controllersData = {'settings': settingsRoot,
         'copyFromAvatarID': 0,
         'avatarID': objID}
        weaponsSettings = hasattr(settingsRoot, 'components') and settingsRoot.components.weapons2 or None
        weapons = None
        gunsData = []
        shelsData = dict()
        weaponSoundID = None
        turretSoundIDByTurretID = None
        if weaponsSettings:
            if weaponsSlot is not None:
                if hasattr(BigWorld.player(), 'globalID'):
                    data = settingsRoot.airplane.flightModel.weaponSlot
                    mainWeaponsInfo = buildAndGetWeaponsInfo(weaponsSettings, weaponsSlot, data)
                else:
                    mainWeaponsInfo = buildAndGetWeaponsInfo(weaponsSettings, weaponsSlot)
                pivots = filterPivots(settingsRoot.pivots, partTypes, weaponsSlot)
                beltsMap = None
                if isPlayer and player.__class__.__name__ == 'PlayerAvatar':
                    beltsMap = dict(((record['key'], record['value']) for record in player.ammoBelts))
                gunGroups = GunsFactory().create(mainWeaponsInfo, settingsRoot.airplane.id, pivots, beltsMap)
                weapons = Weapons(None, gunGroups)
                controllersData['weapons'] = weapons
                weaponSoundID = []
                for group in weapons.guns.groups:
                    weaponSoundID.append(group.gunProfile.sounds.weaponSoundID)

                controllersData['shellController'] = ShellController(owner, mainWeaponsInfo, pivots)
                shelsData = controllersData['shellController'].getShelsModels()
                gunsData = [ (gun.flamePath,
                 group.gunProfile.bulletShot,
                 gun.uniqueId,
                 gun.shellPath,
                 getattr(group.gunDescription, 'bulletShell', '')) for group in weapons.getGunGroups() for gun in group.guns ]
        turretName = turretsName[0] if turretsName else ''
        if turretName and db.DBLogic.g_instance.getTurretData(turretName) is not None:
            isTeamObject = False
            if turretName == 't_h' or turretName == 't1':
                isTeamObject = True
            gunnersPartsMap = buildPartsMapByPartName('Gunner', logicSettings.partsSettings, partTypes)
            if gunnersPartsMap:
                if not isTeamObject:
                    component, turretSoundIDByTurretID, turretGunsData = DestructibleObjectFactory._createMultiTurret(owner, logicSettings, turretsName, gunnersPartsMap)
                    controllersData['turretsLogic'] = component
                    gunsData.extend(turretGunsData)
                else:
                    gunnersParts = dict(((partID, (True, partType)) for partID, partType in gunnersPartsMap.items()))
                    turrets = ClientGroundTurretLogic(owner, gunnersParts, turretName)
                    controllersData['turretsLogic'] = turrets
                    profile = db.DBLogic.g_instance.getGunProfileData(turrets.gunDescription.gunProfileName)
                    for gunner in turrets.gunners.values():
                        if turrets.settings.flamePathes:
                            for i, flamePath in enumerate(turrets.settings.flamePathes):
                                path = flamePath
                                shellPath = turrets.settings.shellPathes[i] if turrets.settings.shellPathes and i < len(turrets.settings.shellPathes) else ''
                                gunsData.append((path,
                                 profile.bulletShot[0],
                                 gunner.gun.uniqueId + i,
                                 shellPath,
                                 profile.bulletShell))

                    turretSoundIDByTurretID = {}
                    for gunnerId, group in turrets.gunners.iteritems():
                        profile = db.DBLogic.g_instance.getGunProfileData(group.ammoBelt.gunDescription.gunProfileName)
                        turretSoundIDByTurretID[gunnerId] = profile.sounds.weaponSoundID

        modelManipulator = ModelManipulator3(isPlayer, objID, logicSettings, partTypes, partStates, gunsData, shelsData, weaponsSettings, weaponsSlot, fullLoading, callback, 0, weaponSoundID, turretSoundIDByTurretID, camouflage=camouflage, decals=decals)
        controllersData['modelManipulator'] = modelManipulator
        controllersData['soundController'] = SoundController(owner, modelManipulator, objID, weaponSoundID, turretSoundIDByTurretID)
        return controllersData

    @staticmethod
    def _createMultiTurret(owner, logicSettings, turretsName, gunnersPartsMap):
        from ClientPlaneTurret.TurretComponent import TurretComponent
        from ClientPlaneTurret.TurretBuilder import PrepareTurretData, PlaneTurretBuilder
        turretNameDict = {}
        for turretName in turretsName:
            partIDs = db.DBLogic.g_instance.findAircraftPartIDsByUpgradeName(logicSettings.name, turretName)
            for partID in partIDs:
                if partID in gunnersPartsMap:
                    turretNameDict[partID] = turretName
                    break

        tdb = dict(((partID, (turretNameDict.get(partID, turretsName[0]), partType)) for partID, partType in gunnersPartsMap.iteritems()))
        data = PrepareTurretData(tdb)
        component = TurretComponent(owner, PlaneTurretBuilder(data.turretsData))
        return (component, data.turretSoundIDsByTurretID, data.turretGunsData)