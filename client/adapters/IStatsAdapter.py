# Embedded file name: scripts/client/adapters/IStatsAdapter.py
from locale import getpreferredencoding
from time import localtime, strftime
import Settings
import db.DBLogic
from HelperFunctions import wowpRound
from Helpers.i18n import localizeAchievements, getFormattedTime, localizeAirplaneLong, localizeTimeIntervalHM, localizeTimeIntervalMS, localizeTooltips, separateThousandths
from adapters.DefaultAdapter import DefaultAdapter
from consts import PLANE_TYPE, PLANE_TYPE_NAME
NATION_FLAG_TEMPLATE = 'icons/shop/flagAchiev{0}.dds'

class IPlaneStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        stats = ob['stats']
        lastGameTime = stats['lastGameTime']
        ob['lastGameTime'] = getFormattedTime(lastGameTime, Settings.g_instance.scriptConfig.timeFormated['dmYHM']) if lastGameTime > 0 else ''
        ob['row'] = stats
        ob['stats'] = _convertPlaneStats(stats)
        return ob


class ISummaryStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        stats = ob['stats']
        lastGameTime = stats['lastGameTime']
        ob['lastGameTime'] = getFormattedTime(lastGameTime, Settings.g_instance.scriptConfig.timeFormated['dmYHM']) if lastGameTime > 0 else ''
        ob['flighttime'] = stats['flighttime']
        ob['flighttimeStr'] = localizeTimeIntervalHM(stats['flighttime'])
        ob['createdAt'] = strftime(Settings.g_instance.scriptConfig.timeFormated['dmYHM'], localtime(float(ob['stats']['createdAt']))).decode(getpreferredencoding())
        ob['stats'] = _convertSummeryStats(stats)
        return ob


class IShortPlaneStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(IShortPlaneStatsAdapter, self).__call__(account, ob, **kw)
        ob['flighttimeStr'] = localizeTimeIntervalHM(ob['flighttime'])
        return ob


class IShortPlaneDescription(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(IShortPlaneDescription, self).__call__(account, ob, **kw)
        planeID = kw['idTypeList'][0][0]
        planeData = db.DBLogic.g_instance.getAircraftData(planeID).airplane
        ob['planeName'] = localizeAirplaneLong(planeData.name)
        ob['level'] = planeData.level
        ob['icoPath'] = planeData.iconPath
        ob['flagPath'] = NATION_FLAG_TEMPLATE.format(planeData.country)
        ob['nationID'] = db.DBLogic.g_instance.getNationIDbyAircraftID(planeID)
        ob['planeID'] = planeID
        return ob


class IPlayerSummaryStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        stats = ob['stats']
        lastGameTime = stats['lastGameTime']
        ob['lastGameTime'] = getFormattedTime(lastGameTime, Settings.g_instance.scriptConfig.timeFormated['dmYHM']) if lastGameTime > 0 else ''
        ob['flighttime'] = stats['flighttime']
        ob['flighttimeStr'] = localizeTimeIntervalHM(stats['flighttime'])
        ob['createdAt'] = strftime(Settings.g_instance.scriptConfig.timeFormated['dmYHM'], localtime(float(stats['createdAt']))).decode(getpreferredencoding()) if stats['createdAt'] > 0 else ''
        ob['stats'] = _convertSummeryStats(stats)
        return ob


class IPlayerShortPlaneStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(IPlayerShortPlaneStatsAdapter, self).__call__(account, ob, **kw)
        ob['flighttimeStr'] = localizeTimeIntervalHM(ob['flighttime'])
        return ob


class IPlayerShortPlaneDescriptionAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        ob = super(IPlayerShortPlaneDescriptionAdapter, self).__call__(account, ob, **kw)
        import db.DBLogic
        planeData = db.DBLogic.g_instance.getAircraftData(kw['idTypeList'][1][0]).airplane
        ob['planeName'] = localizeAirplaneLong(planeData.name)
        ob['level'] = planeData.level
        ob['icoPath'] = planeData.iconPath
        ob['flagPath'] = NATION_FLAG_TEMPLATE.format(planeData.country)
        ob['nationID'] = db.DBLogic.g_instance.getNationIDbyAircraftID(kw['idTypeList'][1][0])
        ob['planeID'] = kw['idTypeList'][1][0]
        return ob


class IPlayerPlaneStatsAdapter(DefaultAdapter):

    def __call__(self, account, ob, **kw):
        stats = ob['stats']
        lastGameTime = stats['lastGameTime']
        ob['lastGameTime'] = getFormattedTime(lastGameTime, Settings.g_instance.scriptConfig.timeFormated['dmYHM']) if lastGameTime > 0 else ''
        ob['stats'] = _convertPlaneStats(stats)
        return ob


def _percent(total, partial, precision = 0):
    if total > 0:
        return wowpRound(partial * 100.0 / total, precision)
    return 0


def _statRecord(name = None, value = None, percentValue = None, title = None, tooltip = None):
    return dict(name=localizeAchievements(name), value=separateThousandths(value) if isinstance(value, int) else value, percentValue=percentValue, title=localizeAchievements(title) if title else None, tooltip=localizeTooltips(tooltip) if tooltip else None)


def ftostr(val):
    return format(val, '.2f')


def _convertCommonStats(stats):
    return [_statRecord(None, None, None, 'ACHIEVEMENTS_BETTLE_EFFICIENCY'),
     _statRecord('ACHIEVEMENTS_AIRCRAFTS_DESTROYED_2-0', stats['pKill']),
     _statRecord('ACHIEVEMENTS_WINS_IN_GROUP_2-0', stats['pAssist']),
     _statRecord('ACHIEVEMENTS_DEFENDER-BOMBER_DESTROYED', stats['dKill'] + stats['bKill']),
     _statRecord('ACHIEVEMENTS_DEFENDER-BOMBER_DESTROYED_ASSISTS', stats['dAssist'] + stats['bAssist']),
     _statRecord('ACHIEVEMENTS_AIR_TARGETS_DESTROYED_AVERAGE_PER_FLIGHT', int(round((stats['pKill'] + stats['dKill'] + stats['bKill']) / float(stats['flights']) if stats['flights'] else 0))),
     _statRecord('ACHIEVEMENTS_GROUND_OBJECTS_DESTROYED', stats['gKill']),
     _statRecord('ACHIEVEMENTS_GROUND_OBJECTS_DESTROYED_ASSIST', stats['gAssist']),
     _statRecord('ACHIEVEMENTS_GROUND_OBJECTS_DESTROYED_AVERAGE_PER_FLIGHT', int(round(stats['gKill'] / float(stats['flights']) if stats['flights'] else 0))),
     _statRecord('ACHIEVEMENTS_PARTICIPATION_IN_CAP_SECTOR', stats['zoneCapture']),
     _statRecord('ACHIEVEMENTS_AIRCRAFTS_DESTROED_IN_DEF_SECTOR', stats['pKillDefZone']),
     _statRecord(None, None, None, 'ACHIEVEMENTS_HEROIC_DEEDS'),
     _statRecord('ACHIEVEMENTS_MAX_AIRCRAFTS_DESTROED_PER_BATTLE', stats['pKillMax']),
     _statRecord('ACHIEVEMENTS_MAX_DEFENDER-BOMBER_DESTROED_PER_BATTLE', stats['dbKillMax']),
     _statRecord('ACHIEVEMENTS_MAX_GROUND_OBJECT_DESTROED_PER_BATTLE', stats['gKillMax']),
     _statRecord('ACHIEVEMENTS_MAX_DAMAGE_AIR_TARGETS_PER_BATTLE', int(round(stats['atDamageMax']))),
     _statRecord('ACHIEVEMENTS_MAX_DAMAGE_AIRCRAFT_PER_BATTLE', int(round(stats['pDamageMax']))),
     _statRecord('ACHIEVEMENTS_MAX_DAMAGE_DEFENDER-BOMBER_PER_BATTLE', int(round(stats['dbDamageMax']))),
     _statRecord('ACHIEVEMENTS_MAX_DAMAGE_GROUND_OBJECT_PER_BATTLE', int(round(stats['gDamageMax']))),
     _statRecord('ACHIEVEMENTS_MAX_AIRCRAFT_DESTROED_IN_DEF_SECTOR', stats['pKillDefZoneMax'])]


def _convertSummeryStats(stats):
    records = [_statRecord('ACHIEVEMENTS_TOTAL_BATTLES', stats['battles']),
     _statRecord('ACHIEVEMENTS_WINS', stats['wins'], _percent(stats['battles'], stats['wins'], 2)),
     _statRecord('ACHIEVEMENTS_DEFEATS', stats['losses'], _percent(stats['battles'], stats['losses'], 2)),
     _statRecord('ACHIEVEMENTS_DRAWS', stats['draws'], _percent(stats['battles'], stats['draws'], 2)),
     _statRecord('ACHIEVEMENTS_STAT_IN_NEW_MODE_CONQUEST', localizeTimeIntervalHM(stats['flighttime']))]
    records.extend(_convertCommonStats(stats))
    records.append(_statRecord(None, None, None, 'ACHIEVEMENTS_XP_AND_BATTLESCORE'))
    records.append(_statRecord('ACHIEVEMENTS_AVG_XP_PER_BATTLE', int(stats['baseXPAvg'])))
    records.append(_statRecord('ACHIEVEMENTS_MAX_XP_FOR_BATTLE', stats['baseXPMax']))
    records.append(_statRecord('ACHIEVEMENTS_AVERAGE_BATTLE_POINTS_PER_BATTLE', int(stats['bScoreAvg'])))
    records.append(_statRecord('ACHIEVEMENTS_MAX_BATTLE_POINTS_PER_BATTLE', stats['bScoreMax']))
    idx = 16
    coeff = 20

    def _addEfficiency(plType):
        flights = stats['flightsByPlType'].get(plType, 0)
        return _statRecord('ACHIEVEMENTS_CLASS_EFFICIENCY_%s' % PLANE_TYPE.toStr(plType), '{}%'.format(round(stats['ranksByPlType'].get(plType, 0) / float(flights) * coeff, 1) if flights else 0.0))

    records.insert(idx, _addEfficiency(PLANE_TYPE.BOMBER))
    records.insert(idx, _addEfficiency(PLANE_TYPE.ASSAULT))
    records.insert(idx, _addEfficiency(PLANE_TYPE.HFIGHTER))
    records.insert(idx, _addEfficiency(PLANE_TYPE.NAVY))
    records.insert(idx, _addEfficiency(PLANE_TYPE.FIGHTER))
    records.insert(idx, _statRecord(None, None, None, 'ACHIEVEMENTS_CLASS_EFFICIENCY'))
    return records


def _convertPlaneStats(stats):
    records = [_statRecord('ACHIEVEMENTS_TOTAL_BATTLES', stats['battles']),
     _statRecord('ACHIEVEMENTS_TOTAL_FLIGHT', stats['flights']),
     _statRecord('ACHIEVEMENTS_AVERAGE_DURATION_FLIGHT', localizeTimeIntervalMS(stats['flighttimeAvg'])),
     _statRecord('ACHIEVEMENTS_ALL_DURATION_ON_PLANES', localizeTimeIntervalHM(stats['flighttime']))]
    records.extend(_convertCommonStats(stats))
    records.append(_statRecord(None, None, None, 'ACHIEVEMENTS_XP_AND_BATTLESCORE'))
    records.append(_statRecord('ACHIEVEMENTS_AVERAGE_EXP_PER_FLIGHT', int(stats['baseXPAvg'])))
    records.append(_statRecord('ACHIEVEMENTS_MAX_XP_FOR_BATTLE', stats['baseXPMax']))
    records.append(_statRecord('ACHIEVEMENTS_AVERAGE_BATTLE_POINTS_PER_FLIGHT', int(stats['bScoreAvg'])))
    records.append(_statRecord('ACHIEVEMENTS_MAX_BATTLE_POINTS_PER_BATTLE', stats['bScoreMax']))
    return records