# Embedded file name: scripts/common/db/DBAreaConquest/Hud/ACHudHint.py
import ResMgr
from consts import AC_GAME_MODE_HUD_PLANE_HINT_PATH
from db.DBHelpers import readValues, LOG_DEBUG

class ACHudPlaneHint(object):

    def __init__(self, data):
        self.planeClass = ''
        self.hintLocalizationID = ''
        if data:
            params = (('planeClass', ''), ('hintLocalizationID', ''))
            readValues(self, data, params)


class ACHudSectorItem(object):

    def __init__(self, data):
        self.id = 0
        self.nameLocalID = ''
        self.iconPath = ''
        self.typeLocalID = ''
        if data:
            params = (('id', -1),
             ('nameLocalID', ''),
             ('iconPath', ''),
             ('typeLocalID', ''))
            readValues(self, data, params)


class ACHudCommonHint(object):

    def __init__(self, data):
        self.commonHintLocalizationID = ''
        if data:
            params = (('commonHintLocalizationID', ''),)
            readValues(self, data, params)


class ACHudHint(object):

    def __init__(self):
        self._setHints()
        self._setSectorObjectsData()

    def _setSectorObjectsData(self):
        LOG_DEBUG('_setSectorObjectsData')
        self._sectorObjects = {}
        path = AC_GAME_MODE_HUD_PLANE_HINT_PATH + 'sectorItems.xml'
        sectionRoot = ResMgr.openSection(path)
        for section in sectionRoot.values():
            sector = ACHudSectorItem(section)
            self._sectorObjects[sector.id] = sector
            LOG_DEBUG('_setSectorObjectsData   id: ', sector.id)

    def _setHints(self):
        path = AC_GAME_MODE_HUD_PLANE_HINT_PATH + 'planeHints.xml'
        sectionRoot = ResMgr.openSection(path)
        self._hintsDict = {}
        self._hintsDict['common'] = []
        for section in sectionRoot.values():
            if section.name == 'planeHints':
                for hintSection in section.values():
                    planeHint = ACHudPlaneHint(hintSection)
                    if planeHint.planeClass not in self._hintsDict.keys():
                        self._hintsDict[planeHint.planeClass] = []
                    self._hintsDict[planeHint.planeClass].append(planeHint)

            if section.name == 'commonHints':
                for hintSection in section.values():
                    commonHint = ACHudCommonHint(hintSection)
                    self._hintsDict['common'].append(commonHint)

    def getHintByPlaneType(self, planeType):
        """ return ACHudPlaneHint by plane type
        :param planeType:
        @rtype: list[ACHudPlaneHint]
        """
        return self.hintsDict[planeType]

    @property
    def getSectorItemsDict(self):
        """ return ACHudSectorItem dict
        @rtype: dict[ACHudSectorItem]
        """
        return self._sectorObjects

    def getCommonHint(self, planeType):
        return self.hintsDict['common']

    @property
    def hintsDict(self):
        """ hintsList
        @rtype: list[ACHudPlaneHint]
        """
        return self._hintsDict