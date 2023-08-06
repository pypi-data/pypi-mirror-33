# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 24, 2013

@author: J. Akeret
'''


# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

class SSHWrapper(object):
    '''
    Wrapps the ssh unix command
    
    :param dataSourcConfig: configuration of the data source
    :param sshExec: name of the ssh command to use. Default is 'ssh'
    '''
    LIST_CMD = "ls"

    def __init__(self, dataSourceConfig, sshExec="ssh"):
        '''
        Constructor
        '''
        self.dataSourceConfig = dataSourceConfig
        self.remoteFileSystem = self.dataSourceConfig.remote
        self.sshExec = sshExec
        
    def prepareSshFileCmds(self):
        """
        Prepares the commands for the file transfer
        """
        sshCmd, sshDestCmd = self.prepareSshCmds()
        
        sshFileCmd = "%s:%s" % (sshDestCmd, self.remoteFileSystem.filePath)
        return sshCmd, sshFileCmd
        
    def prepareSshCmds(self):
        """
        Prepares the ssh command in order to use the configured known hosts and private key files
        """
        
        sshCmd = "ssh -o UserKnownHostsFile='%s'BatchMode=yes -i '%s'" % (self.remoteFileSystem.login.known_hosts, 
                                                                          self.remoteFileSystem.login.user_key_private)
        
        sshDestCmd = "%s@%s" % (self.remoteFileSystem.login.username, self.remoteFileSystem.host)
        
        return sshCmd, sshDestCmd