'''
Created on Sep 23, 2013

@author: J. Akeret
'''

from tests.ConfigHelper import ConfigHelper


class TestConfigReader(object):

    config = None

    def setup(self):
        helper = ConfigHelper()
        self.config = helper.loadConfig()

    def test_readConfig(self):
        assert self.config is not None

        assert "master" in self.config

        assert "default" in self.config["master"]["datasource"]["local"]
        assert "darksky" in self.config["master"]["datasource"]["remote"]
        assert "darksky" in self.config["master"]["remote"]["login"]


if __name__ == '__main__':
    testConfigReader = TestConfigReader()
    testConfigReader.setup()
    testConfigReader.test_readConfig()
