# Embedded file name: scripts/client/audio/SoundBanksManager.py
import WWISE_
g_soundBanksManager = None

class SoundBanksManager:
    PREPARATION_LOAD = True
    PREPARATION_UNLOAD = False
    REFS_COUNTING_ENABLE = True

    def __init__(self):
        pass

    @staticmethod
    def instance():
        global g_soundBanksManager
        if not g_soundBanksManager:
            g_soundBanksManager = SoundBanksManager()
        return g_soundBanksManager

    def loadInitBank(self, bankName):
        """
        Load wwise init bank, which contains metadata (events and structures info without media content)
        Similar to loadBank function, but additionaly sets "init" flag for prepareEvent usage
        
        @type bankName: str
        @param bankName: name of loading bank
        """
        WWISE_.loadInitBank(bankName)

    def loadBank(self, bankName, callback = None, refsCountingEnable = False, caseID = 0):
        """
        Load bank directly by name (async)
        
        @type bankName: str
        @param bankName: wwise bank name
        @type callback: func ref
        @param callback: python callback function
        @type refsCountingEnable: bool
        @param refsCountingEnable: enable refernces counting mechanism. If true - number of loads must be equal to unload.
        @type caseID: int
        @param caseID: using only for specific case when it's necessery to unload bank by soundCaseID with enabled refsCountingEnable flag;
               caseID: attachWwiseObjectToCase must be called manualy again
        """
        WWISE_.loadBank(bankName, callback, refsCountingEnable, caseID)

    def loadBankSync(self, bankName, refsCountingEnable = False):
        """
        Load bank directly by name (sync)
        
        @type bankName: str
        @param bankName: wwise bank name
        @type refsCountingEnable: bool
        @param refsCountingEnable: enable refernces counting mechanism. If true - number of loads must be equal to unload.
        """
        WWISE_.loadBankSync(bankName, refsCountingEnable)

    def isBankLoaded(self, bankName):
        """
        Check if bank already loaded
        
        @type bankName: str
        @param bankName: wwise bank name
        @return bool
        """
        return WWISE_.isBankLoaded(bankName)

    def unloadBank(self, bankName):
        """
        Unload wwise sound bank directly by name
        @type bankName: str
        @param bankName: name of unloading bank
        """
        WWISE_.unloadBank(bankName)

    def prepareEvent(self, eventName, preparationType):
        """
        Prepare event content by event name
        
        @type eventName: str
        @param eventName: preparing event name
        @type preparationType: bool
        @param eventName: PREPARATION_LOAD or PREPARATION_UNLOAD
        """
        WWISE_.prepareEvent(eventName, preparationType)

    def attachWwiseObjectToCase(self, wwiseObjectName, soundCaseID):
        """
        Attaches wwise object (bank, event, game sync) for specific case (hangar, arena)
        
        @type wwiseObjectName: str
        @param wwiseObjectName: name of wwise bank or event
        @type soundCaseID: int
        @param soundCaseID: user defined category of specified object
        """
        WWISE_.attachWwiseObjectToCase(wwiseObjectName, soundCaseID)

    def loadBankAndAttachToCase(self, soundCaseID, bankName, callback = None, refsCountingEnable = False):
        """
        Async bank loading with attaching to specific soundCase
        
        @type soundCaseID: int
        @param soundCaseID: soundCaseID
        @type bankName: str
        @param bankName: name of loading bank
        @type callback: cb function
        @param callback: function with will be called after bank fully loading
        @type refsCountingEnable: bool
        @param refsCountingEnable: if True - reference counting mechanism for current bank will be enabled
        """

        def cb():
            self.attachWwiseObjectToCase(bankName, soundCaseID)
            if callback:
                callback()

        self.loadBank(bankName, cb, refsCountingEnable, soundCaseID)

    def unloadSoundCase(self, soundCaseID):
        """
        Anload all wwise resources for selected sound case
        
        @type soundCaseID: int
        @param soundCaseID: user defined category which must be unloaded
        """
        WWISE_.unloadSoundCase(soundCaseID)

    def loadFilePackage(self, packageName):
        """
        Load initialization table of specific package
        
        @type packageName: string
        @param packageName: wwise package name
        """
        WWISE_.loadFilePackage(packageName)

    def unloadFilePackage(self, packageName):
        """
        Unload initialization table of specific package
        
        @type packageName: string
        @param packageName: wwise package name
        """
        WWISE_.unloadFilePackage(packageName)

    def unloadAllFilePackages(self):
        """
        Unload initialization tables of all previously loaded packages
        """
        WWISE_.unloadAllFilePackages()