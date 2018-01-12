# Embedded file name: scripts/common/db/DBAreaConquest/Hud/ACHudSector.py
from db.DBHelpers import readValues, LOG_DEBUG, findSection

class ACHudSectorData(object):

    def __init__(self, data):
        self.id = ''
        self.posX = 0
        self.posY = 0
        self.lineHeight = 0
        if data:
            params = (('id', ''),
             ('posX', 0),
             ('posY', 0),
             ('lineHeight', 0))
            readValues(self, data, params)


class ACHudMapInfo(object):

    def __init__(self, data):
        self.posX = 0
        self.posY = 0
        self.mapWidth = 0
        self.mapHeight = 0
        if data:
            params = (('posX', 0),
             ('posY', 0),
             ('mapWidth', 0),
             ('mapHeight', 0))
            readValues(self, data, params)


class ACHudSector(object):

    def __init__(self, data):
        TAG = ' TEST SECTION '
        section = findSection(data, 'hudMapSettings')
        self._sectors = []
        self._mapInfo = None
        self._arenaMiniMapPath = ' no path '
        self._radarPath = ' no path '
        if section:
            self._mapPath = section['mapPath'].asString
            self._mapPathF1 = section['mapPathF1'].asString if section.has_key('mapPathF1') else '@need path'
            self._arenaMiniMapPath = section['miniMapBack'].asString if section.has_key('miniMapBack') else ''
            self._radarPath = section['radarBack'].asString if section.has_key('radarBack') else ''
            self._radarOutlandPath = section['radarOutland'].asString if section.has_key('radarOutland') else ''
            self._mapInfo = ACHudMapInfo(section['outlandInfo']) if section.has_key('outlandInfo') else None
            sectorList = section['sectorsList']
            for sectorId, sData in sectorList.items():
                sectorData = ACHudSectorData(sData)
                self._sectors.append(sectorData)

        LOG_DEBUG(' mapData ::: ', self._mapInfo)
        return

    @property
    def mapPath(self):
        """ path for map
        @rtype: str
        """
        return self._mapPath

    @property
    def arenaMiniMapPath(self):
        """ path for miniMap
        @rtype: str
        """
        return self._arenaMiniMapPath

    @property
    def radarPath(self):
        """ path for radar
        @rtype: str
        """
        return self._radarPath

    @property
    def radarOutlandPath(self):
        """ path for radar outland
        @rtype: str
        """
        return self._radarOutlandPath

    @property
    def mapPathF1(self):
        """ path for map in F1
        @rtype: str
        """
        return self._mapPathF1

    @property
    def sectors(self):
        """ sectors
        @rtype: list[ACHudSectorData]
        """
        return self._sectors

    @property
    def mapInfo(self):
        """ background info
        @rtype: ACHudMapInfo
        """
        return self._mapInfo