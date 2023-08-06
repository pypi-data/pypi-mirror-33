'''
Created on Sep 23, 2013

@author: J. Akeret
'''

from tests.ConfigHelper import ConfigHelper
from darkskysync.DataSourceFactory import ConfigValidator


class TestConfigValidator(object):

    config = None

    def setup(self):
        helper = ConfigHelper()
        self.config = helper.loadConfig()

    def test_valid_config(self):
        '''
        Valid configuration
        '''
        validator = ConfigValidator(self.config)
        validator.validate()


if __name__ == '__main__':
    v = TestConfigValidator()
    v.setup()
    v.test_valid_config()
