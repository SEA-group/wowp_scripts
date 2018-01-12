# Embedded file name: scripts/client/audio/InteractiveMix/InteractiveMixHandler.py
from GamePhases import GamePhases
from MixFocus import MixFocus
from audio.AKConsts import INTERACTIVE_MIX_TYPES
g_instance = None

class InteractiveMixHandler:

    def __init__(self):
        self.__features = {}
        self.__cases = {}

    @staticmethod
    def instance():
        global g_instance
        if not g_instance:
            g_instance = InteractiveMixHandler()
        return g_instance

    def push(self, id, feature):
        self.__features[id] = feature

    def get(self, id):
        return self.__features.get(id, None)

    def create(self):
        self.push(INTERACTIVE_MIX_TYPES.GAME_PHASE, GamePhases.instance())

    def createArena(self):
        self.push(INTERACTIVE_MIX_TYPES.MIX_FOCUS, MixFocus())

    def clearArena(self):
        self.remove(INTERACTIVE_MIX_TYPES.MIX_FOCUS)

    def remove(self, id):
        if id in self.__features:
            self.__features[id].clear()
            del self.__features[id]

    @property
    def mixFocus(self):
        return self.get(INTERACTIVE_MIX_TYPES.MIX_FOCUS)