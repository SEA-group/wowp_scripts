# Embedded file name: scripts/client/adapters/IConfigSpecsAdapter.py
import db
from Helpers.PerformanceSpecsHelper import getMainCharacteristicBoundariesForPlane, getGlobalCharacteristicBoundaries
from Helpers.PerformanceSpecsHelper import getPerformanceSpecsTable
from adapters.DefaultAdapter import DefaultAdapter
from consts import SPECS_BOUNDARIES, SPECS_KEY_MAP, MAIN_CHARACTERISTICS_LIST, DEFAULT_CHARACTERISTICS_STATE
from exchangeapi.CommonUtils import splitIDTypeList
from gui.Scaleform.LobbyAirplaneHelper import getLobbyAirplane
from gui.Scaleform.utils.MeasurementSystem import MeasurementSystem

class IConfigSpecsAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        import BWPersonality
        lch = BWPersonality.g_lobbyCarouselHelper
        globalID = kw['idTypeList'][0][0]
        planeID = db.DBLogic.g_instance.getPlaneIDByGlobalID(globalID)
        ob = None
        measurementSystem = None
        obCompare = None
        _, typeList = splitIDTypeList(kw['idTypeList'])
        if isinstance(obList, list):
            for idx in xrange(0, len(typeList)):
                if typeList[idx] == 'measurementSystem':
                    measurementSystem = MeasurementSystem(obList[idx])
                elif typeList[idx] == 'planePreset':
                    if ob is None:
                        ob = obList[idx]
                    else:
                        obCompare = obList[idx]

        if obCompare is not None:
            airplaneForCompare = lch.getCarouselAirplane(obCompare['plane'].planeID) or getLobbyAirplane(obCompare['plane'].planeID)
        else:
            airplaneForCompare = None
        carouselAirplane = lch.getCarouselAirplaneSelected()
        if carouselAirplane is not None:
            currentPlaneID = carouselAirplane.planeID
            installedGlobalID = lch.inventory.getInstalledUpgradesGlobalID(currentPlaneID) if lch.inventory.isAircraftBought(currentPlaneID) else 0
        else:
            installedGlobalID = 0
        modify = globalID == installedGlobalID
        adaptedOb = super(IConfigSpecsAdapter, self).__call__(account, ob, **kw)
        if ob is not None:
            plane = ob['plane']
            lobbyPlane = lch.getCarouselAirplane(plane.planeID) or getLobbyAirplane(plane.planeID)
            equipment = lch.inventory.getEquipment(planeID)
            crewList = lch.inventory.getCrewList(planeID)
            if airplaneForCompare is None:
                projectiles = lobbyPlane.weapons.getInstalledProjectiles()
            else:
                projectiles = None
            specs = getPerformanceSpecsTable(globalID, modify, projectiles, equipment, crewList)
            if specs is not None:
                for key, value in specs.__dict__.iteritems():
                    if key in self._iface.attr:
                        ob[key] = value

            specs = lobbyPlane.getGroupedDescriptionFields(True, airplaneForCompare, globalID, modify, measurementSystem)
            adaptedOb['specs'] = []
            for el in specs:
                group = {}
                for i, j in el.__dict__.iteritems():
                    if isinstance(j, list):
                        vlist = []
                        for jel in j:
                            vlist.append(jel.__dict__)

                        group[i] = vlist
                    elif j is not None:
                        group[i] = j.__dict__

                adaptedOb['specs'].append(group)

        return adaptedOb

    def edit(self, account, requestID, idTypeList, data, ob = None, **kw):
        return super(IConfigSpecsAdapter, self).view(account, requestID, idTypeList, ob, **kw)


class IPlaneCharacteristicsGlobalBoundariesAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        return {'boundaries': {tag:getGlobalCharacteristicBoundaries(tag) for tag in SPECS_BOUNDARIES}}


class IPlaneCharacteristicsBoundariesAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        planeID = kw['idTypeList'][0][0]
        return {'boundaries': {tag:getMainCharacteristicBoundariesForPlane(planeID, tag) for tag in SPECS_BOUNDARIES}}


class IPlaneCharacteristicsConstantsAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        return {SPECS_KEY_MAP[tag]:tag for tag in MAIN_CHARACTERISTICS_LIST if SPECS_KEY_MAP[tag] in self._iface.attr}


class IPlaneCharacteristicsDefaultStateAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        return {'state': DEFAULT_CHARACTERISTICS_STATE}