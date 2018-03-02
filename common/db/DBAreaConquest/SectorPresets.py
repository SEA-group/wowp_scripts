# Embedded file name: scripts/common/db/DBAreaConquest/SectorPresets.py
import ResMgr
import debug_utils
from consts import AC_SECTOR_PRESETS_PATH, GAME_MODE, GAME_MODE_PATH_NAMES
from SectorPresetModel import SectorPresetModel
_LOADED_PRESETS = {}

def makeKey(name, gameModeDir):
    return name + ':' + gameModeDir


def getPresetByName(name, gameModeDir):
    global _LOADED_PRESETS
    key = makeKey(name, gameModeDir)
    return _LOADED_PRESETS.get(key)


def init():
    debug_utils.LOG_INFO('SectorPresets: loading started')
    gameModesFile = AC_SECTOR_PRESETS_PATH + 'submodes.xml'
    gameModesSection = ResMgr.openSection(gameModesFile)
    gameModeNames = gameModesSection.readStrings('name')
    for gm_dir in gameModeNames:
        gameModePath = AC_SECTOR_PRESETS_PATH + gm_dir + '/'
        presetsListFile = gameModePath + 'list.xml'
        debug_utils.LOG_INFO("SectorPresets: read presets list from '{0}'".format(presetsListFile))
        sectionRoot = ResMgr.openSection(presetsListFile)
        presetsNames = sectionRoot.readStrings('name')
        for name in presetsNames:
            debug_utils.LOG_INFO("SectorPresets: loading preset '{0}'".format(name))
            presetFile = gameModePath + name + '.xml'
            sectionPreset = ResMgr.openSection(presetFile)
            key = makeKey(name, gm_dir)
            _LOADED_PRESETS[key] = SectorPresetModel(gm_dir)
            _LOADED_PRESETS[key].read(sectionPreset)
            ResMgr.purge(presetFile)

        ResMgr.purge(presetsListFile)

    ResMgr.purge(gameModesFile)
    debug_utils.LOG_INFO('SectorPresets: loading finished, loaded presets count: {0}'.format(len(_LOADED_PRESETS)))