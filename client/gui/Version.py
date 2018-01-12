# Embedded file name: scripts/client/gui/Version.py
from Singleton import singleton
from debug_utils import LOG_INFO
import BigWorld

@singleton

class Version(object):

    def __init__(self):
        self.__version = '{} {}.{}'.format(BigWorld.getProductName(), BigWorld.getVersion(), BigWorld.getRevision())
        LOG_INFO('Version::Version()', self.__version)

    def getVersion(self):
        return self.__version