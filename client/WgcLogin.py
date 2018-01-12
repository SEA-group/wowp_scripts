# Embedded file name: scripts/client/WgcLogin.py
import config_consts
from config_consts import IS_DEVELOPMENT
import consts
from clientConsts import CLIENT_INACTIVITY_TIMEOUT
import BigWorld
from Event import Event
from Singleton import singleton
from enumerations import Enumeration
from debug_utils import LOG_UNEXPECTED, LOG_MX, LOG_DEBUG, LOG_INFO
from predefined_hosts import g_preDefinedHosts
from ConnectionManager import connectionManager
from gui.Scaleform.EULA import EULAInterface
import datetime
import Settings
import hashlib
import json
import ClientLog
autorization_mehtod = ''

def try_to_connect_with_token2():
    global autorization_mehtod
    LOG_DEBUG('try_to_connect_with_token2')
    token2 = BigWorld.getToken2fromWGCApi()
    if len(token2):
        url = g_preDefinedHosts.first().url
        autorization_mehtod = 'token2'
        connectionManager.connectionStatusCallbacks += handleConnectionStatusAll
        connectionManager.connect_with_token2(url, token2)
    else:
        try_to_connect_with_token1()


def try_to_connect_with_token1():
    global autorization_mehtod
    LOG_DEBUG('try_to_connect_with_token1')
    token = BigWorld.getToken1fromWGCApi()
    if token is not None:
        url = g_preDefinedHosts.first().url
        autorization_mehtod = 'token1'
        connectionManager.connectionStatusCallbacks += handleConnectionStatusAll
        connectionManager.connect_with_token1(url, token['token1'], str(token['spa_id']))
    else:
        show_login_screen()
    return


def show_login_screen():
    LOG_DEBUG('show_login_screen')
    BigWorld.storeToken2toWGCApi('')
    connectionManager.connectionStatusCallbacks -= handleConnectionStatusAll
    from gui.WindowsManager import g_windowsManager
    g_windowsManager.showLogin()


def handleConnectionStatusAll(stage, status, message, isAutoRegister):
    LOG_DEBUG('handleConnectionStatusAll', message)
    connectionManager.connectionStatusCallbacks -= handleConnectionStatusAll
    if stage == 1:
        if status == 'LOGGED_ON':
            try:
                if autorization_mehtod == 'token2':
                    LOG_DEBUG('handleWGCtoken2LogOnSuccess', message)
                else:
                    LOG_DEBUG('handleWGCLogOnSuccess', message)
                msg_dict = json.loads(message)
                if not isinstance(msg_dict, dict):
                    raise Exception, ''
            except Exception:
                if autorization_mehtod == 'token2':
                    BigWorld.callback(0.1, try_to_connect_with_token1)
                else:
                    show_login_screen()
                return

            connectionManager.loginPriority = msg_dict.get('login_priority', 0)
            token2 = str(msg_dict.get('token2', ''))
            BigWorld.storeToken2toWGCApi(token2)
            return
        BigWorld.storeToken2toWGCApi('')
        if autorization_mehtod == 'token2':
            BigWorld.callback(0.1, try_to_connect_with_token1)
        else:
            show_login_screen()


def try_to_login_with_wgc_api():
    LOG_DEBUG('try_to_login_with_wgc_api')
    eula = EULAInterface()
    if eula.needShowLicense():
        LOG_DEBUG('eula.needShowLicense() - wgc_login skipped')
        return False
    g_preDefinedHosts.readScriptConfig(Settings.g_instance.scriptConfig.scriptData)
    connectionManager.connectionStatusCallbacks += handleConnectionStatusAll
    if len(g_preDefinedHosts._hosts):
        try_to_connect_with_token2()
        return True
    connectionManager.connectionStatusCallbacks -= handleConnectionStatusAll
    return False