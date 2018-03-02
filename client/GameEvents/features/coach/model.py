# Embedded file name: scripts/client/GameEvents/features/coach/model.py
from __future__ import absolute_import
from consts import PLANE_TYPE
from GameEventsCommon.db.backends import BundledBackend
from GameEventsCommon.db.model import Model
from GameEventsCommon.features.coach.RanksDBMixin import RanksDBMixin
from GameEventsCommon.features.coach.RankObjectMixin import RankObjectMixin
from GameEvents.model import GameEventObject

class RankModelBase(Model, RanksDBMixin):

    def __init__(self, backend, instances = None, filters = None):
        Model.__init__(self, backend, instances, filters)
        RanksDBMixin.__init__(self)


class RankObject(GameEventObject, RankObjectMixin):

    @property
    def client(self):
        return self._attrs.client

    @property
    def title(self):
        return self.client.name.locale

    @property
    def description(self):
        return self.client.description.locale

    @property
    def iconPath(self):
        return self.client.icon.template

    @property
    def isRankRootModel(self):
        """Indicate if this instance is rank root model
        :rtype: bool
        """
        return self.type == 'rank'

    @property
    def isObjectiveRootModel(self):
        """Indicate if this instance is plane type objective root model
        :rtype: bool
        """
        return self.type == 'objective'

    @property
    def relatedPlaneType(self):
        """Relative plane type for this object.
        :return: One of PLANE_TYPE.*
        """
        if self.isRankRootModel or self.isObjectiveRootModel:
            planeTypeName = self.group
        else:
            parentModel = RankModel.get(id=self.parent)
            raise parentModel or AssertionError('Plane type requested for unknown subscriber: name = {0}, type = {1}, group = {2}'.format(self.name, self.type, self.group))
            planeTypeName = parentModel.group
        if planeTypeName == 'heavy.fighter':
            return PLANE_TYPE.HFIGHTER
        return getattr(PLANE_TYPE, planeTypeName.upper())

    @property
    def params(self):
        icons = getattr(self.client, 'icon', None)
        return {'iconPath': getattr(icons, 'template', ''),
         'orderIndex': self.client.order,
         'countDescription': self.localized.countDescription}

    @property
    def rankID(self):
        return self._attrs.rankID

    def updateRankID(self, rankID):
        self._attrs.rankID = rankID


RankModel = RankModelBase(backend=BundledBackend(modules=['_ge_coach_ranks',
 '_ge_coach_fighter',
 '_ge_coach_heavyfighter',
 '_ge_coach_navy',
 '_ge_coach_assault',
 '_ge_coach_bomber',
 '_ge_coach_ranks_empty',
 '_ge_coach_invasion_attack_assault',
 '_ge_coach_invasion_attack_bomber',
 '_ge_coach_invasion_attack_fighter',
 '_ge_coach_invasion_attack_heavyfighter',
 '_ge_coach_invasion_attack_navy',
 '_ge_coach_invasion_defense_assault',
 '_ge_coach_invasion_defense_bomber',
 '_ge_coach_invasion_defense_fighter',
 '_ge_coach_invasion_defense_heavyfighter',
 '_ge_coach_invasion_defense_navy']), instances=[(RankObject, {})])
RankModel.loadData()