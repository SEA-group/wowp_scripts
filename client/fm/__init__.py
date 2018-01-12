# Embedded file name: scripts/client/fm/__init__.py
import Avatar
import BigWorld
import DestructibleObjectFactory
import PlayerAvatar
import GunsController.GunsFactory
from fm.FMAvatar import fmAvatar
from fm.FMGuns import fmGuns
from fm.FMPlayerAvatar import fmPlayerAvatar
from fm.FMWeapons import fmWeapons
Avatar.Avatar = fmAvatar(Avatar.Avatar)
Avatar.PlayerAvatar = fmPlayerAvatar(Avatar.PlayerAvatar)
GunsController.GunsFactory.GunsController = fmGuns(GunsController.GunsFactory.GunsController)
DestructibleObjectFactory.Weapons = fmWeapons(DestructibleObjectFactory.Weapons)