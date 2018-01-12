# Embedded file name: scripts/client/Helpers/iconPathHelper.py
ICON_24 = 'modules_24x24'
ICON_48 = 'modules_48x48'
ICON_MODULES_PATH = 'icons/modules/%s/%s'
ICON_MODULE_DEFAULT_PATH = 'icons/modules/iconTemp.png'
EMPTY_WEAPON_SLOT_ICON_PATH = 'emptySlot.dds'

def get24ModuleIconPath(fileName):
    if '/' in fileName:
        return fileName
    return ICON_MODULES_PATH % (ICON_24, fileName)


def get48ModuleIconPath(fileName):
    if '/' in fileName:
        return fileName
    return ICON_MODULES_PATH % (ICON_48, fileName)