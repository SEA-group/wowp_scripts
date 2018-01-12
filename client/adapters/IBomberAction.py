# Embedded file name: scripts/client/adapters/IBomberAction.py
from adapters.DefaultAdapter import DefaultAdapter
from exchangeapi.Connectors import getObject
from Helpers.i18n import localizeLobby, localizeTooltips

def part2bomber(partId):
    from GameEvents.features.bomber.model import BomberModel
    for bomber in BomberModel.filter(type='bomber'):
        for part in bomber.nested.subscriber:
            if part.id == partId:
                return int(bomber.name)


class IBomberPartAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        name = ob.client.name.locale
        description = ob.client.description.locale
        planeId = part2bomber(ob.id)
        bigIconPath = ob.client.icon.big
        smallIconPath = ob.client.icon.small
        position = ob.client.place
        adaptedOB = super(IBomberPartAdapter, self).__call__(account, getObject(kw['idTypeList']), **kw)
        if adaptedOB:
            adaptedOB['name'] = localizeLobby(name)
            adaptedOB['description'] = localizeTooltips(description)
            adaptedOB['planeID'] = planeId
            adaptedOB['bigIconPath'] = bigIconPath
            adaptedOB['smallIconPath'] = smallIconPath
            adaptedOB['position'] = position
        return adaptedOB