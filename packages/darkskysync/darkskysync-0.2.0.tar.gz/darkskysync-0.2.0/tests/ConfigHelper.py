'''
Created on Sep 23, 2013

@author: J. Akeret
'''
import os
import tempfile

from darkskysync.DataSourceFactory import ConfigReader


class ConfigHelper(object):

    SSH_CONFIG = """
            [local/default]
            path = %s

            [remote/darksky]
            type = ssh
            host = darksky.ethz.ch
            port = 22
            path = /data/darksky/...
            login = darksky

            [login/darksky]
            name = username
            user_key_private = %s
            user_key_public = %s
            known_hosts = %s

            [datasource/master]
            local = default
            remote = darksky
        """

    @staticmethod
    def createConfig():
        tempPath = tempfile.mkdtemp()

        idRsaFile = os.path.join(tempPath, "id_rsa")
        os.mkdir(idRsaFile)
        idRsaPubFile = os.path.join(tempPath, "id_rsa.pub")
        os.mkdir(idRsaPubFile)
        idKnownHostsFile = os.path.join(tempPath, "known_hosts")
        os.mkdir(idKnownHostsFile)

        conf = ConfigHelper.SSH_CONFIG % (
            tempPath, idRsaFile, idRsaPubFile, idKnownHostsFile)

        (conf_file, conf_path) = tempfile.mkstemp()
        conf_file = os.fdopen(conf_file, 'w+')
        conf_file.write(conf)
        conf_file.close()
        return conf_path

    def loadConfig(self):
        conf_path = self.createConfig()

        result = None
        try:
            config_reader = ConfigReader(conf_path)
            result = config_reader.read_config()
        except:
            raise
        finally:
            os.unlink(conf_path)

        return result
