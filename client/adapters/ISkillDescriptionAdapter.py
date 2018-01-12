# Embedded file name: scripts/client/adapters/ISkillDescriptionAdapter.py
from DefaultAdapter import DefaultAdapter
from Helpers.i18n import localizeSkill, localizeLobby

class ISkillDescriptionAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        isSpecialization = hasattr(ob, 'mainForSpecialization')
        aob = super(ISkillDescriptionAdapter, self).__call__(account, ob, **kw)

        def loc(key):
            modifier = int(abs(100 - ob.mods[0].states[0] * 100))
            aob[key] = (isSpecialization and localizeLobby or localizeSkill)(aob[key], skill_modifier=modifier)

        loc('name')
        loc('description')
        loc('fullDescription')
        loc('middleDescription')
        return aob