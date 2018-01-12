# Embedded file name: scripts/client/gui/LocalizationHolder.py
from Helpers import i18n
from Singleton import singleton
from debug_utils import LOG_INFO
from gui.Scaleform import main_interfaces
LOC_DICT = {main_interfaces.GUI_SCREEN_LOGIN: ['menu',
                                    'lobby',
                                    'messages',
                                    'tooltips'],
 main_interfaces.GUI_SCREEN_LOBBY: ['lobby',
                                    'hud',
                                    'tooltips',
                                    'options',
                                    'messages',
                                    'chat',
                                    'achievements',
                                    'skills',
                                    'tutorial',
                                    'airplanes',
                                    'components',
                                    'battle_results',
                                    'maps',
                                    'common_hud_lobby'],
 main_interfaces.GUI_SCREEN_OPTIONS: ['options', 'tooltips'],
 main_interfaces.GUI_SCREEN_UI: ['hud',
                                 'options',
                                 'lobby',
                                 'tutorial',
                                 'battle_results',
                                 'messages',
                                 'keys',
                                 'tooltips',
                                 'skills',
                                 'maps',
                                 'achievements',
                                 'components',
                                 'common_hud_lobby'],
 main_interfaces.GUI_SCREEN_PREBATTLE: ['lobby',
                                        'hud',
                                        'tooltips',
                                        'options',
                                        'messages',
                                        'chat',
                                        'components',
                                        'common_hud_lobby'],
 main_interfaces.GUI_SCREEN_INTERVIEW: ['lobby']}

@singleton

class LocalizationHolder(object):

    def __init__(self):
        self.language = ''

    def fillLocalization(self, language, domain):
        LOG_INFO('___fillLocalization', language, domain)
        self.language = language
        d = i18n.getTranslationTable(domain, language)
        for key, value in d.items():
            self.localization.append(key)
            self.localization.append(value)

    def getLocalization(self, language, screenName):
        self.localization = []
        return self.localization