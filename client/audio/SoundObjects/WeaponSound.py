# Embedded file name: scripts/client/audio/SoundObjects/WeaponSound.py
from WwiseGameObject import WwiseGameObject, GS, WwiseGameObjectFactory
import BigWorld
import math
import GameEnvironment
import Settings
from audio.AKTunes import Weapon_Orientation_Update_Ms, RTPC_Zoomstate_MAX, RTPC_Aircraft_Camera_Zoomstate_VDT, RTPC_Zoomstate_MAX, FREECAM_DIST_STEP, SOUND_CALLBACKS_PER_TICK
import db.DBLogic
from WWISE_ import setState
from audio.SoundBanksManager import SoundBanksManager
from audio.SoundObjectSettings import SoundObjectSettings
from audio.AKConsts import SOUND_CASES, SOUND_OBJECT_TYPES

class WeaponSound(WwiseGameObject):

    def __init__(self, eid, cid, node, weaponSoundID, shootEvent, isAA = False, isTL = False):
        self.__eid = eid
        isPlayer = isAA == False and isTL == False and BigWorld.player().id == eid
        self.__isTL = isTL
        self.__shootEvent = shootEvent
        self.__stopEvent = str(self.__shootEvent).replace('Play_', 'Stop_')
        self.__looped = str(self.__shootEvent).find('loop') != -1
        self.__started = False
        if isPlayer:
            WwiseGameObject.__init__(self, '{0}-{1}'.format('Player', weaponSoundID), cid, node)
        elif isAA:
            WwiseGameObject.__init__(self, '{0}-{1}'.format('AA', weaponSoundID), cid, node)
        elif isTL:
            WwiseGameObject.__init__(self, '{0}-{1}'.format('TL', weaponSoundID), cid, node)
        else:
            WwiseGameObject.__init__(self, '{0}-{1}'.format('NPC', weaponSoundID), cid, node)
        if not isPlayer or isAA or isTL:
            return
        self.__registerEvents()
        self.__onZoomStateChanged(Settings.g_instance.camZoomIndex)

    def __registerEvents(self):
        cam = GameEnvironment.getCamera()
        cam.eZoomStateChanged += self.__onZoomStateChanged
        cam.eDistanceChanged += self.__onDistanceChanged
        BigWorld.player().eReportDestruction += self.__onReportDestruction

    def __clearEvents(self):
        cam = GameEnvironment.getCamera()
        cam.eZoomStateChanged -= self.__onZoomStateChanged
        cam.eDistanceChanged -= self.__onDistanceChanged
        BigWorld.player().eReportDestruction -= self.__onReportDestruction

    def play(self):
        if GS().isReplayMute:
            return
        if self.__looped and self.__started and not self.__isTL:
            return
        self.postEvent(self.__shootEvent)
        self.__started = True

    def stop(self, stopMarker = True):
        if not self.__started:
            return
        else:
            self.postEvent(self.__stopEvent, None, stopMarker)
            self.__started = False
            return

    def isOneshot(self):
        return not self.__looped

    @staticmethod
    def getShootEventName(isPlayer, isAA, isTL, eventSet):
        tag = 'WeaponShootingNPC'
        if isPlayer:
            tag = 'WeaponShootingPlayer'
        elif isAA:
            tag = 'WeaponShootingAA'
        elif isTL:
            tag = 'WeaponShootingPlayerTL'
        return eventSet.get(tag, None)

    def __onLeaveWorld(self):
        WwiseGameObject.stopAll(self, 500, True)

    def __RTPC_Zoomstate(self, val):
        self.setRTPC('RTPC_Aircraft_Camera_Zoomstate', min(max(0, val), RTPC_Zoomstate_MAX), RTPC_Aircraft_Camera_Zoomstate_VDT)

    def __onZoomStateChanged(self, val):
        self.__RTPC_Zoomstate(RTPC_Zoomstate_MAX - val)

    def __onDistanceChanged(self, d):
        self.__RTPC_Zoomstate(math.floor(d / FREECAM_DIST_STEP))

    def __onReportDestruction(self, ki):
        if ki['victimID'] == self.__eid:
            self.stop()

    def __onAvatarLeaveWorld(self, avatar, eid):
        if self.__eid != eid:
            return
        self.stop()

    def clear(self):
        self.__clearEvents()
        self.__onLeaveWorld()


g_factory = None

class WeaponSoundFactory(WwiseGameObjectFactory):

    def __init__(self):
        self.__playerWeaponCounter = 0

    def createPlayer(self, so):
        shootEvent = WeaponSound.getShootEventName(True, False, False, so.soundSet)
        player = BigWorld.player()
        if shootEvent:
            so.wwiseGameObject = WeaponSound(player.id, so.context.cidProxy.handle, so.node.id, so.weaponID, shootEvent)
            weapons = player.controllers.get('weapons', None)
            weapons.linkSound(so.weaponID, so.wwiseGameObject)
            self.__playerWeaponCounter += 1
        if self.__playerWeaponCounter > 0:
            setState('STATE_Aircraft_Main_Weapons_Quantity', 'Shooting_{0}_GO'.format(min(4, self.__playerWeaponCounter)))
        else:
            setState('STATE_Aircraft_Main_Weapons_Quantity', 'None')
        return

    def createAvatar(self, avatar, so):
        if so.wwiseGameObject:
            return
        shootEvent = WeaponSound.getShootEventName(False, False, False, so.soundSet)
        if shootEvent:
            so.wwiseGameObject = WeaponSound(avatar.id, so.context.cidProxy.handle, so.node.id, so.weaponID, shootEvent)
            arena = GameEnvironment.getClientArena()
            avatarInfo = arena.avatarInfos.get(avatar.id, {})
            weapons = avatarInfo.get('weapons')
            weapons.linkSound(so.weaponID, so.wwiseGameObject)

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = WeaponSoundFactory()
        return g_factory

    @staticmethod
    def getSoundObjectSettings(data):
        info = data['info']
        isPlayer = data['isPlayer']
        weaponSoundID = data['weaponSoundID']
        soundObjects = data['soundObjects']
        context = data['context']
        alreadyLoadedWeaponsID = set()
        slot = -1
        for w in info.weapons:
            slot += 1
            if len(weaponSoundID) == slot:
                break
            if not isPlayer and weaponSoundID[slot] in alreadyLoadedWeaponsID:
                continue
            for hp in w:
                so = SoundObjectSettings()
                so.context = context
                so.mountPoint = hp
                so.weaponID = weaponSoundID[slot] if slot < len(weaponSoundID) else 'weapon_default'
                so.soundSet = GS().findLoadSet(db.DBLogic.g_instance.getWeaponSoundSet(so.weaponID), isPlayer)
                so.factory = WeaponSoundFactory.instance()
                soundObjects[SOUND_OBJECT_TYPES.WEAPONS[slot]] = so
                if not isPlayer:
                    alreadyLoadedWeaponsID.add(so.weaponID)
                    break