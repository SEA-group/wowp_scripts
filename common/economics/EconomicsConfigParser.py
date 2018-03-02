# Embedded file name: scripts/common/economics/EconomicsConfigParser.py
import ResMgr
from consts import GAME_MODE
import consts
from itertools import ifilter
from debug_utils import LOG_WARNING
ID_FIELD = 'id'
INDEX_FIELD = 'index'
TYPE_FIELD = 'type'
SUBTYPE_FIELD = 'subtype'
REWARD_FIELD = 'reward'
EXPERIENCE_FIELD = 'experience'
EXPERIENCE_FIELDID_INLEVEL = 1
COUNT_FIELDID_INLEVEL = 0
PREDICATES_FIELD = 'predicates'
PARAMS_FIELD = 'params'
TEXT_FIELD = 'text'
TITLE_FIELD = 'title'
ICON_FIELD = 'icon'
LEVELS_FIELD = 'levels'
GROUP_FIELD = 'group'
PROGRESS_STEP_FIELD = 'progressStep'
RESET_ON_DEATH_FIELD = 'resetOnDeath'
ONCEPERBATTLE_FIELD = 'once'
SUBJECT_FIELD = 'subject'
ACTION_FIELD = 'action'

class PROCESSOR_SUBTYPES:
    TEAM_ACTIONS = 'TeamActions'


GAMEMODE_TO_FILENAME_SUFFIX = {GAME_MODE.AREA_CONQUEST: '',
 GAME_MODE.OFFENSE_DEFENCE: '_od',
 GAME_MODE.ATTRITION_WARFARE: '_aw'}

def _addProcessor(config, dataSection, index):
    id = dataSection.readString(ID_FIELD)
    type = dataSection.readString(TYPE_FIELD)
    subtype = dataSection.readString(SUBTYPE_FIELD)
    text = dataSection.readString(TEXT_FIELD)
    group = dataSection.readString(GROUP_FIELD)
    params = {ID_FIELD: id,
     INDEX_FIELD: index,
     TEXT_FIELD: text,
     GROUP_FIELD: group,
     SUBTYPE_FIELD: subtype}
    reward = dataSection.readInt(REWARD_FIELD)
    if reward:
        params[REWARD_FIELD] = reward
    experience = dataSection.readInt(EXPERIENCE_FIELD)
    if experience:
        params[EXPERIENCE_FIELD] = experience
    predicates = _readPredicates(dataSection)
    if predicates:
        params[PREDICATES_FIELD] = predicates
    levels = _readLevels(dataSection)
    if levels:
        params[LEVELS_FIELD] = levels
        params[SUBJECT_FIELD] = dataSection.readString(SUBJECT_FIELD)
        params[ACTION_FIELD] = dataSection.readString(ACTION_FIELD)
        params[RESET_ON_DEATH_FIELD] = dataSection.readBool(RESET_ON_DEATH_FIELD)
    progressStep = dataSection.readInt(PROGRESS_STEP_FIELD)
    if progressStep:
        params[PROGRESS_STEP_FIELD] = progressStep
    caption = dataSection.readString(TITLE_FIELD)
    if caption:
        params[TITLE_FIELD] = caption
    icon = dataSection.readString(ICON_FIELD)
    if icon:
        params[ICON_FIELD] = icon
    oncePerBattle = dataSection.readString(ONCEPERBATTLE_FIELD)
    if oncePerBattle:
        params[ONCEPERBATTLE_FIELD] = oncePerBattle.lower() == 'true'
    conf = {TYPE_FIELD: type,
     PARAMS_FIELD: params}
    config.append(conf)


def _readPredicates(dataSection):
    predicatesSections = getChild(dataSection, PREDICATES_FIELD)
    if predicatesSections:
        predicates = {}
        for predId, predConf in predicatesSections.items():
            valVariant = predConf.asString
            valBool = valVariant.lower()
            if valBool in ('true', 'false'):
                predicates[predId] = valBool == 'true'
            else:
                predicates[predId] = valVariant

        return predicates
    else:
        return None
        return None


def _readLevels(dataSection):
    levelsSections = getChild(dataSection, LEVELS_FIELD)
    levels = []
    if levelsSections:
        for id, level in dataSection[LEVELS_FIELD].items():
            levels.append((level.readInt('count'), level.readInt('experience')))

        return levels
    else:
        return None
        return None


def getChild(ds, name):
    if name in ds.keys():
        child = (ds for nm, ds in ds.items() if nm == name).next()
        return child
    else:
        return None
        return None


def getConfig(gameModeEnum):
    _config = []
    xmlFile = consts.DB_PATH + 'config_econom' + GAMEMODE_TO_FILENAME_SUFFIX[gameModeEnum] + '.xml'
    data = ResMgr.openSection(xmlFile)
    indexesData = ResMgr.openSection(consts.ECONOM_INDEXES_PATH)
    eventProcessors = data.values()[0]
    for processor in eventProcessors.values():
        eventID = processor.readString(ID_FIELD)
        indexSection = next(ifilter(lambda x: x.readString(ID_FIELD).lower() == eventID.lower(), indexesData.values()), None)
        index = indexSection.readInt(INDEX_FIELD) if indexSection is not None else -1
        if index == -1:
            LOG_WARNING('Battle Economics: cannot to find index for the econom event, game_mode = {0}, event_id = {1}'.format(gameModeEnum, eventID))
        _addProcessor(_config, processor, index)

    return _config