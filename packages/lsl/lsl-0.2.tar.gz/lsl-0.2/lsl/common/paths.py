# -*- coding: utf-8 -*

"""Module to set up path information for the LWA Software Library.  Two 
variables are defined by this module:  module and data.  `module' specifies
the absolute path to the module and `data' the abs. path to the data directory
where data files are stored."""

import os
import imp

__version__ = '0.1'
__revision__ = '$ Revision: 6 $'
__all__ = ['module', 'data', 'moduleBuild', 'dataBuild']

modInfo = imp.find_module('lsl')
module = os.path.abspath(modInfo[1])
data = os.path.join(module, 'data')

# If we seem to be in the building directory, make the module and 
# data build paths point to the right place.  This is done so that 
# the testing scripts run via:
#	python setup.py test
# access the right files and tests.
# 
# If we don't seem to be in the 
# source directory, moduleBuild points to module and dataBuild 
# points to data.
currentDir = os.path.abspath(os.getcwd())
if os.path.exists(os.path.join(currentDir, 'setup.py')):
	modInfoBuild = imp.find_module('lsl', [currentDir])
	moduleBuild =  os.path.abspath(modInfoBuild[1])
	dataBuild = os.path.join(moduleBuild, 'data')
else:
	moduleBuild = module
	dataBuild = data
