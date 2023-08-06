'''
Created on Sep 17, 2013

@author: J. Akeret
'''
from mock import patch
from tests.ConfigHelper import ConfigHelper

from darkskysync.DataSourceFactory import DataSourceFactory
from darkskysync.RsyncWrapper import RsyncWrapper

class TestRsyncWrapper(object):
    '''
    classdocs
    '''
    remoteFS = None
    localFS = None
    dataSource = None

    def setup(self):
        self.helper = ConfigHelper()
        configFile = self.helper.createConfig()
#         configFile = os.path.join(os.path.dirname(__file__), "test.config")
#         print configFile
        dsFactory = DataSourceFactory.fromConfig(configFile)
        self.dataSourceConfig = dsFactory.createDataSource("master")

        self.dataSource = RsyncWrapper(self.dataSourceConfig)

    def test_prepareRsyncCommands(self):
        cmds = self.dataSource.prepareRsyncCommands(None)
        assert cmds is not None
        assert len(cmds) == 0

        cmds = self.dataSource.prepareRsyncCommands("wmap*")
        assert cmds is not None
        assert len(cmds) == 1

        cmds = self.dataSource.prepareRsyncCommands(["wmap*"])
        assert cmds is not None
        assert len(cmds) == 1

        cmds = self.dataSource.prepareRsyncCommands(["wmap1", "wmap1"])
        assert cmds is not None
        assert len(cmds) == 2

    def test_loadFiles(self):
        with patch("subprocess.Popen") as Popen_mock:
            fileList = self.dataSource.loadFiles(None)
            assert fileList is not None
            assert len(fileList) == 0

            self.dataSource.dry_run = True
            fileList = self.dataSource.loadFiles("A611")
            assert fileList is not None
            assert len(fileList) == 1

            fileList = self.dataSource.loadFiles(["A611", "A611"])
            assert fileList is not None
            assert len(fileList) == 2

if __name__ == '__main__':
    test = TestRsyncWrapper()
    test.setup()
    test.test_loadFiles()
