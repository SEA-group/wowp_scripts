# Embedded file name: scripts/client/gui/HUD2/hudFeatures.py
import messenger
from _preparedBattleData_db import preparedBattleData
from gui.Scaleform.utils.MeasurementSystem import MeasurementSystem
from PlayerAvatarProxy import PlayerAvatarProxy

class Feature:
    BIG_WORLD = 'BigWorld'
    GAME_MODEL = 'GameModel'
    GAME_ENVIRONMENT = 'GameEnvironment'
    PLAYER_AVATAR = 'PlayerAvatar'
    REAL_PLAYER_AVATAR = 'RealPlayerAvatar'
    CLIENT_ARENA = 'ClientArena'
    CLIENT_ECONOMICS = 'ClientEconomics'
    TIMER_SERVICE = 'TimerService'
    INPUT = 'Input'
    CAMERA = 'Camera'
    GAME_PLAY_HINTS = 'GamePlayHints'
    MEASUREMENT_SYSTEM = 'MeasurementSystem'
    PREPARED_BATTLE_DATA = 'PreparedBattleData'
    PLANES_CONFIGURATIONS_DB = 'PlanesConfigurationsDB'
    BATTLE_HINTS = 'BattleHints'
    UI_SETTINGS = 'UISettings'
    UI_SOUND = 'uiSound'
    DB_LOGIC = 'DBLogic'
    STATE_MANAGER = 'StateManager'
    XMPP_CHAT = 'XmppChat'
    BATTLE_REPLAY = 'BattleReplay'


def buildHudFeatures(gameModel, features, stateManager):
    import BigWorld
    import GameEnvironment
    import Settings
    import audio
    import db.DBLogic
    import BattleReplay
    import _airplanesConfigurations_db
    features.provide(Feature.BIG_WORLD, BigWorld)
    features.provide(Feature.UI_SOUND, audio.GameSound().ui)
    features.provide(Feature.DB_LOGIC, db.DBLogic.g_instance)
    gameEnvironment = GameEnvironment.g_instance
    features.provide(Feature.GAME_ENVIRONMENT, gameEnvironment)
    features.provide(Feature.INPUT, gameEnvironment.service(Feature.INPUT))
    features.provide(Feature.CAMERA, gameEnvironment.service(Feature.CAMERA))
    features.provide(Feature.GAME_PLAY_HINTS, gameEnvironment.service(Feature.GAME_PLAY_HINTS))
    features.provide(Feature.CLIENT_ARENA, GameEnvironment.getClientArena())
    features.provide(Feature.PLAYER_AVATAR, GameEnvironment.g_instance.playerAvatarProxy)
    features.provide(Feature.REAL_PLAYER_AVATAR, BigWorld.player())
    features.provide(Feature.TIMER_SERVICE, GameEnvironment.g_instance.getTimer())
    features.provide(Feature.CLIENT_ECONOMICS, GameEnvironment.getClientEconomics())
    features.provide(Feature.MEASUREMENT_SYSTEM, MeasurementSystem())
    features.provide(Feature.PREPARED_BATTLE_DATA, preparedBattleData)
    features.provide(Feature.PLANES_CONFIGURATIONS_DB, _airplanesConfigurations_db)
    features.provide(Feature.GAME_MODEL, gameModel)
    features.provide(Feature.UI_SETTINGS, Settings.g_instance)
    features.provide(Feature.STATE_MANAGER, stateManager)
    features.provide(Feature.XMPP_CHAT, messenger.g_xmppChatHandler)
    features.provide(Feature.BATTLE_REPLAY, BattleReplay.g_replay)
    features.provide(Feature.BATTLE_HINTS, GameEnvironment.getBattleHintMessenger())