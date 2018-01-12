# Embedded file name: scripts/common/debug_ipc.py
import os
import sys
import BigWorld
from debug_utils import LOG_WARNING, LOG_ERROR

def initDebug(configSection):
    if not configSection:
        return
    else:
        import importlib
        import db.DBLogic
        import ResMgr
        if configSection.readBool('dbCache'):
            db.DBLogic.CACHED_DB_FILE = ResMgr.resolveToAbsolutePath(db.DBLogic.CACHED_DB_FILE)
            db.DBLogic.initDB(loadFromCache=True)
            if BigWorld.component == 'service' and not os.path.exists(db.DBLogic.CACHED_DB_FILE):
                db.DBLogic.tryPicleDB(db.DBLogic.g_instance)
        if configSection['pythonpath']:
            for name, pathSection in configSection['pythonpath'].items():
                path = pathSection.asString
                if path in sys.path:
                    sys.path.remove(path)
                if name == 'insert':
                    sys.path.insert(0, path)
                else:
                    sys.path.append(path)

        if BigWorld.component == 'service':
            return
        if configSection['bwreactor'] is not None or configSection['ipc']:
            if 'twisted.internet.reactor' in sys.modules:
                LOG_WARNING('removing already installed reactor: %s' % sys.modules['twisted.internet.reactor'])
                del sys.modules['twisted.internet.reactor']
            from testcore import bwreactor
            bwreactor.install()
        if configSection['ipc']:
            try:
                from testcore.ipc import peers
                peerData = {k:v.asString for k, v in configSection['ipc'].items()}
                peerName = peerData.pop('peer')
                peer = importlib.import_module('.' + peerName, 'testcore.ipc.peers')
            except (ImportError, AttributeError) as e:
                LOG_ERROR("Can't load ipc peer: %s" % e)
            else:
                peer.init(BigWorld.component, **peerData)

        return