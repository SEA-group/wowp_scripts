# Embedded file name: scripts/common/db/DBAreaConquest/SectorPresets.py
import ResMgr
import debug_utils
from consts import AC_SECTOR_PRESETS_PATH
from SectorPresetModel import SectorPresetModel
_LOADED_PRESETS = {}

def getPresetByName(name):
    global _LOADED_PRESETS
    return _LOADED_PRESETS.get(name)


def init():
    debug_utils.LOG_INFO('SectorPresets: loading started')
    listPath = AC_SECTOR_PRESETS_PATH + 'list.xml'
    sectionRoot = ResMgr.openSection(listPath)
    presetsNames = sectionRoot.readStrings('name')
    for name in presetsNames:
        debug_utils.LOG_INFO("SectorPresets: loading preset '{0}'".format(name))
        presetPath = AC_SECTOR_PRESETS_PATH + name + '.xml'
        sectionPreset = ResMgr.openSection(presetPath)
        _LOADED_PRESETS[name] = SectorPresetModel()
        _LOADED_PRESETS[name].read(sectionPreset)
        ResMgr.purge(presetPath)

    ResMgr.purge(listPath)
    debug_utils.LOG_INFO('SectorPresets: loading finished, loaded presets count: {0}'.format(len(_LOADED_PRESETS)))