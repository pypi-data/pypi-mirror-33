# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 17, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

class SshLoginInfo(object):
    '''
    Represents the configuration for the remote login informations
    '''
    name = None
    username = None
    user_key_private = None
    known_hosts = None



    def __init__(self, name, username, user_key_private="~/.ssh/id_rsa", known_hosts="~/.ssh/known_hosts"):
        '''
        Constructor
        '''
        self.name = name
        self.username = username
        self.user_key_private = user_key_private
        self.known_hosts = known_hosts
        