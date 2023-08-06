# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 23, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

from darkskysync.SSHRemoteFileSystemLocation import \
    SSHRemoteFileSystemLocation
from darkskysync.SshLoginInfo import SshLoginInfo


# stdlib imports
from abc import ABCMeta, abstractmethod


class AbstractRemoteLocationFactory:
    """
    Defines the contract for a remote location factory to proper function
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self, name, conf):
        """
        Creates a new instance with the given properties 
        """
        pass

class SSHRemoteLocationFactory(AbstractRemoteLocationFactory):
    
    def __init__(self):
        pass
    
    def create(self, name, conf):
        remoteConf = conf["remote"]
        return SSHRemoteFileSystemLocation(name, 
                                           remoteConf["type"],
                                           remoteConf["host"],
                                           remoteConf["port"],
                                           remoteConf["path"],
                                           self.createLogin(remoteConf["login"], conf["login"]))
    def createLogin(self, name, conf):
        return SshLoginInfo(name, 
                            conf["name"], 
                            conf["user_key_private"], 
                            conf["known_hosts"])

