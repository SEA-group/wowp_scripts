# Embedded file name: scripts/client/adapters/IAwardDescriptionAdapter.py
from DefaultAdapter import DefaultAdapter
from GameEvents.features.achievements.model import AchievementModel

class IAwardDescriptionAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        obID = kw['idTypeList'][0][0]
        ob = AchievementModel.get(id=obID, type='achievement')
        if ob is None:
            return ob
        else:
            return dict(name=ob.localized.name, description=ob.localized.descriptionWithProcessorData, level=ob.levelConditionLocale, history=ob.localized.history, steps=ob.steps, icoPath=ob.client.icon.small, icoPath_Outline=ob.client.icon.faded, icoBigPath=ob.client.icon.big, group=ob._attrs.markers.group, index=ob.client.order, page=ob.client.page, multiple=ob.client.multiple, outBlock=ob.client.place)