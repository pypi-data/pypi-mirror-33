# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 24, 2013

@author: J. Akeret
'''


# System imports
from __future__ import print_function, division, absolute_import, \
    unicode_literals

import os
import shutil
import sys

from pkg_resources import resource_filename

import darkskysync
from darkskysync.DataSourceFactory import DataSourceFactory
from darkskysync.Exceptions import ConfigurationError
from darkskysync.Exceptions import ConnectionError, FileSystemError
from darkskysync.Exceptions import IllegalArgumentException
from darkskysync.RsyncWrapper import RsyncWrapper
from darkskysync.SSHClientAdapter import SSHClientAdapter
from darkskysync.LocalSyncAdapter import LocalSyncAdapter


class DarkSkySync(object):
    '''
    Helps to access and synchronize with a remote data storage. Features are:
        - lists the available file structure on the remote host
        - lists the file structure in the local cache
        - synchronizes the local cache with the remote file structure
        - allows for removing files from the local file system

    It delegates the remote access to the according wrappers (currently either scp over ssh or
    rsync over ssh) and manages the local file structure

    :param template: [optional] alternate name for the config template to use
    :param configFile: [optional] alternate config file to use
    :param verbose: [optional] flag to enable verbose mode

    :raises ConfigurationError: error while reading the config file
    '''

    REMOTE_WRAPPER_TYPE_MAP = {"rsync": SSHClientAdapter,
                               "ssh": SSHClientAdapter}

    REMOTE_SYNC_WRAPPER_TYPE_MAP = {"rsync": RsyncWrapper,
                                    "ssh": SSHClientAdapter,
                                    "local": LocalSyncAdapter,
                                    }

    DEFAULT_TEMPLATE = "master"

    def __init__(self, template=DEFAULT_TEMPLATE, configFile=None, verbose=False):
        '''
        Constructor
        '''
        self.configFile=configFile

        if(template is None):
            template = DarkSkySync.DEFAULT_TEMPLATE

        self._verifyConfigFile()

        self.verbose = verbose
        if(self.verbose):
            darkskysync.logger.info("Using config file: %s" % self.configFile)

        dsFactory = DataSourceFactory.fromConfig(self.configFile)
        self.dataSourceConfig = dsFactory.createDataSource(template)

    def avail(self, path=None):
        """
        Lists the available file structure on the remote host

        :param path: [optional] sub path to directory structure to check

        :return: list of file available on remote host

        :raises ConnectionError: remote host could not be accessed
        """

        try:
            RemoteWrapper = DarkSkySync.REMOTE_WRAPPER_TYPE_MAP[self.dataSourceConfig.remote.type]

            remoteWrapper = RemoteWrapper(self.dataSourceConfig)
            fileList = remoteWrapper.getRemoteFilesList(path)
            return self._filterFileList(fileList)
        except ConnectionError as ex:
            darkskysync.logger.error(str(ex))
            raise ex

    def list(self, path=None, recursive=False):
        """
        Lists the available files in the local cache

        :param path: [optional] sub path to directory structure to check
        :param recursive: [optional] flag indicating if the cache should be browsed recursively

        :return: list of files in the local cache

        """

        filePath = self.dataSourceConfig.local.filePath
        if(path is not None):
            filePath = os.path.join(filePath, path)

        fileList = []

        if (not os.path.exists(filePath)):
            return fileList

        if(recursive):
            for dirpath, dirnames, filenames in os.walk(filePath):
                for fileName in filenames:
                        fileList.append(os.path.join(dirpath,fileName))
        else:
            pathContent = os.listdir(filePath)
            fileList = [os.path.join(filePath, file) for file in pathContent]

        return fileList

    def load(self, names, dry_run=False, force=False):
        """
        Loads the given file names. Checks first if the requested files are available on the file system.
        If not, they will be downloaded from the remote host

        :param names: a list of names which should be loaded
        :param dry_run: [optional] flag indicating a dry run. No files will be downloaded
        :param force: [optional] flag indicating that the files should be downloaded even
            if they already exist on the local file system

        :retun: list of files loaded from the remote host

        :raises ConnectionError: remote host could not be accessed
        :raises FileSystemError: error while accesing the local file system

        """

        try:
            RemoteWrapper = DarkSkySync.REMOTE_SYNC_WRAPPER_TYPE_MAP[self.dataSourceConfig.remote.type]

            remoteWrapper = RemoteWrapper(self.dataSourceConfig, dry_run=dry_run, force=force, verbose=self.verbose)
            loadedFiles = remoteWrapper.loadFiles(names)
            return self._postProcessFileList(loadedFiles)
        except ConnectionError as ex:
            darkskysync.logger.error(str(ex))
            raise ex
        except FileSystemError as ex:
            darkskysync.logger.error(str(ex))
            raise ex

    def remove(self, files=None, allFiles=False):
        """
        Removes files and filetrees from the local cache

        :param files: [optional] list of files or directories to delete
        :param allFiles: [optional] flag indicating that all files shoudl be removed from the cache

        :raises FileSystemError: error while accessing the local file system
        :raises IllegalArgumentException: Illegal parameter combination

        """
        if(files is None and not allFiles):
            darkskysync.logger.warn("At least a file has to be given")
            raise IllegalArgumentException("At least a file has to be given")

        if(files is not None):
            if isinstance(files, str):
                files = [files]
            for file in files:
                path = os.path.join(self.dataSourceConfig.local.filePath, file)
                if(self.verbose):
                    darkskysync.logger.info("Removing: %s"%path)

                if(os.path.exists(path)):
                    if(os.path.isfile(path)):
                        os.remove(path)
                    else:
                        shutil.rmtree(path)

        if(allFiles):
            path = self.dataSourceConfig.local.filePath
            if(self.verbose):
                darkskysync.logger.info("Removing content of: %s"%path)
            for file in os.listdir(path):
                filePath = os.path.join(path, file)
                try:
                    if os.path.isfile(filePath):
                        os.unlink(filePath)
                    else:
                        shutil.rmtree(filePath)
                except Exception as e:
                    darkskysync.logger.warn(e)
                    raise FileSystemError(e)


    def _verifyConfigFile(self):
        if(self.configFile is None):
            self.configFile = DataSourceFactory.DEFAULT_CONFIGURATION_FILE
            if not os.path.isfile(self.configFile):
                if not os.path.exists(os.path.dirname(self.configFile)):
                    os.mkdir(os.path.dirname(self.configFile))

                template = resource_filename(darkskysync.__name__, "data/config.template")

                darkskysync.logger.warning("Deploying default configuration file to %s.",
                            self.configFile)
                shutil.copyfile(template, self.configFile)

        else:
            # Exit if supplied configuration file does not exists.
            if not os.path.isfile(self.configFile):
                sys.stderr.write(
                    "Unable to read configuration file `%s`.\n" %
                    self.configFile)
                raise ConfigurationError("Unable to read configuration file `%s`.\n" %
                    self.configFile)

    def _filterFileList(self, fileList):
        fileList = filter(lambda x: (not x.startswith(".")), fileList)
        fileList.sort()
        return fileList

    def _postProcessFileList(self, fileList):
        files = []
        for filePath in fileList:
            if(os.path.exists(filePath)):
                if(not os.path.isfile(filePath)):
                    filePath = filePath+"/"
                files.append(filePath)
        return files
