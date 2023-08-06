# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

'''
Created on Sep 23, 2013

@author: J. Akeret
'''

# System imports
from __future__ import print_function, division, absolute_import, unicode_literals


class ConfigurationError(Exception):
    pass


class ConnectionError(Exception):
    pass

class FileSystemError(Exception):
    pass

class IllegalArgumentException(Exception):
    pass

class FileNotFoundError(Exception):
    pass