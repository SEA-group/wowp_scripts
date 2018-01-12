# Embedded file name: scripts/client/adapters/IGameEventObject.py
from adapters.DefaultAdapter import DefaultAdapter
from GameEvents.features.quests.model import QuestModel
from GameEvents.features.tutorial.model import TutorialModel
from GameEvents.features.coach.model import RankModel
from GameEventsCommon.db.model import Model

class IGameEventObjectStaticInfo(DefaultAdapter):

    def __call__(self, account, obj, **kwargs):
        obj = super(IGameEventObjectStaticInfo, self).__call__(account, obj, **kwargs)
        id_ = kwargs['idTypeList'][0][0]
        model = None
        for model in Model.registered:
            item = model.get(id=id_)
            if item:
                break

        if not item or not model:
            return obj
        else:
            name = item.localized.name
            description = item.localized.descriptionWithProcessorData
            if item.parent:
                parent = model.get(id=item.parent)
                if not name and item.parent:
                    name = parent.localized.name
                if not description and item.parent:
                    description = parent.localized.descriptionWithProcessorData
            return {'order': getattr(item.client, 'order', 0),
             'name': name,
             'description': description,
             'params': item.params}