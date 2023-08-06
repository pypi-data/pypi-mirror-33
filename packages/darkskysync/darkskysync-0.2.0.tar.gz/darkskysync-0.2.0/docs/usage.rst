========
Usage
========

To use DarkSkySync in a project::

	from darkskysync.DarkSkySync import DarkSkySync
	dssync = DarkSkySync()
	
	path = "A611/"
	
	available = dssync.avail(path)
	print("Available files in '%s': '%s'"%(path, "', '".join(available)) )
	
	file_path = "A611/a611_mask.fits"
	print("loading '%s'... "%(file_path)) 
	a611_mask_path = dssync.load(file_path)[0]
	print("done\n")
	
	print("local path is '%s'"%(a611_mask_path))
	
	#clear the cache
	dssync.remove(allFiles=True)


The DarkSkySync can also be used from the command line:
::

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
	