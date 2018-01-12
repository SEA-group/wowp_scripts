# Embedded file name: scripts/client/audio/SoundEventDispatcher.py
import BigWorld
import GameModeSettings.ACSettings as SETTINGS
from Event import EventDispatcher, eventHandler
from ArenaHelpers.GameModes.AreaConquest.ACGameModeClient import AC_ARENA_UPDATE_EVENTS
from ArenaHelpers.GameModes.AreaConquest import AC_EVENTS
from functools import partial
from consts import SECTOR_GAMEPLAY_TYPE, TEAM_ID
from AKConsts import VOICE, MUSIC_SOUND, SECTOR_VOICES, SECTOR_VOICES_TYPE
from SoundObjects import MusicSound
from gui.HUDconsts import PERCENT_BEFORE_DOMINATION_WIN
from debug_utils import LOG_DEBUG
from EntityHelpers import EntityStates, isAirStrikeBomber
from AudioHelpers.AirStrikeDefeatedEventProvider import AirStrikeDefeatedEventProvider
import GameEnvironment
from Event import Event
eVoiceoverRequest = Event()

class SoundEventSectorCondition:
    TEAM_FRIENDLY = 0
    TEAM_ENEMY = 1
    TEAM_DEFENDER = 2

    def __init__(self, teamType, count, voiceEvent):
        self.teamType = teamType
        self.count = count
        self.voiceEvent = voiceEvent

    def playSound(self):
        global eVoiceoverRequest
        if self.voiceEvent:
            eVoiceoverRequest(self.voiceEvent)


class SoundEventDispatcherSettings:
    BATTLE_EVENT_NR_CONTDOWN = 45
    MINUTES_ARENA_LEFT_TO_WIN = 1
    MINUTES_ARENA_LEFT_TO_LOSE = 1
    SECONDS_ARENA_LEFT_TO_FINISH_BATTLE = 30
    SectorConditionDict = {SECTOR_GAMEPLAY_TYPE.DEFAULT: [],
     SECTOR_GAMEPLAY_TYPE.AIRFIELD: [SoundEventSectorCondition(SoundEventSectorCondition.TEAM_ENEMY, 5, VOICE.AIRFIELD_ALARM)],
     SECTOR_GAMEPLAY_TYPE.FACTORY: [SoundEventSectorCondition(SoundEventSectorCondition.TEAM_ENEMY, 5, VOICE.FACTORY_ALARM)],
     SECTOR_GAMEPLAY_TYPE.MILITARY_BASE: [SoundEventSectorCondition(SoundEventSectorCondition.TEAM_ENEMY, 5, VOICE.BASE_ALARM)],
     SECTOR_GAMEPLAY_TYPE.RADAR: [SoundEventSectorCondition(SoundEventSectorCondition.TEAM_ENEMY, 5, VOICE.CENTER_ALARM)],
     SECTOR_GAMEPLAY_TYPE.NEUTRAL: [],
     SECTOR_GAMEPLAY_TYPE.SPAWNPOINT: []}


class SoundEventDispatcher(EventDispatcher):

    def __init__(self, gameMode):
        """
        @type gameMode: ArenaHelpers.GameModes.AreaConquest.ACGameModeClient.ACGameModeClient
        """
        super(SoundEventDispatcher, self).__init__()
        self.__gameMode = gameMode
        self.__gameModeReady = False
        self.__CheckXMinutesLeftToWin = True
        self.__CheckXMinutesLeftToLose = True
        self.__CheckXSecondsLeftToFinishBattle = True
        self.__sectorCounters = None
        self.__sectorCountersOld = None
        self.__friendlyTeamIndex = BigWorld.player().teamIndex
        self.__enemyTeamIndex = 1 if self.__friendlyTeamIndex == 0 else 0
        self.__defenderTeamIndex = TEAM_ID.TEAM_2
        self.__pointsToWin = self.__gameMode.arenaTypeData.gameModeSettings.pointsToWin
        self.__NR_CountdownCallbackID = None
        self.__TickSecCallback = None
        self.__finished = False
        self.__mapRealTiToInternal = {self.__friendlyTeamIndex: SoundEventSectorCondition.TEAM_FRIENDLY,
         self.__enemyTeamIndex: SoundEventSectorCondition.TEAM_ENEMY,
         self.__defenderTeamIndex: SoundEventSectorCondition.TEAM_DEFENDER}
        self.__airStrikeDefeatedEventProvider = AirStrikeDefeatedEventProvider(GameEnvironment.g_instance, gameMode)
        self.__lastPlayerReported = False
        self.__lastEnemyReported = False
        self.__thunderheadModeStarted = False
        self.__restartOneSecTick()
        return

    def __playVoice(self, voiceover):
        eVoiceoverRequest(voiceover)

    def __clearEvents(self):
        if self.__gameModeReady:
            self.__gameMode.removeEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self.onUpdateSectorState)
            self.__gameMode.removeEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self.onGlobalScoreUpdate)
        self.__airStrikeDefeatedEventProvider.eAirStrikeDefeated -= self.__onAirStrikeDefeated()
        self.__gameMode.lastPlayerManager.eUpdateLastPlayer -= self.__onUpdateLastPlayer

    def __releaseCallbacks(self):
        if self.__NR_CountdownCallbackID:
            BigWorld.cancelCallback(self.__NR_CountdownCallbackID)
            self.__NR_CountdownCallbackID = None
        if self.__TickSecCallback:
            BigWorld.cancelCallback(self.__TickSecCallback)
            self.__TickSecCallback = None
        super(SoundEventDispatcher, self).clear()
        return

    def finish(self):
        if not self.__finished:
            self.__releaseCallbacks()
            self.__clearEvents()
            self.__airStrikeDefeatedEventProvider.destroy()
            self.__airStrikeDefeatedEventProvider = None
            eVoiceoverRequest.clear()
            self.__finished = True
        return

    def __del__(self):
        self.finish()

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_ROCKET_V2_HIT_TARGET)
    def onRocketV2HitTarget(self, payload, *args, **kwargs):
        sectorIdent, teamIndex, targetTeamObjectId, targetPositionX, targetPositionY, targetPositionZ, targetTeamIndex = payload
        if teamIndex == self.__friendlyTeamIndex:
            LOG_DEBUG('SOUNDEVN: event 41 \xd0\xa0\xd0\xb0\xd0\xba\xd0\xb5\xd1\x82\xd0\xb0 \xd0\xa4\xd0\xb0\xd1\x83-2 \xd1\x81\xd0\xbe\xd1\x8e\xd0\xb7\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb2\xd0\xbe\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb1\xd0\xb0\xd0\xb7\xd1\x8b \xd0\xbd\xd0\xb0\xd0\xbd\xd0\xb5\xd1\x81\xd0\xbb\xd0\xb0 \xd1\x83\xd1\x80\xd0\xbe\xd0\xbd \xd0\xba\xd0\xbe\xd0\xbc\xd0\xbf\xd0\xbb\xd0\xb5\xd0\xba\xd1\x81\xd1\x83 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x82\xd0\xb8\xd0\xb2\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb0')
            self.__playVoice(VOICE.FAU2_LAUNCH_POS)
        elif targetTeamIndex == self.__friendlyTeamIndex:
            LOG_DEBUG('SOUNDEVN: event 40 \xd0\xa0\xd0\xb0\xd0\xba\xd0\xb5\xd1\x82\xd0\xb0 \xd0\xa4\xd0\xb0\xd1\x83-2 \xd0\xb2\xd0\xbe\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb1\xd0\xb0\xd0\xb7\xd1\x8b \xd0\xbf\xd1\x80\xd0\xbe\xd1\x82\xd0\xb8\xd0\xb2\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb0 \xd0\xbd\xd0\xb0\xd0\xbd\xd0\xb5\xd1\x81\xd0\xbb\xd0\xb0 \xd1\x83\xd1\x80\xd0\xbe\xd0\xbd \xd1\x81\xd0\xbe\xd1\x8e\xd0\xb7\xd0\xbd\xd0\xbe\xd0\xbc\xd1\x83 \xd0\xba\xd0\xbe\xd0\xbc\xd0\xbf\xd0\xbb\xd0\xb5\xd0\xba\xd1\x81\xd1\x83.')
            self.__playVoice(VOICE.FAU2_LAUNCH_NEG)

    @eventHandler(AC_EVENTS.BOMBERS_LAUNCHED)
    def onBombersWaveLaunched(self, sectorID, targetID, teamIndex, waveID, bombersIDsStates, startTime, *args, **kwargs):
        if self.__enemyTeamIndex == teamIndex:
            LOG_DEBUG('SOUNDEVN: event 27 \xd0\x92\xd1\x8b\xd0\xbb\xd0\xb5\xd1\x82\xd0\xb5\xd0\xbb\xd0\xb8 \xd0\xb1\xd0\xbe\xd0\xbc\xd0\xb1\xd0\xb0\xd1\x80\xd0\xb4\xd0\xb8\xd1\x80\xd0\xbe\xd0\xb2\xd1\x89\xd0\xb8\xd0\xba\xd0\xb8 \xd0\xbf\xd1\x80\xd0\xbe\xd1\x82\xd0\xb8\xd0\xb2\xd0\xbd\xd0\xb8\xd0\xba\xd0\xb0(AirStrike)')
            self.__playVoice(VOICE.AIRSTRIKE_SPAWNED)

    @eventHandler(AC_ARENA_UPDATE_EVENTS.AC_BATTLE_EVENT)
    def onBattleEvent(self, payload, *args, **kwargs):
        battleEvent = payload
        if battleEvent == SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE:
            LOG_DEBUG('SOUNDEVN: event 19\t\xd0\xa1\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x82\xd0\xb8\xd0\xb5 \xd0\x93\xd1\x80\xd0\xbe\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb9 \xd1\x84\xd1\x80\xd0\xbe\xd0\xbd\xd1\x82. \xd0\x9e\xd1\x82\xd1\x81\xd1\x87\xd1\x91\xd1\x82 \xd0\xb7\xd0\xb0\xd0\xb2\xd0\xb5\xd1\x80\xd1\x88\xd1\x91\xd0\xbd')
            self.__playVoice(VOICE.CDOWN_THUNDERHEAD_END)
            MusicSound.instance().playBattleMusic()
            self.__thunderheadModeStarted = True

    def onGlobalScoreUpdate(self, scoreGlobal, *args, **kwargs):
        player = BigWorld.player()
        enemyTeamIndex = 1 - player.teamIndex
        globalScoreAlly = scoreGlobal[player.teamIndex]
        globalScoreEnemy = scoreGlobal[enemyTeamIndex]
        normalizedPoints = max(float(globalScoreAlly) / self.__pointsToWin, float(globalScoreEnemy) / self.__pointsToWin)
        if not self.__voice_CLOSE_TO_played and normalizedPoints * 100 > PERCENT_BEFORE_DOMINATION_WIN:
            self.__voice_CLOSE_TO_played = True
            if globalScoreAlly > globalScoreEnemy:
                self.__playVoice(VOICE.CLOSE_TO_WIN)
            elif globalScoreAlly < globalScoreEnemy:
                self.__playVoice(VOICE.CLOSE_TO_LOSE)
            MusicSound.instance().playBattleMusic()

    def onUpdateSectorState(self, sectorId, oldState, oldTeamIndex, state, teamIndex, *args, **kwargs):
        sector = self.__gameMode.sectors[sectorId]
        soundSettings = self.__gameMode.arenaTypeData.sectors.getSector(sectorId).soundSettings
        if teamIndex != oldTeamIndex:
            sectorGameplayType = sector.settings.gameplayType
            sectorGameplayLevel = sector.settings.gameplayLevel
            if self.__isAllSectorsCaptured(teamIndex):
                if self.__isTeamate(teamIndex):
                    self.__playVoice(VOICE.ALL_SECTORS_CAPTURED)
                    MusicSound.instance().playStinger(MUSIC_SOUND.MUSIC_STINGER.POSITIVE)
                else:
                    self.__playVoice(VOICE.ALL_SECTORS_LOST)
                    MusicSound.instance().playStinger(MUSIC_SOUND.MUSIC_STINGER.NEGATIVE)
                return
            if self.__isTeamate(teamIndex):
                if self.__isCapturedLastSectorWithType(sectorGameplayType, sectorGameplayLevel):
                    self.__playVoice(soundSettings.captureLastModel.allyEvent)
                elif self.__isPlayerHelpCaptureSector(sectorId):
                    self.__playVoice(soundSettings.captureModel.allyEvent)
                MusicSound.instance().playStinger(MUSIC_SOUND.MUSIC_STINGER.POSITIVE)
            elif oldTeamIndex in (TEAM_ID.TEAM_0, TEAM_ID.TEAM_1):
                self.__playVoice(soundSettings.captureModel.enemyEvent)

    def onBattleEventCountdown(self, battleEvent, timeBefore):
        if battleEvent == SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE:
            LOG_DEBUG('SOUNDEVN: event 18\t\xd0\xa1\xd0\xbe\xd0\xb1\xd1\x8b\xd1\x82\xd0\xb8\xd0\xb5 \xd0\x93\xd1\x80\xd0\xbe\xd0\xb7\xd0\xbe\xd0\xb2\xd0\xbe\xd0\xb9 \xd1\x84\xd1\x80\xd0\xbe\xd0\xbd\xd1\x82. \xd0\x97\xd0\xb0\xd0\xbf\xd1\x83\xd1\x81\xd0\xba \xd0\xbe\xd1\x82\xd1\x81\xd1\x87\xd1\x91\xd1\x82\xd0\xb0 (45 \xd1\x81\xd0\xb5\xd0\xba.)')
            self.__playVoice(VOICE.CDOWN_THUNDERHEAD_START)

    def __prepareForUpdates(self):
        triggers = self.__gameMode.arenaTypeData.gameModeSettings.battleEvents.triggers
        eventRDTrigger = next((x for x in triggers if x.battleEvent == SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE), None)
        if eventRDTrigger:
            csTriggerTime = eventRDTrigger.predicate.options['duration']
            arenaTimePassed = BigWorld.serverTime() - BigWorld.player().arenaStartTime
            timeToNRCountdown = csTriggerTime - arenaTimePassed - SoundEventDispatcherSettings.BATTLE_EVENT_NR_CONTDOWN
            self.__NR_CountdownCallbackID = BigWorld.callback(timeToNRCountdown, partial(self.onBattleEventCountdown, SETTINGS.BATTLE_EVENT_TYPE.RESPAWN_DISABLE, SoundEventDispatcherSettings.BATTLE_EVENT_NR_CONTDOWN))
        self.__sectorCounters = dict()
        for sectorID, sectorModel in self.__gameMode.arenaTypeData.sectors.sectors.iteritems():
            self.__sectorCounters[sectorID] = 0

        self.__voice_CLOSE_TO_played = False
        return

    def __registerAdditionalEvents(self):
        self.__gameMode.addEventHandler(AC_EVENTS.SECTOR_STATE_CHANGED, self.onUpdateSectorState)
        self.__gameMode.addEventHandler(AC_EVENTS.GLOBAL_SCORE_UPDATED, self.onGlobalScoreUpdate)
        self.__gameMode.lastPlayerManager.eUpdateLastPlayer += self.__onUpdateLastPlayer
        self.__airStrikeDefeatedEventProvider.eAirStrikeDefeated += self.__onAirStrikeDefeated

    def __onAirStrikeDefeated(self):
        self.__playVoice(VOICE.AIRSTRIKE_DEFEATED)

    def __onUpdateLastPlayer(self, isEnemy, *args, **kwargs):
        if isEnemy:
            self.__reportLastEnemy()
        else:
            self.__reportLastPlayer()

    def __reportLastPlayer(self):
        self.__playVoice(VOICE.LAST_PLAYER)

    def __reportLastEnemy(self):
        self.__playVoice(VOICE.LAST_ENEMY)

    def onTickOneSec(self):
        if not self.__gameModeReady and self.__gameMode.isReady and BigWorld.player().arenaStartTime >= 0:
            self.__prepareForUpdates()
            self.__registerAdditionalEvents()
            self.__gameModeReady = True
        if self.__gameModeReady:
            if self.__CheckXMinutesLeftToWin or self.__CheckXMinutesLeftToLose or self.__CheckXSecondsLeftToFinishBattle:
                arenaTime = BigWorld.serverTime() - BigWorld.player().arenaStartTime
                secondsLeft = self.__gameMode.arenaTypeData.gameModeSettings.battleDuration - arenaTime
                m, s = divmod(secondsLeft, 60)
                win = self.__gameMode.scoreGlobal[self.__friendlyTeamIndex] > self.__gameMode.scoreGlobal[self.__enemyTeamIndex]
                if win and self.__CheckXMinutesLeftToWin and m <= SoundEventDispatcherSettings.MINUTES_ARENA_LEFT_TO_WIN:
                    LOG_DEBUG('SOUNDEVN: event 37 \xd0\x94\xd0\xbe \xd0\xba\xd0\xbe\xd0\xbd\xd1\x86\xd0\xb0 \xd0\xb1\xd0\xbe\xd1\x8f \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd0\xbe\xd1\x81\xd1\x8c X \xd0\xbc\xd0\xb8\xd0\xbd\xd1\x83\xd1\x82. \xd0\x9a\xd0\xbe\xd0\xbc\xd0\xb0\xd0\xbd\xd0\xb4\xd0\xb0 \xd0\xb8\xd0\xb3\xd1\x80\xd0\xbe\xd0\xba\xd0\xb0 \xd0\xb2\xd1\x8b\xd0\xb8\xd0\xb3\xd1\x80\xd1\x8b\xd0\xb2\xd0\xb0\xd0\xb5\xd1\x82')
                    self.__playVoice(VOICE.BATTLE_TIME_NOTIFY_POS)
                    self.__CheckXMinutesLeftToWin = False
                if not win and self.__CheckXMinutesLeftToLose and m <= SoundEventDispatcherSettings.MINUTES_ARENA_LEFT_TO_LOSE:
                    self.__playVoice(VOICE.BATTLE_TIME_NOTIFY_NEG)
                    self.__CheckXMinutesLeftToLose = False
                if self.__CheckXSecondsLeftToFinishBattle and secondsLeft <= SoundEventDispatcherSettings.SECONDS_ARENA_LEFT_TO_FINISH_BATTLE:
                    LOG_DEBUG('SOUNDEVN: event 38 \xd0\x94\xd0\xbe \xd0\xba\xd0\xbe\xd0\xbd\xd1\x86\xd0\xb0 \xd0\xb1\xd0\xbe\xd1\x8f \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd0\xbe\xd1\x81\xd1\x8c 30 \xd1\x81\xd0\xb5\xd0\xba\xd1\x83\xd0\xbd\xd0\xb4')
                    self.__playVoice(VOICE.BATTLE_30SEC_NOTIFY)
                    self.__CheckXSecondsLeftToFinishBattle = False
            self.__sectorCountersOld = dict(self.__sectorCounters)
            for sectorID in self.__gameMode.arenaTypeData.sectors.sectors.iterkeys():
                self.__sectorCounters[sectorID] = 0

            avatarsCounted = 0
            for avatarID in self.__gameMode.clientArena.avatarInfos:
                avatarInfo = self.__gameMode.clientArena.getAvatarInfo(avatarID)
                entity = BigWorld.entities.get(avatarID, None)
                if entity:
                    teamIndex = entity.teamIndex
                    isValidPlane = not bool(avatarInfo.get('defendSector')) and not isAirStrikeBomber(entity)
                    if teamIndex == self.__enemyTeamIndex and isValidPlane:
                        sectorID = self.__gameMode.arenaTypeData.sectors.getSectorIdByPosition(entity.position)
                        if sectorID:
                            sector = self.__gameMode.sectors[sectorID]
                            if sector.teamIndex != self.__enemyTeamIndex:
                                self.__sectorCounters[sectorID] += 1
                                avatarsCounted += 1

            if avatarsCounted > 0:
                for sectorID, sectorCounters in self.__sectorCounters.iteritems():
                    alarmModel = self.__gameMode.arenaTypeData.sectors.getSector(sectorID).soundSettings.alarmModel
                    needCount = alarmModel.conditions
                    if needCount > 0:
                        curCount = sectorCounters
                        oldCount = self.__sectorCountersOld[sectorID]
                        if oldCount < needCount <= curCount:
                            self.__playVoice(alarmModel.enemyEvent)

        self.__restartOneSecTick()
        return

    def __restartOneSecTick(self):
        self.__TickSecCallback = None
        self.__TickSecCallback = BigWorld.callback(1.0, self.onTickOneSec)
        return

    def __isTeamate(self, teamIndex):
        return BigWorld.player().teamIndex == teamIndex

    def __isAllSectorsCaptured(self, teamIndex):
        for sector in self.__gameMode.sectors.values():
            if sector.isCapturable and sector.teamIndex != teamIndex:
                return False

        return True

    def __isCapturedLastSectorWithType(self, sector_type, sector_level):
        teamIndex = BigWorld.player().teamIndex
        sectors_count = 0
        for sector in self.__gameMode.sectors.values():
            if sector.settings.gameplayType == sector_type and sector.settings.gameplayLevel == sector_level:
                if sector.teamIndex != teamIndex:
                    return False
                sectors_count += 1

        if sectors_count > 1:
            return True
        else:
            return False

    def __isPlayerHelpCaptureSector(self, sector):
        return sector == BigWorld.player().currentSector