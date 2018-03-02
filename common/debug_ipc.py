# Embedded file name: scripts/common/debug_ipc.py
import cProfile
import os
import sys
import time
from datetime import datetime
import BigWorld
from BWLogging import getLogger
logger = getLogger(__name__)
profiler = None

def initDebug(configSection):
    global profiler
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
                logger.warn('removing already installed reactor: %s' % sys.modules['twisted.internet.reactor'])
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
                logger.error("Can't load ipc peer: %s" % e)
            else:
                peer.init(BigWorld.component, **peerData)

        if configSection.readBool('tickProfile'):
            profiler = Profiler('~/profiles')
            profiler.start(0.1)
        return


class Profiler(object):

    def __init__(self, location):
        self.location = os.path.expanduser(location)
        self.max_overtick_times = 10
        self.active = False
        self.profile = None
        self.last_time = None
        self.interval = None
        if not os.path.exists(self.location):
            os.mkdir(self.location)
        return

    def start(self, interval):
        self.active = True
        self.interval = interval
        logger.info('overtick profiling enabled with %s s. inverval', interval)
        BigWorld.addTimer(self.tick_took, self.interval)

    def stop(self):
        self.active = False
        logger.info('overtick profiling disabled')

    def tick_took(self, *_):
        if self.profile:
            took = time.time() - self.last_time
            self.profile.disable()
            if took > self.interval * self.max_overtick_times:
                now = datetime.now().isoformat()
                pfile = os.path.join(self.location, '%s_%s_%.1f_seconds.pstats' % (BigWorld.component, now, took))
                self.profile.dump_stats(pfile)
                logger.warn('overtick detected! last tick took %s seconds. pstats file saved to: %s', took, pfile)
            self.profile = None
        if self.active:
            self.profile = cProfile.Profile()
            self.profile.enable()
            self.last_time = time.time()
            BigWorld.addTimer(self.tick_took, self.interval)
        return