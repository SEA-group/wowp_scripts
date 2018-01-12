# Embedded file name: scripts/client/gui/Scaleform/GameOptions/loaders/GameSettingsLoader.py
from consts import MEASUREMENT_SYSTEMS
__author__ = 's_karchavets'
from Helpers.i18n import localizeOptions, localizeLobby
from gui.Scaleform.GameOptions.utils import BaseLoader, XMPP_CHAT_KEYS, GAME_SETTINGS_MAIN_UI_DATA, KeyValue
from gui.Scaleform.GameOptions.utils import GAME_SETTINGS_MAIN_DATA
from clientConsts import GUI_TYPES
import Settings
import db.DBLogic as DB
from adapters.IHangarSpacesAdapter import IHangarSpacesAdapter
import gui.WindowsManager
from consts import WAR_STATE

class GameSettingsLoader(BaseLoader):

    def load(self, src, pList, settings, forceLoad):
        src.measurementSystem.data = [ localizeOptions(''.join(['SETTINGS_COMMON_MEASUREMENT_', ms])) for ms in MEASUREMENT_SYSTEMS ]
        src.measurementSystem.index = settings.getGameUI()['measurementSystem']
        src.heightMode.index = settings.getGameUI()['heightMode']
        src.heightMode.data = [localizeOptions('battleui/schema_height_v1'), localizeOptions('battleui/schema_height_v2'), localizeOptions('SETTINGS_ALTIMETER_DROPDOWN_MENU_VARIANT_BOTH')]
        for fKey, sKey in GAME_SETTINGS_MAIN_UI_DATA.iteritems():
            setattr(src, fKey, settings.getGameUI()[sKey])

        for fKey, sKey in GAME_SETTINGS_MAIN_DATA.iteritems():
            setattr(src, fKey, getattr(settings, sKey))

        for flashKey, SettingsKey in XMPP_CHAT_KEYS.iteritems():
            setattr(src, flashKey, settings.getXmppChatSettings()[SettingsKey])

        for key in Settings.REPLAY_KEYS.iterkeys():
            setattr(src, key, settings.getReplaySettings()[key])

        src.pathSaveBattleReplays = settings.getReplaysDirectory()
        src.pathSaveScreenshots = settings.getScreenShotDirectory()
        import BWPersonality
        warAction = BWPersonality.gameParams.get('warAction', {})
        warActionEnabled = warAction.get('enabled', False)
        warActionState = warAction.get('state', WAR_STATE.UNDEFINED)
        src.radarSettings.radarState.data = [localizeOptions('SETTINGS_MARKERS_ZOOM_CLOSE'), localizeOptions('SETTINGS_MARKERS_ZOOM_MEDIUM'), localizeOptions('SETTINGS_MARKERS_ZOOM_FAR')]
        src.radarSettings.radarState.index = settings.getGameUI()['radarState']
        src.radarSettings.radarSize.data = [localizeOptions('SETTINGS_MARKERS_SMALL_SIZE'), localizeOptions('SETTINGS_MARKERS_MEDIUM_SIZE'), localizeOptions('SETTINGS_MARKERS_BIG_SIZE')]
        src.radarSettings.radarSize.index = settings.getGameUI()['radarSize']
        src.radarSettings.radarLockRotation.data = [localizeOptions('SETTINGS_ROTATE_RADAR-MINIMAP'), localizeOptions('SETTINGS_CHECKBOX_ROTATE_PLAYER_MINIMAP_FIXED')]
        src.radarSettings.radarLockRotation.index = settings.getGameUI()['radarLockRotation']
        src.radarSettings.showDefendersActive = settings.getGameUI()['showDefendersActive']
        src.attitudeIndicatorSettings.attitudeMode.data = [localizeOptions('SETTINGS_CHECKBOX_SHOW_ROLL_PLANE'), localizeOptions('SETTINGS_CHECKBOX_SHOW_ROLL_HORIZON')]
        src.attitudeIndicatorSettings.attitudeMode.index = settings.getGameUI()['attitudeMode']
        if warActionEnabled and warActionState not in [WAR_STATE.UNDEFINED, WAR_STATE.OFF, WAR_STATE.END]:
            return
        else:
            count = 0
            isEnableLobbyUI = gui.WindowsManager.g_windowsManager.getLobbyUI() is not None
            if isEnableLobbyUI:
                ad = IHangarSpacesAdapter('ICurrentHangarSpace')
                ob = ad(None, None)
                for i, spaceID in enumerate(ob['spaces']):
                    if DB.g_instance.userHangarSpaces.get(spaceID, None) is not None:
                        count += 1

            src.lobbySettings.isEnabled = (BWPersonality.g_initPlayerInfo.useGUIType == GUI_TYPES.PREMIUM or count > 1) and isEnableLobbyUI
            if src.lobbySettings.isEnabled:
                spaceData = DB.g_instance.userHangarSpaces.get(BWPersonality.g_settings.hangarSpaceSettings['spaceID'], None)
                src.lobbySettings.isEnabled = not spaceData.get('isModal', False)
            if src.lobbySettings.isEnabled:
                currentSpace = settings.getHangarSpaceSettings(BWPersonality.g_initPlayerInfo.databaseID)
                for i, spaceID in enumerate(ob['spaces']):
                    spaceData = DB.g_instance.userHangarSpaces.get(spaceID, None)
                    if spaceData is not None:
                        kv = KeyValue()
                        kv.key = spaceID
                        kv.label = localizeLobby(spaceData['loc'])
                        src.lobbySettings.previewImg.append(spaceData['img'])
                        src.lobbySettings.hangar.data.append(kv)
                        if spaceID == currentSpace['spaceID']:
                            src.lobbySettings.hangar.index = i

            self._isLoaded = True
            return