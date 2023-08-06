# Copyright (C) 2015 ETH Zurich, Institute for Astronomy

'''
Created on Dec 2, 2015

author: jakeret
'''
from __future__ import print_function, division, absolute_import, unicode_literals

import os
from darkskysync.AbstractRemoteSyncAdapter import AbstractRemoteSyncAdapter


class LocalSyncAdapter(AbstractRemoteSyncAdapter):
    '''
    An adapter implementation to the paramiko ssh client

    :param dataSourceConfig: configuration of the data source
    :param rsync_exec: name of the rsync command to use. Default is 'rsync'
    :param dry_run: If true no files are downloaded
    :param force: If true the files in the local cache will be overwritten
    :param verbose: If true additional information will be printed
    
    '''
    
    LIST_CMD = "ls"
    NEWLINE = "\n"

    def __init__(self, dataSourceConfig, dry_run=False, force=False, verbose=True):
        '''
        Constructor
        '''
        self.dataSourceConfig = dataSourceConfig
        self.localFileSystem = self.dataSourceConfig.local
        self.remoteFileSystem = self.dataSourceConfig.remote
        self.dry_run = dry_run
        self.force = force
        self.verbose = verbose
        
    def getRemoteFilesList(self, path=None):
        raise TypeError("Remote files can not be loaded with 'LocalSyncAdapter'")
        
    def loadFiles(self, files):
        """
        Returns the local file path for each requested file
        
        :param files: A single file name or path or a list of file names
        
        :return: a list of downloaded files
        
        """
        if files is None:
            return []
        
        if isinstance(files, str) or isinstance(files, basestring):
            files = [files]
            
        pathPrefix = self.localFileSystem.filePath
        return [os.path.join(pathPrefix, file) for file in files]