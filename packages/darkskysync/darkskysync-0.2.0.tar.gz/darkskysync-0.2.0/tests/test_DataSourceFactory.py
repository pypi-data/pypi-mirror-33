'''
Created on Sep 23, 2013

@author: J. Akeret
'''
from tests.ConfigHelper import ConfigHelper
from darkskysync.DataSourceFactory import DataSourceFactory


class TestDataSourceFactory(object):
    '''
    classdocs
    '''

    config = None

    def setup(self):
        helper = ConfigHelper()
        self.config = helper.loadConfig()

    def test_createDataSource(self):
        '''
        Valid configuration
        '''
        factory = DataSourceFactory(self.config)
        factory.createDataSource("master")


if __name__ == '__main__':
    validator = TestDataSourceFactory()
    validator.setup()
    validator.test_createDataSource()
