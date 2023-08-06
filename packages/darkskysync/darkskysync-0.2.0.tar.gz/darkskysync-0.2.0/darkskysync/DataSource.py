# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 23, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals


class DataSource(object):
    '''
    Represents a configuration of a data source
    '''


    def __init__(self, name, local, remote):
        '''
        Constructor
        '''
        self.name = name
        self.local = local
        self.remote = remote