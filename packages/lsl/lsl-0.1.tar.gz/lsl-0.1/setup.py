# -*- coding: utf-8 -*

import os
import imp
import glob

from distutils.core import setup
from distutils.command.install_data import install_data

__version__ = open('VERSION').read().strip()

def is_package(path):
	"""From:
	http://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
	"""

	return (
		os.path.isdir(path) and
		os.path.isfile(os.path.join(path, '__init__.py'))
	)

def find_packages(path, base="" ):

	"""
	From:
	http://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
	"""

	""" Find all packages in path """
	packages = {}
	for item in os.listdir(path):
		dir = os.path.join(path, item)
		if is_package( dir ):
			if base:
				module_name = "%(base)s.%(item)s" % vars()
			else:
				module_name = item
			packages[module_name] = dir
			packages.update(find_packages(dir, module_name))
	return packages

def non_python_files(path):
	"""From:
	http://wiki.python.org/moin/Distutils/Cookbook/AutoDataDiscovery
	"""


	""" Return all non-python-file filenames in path """
	result = []
	all_results = []
	module_suffixes = [info[0] for info in imp.get_suffixes()]
	ignore_dirs = ['svn']
	for item in os.listdir(path):
		name = os.path.join(path, item)
		if (
			os.path.isfile(name) and
			os.path.splitext(item)[1] not in module_suffixes
			):
			result.append(name)
		elif os.path.isdir(name) and item.lower() not in ignore_dirs:
			all_results.extend(non_python_files(name))
	if result:
		all_results.append((path, result))
	return all_results

class smart_install_data(install_data):
	"""From:
	http://wiki.python.org/moin/Distutils/Cookbook/InstallDataScattered
	"""

	def run(self):
		#need to change self.install_dir to the library dir
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return install_data.run(self)

def get_description(filename):
	desc = ''
	fh = open(filename, 'r')
	lines = fh.readlines()
	fh.close()

	inDescription = False
	for line in lines:
		line = line.replace('\n', '')
		line = line.replace('\t', '')
		if line.find('DESCRIPTION') == 0:
			inDescription = True
			continue
		if line.find('REQUIREMENTS') == 0:
			inDescription = False
			break
		if inDescription:
			desc = ' '.join([desc, line])

	return desc

packages = find_packages(".")
py_files = ["lsl/*", "lsl/common/*", "lsl/correlator/*", "lsl/misc/*", 
		"lsl/reader/*", "lsl/statistics/*", "lsl/writer/*", "lsl/sim/*"]
data_files = non_python_files('lsl')
script_files = glob.glob('scripts/*.py')

setup(
	name = "lsl",
	version = __version__,
	description = "LWA Software Library",
	author = "Jayce Dowell",
	author_email = "jdowell@unm.edu",
	url = "http://panda.unm.edu/Courses/Dowell/",
	long_description = get_description('README'), 
	classifiers = ['Development Status :: 2 - Pre-Alpha',
			'Intended Audience :: Science/Research',
			'License :: OSI Approved :: GNU General Public License (GPL)',
			'Topic :: Scientific/Engineering :: Astronomy'],
	install_requires = ['pyfits>=2.1', 'numpy>=1.2', 'aipy>=0.9.1'],
	dependency_links = ['http://www.stsci.edu/resources/software_hardware/pyfits'],
	package_dir = packages, 
	packages = packages.keys(),
	package_data = {'lsl' : py_files},
	data_files = data_files,
	scripts = script_files,
	cmdclass = {'install_data':smart_install_data}
) 
