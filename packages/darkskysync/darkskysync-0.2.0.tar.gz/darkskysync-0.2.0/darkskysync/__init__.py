#! /usr/bin/env python
#
# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

import logging
from .DarkSkySync import DarkSkySync

# Author:  Joel Akeret
# Contact: jakeret@phys.ethz.ch
"""
This is the mypackage package.
"""

__version__   = '0.2.0'
__author__    = 'Joel Akeret'
__credits__   = 'Institute for Astronomy ETHZ'

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def avail(path=None):
    """
    Lists the available file structure on the remote host
    
    :param path: [optional] sub path to directory structure to check
    
    :return: list of file available on remote host
    
    :raises ConnectionError: remote host could not be accessed
    """
    dss = DarkSkySync()
    return dss.avail(path)

def list(path=None, recursive=False):
    """
    Lists the available files in the local cache
    
    :param path: [optional] sub path to directory structure to check
    :param recursive: [optional] flag indicating if the cache should be browsed recursively
    
    :return: list of files in the local cache
    
    """
    dss = DarkSkySync()
    return dss.list(path, recursive)

def load(names, dry_run=False, force=False):
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
    dss = DarkSkySync()
    return dss.load(names, dry_run, force)

def remove(files=None, allFiles=False):
    """
    Removes files and filetrees from the local cache
    
    :param files: [optional] list of files or directories to delete
    :param allFiles: [optional] flag indicating that all files shoudl be removed from the cache
    
    :raises FileSystemError: error while accessing the local file system
    :raises IllegalArgumentException: Illegal parameter combination
    
    """
    dss = DarkSkySync()
    return dss.load(files, allFiles)
