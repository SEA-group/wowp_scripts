# Embedded file name: scripts/common/db/DBAreaConquest/GameModeSettingsPresets.py
import ResMgr
import BWLogging
from consts import AC_GAME_MODE_PRESETS_PATH
from GMSettings.ArenaGameModeSettingsModel import ArenaGameModeSettingsModel
logger = BWLogging.getLogger('GameModePresets')
_LOADED_PRESETS = {}

def getPresetByName(name):
    global _LOADED_PRESETS
    return _LOADED_PRESETS.get(name)


def init():
    logger.info('Loading started')
    listPath = AC_GAME_MODE_PRESETS_PATH + 'list.xml'
    sectionRoot = ResMgr.openSection(listPath)
    presetsNames = sectionRoot.readStrings('name')
    for name in presetsNames:
        logger.info("Loading preset '{0}'".format(name))
        presetPath = AC_GAME_MODE_PRESETS_PATH + name + '.xml'
        sectionPreset = ResMgr.openSection(presetPath)
        _LOADED_PRESETS[name] = ArenaGameModeSettingsModel()
        _LOADED_PRESETS[name].read(sectionPreset)
        ResMgr.purge(presetPath)

    ResMgr.purge(listPath)
    logger.info('Loading finished, loaded presets count: {0}'.format(len(_LOADED_PRESETS)))