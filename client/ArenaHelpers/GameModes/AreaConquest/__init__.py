# Embedded file name: scripts/client/ArenaHelpers/GameModes/AreaConquest/__init__.py


class AC_EVENTS:
    """Area conquest client events enum
    """
    GLOBAL_SCORE_UPDATED = 'global_score_updated'
    SECTOR_STATE_CHANGED = 'sector_state_changed'
    GAME_MODE_TICK = 'game_tick'
    PLAYER_SCORE_UPDATED = 'player_score_updated'
    GUN_DANGER_ON = 'gun_danger_on'
    GUN_DANGER_OFF = 'gun_danger_off'
    SPAWN_TIME_UPDATE = 'spawn_time_update'
    SPAWN_TIME_OFF = 'spawn_time_off'
    BATTLE_TIME_UPDATE = 'battle_time_update'
    TIME_TO_BATTLE = 'time_to_battle'
    TIME_TO_BATTLE_OFF = 'time_to_battle_off'
    GAME_BREAKER_UPDATE = 'game_breaker'
    GAME_BREAKER_UPDATE_OFF = 'game_breaker_off'
    SELECT_SECTOR = 'select_sector'
    BATTLE_EVENT = 'battle_event'
    SECTOR_CAPTURE_POINTS_CHANGED = 'sector_capture_points_changed'
    SECTOR_ACTION = 'sector_action'
    GLOBAL_COUNTERS_UPDATED = 'global_counters_updated'
    DYNAMIC_TIMER_UPDATE = 'dynamic_timer_update'
    SECTOR_PERMANENT_LOCK = 'sector_permanent_lock'
    RESOURCE_POINTS_UPDATED = 'resource_points_updated'
    AVATAR_CHANGE_RESOURCE_POINTS = 'avatar_change_resource_points'
    ROCKET_V2_LAUNCHED = 'rocket_v2_launched'
    ROCKET_V2_EFFECT_STARTED = 'ROCKET_V2_EFFECT_STARTED '
    ROCKET_V2_TARGET_SECTOR_CHANGED = 'rocket_v2_target_sector_changed'
    ROCKET_V2_EFFECT_ENDED = 'ROCKET_V2_EFFECT_ENDED'
    ROCKET_V2_HIT_TARGET = 'rocket_v2_hit_target'
    ROCKET_V2_TARGET_OBJECT_CHANGED = 'rocket_v2_target_object_changed'
    BOMBERS_LAUNCHED = 'bombers_launched'
    BOMBERS_DIED = 'bombers_died'
    BOMBER_IN_WAVE_DIED = 'bomber_in_wave_died'
    BOMBERS_ATTACK_STARTED = 'bombers_attack_started'
    BOMBERS_ATTACK_NOTIFIED = 'bombers_attack_notified'
    BOMBERS_BOMBS_DROPPED = 'bombers_bombs_dropped'
    BOMBER_ATTACK_NOTIFIED = 'bomber_attack_notified'
    BOMBER_BOMBS_DROPPED = 'bomber_bombs_dropped'
    BOMBER_DISPATCHER_TARGET_SECTOR_CHANGED = 'bomber_dispatcher_target_sector_changed'