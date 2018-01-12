# Embedded file name: scripts/common/db/DBAreaConquest/Hud/ACHudSettings.py
import ResMgr
from consts import AC_GAME_MODE_HUD_PLANE_HINT_PATH
from db.DBHelpers import readValues
from debug_utils import LOG_DEBUG

class ACHudMarkersSettings(object):

    def __init__(self, data):
        self.isShowSectorMarkers = False
        if data:
            params = (('isShowSectorMarkers', False),)
            readValues(self, data, params)


class ACHudSettings(object):

    def __init__(self):
        path = AC_GAME_MODE_HUD_PLANE_HINT_PATH + 'hudSettings.xml'
        sectionRoot = ResMgr.openSection(path)
        for section in sectionRoot.values():
            if section.name == 'markers':
                self._markersSettings = ACHudMarkersSettings(section)

    @property
    def getMarkersSettings(self):
        """ return ACHudMarkersSettings"""
        return self._markersSettings