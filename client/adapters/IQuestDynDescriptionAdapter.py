# Embedded file name: scripts/client/adapters/IQuestDynDescriptionAdapter.py
from Helpers.i18n import localizeLobby
from adapters.DefaultAdapter import DefaultAdapter
from exchangeapi.Connectors import getObject

class IQuestDynDescriptionAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = ob or getObject(kw['idTypeList'])
        adaptedOB = super(IQuestDynDescriptionAdapter, self).__call__(account, ob, **kw)
        for n in ('description',):
            adaptedOB[n], _dynVar = adaptedOB[n]
            if adaptedOB[n].isupper():
                adaptedOB[n] = localizeLobby(adaptedOB[n], **_dynVar)
            else:
                adaptedOB[n] = adaptedOB[n].format(**_dynVar)

        if 'PACK_DUNKIRK_1595Q' in adaptedOB['tokens']:
            adaptedOB['awards'].extend([{'type': 'plane',
              'id': 1595},
             {'type': 'camouflage',
              'id': -1362167281},
             {'type': 'crewmember',
              'id': 4},
             {'type': 'slots',
              'value': 1}])
        if 'PACK_DUNKIRK_5593Q' in adaptedOB['tokens']:
            adaptedOB['awards'].extend([{'type': 'plane',
              'id': 5593},
             {'type': 'camouflage',
              'id': -1513881259},
             {'type': 'crewmember',
              'id': 5},
             {'type': 'slots',
              'value': 1}])
        return adaptedOB