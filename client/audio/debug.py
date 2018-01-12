# Embedded file name: scripts/client/audio/debug.py
from config_consts import IS_DEVELOPMENT
from debug_utils import LOG_INFO
from audio.AKConsts import DEBUG_AUDIO_TAG
from DebugManager import SHOW_DEBUG_OBJ
IS_AUDIO_DEBUG = False

def enable():
    global IS_AUDIO_DEBUG
    IS_AUDIO_DEBUG = True and IS_DEVELOPMENT


def disable():
    global IS_AUDIO_DEBUG
    IS_AUDIO_DEBUG = False


from SoundBanksManager import SoundBanksManager
from WWISE_ import postGlobalEvent
from AKTunes import Arena_Banks
import BigWorld

class SoundBanksManagerTester():
    BANK_NAME = 'test'
    EVENT_NAME = 'Play_01___Mu'

    def __init__(self):
        self.__test = []
        self.__currentStep = 0

    def test(self, testNumb):
        testName = 'test{0}'.format(testNumb)
        if hasattr(self, 'test{0}'.format(testNumb)):
            tst = getattr(self, testName)()
            self.__test = tst.getTest()
            if not self.__currentStep:
                print '========== ' + testName + ' =========='
                print tst.getInfo()
            self.step()
        else:
            self.__test = []

    def step(self):
        if self.__test:
            l = len(self.__test)
            if self.__currentStep < l:
                self.__test[self.__currentStep]()
                self.__currentStep += 1
                if self.__currentStep == l:
                    print '=============================='
                    self.__test = []
                    self.__currentStep = 0

    class test1:

        def step1(self):
            print '1: \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba test \xd0\xb8 \xd1\x81\xd1\x80\xd0\xb0\xd0\xb7\xd1\x83 \xd0\xb6\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb8\xd0\xb3\xd1\x80\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb8\xd0\xb2\xd0\xb5\xd0\xbd\xd1\x82 Play_01___Mu'
            SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME)
            postGlobalEvent(SoundBanksManagerTester.EVENT_NAME)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba test'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 + \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0'

    class test2:

        def step1(self):
            print '1: \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba test 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x80\xd1\x8f\xd0\xb4 \xd1\x81 \xd0\xb2\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xbc \xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd1\x87\xd0\xb8\xd0\xba\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba'
            for i in range(3):
                SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME, True)

            postGlobalEvent(SoundBanksManagerTester.EVENT_NAME)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba 1 \xd1\x80\xd0\xb0\xd0\xb7'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def step3(self):
            print '3: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0'
            for i in range(3):
                SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2, self.step3]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd1\x87\xd0\xb8\xd0\xba\xd0\xb0 \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba \xd0\xb4\xd0\xbb\xd1\x8f \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0'

    class test3:

        def step1(self):
            print '1: \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd0\xb8 \xd0\xb0\xd1\x82\xd0\xb0\xd1\x87\xd0\xb8\xd0\xbc \xd0\xba \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd1\x83'
            SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME)
            SoundBanksManager.instance().attachWwiseObjectToCase(SoundBanksManagerTester.BANK_NAME, 13)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81'
            SoundBanksManager.instance().unloadSoundCase(13)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb0\xd1\x82\xd0\xb0\xd1\x87\xd0\xb8\xd0\xbd\xd0\xb3 \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd0\xba \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd1\x83'

    class test4:

        def step1(self):
            print '1: \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd1\x81 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba \xd0\xb8 2 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xb0\xd1\x82\xd0\xb0\xd1\x87\xd0\xb8\xd0\xbc \xd0\xba \xd1\x80\xd0\xb0\xd0\xb7\xd0\xbb\xd0\xb8\xd1\x87\xd0\xbd\xd1\x8b\xd0\xbc \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd0\xb0\xd0\xbc'
            for i in range(3):
                SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME, True)

            SoundBanksManager.instance().attachWwiseObjectToCase(SoundBanksManagerTester.BANK_NAME, 13)
            SoundBanksManager.instance().attachWwiseObjectToCase(SoundBanksManagerTester.BANK_NAME, 14)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb2\xd1\x8b\xd0\xb9 \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81 (\xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xba\xd0\xbe\xd0\xbb-\xd0\xb2\xd0\xbe \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba)'
            SoundBanksManager.instance().unloadSoundCase(13)

        def step3(self):
            print '3: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xbe\xd0\xb9 \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81 \xd0\xb8 \xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb0\xd0\xbd\xd0\xbb\xd0\xbe\xd0\xb0\xd0\xb4 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0'
            SoundBanksManager.instance().unloadSoundCase(14)
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2, self.step3]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9a\xd0\xbe\xd0\xbc\xd0\xb1\xd0\xb8\xd0\xbd\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x81\xd0\xbf\xd0\xbe\xd1\x81\xd0\xbe\xd0\xb1 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8, \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd1\x81 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba.'

    class test5:

        def step1(self):
            print '1: \xd0\xbe\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd1\x83\xd1\x8e \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd0\xb8 \xd1\x82\xd1\x83\xd1\x82 \xd0\xb6\xd0\xb5 \xd1\x88\xd0\xbb\xd0\xb5\xd0\xbc \xd0\xb8\xd0\xb2\xd0\xb5\xd0\xbd\xd1\x82. \xd0\x98\xd0\xb3\xd1\x80\xd0\xb0\xd1\x82\xd1\x8c \xd0\xb8\xd0\xb2\xd0\xb5\xd0\xbd\xd1\x82 \xd0\xbd\xd0\xb5 \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xb5\xd0\xbd'
            SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME)
            postGlobalEvent(SoundBanksManagerTester.EVENT_NAME)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0'

    class test6:

        def step1(self):
            print '1: \xd0\xbe\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xb7\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd0\xb8 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xbf\xd0\xb8\xd1\x81\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xb5\xd0\xbc\xd1\x81\xd1\x8f \xd0\xbd\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba. \xd0\x9f\xd0\xbe \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd1\x83 \xd0\xbf\xd0\xbe\xd1\x81\xd1\x82\xd0\xb8\xd0\xbc \xd0\xb8\xd0\xb2\xd0\xb5\xd0\xbd\xd1\x82'
            print '1.1: \xd0\x94\xd0\xbe\xd0\xb6\xd0\xb4\xd0\xb8\xd1\x81\xd1\x8c \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0, \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb4 \xd1\x82\xd0\xb5\xd0\xbc \xd0\xba\xd0\xb0\xd0\xba \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb9\xd1\x82\xd0\xb8 \xd0\xba \xd1\x81\xd0\xbb\xd0\xb5\xd0\xb4\xd1\x83\xd1\x8e\xd1\x89\xd0\xb5\xd0\xbc\xd1\x83 \xd1\x88\xd0\xb0\xd0\xb3\xd1\x83'

            def cb():
                postGlobalEvent(SoundBanksManagerTester.EVENT_NAME)
                print '1.2: \xd1\x82\xd0\xb0\xd0\xba\xd1\x81. \xd0\x92\xd0\xbe\xd1\x82 \xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xd1\x80\xd1\x8c \xd0\xbc\xd0\xbe\xd0\xb6\xd0\xbd\xd0\xbe \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x8c \xd0\xba \xd1\x88\xd0\xb0\xd0\xb3\xd1\x83 2'

            SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb)

        def step2(self):
            print '2: \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd1\x8f\xd0\xb5\xd0\xbc, \xd1\x87\xd1\x82\xd0\xbe \xd0\xbf\xd1\x80\xd0\xb8\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba, \xd0\xbf\xd0\xbe\xd1\x81\xd0\xbb\xd0\xb5 \xd1\x82\xd0\xbe\xd0\xb3\xd0\xbe, \xd0\xba\xd0\xb0\xd0\xba \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd1\x83\xd0\xb6\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd'

            def cb():
                print '\xd0\xbe\xd0\xbf. \xd0\x92\xd1\x81\xd0\xb5 \xd0\x9e\xd0\x9a. \xd0\x91\xd0\xb0\xd0\xbd\xd0\xba \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd, \xd0\xbd\xd0\xbe \xd0\xb5\xd1\x81\xd0\xbb\xd0\xb8 \xd0\xbf\xd0\xbe\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xb8\xd1\x82\xd1\x8c \xd0\xb5\xd1\x89\xd0\xb5 \xd1\x80\xd0\xb0\xd0\xb7 \xd0\xb5\xd0\xb3\xd0\xbe \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd1\x82\xd1\x8c, \xd1\x82\xd0\xbe \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd1\x82\xd0\xbe \xd0\xbf\xd1\x80\xd0\xb8\xd0\xb4\xd0\xb5\xd1\x82 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba'

            SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb)

        def step3(self):
            print '3: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2, self.step3]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0 \xd0\xbf\xd1\x80\xd0\xb8 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb5 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe'

    class test7:

        def step1(self):
            print '1: \xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xbe\xd0\xb2 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd1\x81 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xbe\xd0\xbc \xd0\xb8 2 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xb1\xd0\xb5\xd0\xb7 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0 \xd1\x81 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba'
            counter = [0]

            def cb():
                print 'callback N' + str(counter[0])
                counter[0] += 1

            for i in range(3):
                SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb, True)

            for i in range(2):
                SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, refsCountingEnable=True)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba (5 \xd1\x80\xd0\xb0\xd0\xb7) ))'
            for i in range(5):
                SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xbd\xd0\xb5\xd1\x81\xd0\xba\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xba\xd0\xbe \xd1\x80\xd0\xb0\xd0\xb7 \xd1\x81 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0\xd0\xbc\xd0\xb8 \xd0\xb8 \xd0\xb1\xd0\xb5\xd0\xb7 + \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82 \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba'

    class test8:

        def step1(self):
            print '1: \xd0\x9e\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb8 \xd1\x82\xd1\x83\xd1\x82 \xd0\xb6\xd0\xb5 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba. \xd0\x9d\xd1\x83\xd0\xb6\xd0\xbd\xd0\xbe \xd1\x83\xd0\xb1\xd0\xb5\xd0\xb4\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f, \xd1\x87\xd1\x82\xd0\xbe \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd0\xbd\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd0\xbb\xd1\x81\xd1\x8f \xd0\xb8 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0 \xd0\xbd\xd0\xb5\xd1\x82'

            def cb():
                print '\xd0\x92\xd0\xbe\xd1\x82 \xd1\x8d\xd1\x82\xd0\xbe \xd0\xbf\xd0\xbb\xd0\xbe\xd1\x85\xd0\xbe. \xd0\x9f\xd1\x80\xd0\xb8\xd1\x88\xd0\xb5\xd0\xbb \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba, \xd0\xb0 \xd0\xbd\xd0\xb5 \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xb5\xd0\xbd \xd0\xb1\xd1\x8b\xd0\xbb \xd0\xb1\xd1\x8b'

            SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb)
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0, \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd1\x8b\xd0\xb9 \xd0\xbd\xd0\xb0\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd0\xb2 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x86\xd0\xb5\xd1\x81\xd1\x81\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8'

    class test9:

        def step1(self):
            print '1: \xd0\xbe\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x80\xd1\x8f\xd0\xb4 \xd1\x81 \xd0\xb2\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xbc \xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd1\x87\xd0\xb8\xd0\xba\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba. \xd0\xa2\xd1\x83\xd1\x82 \xd0\xb6\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xb8\xd0\xbc \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd1\x82\xd1\x8c \xd0\xb5\xd0\xb3\xd0\xbe 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x80\xd1\x8f\xd0\xb4'

            def cb():
                print '\xd0\x92\xd0\xbe\xd1\x82 \xd1\x8d\xd1\x82\xd0\xbe \xd0\xbf\xd0\xbb\xd0\xbe\xd1\x85\xd0\xbe. \xd0\x9f\xd1\x80\xd0\xb8\xd1\x88\xd0\xb5\xd0\xbb \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba, \xd0\xb0 \xd0\xbd\xd0\xb5 \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xb5\xd0\xbd \xd0\xb1\xd1\x8b\xd0\xbb \xd0\xb1\xd1\x8b'

            for i in range(3):
                SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb)

            for i in range(3):
                SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0, \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd1\x8b\xd0\xb9 \xd0\xbd\xd0\xb0\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd0\xb2 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x86\xd0\xb5\xd1\x81\xd1\x81\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd1\x81 \xd0\xb2\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xbc \xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd1\x87\xd0\xb8\xd0\xba\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba \xd0\xb8 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0\xd0\xbc\xd0\xb8'

    class test10:

        def step1(self):
            print '1: \xd0\x97\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba. \xd0\xa2\xd0\xb5\xd1\x81\xd1\x82\xd0\xb0 \xd1\x80\xd0\xb0\xd0\xb4\xd0\xb8 \xd0\xb8\xd1\x81\xd0\xbf\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xb0\xd0\xbb \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd1\x83\xd1\x8e \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83, \xd1\x85\xd0\xbe\xd1\x82\xd1\x8f \xd0\xbe\xd0\xbd\xd0\xb0 \xd0\xb8 \xd0\xbd\xd0\xb5 \xd0\xbe\xd0\xb1\xd1\x8f\xd0\xb7\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xb0\xd1\x8f'
            SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME)

        def step2(self):
            print '2: \xd0\x9e\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 (\xd0\xbe\xd0\xbd\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe \xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd0\xb0\xd0\xb5\xd1\x82) \xd0\xb8 \xd1\x82\xd1\x83\xd1\x82 \xd0\xb6\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x88\xd1\x83 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd1\x82\xd1\x8c \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

            def cb():
                print '\xd0\xbd\xd0\xb5 \xd0\xb2\xd1\x81\xd0\xb5 \xd1\x82\xd0\xb0\xd0\xba \xd0\xbf\xd0\xbb\xd0\xbe\xd1\x85\xd0\xbe. \xd0\x9f\xd1\x80\xd0\xb8\xd1\x88\xd0\xb5\xd0\xbb \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba. \xd0\x9d\xd0\xb0\xd0\xb4\xd0\xbe \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xb8\xd1\x82\xd1\x8c, \xd1\x87\xd1\x82\xd0\xbe \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd \xd0\xb2 \xd0\xb2\xd0\xb0\xd0\xb9\xd1\x81\xd0\xb5 \xd0\xb8 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x81\xd0\xbe\xd0\xbb\xd0\xb8'

            SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb)

        def step3(self):
            print '3: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2, self.step3]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xbd\xd0\xb0\xd0\xba\xd0\xbb\xd0\xb0\xd0\xb4\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb8 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0'

    class test11:

        def step1(self):
            print '1: \xd0\x9e\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xbe\xd0\xb4\xd0\xbd\xd0\xbe\xd0\xb2\xd1\x80\xd0\xb5\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe 3 \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd0\xb0 \xd0\xbd\xd0\xb0 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd1\x83\xd1\x8e \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xbe\xd0\xb4\xd0\xbd\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xb8 \xd1\x82\xd0\xbe\xd0\xb3\xd0\xbe \xd0\xb6\xd0\xb5 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0 \xd1\x81 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0\xd0\xbc\xd0\xb8 \xd0\xb8 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba. \xd0\xa2\xd1\x83\xd1\x82 \xd0\xb6\xd0\xb5 \xd0\xbe\xd1\x82\xd0\xbf\xd1\x80\xd0\xb0\xd0\xb2\xd0\xbb\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xb7\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 1 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd1\x83 \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd0\xb0 c \xd1\x8d\xd1\x82\xd0\xb8\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0'
            counter = [0]

            def cb():
                LOG_INFO(DEBUG_AUDIO_TAG, 'callback N' + str(counter[0]))
                print 'callback N' + str(counter[0])
                counter[0] += 1

            for i in range(2):
                SoundBanksManager.instance().loadBank(SoundBanksManagerTester.BANK_NAME, cb, True)

            SoundBanksManager.instance().loadBankAndAttachToCase(13, SoundBanksManagerTester.BANK_NAME, cb, True)
            SoundBanksManager.instance().unloadSoundCase(13)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xb4\xd0\xbb\xd1\x8f \xd0\xbd\xd0\xb0\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd0\xb8))'
            for i in range(3):
                SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd1\x87\xd0\xb0\xd1\x81\xd1\x82\xd0\xb8\xd1\x87\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb0, \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd1\x8b\xd0\xb9 \xd0\xbd\xd0\xb0\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f \xd0\xb2 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x86\xd0\xb5\xd1\x81\xd1\x81\xd0\xb5 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd1\x81 \xd0\xb2\xd0\xba\xd0\xbb\xd1\x8e\xd1\x87\xd0\xb5\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xbc \xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd1\x87\xd0\xb8\xd0\xba\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba \xd0\xb8 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0\xd0\xbc\xd0\xb8'

    class test12:

        def step1(self):
            print '1: \xd0\x97\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd1\x81 \xd0\xbf\xd0\xbe\xd0\xb4\xd1\x81\xd1\x87\xd0\xb5\xd1\x82\xd0\xbe\xd0\xbc \xd1\x81\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba 3 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0. (\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xbb \xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe 1 \xd1\x80\xd0\xb0\xd0\xb7 \xd0\xb8 2 \xd0\xb0\xd1\x81\xd0\xb8\xd0\xbd\xd1\x85\xd1\x80\xd0\xbe\xd0\xbd\xd0\xbd\xd0\xbe). 2 \xd0\xb0\xd1\x82\xd0\xb0\xd1\x87\xd0\xb8\xd0\xbc \xd0\xba \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd0\xb0\xd0\xbc.'
            counter = [0]

            def cb():
                print 'callback N' + str(counter[0])
                counter[0] += 1

            SoundBanksManager.instance().loadBankAndAttachToCase(13, SoundBanksManagerTester.BANK_NAME, cb, True)
            SoundBanksManager.instance().loadBankAndAttachToCase(14, SoundBanksManagerTester.BANK_NAME, cb, True)
            SoundBanksManager.instance().loadBankSync(SoundBanksManagerTester.BANK_NAME, True)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc 1 \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81. \xd0\xa1\xd1\x81\xd1\x8b\xd0\xbb\xd0\xbe\xd0\xba \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xbd\xd0\xbe \xd1\x81\xd1\x82\xd0\xb0\xd1\x82\xd1\x8c 2'
            SoundBanksManager.instance().unloadSoundCase(13)

        def step3(self):
            print '3: \xd0\xb4\xd0\xb5\xd0\xbb\xd0\xb0\xd0\xb5\xd0\xbc 2 \xd1\x80\xd0\xb0\xd0\xb7\xd0\xb0 \xd0\xb0\xd0\xbd\xd0\xbb\xd0\xbe\xd0\xb0\xd0\xb4. \xd0\x91\xd0\xb0\xd0\xbd\xd0\xba \xd0\xb4\xd0\xbe\xd0\xbb\xd0\xb6\xd0\xb5\xd0\xbd \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd1\x82\xd1\x81\xd1\x8f'
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)
            SoundBanksManager.instance().unloadBank(SoundBanksManagerTester.BANK_NAME)

        def step4(self):
            print '4: \xd0\xb0 \xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xd1\x80\xd1\x8c \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb1\xd1\x83\xd0\xb5\xd0\xbc \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xb8\xd1\x82\xd1\x8c \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81, \xd0\xba\xd0\xbe\xd1\x82\xd0\xbe\xd1\x80\xd1\x8b\xd0\xb9 \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd1\x81\xd1\x8f \xd0\xb8 \xd1\x81\xd0\xbc\xd0\xbe\xd1\x82\xd1\x80\xd0\xb8\xd0\xbc \xd0\xb1\xd1\x83\xd0\xb4\xd1\x83\xd1\x82 \xd0\xbb\xd0\xb8 \xd0\xba\xd0\xb0\xd0\xba\xd0\xb8\xd0\xb5-\xd1\x82\xd0\xbe \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb1\xd0\xbb\xd0\xb5\xd0\xbc\xd1\x8b \xd1\x81 \xd1\x8d\xd1\x82\xd0\xb8\xd0\xbc'
            SoundBanksManager.instance().unloadSoundCase(14)

        def getTest(self):
            return [self.step1,
             self.step2,
             self.step3,
             self.step4]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x84\xd0\xbb\xd0\xb8\xd0\xba\xd1\x82\xd0\xbe\xd0\xb2 \xd0\xb0\xd0\xbd\xd0\xbb\xd0\xbe\xd0\xb0\xd0\xb4\xd0\xb0 \xd0\xb8 \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xba\xd0\xb5\xd0\xb9\xd1\x81\xd0\xb0'

    class test13:

        def step1(self):
            print '1: \xd0\x97\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba, \xd0\xb0 \xd0\xbf\xd0\xbe \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd1\x83 \xd0\xbd\xd0\xbe\xd0\xb2\xd1\x8b\xd0\xb9. \xd0\x98 \xd1\x82\xd0\xb0\xd0\xba \xd0\xb4\xd0\xbb\xd1\x8f \xd0\xb2\xd1\x81\xd0\xb5\xd1\x85 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xbe\xd0\xb2 \xd0\xb0\xd1\x80\xd0\xb5\xd0\xbd\xd1\x8b'

            def load(inx):
                if inx < len(Arena_Banks):
                    SoundBanksManager.instance().loadBank(Arena_Banks[inx])
                    load(inx + 1)

            load(0)

        def step2(self):
            print '2: \xd0\xb2\xd1\x8b\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb8'
            for bank in Arena_Banks:
                SoundBanksManager.instance().unloadBank(bank)

        def getTest(self):
            return [self.step1, self.step2]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x9f\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd1\x8f\xd0\xb5\xd0\xbc \xd0\xbd\xd0\xb0 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x87\xd0\xbd\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c \xd0\xbc\xd1\x8e\xd1\x82\xd0\xb5\xd0\xba\xd1\x81\xd1\x8b \xd0\xbf\xd1\x80\xd0\xb8 \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb5 \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xbe\xd0\xb2 \xd0\xb8\xd0\xb7 \xd0\xbf\xd0\xbe\xd0\xb4 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xb0'

    class test14:

        def __init__(self):
            self.__iteration = 0
            self.__maxIterations = 1000
            self.__cb = None
            return

        def __load(self):
            banksLeftToLoad = [len(Arena_Banks)]

            def allBanksLoaded():
                SoundBanksManager.instance().loadBank('eng_curtiss')
                self.__cb = BigWorld.callback(0.1, self.__unload)

            def cb():
                banksLeftToLoad[0] -= 1
                if not banksLeftToLoad[0]:
                    allBanksLoaded()

            for bank in Arena_Banks:
                SoundBanksManager.instance().loadBank(bank, cb)

        def __unload(self):
            for bank in Arena_Banks:
                SoundBanksManager.instance().unloadBank(bank)

            SoundBanksManager.instance().unloadBank('eng_curtiss')
            self.__iteration += 1
            if self.__iteration < self.__maxIterations:
                self.__load()
            elif self.__cb:
                BigWorld.cancelCallback(self.__cb)
                self.__cb = None
            return

        def step1(self):
            print '1: \xd0\x97\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb0\xd0\xb5\xd0\xbc \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba\xd0\xb8 \xd0\xb0\xd1\x80\xd0\xb5\xd0\xbd\xd1\x8b, \xd0\xbf\xd0\xbe \xd0\xb7\xd0\xb0\xd0\xb2\xd0\xb5\xd1\x80\xd1\x88\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8e \xd0\xb2\xd1\x81\xd0\xb5\xd1\x85 \xd0\xba\xd0\xbe\xd0\xbb\xd0\xb1\xd0\xb5\xd0\xba\xd0\xbe\xd0\xb2 - \xd0\xb1\xd0\xb0\xd0\xbd\xd0\xba \xd1\x8d\xd0\xbd\xd0\xb6\xd0\xb8\xd0\xbd\xd0\xb0'
            self.__load()

        def getTest(self):
            return [self.step1]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: \xd0\x98\xd0\xbc\xd0\xb8\xd1\x82\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb8 \xd0\xb0\xd1\x80\xd0\xb5\xd0\xbd\xd1\x8b. '

    class test0:

        def step1(self):
            print '1: '

        def step2(self):
            print '2: '

        def step3(self):
            print '3: '

        def step4(self):
            print '4: '

        def getTest(self):
            return [self.step1,
             self.step2,
             self.step3,
             self.step4]

        def getInfo(self):
            return '\xd0\x9e\xd0\xbf\xd0\xb8\xd1\x81\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5: '


def test():
    return SoundBanksManagerTester()