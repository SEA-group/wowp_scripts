# Embedded file name: scripts/client/Bomber.py
from AvatarBot import AvatarBot

class Bomber(AvatarBot):

    def onEnterWorld(self, prereqs):
        AvatarBot.onEnterWorld(self, prereqs)
        self.controllers['modelManipulator'].updateBombersTrailEffect(True)

    def onLeaveWorld(self):
        self.controllers['modelManipulator'].updateBombersTrailEffect(False)
        AvatarBot.onLeaveWorld(self)

    def set_outroState(self, value):
        if self.outroState:
            self.controllers['modelManipulator'].updateBombersTrailEffect(False)