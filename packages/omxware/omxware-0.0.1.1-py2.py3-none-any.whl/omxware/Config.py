import sys

if sys.version_info[0] == (2):
    import ConfigParser
else:
    import configparser
import json, os


class Configuration:
    """OMXWware Configuration class"""
    _configFilename = "config.properties"
    _connectionSection = "connection"

    def __del__(self):
        """Destructor"""
        pass

    def getHostURL(self):
        """Return the Host URL"""
        return "https://omxware.sl.cloud9.ibm.com:9420"

