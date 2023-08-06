'''
Created on Sep 23, 2013

@author: J. Akeret
'''

import os
import tempfile

from darkskysync.DarkSkySync import DarkSkySync
from darkskysync.DataSourceFactory import DataSourceFactory
from darkskysync.Exceptions import IllegalArgumentException

from mock import patch
from tests.ConfigHelper import ConfigHelper
from voluptuous import MultipleInvalid


class TestDarkSkySync(object):

    def setup(self):
        self.helper = ConfigHelper()
        self.config = self.helper.loadConfig()
        factory = DataSourceFactory(self.config)
        self.dataSourceConfig = factory.createDataSource("master")

    def test_dispatch_avail_ssh(self):

        with patch("darkskysync.SSHClientAdapter.SSHClient") as ssh_mock:

            dss = DarkSkySync(configFile=self.helper.createConfig(), verbose=True)

            def side_effect():
                return ([], [], [])

            ssh_mock.exec_command.return_value = ([], [], [])

            ssh_mock.exec_command.side_effect = side_effect
            # TODO fix
            # dss.avail(path=None)

    def test_dispatch_load_ssh(self):

        configFile = self.helper.createConfig()
        with patch("darkskysync.SSHClientAdapter.SSHClient") as ssh_mock:
            ssh_mock.return_value.open_sftp.return_value.stat.return_value = os.stat(".")
            with patch("os.path") as os_path_mock:  # avoid creating new  folders
                dss = DarkSkySync(configFile=configFile, verbose=True)
                os_path_mock.isdir.return_value = True
                fileList = dss.load(names=["test"])

        assert fileList is not None

    def test_dispatch_list_ssh(self, tmpdir):
        configFile = self.helper.createConfig()
        with patch("os.listdir") as os_mock:  # avoid creating new  folders
            with patch("os.path") as os_path_mock:  # avoid creating new  folders
                os_mock.listdir = []
                os_path_mock.exists.return_value = True
                os_path_mock.isdir.return_value = True
                os_path_mock.expanduser.return_value = tmpdir.strpath
                dss = DarkSkySync(configFile=configFile, verbose=True)

                fileList = dss.list()
                assert fileList is not None

                fileList = dss.list("test")
                assert fileList is not None

                fileList = dss.list(recursive=True)
                assert fileList is not None

    def test_set_default_config(self):
        confPath = tempfile.mkdtemp()
        defaultConfigFile = os.path.join(confPath, "config")
        DataSourceFactory.DEFAULT_CONFIGURATION_FILE = defaultConfigFile
        try:
            DarkSkySync(configFile=None, verbose=True)
        except MultipleInvalid:
            pass  # we do not care if the config is not valid just if it has been created

        assert os.path.exists(defaultConfigFile)

    def test_remove(self):
        dss = DarkSkySync(configFile=self.helper.createConfig(), verbose=True)
        dss.dataSourceConfig = self.dataSourceConfig
        cachePath = tempfile.mkdtemp()
        dss.dataSourceConfig.local.filePath = cachePath

        try:
            dss.remove()
            assert False
        except IllegalArgumentException:
            assert True

        def createFiles():
            files = []
            file1 = os.path.join(cachePath, "file1")
            open(file1, 'a').close()
            files.append(file1)
            dir1 = os.path.join(cachePath, "dir1")
            os.mkdir(dir1)
            files.append(dir1)
            file11 = os.path.join(dir1, "file11")
            open(file11, 'a').close()
            files.append(file11)
            return files

        files = createFiles()
        cacheContent = os.listdir(cachePath)
        assert cacheContent is not None
        assert len(cacheContent) == 2

        dss.remove(files[2])
        dss.remove(files[1])
        dss.remove(files[0])
        cacheContent = os.listdir(cachePath)
        assert cacheContent is not None
        assert len(cacheContent) == 0

        files = createFiles()
        dss.remove(allFiles=True)
        cacheContent = os.listdir(cachePath)
        assert cacheContent is not None
        assert len(cacheContent) == 0


if __name__ == '__main__':
    testConfigReader = TestDarkSkySync()
    testConfigReader.setup()
    testConfigReader.test_dispatch_load_ssh()
