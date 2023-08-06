# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 17, 2013

@author: J. Akeret
'''


# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

class LocalFileSystem(object):
    '''
    Represents a configuration for a local file system
    '''
    
    name = None
    filePath = None

    def __init__(self, name, filePath):
        '''
        Constructor
        '''
        self.name = name
        self.filePath = filePath
        
        