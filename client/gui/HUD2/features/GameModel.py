# Embedded file name: scripts/client/gui/HUD2/features/GameModel.py
from gui.HUD2.core.DataModel import DataModel, Structure
from gui.HUD2.features.AmmoBelts.AmmoBeltsModel import AmmoBeltsModel
from gui.HUD2.features.Ammunitions.AmmunitionModel import AmmunitionModel
from gui.HUD2.features.AttitudeIndicator.AttitudeIndicatorModel import AttitudeIndicatorModel
from gui.HUD2.features.Consumables.ConsumableModel import ConsumableModel
from gui.HUD2.features.DeathInfo.DeathInfoModel import DeathInfoModel
from gui.HUD2.features.Denunciation.DenunciationModel import DenunciationModel
from gui.HUD2.features.Entities.EntitiesModel import EntitiesModel
from gui.HUD2.features.Equipment.EquipmentModel import EquipmentModel
from gui.HUD2.features.FastCommands.FastCommandModel import FastCommandModel
from gui.HUD2.features.Freinds.FriendsModel import FriendsModel
from gui.HUD2.features.GameMode.GameModeModel import GameModeModel
from gui.HUD2.features.HudSettings.HudSettingsModel import HudSettingsModel
from gui.HUD2.features.Intro.IntroModel import IntroModel
from gui.HUD2.features.Minimap.MinimapModel import MinimapModel
from gui.HUD2.features.Outro.OutroModel import OutroModel
from gui.HUD2.features.PlaneData.BasePlaneDataModel import BasePlaneDataModel
from gui.HUD2.features.PlaneScheme.PlaneSchemeModel import PlaneSchemeModel
from gui.HUD2.features.Player.PlayerModel import PlayerModel
from gui.HUD2.features.Radar.RadarModel import RadarModel
from gui.HUD2.features.Respawn.RespawnModel import RespawnModel
from gui.HUD2.features.SectorItems.SectorItemsModel import SectorItemsModel
from gui.HUD2.features.Skills.CrewModel import CrewModel
from gui.HUD2.features.Skills.SkillsModel import SkillsModel
from gui.HUD2.features.Spectator.SpectatorModel import SpectatorModel
from gui.HUD2.features.arena.ArenaModel import ArenaModel
from gui.HUD2.features.battleEvent.BattleLogModel import BattleLogModel
from gui.HUD2.features.battleNotifications.BattleNotificationsModel import BattleNotificationsModel
from gui.HUD2.features.battleAlerts.BattleAlertsModel import BattleAlertsModel
from gui.HUD2.features.control.ControlModel import ControlModel
from gui.HUD2.features.hotkeys.HotKeysModel import HotKeysModel
from gui.HUD2.features.loading.LoadingModel import LoadingModel
from gui.HUD2.features.measurement.MeasurementModel import MeasurementModel
from gui.HUD2.features.parameters.ParametersModel import ParametersModel
from gui.HUD2.features.planeCharacteristics.PlaneCharacteristicsModel import PlaneCharacteristicsModel
from gui.HUD2.features.systemInfo.SystemInfoModel import SystemInfoModel
from gui.HUD2.features.target.TargetModel import TargetModel
from gui.HUD2.features.time.TimeModel import TimeModel
from gui.HUD2.features.crosshair.CrosshairModel import CrosshairModel
from gui.HUD2.features.HealthRepair.HealthRepairModel import HealthRepairModel
from gui.HUD2.features.PlayerInfo.PlayerInfoModel import PlayerInfoModel
from gui.HUD2.features.Ranks.RanksModel import RanksModel
from gui.HUD2.features.Achievements.AchievementsModel import AchievementsModel
from gui.HUD2.features.PlaneTypeObjectives.PlaneTypeObjectivesModel import PlaneTypeObjectivesModel
from gui.HUD2.features.BattleReplay.BattleReplayModel import BattleReplayModel
from gui.HUD2.features.Utils.UtilsModel import UtilsModel
from gui.HUD2.features.GameplayHints.GameplayHintsModel import GameplayHintsModel

class GameModel(DataModel):
    SCHEME = Structure(time=TimeModel, arena=ArenaModel, loading=LoadingModel, crosshair=CrosshairModel, respawn=RespawnModel, deathInfo=DeathInfoModel, control=ControlModel, parameters=ParametersModel, player=PlayerModel, domination=GameModeModel, systemInfo=SystemInfoModel, hotkeys=HotKeysModel, planeScheme=PlaneSchemeModel, ammunitions=AmmunitionModel, consumables=ConsumableModel, equipments=EquipmentModel, skills=SkillsModel, crews=CrewModel, battlePoints=BattleLogModel, battleNotifications=BattleNotificationsModel, battleAlerts=BattleAlertsModel, entities=EntitiesModel, target=TargetModel, ammoBelts=AmmoBeltsModel, sectorItems=SectorItemsModel, Intro=IntroModel, outro=OutroModel, spectator=SpectatorModel, fastCommand=FastCommandModel, measurementSystem=MeasurementModel, radar=RadarModel, hudSettings=HudSettingsModel, planeCharacteristics=PlaneCharacteristicsModel, denunciation=DenunciationModel, friends=FriendsModel, planes=BasePlaneDataModel, healthRepair=HealthRepairModel, currentPlayerInfo=PlayerInfoModel, ranks=RanksModel, achievements=AchievementsModel, classTasks=PlaneTypeObjectivesModel, battleReplay=BattleReplayModel, utils=UtilsModel, minimap=MinimapModel, attitudeIndicator=AttitudeIndicatorModel, gameplayHints=GameplayHintsModel)