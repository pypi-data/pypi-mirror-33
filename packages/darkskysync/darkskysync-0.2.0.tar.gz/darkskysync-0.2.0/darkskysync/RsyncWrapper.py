# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 17, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, \
    unicode_literals

from copy import copy
import os
import subprocess

import darkskysync
from darkskysync.AbstractRemoteSyncAdapter import AbstractRemoteSyncAdapter
from darkskysync.Exceptions import FileSystemError, ConnectionError
from darkskysync.SSHWrapper import SSHWrapper


class RsyncWrapper(AbstractRemoteSyncAdapter):
    
    '''
    Wrapper for the rsync unix command.
    
    :param dataSourceConfig: configuration of the data source
    :param rsync_exec: name of the rsync command to use. Default is 'rsync'
    :param dry_run: If true no files are downloaded
    :param force: If true the files in the local cache will be overwritten
    :param verbose: If true additional information will be printed
    
    '''
    
    FAILURE_KEYWORDS_EX_MAP = {"Permission denied": FileSystemError("Unable to write files. Reason: Permission denied"),
                               "Could not resolve hostname": ConnectionError("Name or service not known"),
                               "rsync error": ConnectionError("An unexpected error occured"),}

    def __init__(self, dataSourceConfig, rsync_exec="rsync", dry_run=False, force=False, verbose=True):
        '''
        Constructor
        '''
        self.dataSourceConfig = dataSourceConfig
        self.localFileSystem = self.dataSourceConfig.local
        self.remoteFileSystem = self.dataSourceConfig.remote
        self.rsync_exec = rsync_exec
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        
    def loadFiles(self, files):
        """
        Creates the rsync commands and executes them to download the files from the remote repository.
        :param files: A single file name or path or a list of file names
        
        :return: a list of downloaded files
        """
        
        if files is None:
            return []
        
        if isinstance(files, str):
            files = [files]
        
        self._prepareDestination(self.localFileSystem.filePath)
        
        cmds = self.prepareRsyncCommands(files)
        
        fileList = []
        pathPrefix = self.localFileSystem.filePath
        for file, cmd in zip(files, cmds):
            
            destFile = os.path.join(pathPrefix, os.path.dirname(file))
            
            if (not os.path.isdir(destFile) and not self.dry_run):
                os.makedirs(destFile)

            cmd = subprocess.list2cmdline(cmd)
            #cmd = " ".join(cmd)
            sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = sp.communicate()[0]
            
            if self.verbose:
                darkskysync.logger.info(output)

            self._checkResult(output)
            
            fileList.append(os.path.join(pathPrefix, file))
        
        return fileList
    
    def prepareRsyncCommands(self, files):
        """
        Creates the rsync commands for the given files
        :param files: A single file name or path or a list of file names
        """
        
        if files is None:
            return []
        
        if isinstance(files, str):
            files = [files]
        
        cmd = [self.rsync_exec,
               "-rzt",
               "--delete",
               "--timeout=900",
               "--size-only",
               "--exclude='*.DS_Store' ",
               "--include='*/'" ]
        
        if(self.dry_run):
            cmd.append("--dry-run")
            
        if(self.verbose):
            cmd.append("-v")
            cmd.append("--stats")
            cmd.append("--progress")
        
        #ssh stuff
        
        cmd.append("-e")
        
        sshWrapper = SSHWrapper(self.dataSourceConfig)
        
        sshCmd, sshFileCmd = sshWrapper.prepareSshFileCmds()

        commands = []
        for file in files:
            rsync_cmd = copy(cmd)
            rsync_cmd.append(sshCmd)
            rsync_cmd.append("%s%s"%(sshFileCmd, file))
            rsync_cmd.append("%s/%s" % (self.localFileSystem.filePath, file))
            commands.append(rsync_cmd)
        
        return commands
    
    def _checkResult(self, result):
        if(result is None or len(result)==0):
            return
        
        for keyword, ex in RsyncWrapper.FAILURE_KEYWORDS_EX_MAP.iteritems():
            if(result.find(keyword)!=-1):
                raise ex
        
        