# Embedded file name: scripts/client/adapters/IShortConfigSpecsAdapter.py
from adapters.DefaultAdapter import DefaultAdapter
from Helpers.PerformanceSpecsHelper import getPerformanceSpecsTable, getAirplaneDescriptionPair
from consts import MAIN_CHARACTERISTICS_LIST
import db

class IShortConfigSpecsAdapter(DefaultAdapter):

    def __call__(self, account, obList, **kw):
        globalID = kw['idTypeList'][0][0]
        ob = obList
        retOb = {}
        if ob is not None:
            import BWPersonality
            lch = BWPersonality.g_lobbyCarouselHelper
            planeID = db.DBLogic.g_instance.getPlaneIDByGlobalID(globalID)
            carouselAirplane = lch.getCarouselAirplaneSelected()
            modify = False
            projectiles = None
            equipment = lch.inventory.getEquipment(planeID)
            crewList = lch.inventory.getCrewList(planeID)
            if carouselAirplane is not None:
                currentPlaneID = carouselAirplane.planeID
                installedGlobalID = lch.inventory.getInstalledUpgradesGlobalID(currentPlaneID) if lch.inventory.isAircraftBought(currentPlaneID) else 0
                if installedGlobalID == globalID:
                    projectiles = carouselAirplane.weapons.getInstalledProjectiles()
                    modify = True
            specs = getPerformanceSpecsTable(globalID, modify, projectiles, equipment, crewList)
            mainSpecs = {}
            if specs is not None:
                for tag in MAIN_CHARACTERISTICS_LIST:
                    _, value, _, _ = getAirplaneDescriptionPair(specs, tag)
                    mainSpecs[tag] = value

            retOb['mainSpecs'] = mainSpecs
        return super(IShortConfigSpecsAdapter, self).__call__(account, retOb, **kw)

    def edit(self, account, requestID, idTypeList, data, ob = None, **kw):
        return super(IShortConfigSpecsAdapter, self).view(account, requestID, idTypeList, ob, **kw)