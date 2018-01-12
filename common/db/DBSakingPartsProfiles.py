# Embedded file name: scripts/common/db/DBSakingPartsProfiles.py
import ResMgr
from Curve import Curve
from db.DBHelpers import readValue
from debug_utils import CRITICAL_ERROR, DBLOG_ERROR
import consts
import BigWorld

class ShakeState(object):

    def __init__(self, data):
        self.triggers = []
        if data.has_key('triggers'):
            self.triggers = tuple(data.readString('triggers').split(','))
        if data.has_key('slowTremblingAmplitude') and data.has_key('fastTremblingAmplitude'):
            self.static = True
            self.slowTremblingAmplitude = data.readFloat('slowTremblingAmplitude')
            self.slowTremblingPeriod = data.readFloat('slowTremblingPeriod')
            self.fastTremblingAmplitude = data.readFloat('fastTremblingAmplitude')
            self.fastTremblingPeriod = data.readFloat('fastTremblingPeriod')
        else:
            self.static = False
            self.slowTremblingAmplitudeLow = data.readFloat('slowTremblingAmplitudeLow')
            self.slowTremblingPeriodLow = data.readFloat('slowTremblingPeriodLow')
            self.fastTremblingAmplitudeLow = data.readFloat('fastTremblingAmplitudeLow')
            self.fastTremblingPeriodLow = data.readFloat('fastTremblingPeriodLow')
            self.slowTremblingAmplitudeHigh = data.readFloat('slowTremblingAmplitudeHigh')
            self.slowTremblingPeriodHigh = data.readFloat('slowTremblingPeriodHigh')
            self.fastTremblingAmplitudeHigh = data.readFloat('fastTremblingAmplitudeHigh')
            self.fastTremblingPeriodHigh = data.readFloat('fastTremblingPeriodHigh')
            self.amplitudeInterFunc = data.readString('amplitudeInterFunc')
            self.periodInterFunc = data.readString('periodInterFunc')

    def getSlowAmplitude(self, normSpeed):
        if self.static:
            return self.slowTremblingAmplitude
        else:
            amplitudeInterFunc = getattr(BigWorld, self.amplitudeInterFunc, None)
            return amplitudeInterFunc(self.slowTremblingAmplitudeLow, self.slowTremblingAmplitudeHigh, normSpeed, 1)
            return

    def getSlowPeriod(self, normSpeed):
        if self.static:
            return self.slowTremblingPeriod
        else:
            periodInterFunc = getattr(BigWorld, self.periodInterFunc, None)
            return periodInterFunc(self.slowTremblingPeriodLow, self.slowTremblingPeriodHigh, normSpeed, 1)
            return

    def getFastAmplitude(self, normSpeed):
        if self.static:
            return self.fastTremblingAmplitude
        else:
            amplitudeInterFunc = getattr(BigWorld, self.amplitudeInterFunc, None)
            return amplitudeInterFunc(self.fastTremblingAmplitudeLow, self.fastTremblingAmplitudeHigh, normSpeed, 1)
            return

    def getFastPeriod(self, normSpeed):
        if self.static:
            return self.fastTremblingPeriod
        else:
            periodInterFunc = getattr(BigWorld, self.periodInterFunc, None)
            return periodInterFunc(self.fastTremblingPeriodLow, self.fastTremblingPeriodHigh, normSpeed, 1)
            return


class ShakeSettings(object):

    def __init__(self, rawData):
        """
        @type rawData: ResMgr.DataSection
        """
        self.shakable = rawData.readBool('shakable', False)
        self.delay = rawData.readFloat('delay', 0.0)
        self.defaultState = None
        self.fadeTime = rawData.readFloat('fadeTime', 0.0)
        self.states = []
        if rawData.has_key('defaultState'):
            self.defaultState = ShakeState(rawData['defaultState'])
        self.fadeInterpFuncName = rawData.readString('fadeInterpolationFunc', '')
        if rawData.has_key('states'):
            self.states = map(ShakeState, rawData['states'].values())
        return

    class DoesNotExist(Exception):

        def __init__(self, profileId, stageId):
            self.message = "Shaking profile '{}' has no setting for '{}' controller.".format(profileId, stageId)

    class InterpolationFuncDoesNotExist(Exception):

        def __init__(self, interFuncName):
            self.message = "There is no '{}' func in BigWorld please read surrogates/_easingInterpolation.py file".format(interFuncName)

    @property
    def fadeInterpolationFunc(self):
        return getattr(BigWorld, self.fadeInterpFuncName, lambda *x: 0.0)


class Profile(object):

    def __init__(self, rawData):
        """
        @type rawData: ResMgr.DataSection
        """
        self.id = rawData['id'].asString
        self.parts = {}
        for controllerName, rawShakeData in rawData['parts'].items():
            self.parts[controllerName] = ShakeSettings(rawShakeData)

    def getPartData(self, controllerName):
        try:
            return self.parts[controllerName]
        except KeyError:
            raise ShakeSettings.DoesNotExist(self.id, controllerName)

    class DoesNotExist(Exception):

        def __init__(self, profileId):
            self.message = 'Destruction profile [{}] does not exist.'.format(profileId)


class DBShakingPartsProfiles(object):

    def __init__(self):
        self._profiles = {}
        destructionProfilesRaw = ResMgr.openSection(consts.SHAKING_PROFILES_PATH)
        if destructionProfilesRaw:
            rawProfiles = destructionProfilesRaw['profiles']
            for rawProfile in rawProfiles.values():
                profileId = rawProfile['id'].asString
                self._profiles[profileId] = Profile(rawProfile)

            ResMgr.purge(consts.SHAKING_PROFILES_PATH)
        else:
            CRITICAL_ERROR("Can't load or corrupted data file.", consts.SHAKING_PROFILES_PATH)

    def getProfileById(self, requestedId):
        """
        @type requestedId: str
        @rtype: Profile
        """
        try:
            return self._profiles[requestedId]
        except KeyError:
            raise Profile.DoesNotExist(requestedId)