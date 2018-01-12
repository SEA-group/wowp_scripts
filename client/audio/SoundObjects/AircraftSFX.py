# Embedded file name: scripts/client/audio/SoundObjects/AircraftSFX.py
from WwiseGameObject import WwiseGameObject, GS, WwiseGameObjectFactory
import BigWorld
from audio.AKTunes import CritParts
from audio.AKConsts import AIRCRAFT_SFX, SOUND_OBJECT_TYPES
from consts import UPDATABLE_TYPE
from audio.AKConsts import PartState, SFX_SHELL_MECHANICS
import db.DBLogic
from audio.SoundObjectSettings import SoundObjectSettings
from EntityHelpers import EntityStates

class AircraftSFX(WwiseGameObject):

    def __init__(self, cid, node, set):
        self.__eventSet = set
        self.__flaps = False
        self.__player = BigWorld.player()
        self.__registerEvents()
        WwiseGameObject.__init__(self, 'AircraftSFX', cid, node)

    def __registerEvents(self):
        self.__player.ePartCrit += self.__onPartCrit
        self.__player.eReportDestruction += self.__onReportDestruction
        self.__player.onStateChanged += self.__onPlayerStateChanged
        self.__player.eLaunchShell += self.__onLaunchShell

    def __clearEvents(self):
        self.__player.ePartCrit -= self.__onPartCrit
        self.__player.eReportDestruction -= self.__onReportDestruction
        self.__player.onStateChanged -= self.__onPlayerStateChanged
        self.__player.eLaunchShell -= self.__onLaunchShell

    def __onPlayerStateChanged(self, oldState, state):
        if state == EntityStates.OUTRO:
            self.__onBattleEnd()

    def play(self, what, cat = AIRCRAFT_SFX.CATEGORY.MISC, cb = None):
        tag = '{0}{1}'.format(cat, what)
        e = self.__eventSet[tag]
        self.postEvent(e, cb)

    def stop(self, what, cat = AIRCRAFT_SFX.CATEGORY.MISC, cb = None):
        tag = '{0}{1}'.format(cat, what)
        e = str(self.__eventSet[tag]).replace('Play_', 'Stop_')
        self.postEvent(e, cb)

    def playFlaps(self, value):
        if value == 0:
            self.stop(AIRCRAFT_SFX.TYPE.FLAPS)
        elif not self.__flaps:
            self.play(AIRCRAFT_SFX.TYPE.FLAPS, AIRCRAFT_SFX.CATEGORY.MISC, self.__stoppedFlapsCB)
            self.__flaps = True

    def __stoppedFlapsCB(self):
        self.__flaps = False

    def __onReportDestruction(self, ki):
        if ki['victimID'] == BigWorld.player().id:
            WwiseGameObject.stopAll(self, 100)

    def __onLeaveWorld(self):
        WwiseGameObject.stopAll(self, 500, True)

    def __onPartCrit(self, part):
        stateID = part.logicalState
        name = part.partTypeData.componentType
        if stateID == PartState.Damaged and name in CritParts:
            self.play(AIRCRAFT_SFX.TYPE.CRIT, AIRCRAFT_SFX.CATEGORY.STATE)
        else:
            self.stop(AIRCRAFT_SFX.TYPE.CRIT, AIRCRAFT_SFX.CATEGORY.STATE)

    def __onBattleEnd(self):
        self.stop(AIRCRAFT_SFX.TYPE.FLAPS, AIRCRAFT_SFX.CATEGORY.MISC, self.__stoppedFlapsCB)

    def __onLaunchShell(self, shellIndex):
        shellType = self.__player.controllers['shellController'].getShellType(shellIndex)
        if shellType == UPDATABLE_TYPE.BOMB:
            self.postEvent(SFX_SHELL_MECHANICS.BOMB)
        elif shellType == UPDATABLE_TYPE.ROCKET:
            self.postEvent(SFX_SHELL_MECHANICS.ROCKET)

    def clear(self):
        self.__clearEvents()
        self.__onLeaveWorld()


g_factory = None

class AircraftSFXFactory(WwiseGameObjectFactory):

    def createPlayer(self, so):
        so.wwiseGameObject = AircraftSFX(so.context.cidProxy.handle, so.node.id, so.soundSet)

    @staticmethod
    def instance():
        global g_factory
        if not g_factory:
            g_factory = AircraftSFXFactory()
        return g_factory

    @staticmethod
    def getSoundObjectSettings(data):
        if not data['isPlayer']:
            return
        info = data['info']
        soundObjects = data['soundObjects']
        context = data['context']
        so = SoundObjectSettings()
        so.mountPoint = 'plane/HP_mass'
        misc = db.DBLogic.g_instance.getAircraftSFX(info.misc)
        states = db.DBLogic.g_instance.getAircraftStates(info.states)
        so.soundSet = misc.copy()
        so.soundSet.update(states)
        so.factory = AircraftSFXFactory.instance()
        so.context = context
        soundObjects[SOUND_OBJECT_TYPES.SFX] = so