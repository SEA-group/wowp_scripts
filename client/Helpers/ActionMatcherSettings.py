# Embedded file name: scripts/client/Helpers/ActionMatcherSettings.py
from consts import SHELL_INDEX
ROCKET_SLOT = SHELL_INDEX.TYPE1
BOMB_SLOT = SHELL_INDEX.TYPE2
SHELL_LAUNCHED_TRIGGER_NAMES = {ROCKET_SLOT: 'ROCKET_SLOT_SHELL_LAUNCHED',
 BOMB_SLOT: 'BOMB_SLOT_SHELL_LAUNCHED'}