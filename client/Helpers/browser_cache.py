# Embedded file name: scripts/client/Helpers/browser_cache.py
import os
import sys
from shutil import rmtree
from debug_utils import LOG_ERROR, LOG_DEBUG
CACHE_PATH = None
CLEAR_CACHE_TAG = 'clear-cache'
CLEAR_CACHE_DONE = False

def init(cachePath):
    global CACHE_PATH
    global CLEAR_CACHE_DONE
    CACHE_PATH = cachePath
    if CLEAR_CACHE_TAG in sys.argv and not CLEAR_CACHE_DONE:
        LOG_DEBUG('Delete browser cache from command line option... path: %s' % CACHE_PATH)
        deleteCache()
        CLEAR_CACHE_DONE = True
        LOG_DEBUG('Done')


def deleteCache():
    if os.path.exists(CACHE_PATH):
        _rmFiles()
        LOG_DEBUG('browser cache invalidated. path: %s' % CACHE_PATH)


def _rmFiles(retries = 10):
    for ret in xrange(retries):
        try:
            rmtree(CACHE_PATH)
            break
        except WindowsError:
            time.sleep(1)
            LOG_ERROR("Can't delete cache {}, retry: {}".format(CACHE_PATH, ret))