#! /usr/bin/env python
# Copyright (C) 2013 ETH Zurich, Institute of Astronomy

"""
This is the DarkSkySync command line interface

Created on Sep 23, 2013

@author: J. Akeret


Usage:
  DarkSkySync avail [<path>] [--config=<file>] [--template=<template>] [-v|--verbose]
  DarkSkySync list [<path>] [-r|--recursive] [--config=<file>] [--template=<template>] [-v|--verbose]
  DarkSkySync load <name>... [--dry_run] [-f|--force] [--config=<file>] [--template=<template>] [-v|--verbose]
  DarkSkySync remove (<name>...|--all) [--config=<file>] [--template=<template>] [-v|--verbose]
  DarkSkySync -h | --help
  DarkSkySync --version
  
Options
  -h --help     Show this screen.
  --version     Show version.
  --config=<file>  The configfile to use.
  --template=<template>  The template to use [default:master]
  --all         All files
  -v --verbose  More output
  -f --force    Force the download
  -r --recursive  List the directories in a recursive way
  --dry_run     Dry run - Not loading any files
"""
# System imports
from __future__ import print_function, division, absolute_import, unicode_literals

import sys

from darkskysync import __version__
from darkskysync.DarkSkySync import DarkSkySync
from docopt import docopt
from darkskysync.Exceptions import ConfigurationError


class DarkSkySyncCLI(object):
    """
    Command line interface for the darkskysync
    """

    def __init__(self):
        pass
    
    def launch(self):
        """
        Starts the darkskysync by parsing the args and the config
        """
        
        args = docopt(__doc__, version='DarkSkySync CLI {}'.format(__version__))
        
#        print args
        try:
            dam = DarkSkySync(template=args["--template"], configFile=args["--config"], verbose=args["--verbose"])
            self.dispatch(dam, args)
        except ConfigurationError:
            sys.exit(1)
        
        
    def dispatch(self, dam, args):
        """
        Dispatches the sub command to the given darkskysync instance
        
        :param dam: the instance of the darkskysync to us
        :param args: the arguments passed by the used
        """
        try:
            if(args["avail"]):
                filesList = dam.avail(path=args["<path>"])
                self._printFilesList("Available files:", filesList)
                
            elif(args["list"]):
                filesList = dam.list(path=args["<path>"], recursive=args["--recursive"])
                self._printFilesList("Available files:", filesList)
                
            elif(args["load"]):
                filesList = dam.load(args["<name>"], args["--dry_run"], args["--force"])
                self._printFilesList("Loaded files:", filesList)
                
            elif(args["remove"]):
                dam.remove(args["<name>"], args["--all"])
                
        except Exception as ex:
            sys.exit(1)

    def _printFilesList(self, message, filesList):
        print(message)
        if(len(filesList)>0):
            for fileName in filesList:
                print(fileName)
                
        else:
            print("-")


def main():
    cli = DarkSkySyncCLI()
    cli.launch()
        

if __name__ == '__main__':
    main()