# Embedded file name: scripts/common/db/DBSoundSettings.py
from db.DBHelpers import *
from consts import WORLD_SCALING, SPEED_SCALING, DB_PATH, GAME_MODE
from math import radians

class Interval:

    def __init__(self, root):
        self.min = root.readInt('min')
        self.max = root.readInt('max')


class EventSet:

    def __init__(self, root):
        self.__entries = dict()
        fillDictionaryByValues(self.entries, root)

    @property
    def entries(self):
        return self.__entries


class AircraftEventSet:

    def __init__(self, root):
        self.entries = dict()
        fillDictionaryByValues(self.entries, root)
        for k in self.entries.keys():
            self.entries[k] = dict()
            fillDictionaryByValues(self.entries[k], findSection(root, k, False))


class AircraftSounds:

    def __init__(self, root):
        self.aircrafts = Aircrafts(root)
        self.engineSet = AircraftEventSet(findSection(root, 'EngineSet'))
        self.misc = AircraftEventSet(findSection(root, 'Misc'))
        self.air = AircraftEventSet(findSection(root, 'Air'))
        self.states = AircraftEventSet(findSection(root, 'States'))


class WeaponProfiles:

    def __init__(self, root):
        self.__profiles = {}
        for wpn in root.items():
            fd = {}
            fillDictionaryByValues(fd, wpn[1])
            if 'WeaponSoundID' not in fd:
                continue
            wpnSndId = fd.pop('WeaponSoundID')
            self.__profiles[wpnSndId] = fd

    @property
    def profiles(self):
        return self.__profiles


class EffectProfiles:

    def __init__(self, root):
        self.__effects = {}
        for eff in root.items():
            fd = {}
            fillDictionaryByValues(fd, eff[1])
            if 'SoundEffectID' not in fd or 'Event' not in fd:
                continue
            snd = fd.pop('SoundEffectID')
            self.__effects[snd] = fd['Event']

    @property
    def sounds(self):
        return self.__effects


class Aircrafts:

    def __init__(self, root):
        self.entries = {}
        for i in root.items():
            if i[0] != 'Aircraft':
                continue
            name = str(i[1].readString('Name')).lower()
            self.entries[name] = AircraftSound(i[1])


class AircraftSound:

    def __init__(self, root):
        self.engineSet = root.readString('EngineSet')
        self.mointPoint = root.readString('EngineMountPosition')
        self.air = root.readString('Air')
        self.misc = root.readString('Misc')
        self.states = root.readString('States')
        self.weapons = []
        wpnMntPts = findSection(root, 'WeaponMountPoints')
        if wpnMntPts is None:
            return
        else:
            for i in wpnMntPts.values():
                slot = i.readInt('Slot')
                HPs = []
                for j in i.items():
                    if str(j[0]).lower() == 'slot':
                        continue
                    if str(j[0]).lower() == 'mountpoint':
                        HPs.append(j[1].readString(''))

                self.weapons.insert(slot, HPs)

            return


class MusicSound:

    def __init__(self, root):
        self.__events = {}
        for i in root.items():
            fd = {}
            fillDictionaryByValues(fd, i[1])
            id = fd.pop('musicPrefix')
            self.__events[id] = fd

    @property
    def events(self):
        return self.__events


class VoiceoverSetsHolder:

    def __init__(self, root):
        self.__voiceoverSets = {}
        for item in root.items():
            gameMode = item[0]
            gameModeVoiceoversXMLPath = DB_PATH + item[1].readString('')
            voiceoverSet = Voiceovers(ResMgr.openSection(gameModeVoiceoversXMLPath))
            gameModeIndex = GAME_MODE.NAME_TO_MODE[gameMode] - GAME_MODE.AREA_CONQUEST
            self.__voiceoverSets[gameModeIndex] = voiceoverSet

    @property
    def voiceoverSets(self):
        return self.__voiceoverSets


class Voiceovers:

    def __init__(self, root):
        self.__voiceovers = {}
        for item in root.items():
            vo = {}
            event = item[0]
            fillDictionaryByValues(vo, item[1])
            if event:
                self.__voiceovers[event] = vo

    @property
    def voiceovers(self):
        return self.__voiceovers


class Hangar:
    PREFIX = 'Hangar_'

    def __init__(self, root):
        self.__musicLoopInterval = Interval(findSection(root, 'MusicLoopInterval'))
        self.__hangarSpaces = self.__getHangarSpaces(findSection(root, 'Spaces'))

    def __getHangarSpaces(self, root):
        hangarSpaces = {}
        for item in root.items():
            vo = {}
            hangarSpaceName = item[0]
            fillDictionaryByValues(vo, item[1])
            if hangarSpaceName:
                hangarSpaces[hangarSpaceName.replace(Hangar.PREFIX, '', 1)] = vo

        return hangarSpaces

    @property
    def hangarSet(self):
        return self.__hangarSpaces

    @property
    def musicLoopInterval(self):
        return self.__musicLoopInterval


class Airshow:

    def __init__(self, root):
        self.externalSphereRadius = root.readInt('ExternalSphereRadius') * WORLD_SCALING
        self.internalShpereRadius = root.readFloat('InternalShpereRadius') * WORLD_SCALING
        self.externalSphereRange = root.readFloat('ExternalSphereRange')
        self.minSpeed = root.readInt('MinSpeed') * WORLD_SCALING * WORLD_SCALING
        self.cooldownTime = root.readFloat('CooldownTime')
        self.timeIntervals = {}
        for timeInterval in findSection(root, 'TimeIntervals').items():
            temp = {}
            fillDictionaryByValues(temp, timeInterval[1])
            self.timeIntervals[float(temp['Time'])] = temp['Switch']

    @property
    def externalSphereRadius(self):
        return self.externalSphereRadius

    @property
    def internalShpereRadius(self):
        return self.internalShpereRadius

    @property
    def externalSphereRange(self):
        return self.externalSphereRange

    @property
    def minSpeed(self):
        return self.minSpeed

    @property
    def cooldownTime(self):
        return self.cooldownTime

    @property
    def timeIntervals(self):
        return self.timeIntervals


class Wind:

    def __init__(self, root):
        self.altitudeTop = root.readInt('AltitudeTop')
        self.altitudeBottom = root.readInt('AltitudeBottom')
        self.maneuversAngleTop = root.readInt('ManeuversAngleTop')
        self.maneuversAngleBottom = root.readInt('ManeuversAngleBottom')
        self.cameraSpeedTop = root.readInt('CameraSpeedTop')
        self.cameraSpeedBottom = root.readInt('CameraSpeedBottom')
        self.onDestroyFadeTime = root.readInt('OnDestroyFadeTime')

    @property
    def altitudeTop(self):
        return self.altitudeTop

    @property
    def altitudeBottom(self):
        return self.altitudeBottom

    @property
    def maneuversAngleTop(self):
        return self.maneuversAngleTop

    @property
    def maneuversAngleBottom(self):
        return self.maneuversAngleBottom

    @property
    def cameraSpeedTop(self):
        return self.cameraSpeedTop

    @property
    def cameraSpeedBottom(self):
        return self.cameraSpeedBottom

    @property
    def onDestroyFadeTime(self):
        return self.onDestroyFadeTime


class InteractiveMix:

    def __init__(self, root):
        self.gamePhases = self.fillDictionaryFull(findSection(root, 'GamePhases'))

    def __fillDictionaryFull(self, root):
        items = root.items()
        tempDict = {}
        finBit = False
        if items:
            for item in [ i[1] for i in items ]:
                childDict, isFin = self.__fillDictionaryFull(item)
                if isFin:
                    tempDict[item.name] = childDict[item.name]
                else:
                    tempDict[item.name] = childDict

        else:
            tempDict[root.name] = root.asString
            finBit = True
        return (tempDict, finBit)

    def fillDictionaryFull(self, root):
        return self.__fillDictionaryFull(root)[0]

    @property
    def gamePhases(self):
        return self.gamePhases


class SoundSettings:

    def __init__(self, data):
        self.__aircraftSounds = AircraftSounds(findSection(data, 'AircraftSounds'))
        self.weapons = WeaponProfiles(findSection(data, 'Weapons'))
        self.hangar = Hangar(findSection(data, 'Hangar'))
        self.effects = EffectProfiles(findSection(data, 'Effects'))
        self.musicSound = MusicSound(findSection(data, 'Ambient'))
        self.wooshSphere = EventSet(findSection(data, 'WooshSphere'))
        self.voiceoverSetsHolder = VoiceoverSetsHolder(findSection(data, 'Voiceovers'))
        self.ui = EventSet(findSection(data, 'UI'))
        self.airshow = Airshow(findSection(data, 'Airshow'))
        self.wind = Wind(findSection(data, 'Wind'))
        self.interactiveMix = InteractiveMix(findSection(data, 'InteractiveMix'))

    def aircraftSound(self, name):
        k = str(name).lower()
        if k not in self.__aircraftSounds.aircrafts.entries:
            return None
        else:
            return self.__aircraftSounds.aircrafts.entries[k]

    @property
    def engineSet(self):
        return self.__aircraftSounds.engineSet

    @property
    def aircraftSFX(self):
        return self.__aircraftSounds.misc

    @property
    def aircraftStates(self):
        return self.__aircraftSounds.states

    @property
    def aircraftAir(self):
        return self.__aircraftSounds.air

    @property
    def musicSound(self):
        return self.musicSound

    @property
    def weapons(self):
        return self.ambient

    @property
    def woosh(self):
        return self.wooshSphere

    @property
    def voiceoverSetsHolder(self):
        return self.voiceoverSetsHolder

    @property
    def ui(self):
        return self.ui

    @property
    def airshow(self):
        return self.airshow

    @property
    def wind(self):
        return self.wind