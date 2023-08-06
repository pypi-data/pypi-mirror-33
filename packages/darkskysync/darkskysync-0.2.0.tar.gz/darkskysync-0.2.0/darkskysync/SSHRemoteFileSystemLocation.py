# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 17, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

class SSHRemoteFileSystemLocation(object):
    '''
    Represents the configuration for the remote file system informations
    '''

    def __init__(self, name, type, host, port, filePath, login):
        '''
        Constructor
        '''
        self.name = name
        self.type = type
        self.host = host
        self.port = port
        self.filePath = filePath
        self.login = login
        