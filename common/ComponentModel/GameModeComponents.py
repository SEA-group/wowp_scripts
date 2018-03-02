# Embedded file name: scripts/common/ComponentModel/GameModeComponents.py
import sys
import inspect
from consts import TEAM_INDEX_TO_INVASION_SIDE, IS_CELLAPP
from ComponentLoggingHelpers import logError
from Component import Component, InputSlot, OutputSlot
if IS_CELLAPP:
    import CellEntityHelpers

class TeamIdToInvasionSide(Component):

    @classmethod
    def componentCategory(cls):
        return 'GameMode'

    def slotDefinitions(self):
        return [InputSlot('team_id', Component.SLOT_TEAM_ID, None), OutputSlot('res', Component.SLOT_STR, TeamIdToInvasionSide._execute)]

    def _execute(self, team_id):
        res = TEAM_INDEX_TO_INVASION_SIDE.get(team_id)
        if res is None:
            logError(self, 'Invalid team id, team code: ' + str(team_id))
            return ''
        else:
            return res


class BattleGameMode(Component):

    @classmethod
    def componentAspects(cls):
        return [Component.ASPECT_SERVER]

    @classmethod
    def componentCategory(cls):
        return 'GameMode'

    def slotDefinitions(self):
        return [OutputSlot('res', Component.SLOT_STR, BattleGameMode._execute)]

    def _execute(self):
        arena = CellEntityHelpers.getArena(self)
        if arena is not None:
            return arena.settings.gameType
        else:
            return ''


def getModuleComponents():
    return list((value for key, value in inspect.getmembers(sys.modules[__name__], inspect.isclass) if issubclass(value, Component) and value is not Component))