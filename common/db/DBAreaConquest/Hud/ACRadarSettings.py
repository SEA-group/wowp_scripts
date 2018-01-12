# Embedded file name: scripts/common/db/DBAreaConquest/Hud/ACRadarSettings.py
import ResMgr
from consts import AC_GAME_MODE_HUD_PLANE_HINT_PATH
from db.DBHelpers import readValues
MINIMAP_STATE = 2
MINIMAP_RADAR_STATE = 1
RADAR_STATE = 0
STATE_MAP = {MINIMAP_STATE: 'minimap',
 MINIMAP_RADAR_STATE: 'minimapRadar',
 RADAR_STATE: 'radar'}

class RadarSettings(object):

    def __init__(self, data):
        self.radius = 0
        self.selectTargetDistanceKoef = 0.0
        self.scale = 0.0
        self.visibilityDistanceKoef = 0.0
        if data:
            params = (('radius', 0),
             ('scale', 0.0),
             ('selectTargetDistanceKoef', 0.0),
             ('visibilityDistanceKoef', 0.0))
            readValues(self, data, params)


class ACRadarSettings(object):

    def __init__(self):
        self._miniMapList = []
        self._miniMapRadarList = []
        self._radarList = []
        self._setRadarSettings()

    def _setRadarSettings(self):
        self._sectorObjects = {}
        path = AC_GAME_MODE_HUD_PLANE_HINT_PATH + 'radarSettings.xml'
        sectionRoot = ResMgr.openSection(path)
        for section in sectionRoot.values():
            for item in section.values():
                levelSettings = RadarSettings(item)
                if section.name == STATE_MAP[MINIMAP_STATE]:
                    self._miniMapList.append(levelSettings)
                if section.name == STATE_MAP[MINIMAP_RADAR_STATE]:
                    self._miniMapRadarList.append(levelSettings)
                if section.name == STATE_MAP[RADAR_STATE]:
                    self._radarList.append(levelSettings)

    def getSettingsByLevel(self, state, level):
        source = self._miniMapList
        if state == MINIMAP_RADAR_STATE:
            source = self._miniMapRadarList
        if state == RADAR_STATE:
            source = self._radarList
        return source[level - 1]