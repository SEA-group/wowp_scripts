# Embedded file name: scripts/client/GamePlayHints.py
from GameServiceBase import GameServiceBase

class GamePlayHints(GameServiceBase):

    def __init__(self):
        super(GamePlayHints, self).__init__()
        self.__hintVisible = False

    def setHintVisibility(self, value):
        self.__hintVisible = value

    @property
    def hintVisible(self):
        return self.__hintVisible