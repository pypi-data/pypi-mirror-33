# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 25, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

import logging
import os
import socket
from stat import S_ISDIR

from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.sftp_client import SFTPClient
from paramiko.ssh_exception import BadHostKeyException, AuthenticationException, \
    SSHException

import darkskysync
from darkskysync.AbstractRemoteSyncAdapter import AbstractRemoteSyncAdapter
from darkskysync.Exceptions import ConnectionError, FileSystemError
from darkskysync.Exceptions import FileNotFoundError


try:
    basestring
except NameError:
    basestring = str  # python 3


class SSHClientAdapter(AbstractRemoteSyncAdapter):
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

        #supress paramiko info msg
        logging.getLogger("paramiko").setLevel(logging.WARNING)

    def getRemoteFilesList(self, path=None):
        """
        Lists the files available on the remote host

        :param path: Relative path to the resource of interest

        """

        client = None
        sftpclient = None
        try:
            client = self._connectToHost()
            sftpclient = self._openSftp(client)
            filePath = self.remoteFileSystem.filePath
            if(path is not None):
                filePath = os.path.join(filePath, path)
            else:
                filePath = "."

            fileList = sftpclient.listdir(filePath)
            return fileList
        except AuthenticationException as ex:
            raise ConnectionError("Make sure %s can be accessed without password prompt" % self.remoteFileSystem.host)
        except (BadHostKeyException, SSHException, socket.error) as ex:
            raise ConnectionError(ex)
        except (IOError) as ex:
            raise ConnectionError(ex)
        finally:
            if sftpclient is not None:
                sftpclient.close()
            if client is not None:
                client.close()


    def loadFiles(self, files):
        """
        Downloads the files form the remote host

        :param files: A single file name or path or a list of file names

        :return: a list of downloaded files

        """
        if files is None:
            return []

        if isinstance(files, str) or isinstance(files, basestring):
            files = [files]

        self._prepareDestination(self.localFileSystem.filePath)
        client = None
        sftpclient = None
        fileList = []
        try:
            client = self._connectToHost()

            sftpclient = self._openSftp(client)

            for file in files:
                self._downloadFiles(sftpclient, file)
                pathPrefix = self.localFileSystem.filePath
                destFile = os.path.join(pathPrefix, file)
                fileList.append(destFile)
        except OSError as ex:
            raise FileSystemError("Unable to write files. Reason: %s"%str(ex))
        except AuthenticationException as ex:
            raise ConnectionError("Make sure %s can be accessed without password prompt" % self.remoteFileSystem.host)
        except (BadHostKeyException, SSHException, socket.error) as ex:
            raise ConnectionError(ex)
        except (IOError) as ex:
            raise ConnectionError(ex)
        finally:
            if sftpclient is not None:
                sftpclient.close()
            if client is not None:
                client.close()

        return fileList

    def _downloadFiles(self, sftpclient, fileName):
#        srcFile = os.path.join(self.remoteFileSystem.filePath, fileName)
        srcFile = fileName
        pathPrefix = self.localFileSystem.filePath
        destFile = os.path.join(pathPrefix, fileName)

        if(self._isdir(sftpclient, srcFile)):
            if (not os.path.isdir(destFile) and not self.dry_run):
                os.makedirs(destFile)
            fileList = sftpclient.listdir(srcFile)
            for file in fileList:
                self._downloadFiles(sftpclient, os.path.join(fileName,file))
        else:
            self._downloadFile(sftpclient, srcFile, destFile)

    def _downloadFile(self, sftpclient, srcFile, destFile):
        destPath = os.path.dirname(destFile)
        try:
            if (not os.path.isdir(destPath) and not self.dry_run):
                os.makedirs(destPath)

            self._log("Loading file %s"%srcFile)

            if(not self.dry_run):
                if(self.force and os.path.exists(destFile)):
                    os.remove(destFile)

                if(not os.path.exists(destFile)):
                    try:
                        open(destFile, "w")
                        sftpclient.get(srcFile, destFile)
                    except IOError as ex:
                        os.remove(destFile)
                        raise ex

        except IOError as ex:
            self._log("File '%s' not found" % srcFile)
            raise FileNotFoundError("File '%s' not found" % srcFile)

    def _isdir(self, sftpclient, path):
        try:
            print("00000000")
            print(self)
            print(sftpclient)
            print(sftpclient.stat(path))
            print("00000000")

            return S_ISDIR(sftpclient.stat(path).st_mode)
        except IOError:
            #Path does not exist, so by definition not a directory
            return False


    def _openSftp(self, sshClient):
        sftpclient = sshClient.open_sftp()
        return sftpclient

    def _connectToHost(self):
        self._log("Connecting to remote host %s"%self.remoteFileSystem.host)
        client = SSHClient()
        client.load_system_host_keys(self.remoteFileSystem.login.known_hosts)
        client.set_missing_host_key_policy(AutoAddPolicy())

        client.connect(hostname=self.remoteFileSystem.host,
                       port=int(self.remoteFileSystem.port),
                       username=self.remoteFileSystem.login.username,
                       key_filename=self.remoteFileSystem.login.user_key_private)

        return client


    def _log(self, msg):
        if(self.verbose):
            darkskysync.logger.debug(msg)


