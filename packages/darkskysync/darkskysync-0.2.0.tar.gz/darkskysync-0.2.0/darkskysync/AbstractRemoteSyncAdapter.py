# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 24, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod
import os
from darkskysync.Exceptions import FileSystemError

'''
Created on Sep 30, 2013

@author: J. Akeret
'''

class AbstractRemoteSyncAdapter(object):
    '''
    Abstract class for all synchronization adapters
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def loadFiles(self, files):
        """
        Loads files from the remote location
        """
        pass


    def _prepareDestination(self, path):
        if not os.path.isdir(path):
            # We do not create *all* the parents, but we do create the
            # directory if we can.
            try:
                os.makedirs(path)
            except OSError as ex:
                raise FileSystemError("Unable to create storage directory: "
                                 "%s" % (str(ex)))
