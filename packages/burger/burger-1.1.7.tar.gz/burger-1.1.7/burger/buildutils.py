#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package that contains build helper functions
"""

## \package burger.buildutils

from __future__ import absolute_import, print_function, unicode_literals

import errno
import os
import platform
import subprocess
import sys

from .strutils import is_string, PY2, PY3_3_OR_HIGHER, PY3_5_OR_HIGHER

# pylint: disable=C0302

if PY2:
	from cStringIO import StringIO
else:
	from io import StringIO

# Redefining built-in W0622 (Ignore redefinition of zip)

try:
	import itertools.izip as zip		# pylint: disable=W0622
except ImportError:
	pass

## Cached location of the BURGER_SDKS folder
_BURGER_SDKS_FOLDER = None

## Cached location of doxygen
_DOXYGEN_PATH = None

## Cached location of p4 from Perforce
_PERFORCE_PATH = None

## Environment variable locations of window applications
_WINDOWS_ENV_PATHS = [
	'ProgramFiles',
	'ProgramFiles(x86)'
]

########################################


def get_sdks_folder(verbose=False, refresh=False, folder=None):
	"""
	Return the path of the BURGER_SDKS folder

	If the environment variable BURGER_SDKS is set,
	return the pathname it contains. Otherwise,
	print a warning if verbose is True and then attempt to find
	the 'sdks' folder by traversing the current working directory
	for a folder named 'sdks'. If one isn't found, return None.

	Examples:
		# Normal use
		sdksfolder = burger.buildutils.get_sdks_folder()
		if not sdksfolder:
			print('failure')
			raise NameError("sdks not found, set BURGER_SDKS")

		# Alert the user if BURGER_SDKS isn't set
		burger.buildutils.get_sdks_folder(verbose=True)

		# Force the use of a supplied folder for sdks
		burger.buildutils.get_sdks_folder(refresh=True, folder='./foo/sdks/')

	Args:
		verbose: If True, print a message if BURGER_SDKS was not present
		refresh: If True, reset the cache and force a reload.
		folder: Path to use as BURGER_SDKS in the cache as an override

	Returns:
		None if the environment variable is not set, or the
		value of BURGER_SDKS.
	"""

	global _BURGER_SDKS_FOLDER				# pylint: disable=W0603

	# Clear the cache if needed
	if refresh:
		_BURGER_SDKS_FOLDER = None

	# Set the override, if found
	if folder:
		_BURGER_SDKS_FOLDER = folder

	# Not cached?
	if _BURGER_SDKS_FOLDER is None:

		# Load from the system
		_BURGER_SDKS_FOLDER = os.getenv('BURGER_SDKS', default=None)

		# Test for None or empty string
		if not _BURGER_SDKS_FOLDER:

			# Warn about missing environment variable
			if verbose:
				print('The environment variable "BURGER_SDKS" is not set')

			# Try to find the directory in the current path
			from .fileutils import traverse_directory
			sdks = traverse_directory(os.getcwd(), 'sdks', \
				find_directory=True, terminate=True)
			if sdks:
				_BURGER_SDKS_FOLDER = sdks[0]
				if verbose:
					print('Assuming {} is the BURGER_SDKS folder'.format(sdks[0]))

	return _BURGER_SDKS_FOLDER

########################################


def host_machine():
	"""
	Return the high level operating system's name

	Return the machine this script is running on, 'windows', 'macosx',
	'linux' or 'unknown'

	Returns:
		The string 'windows', 'macosx', 'linux', or 'unknown'

	See:
		get_mac_host_type() or get_windows_host_type()
	"""
	# Only windows reports as NT

	if os.name == 'nt':
		return 'windows'

	# BSD and GNU report as posix

	if os.name == 'posix':

		# MacOSX is the Darwin kernel

		if platform.system() == 'Darwin':
			return 'macosx'

		# Assume linux (Tested on Ubuntu and Red Hat)

		return 'linux'

	# Surrender Dorothy

	return 'unknown'

########################################


def fix_csharp(csharp_application_path):
	"""
	Convert pathname to execute a C# exe file

	C# applications can launch as is on Windows platforms,
	however, on Mac OSX and Linux, it must be launched
	from mono. Determine the host machine and if not
	windows, automatically prepend 'mono' to
	the application's name to properly launch it

	This will also encase the name in quotes in case there are
	spaces in the pathname

	Args:
		csharp_application_path: Pathname string to update

	Returns:
		Command line appropriate for the platform to launch a C# application.
	"""

	# Encapsulate in quotes if needed
	from .strutils import encapsulate_path
	quoted = encapsulate_path(csharp_application_path)

	# Prepend mono on non-windows systems
	if host_machine() != 'windows':
		return 'mono {}'.format(quoted)
	return quoted


########################################


def get_windows_host_type():
	"""
	Return windows host type (32 or 64 bit)

	Return False if the host is not Windows, 'x86' if it's a 32 bit host
	and 'x64' if it's a 64 bit host, and possibly 'arm' if an arm host

	Returns:
		The string 'x64', 'x86', 'arm' or False
	See:
		get_mac_host_type() or host_machine()

	"""

	# Not windows?

	if os.name != 'nt':
		return False

	# Test the CPU for the type

	machine = platform.machine()
	if machine in ('AMD64', 'x86_64'):
		return 'x64'
	return 'x86'

########################################


def get_mac_host_type():
	"""
	Return Mac OSX host type (PowerPC/Intel)

	Return False if the host is not Mac OSX. 'ppc' if it's a Power PC based
	system, 'x86' for Intel (Both 32 and 64 bit)

	Returns:
		The string 'x86', 'ppc' or False

	See:
		get_windows_host_type() or host_machine()
	"""

	# Mac/Linux?
	if os.name != 'posix':
		return False

	# Not linux?

	if platform.system() != 'Darwin':
		return False

	# Since it's a mac, query the Mac OSX cpu type
	# using the MacOSX python extensions

	cpu = platform.machine()
	if cpu in ('x86', 'x86_64'):
		return 'x86'

	if cpu in ('PowerPC', 'ppc', 'Power Macintosh'):
		return 'ppc'

	# Defaults to PowerPC
	return 'ppc'

########################################


def is_exe(exe_path):
	"""
	Return True if the file is executable

	Note:
		Windows platforms don't support the 'x' bit so all
		files are executable if they exist.

	Args:
		exe_path: Full or partial pathname to test for existance
	Returns:
		True if the file is executable, False if the file doesn't exist or
		is not valid.
	"""
	return os.path.isfile(exe_path) and os.access(exe_path, os.X_OK)

########################################


def get_path_ext(pathext=None):
	"""
	Return a list of executable extensions

	If pathext is None, query the environment variable PATHEXT and
	return the entries as a string list. If pathext is a string,
	parse it as if it was a system specific PATHEXT string and
	if it's an iterable, return the value as is. If PATHEXT doesn't exist
	or is empty, return an empty list.

	Windows usually sets the value like this
	``PATHEXT=.COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC``

	Args:
		pathext: String parsed as PATHEXT, iterable returned as is
	Returns:
		List of file name extension strings.
	See:
		burger.buildutils.make_exe_path() or burger.buildutils.find_in_path()
	"""

	# Read the environment variable?
	if pathext is None:
		pathext = os.getenv('PATHEXT', [])

	# If a string, or environment variable?
	if is_string(pathext):
		# Parse the string
		pathext = pathext.split(os.pathsep)

	# Return the list or iterable
	return pathext

########################################


def make_exe_path(exe_path, pathext=None):
	"""
	Given a folder and a executable name, return the true absolute path

	Examples:
		# exe could be returned as exe, exe.exe, exe.cmd, etc...
		path = make_exe_path('C:\\code\\exe')
		if path is None:
			print('No file named exe at C:\\code')

	Note:
		On macOS and Linux, PATHEXT is not set, this is for supporting
		extension types for common batch files or other executable extensions.

	Args:
		exe_path: Path of the executable to test
		pathext: Extension list to test
	Returns:
		None if a match was not found, or a full pathname with extension.

	See:
		burger.buildutils.get_path_ext() or burger.buildutils.find_in_path()
	"""
	# Test the path as is
	if is_exe(exe_path):
		return exe_path

	# Try all the extensions (Can be an empty list)
	for ext in get_path_ext(pathext):
		temp_path = exe_path + ext
		if is_exe(temp_path):
			break
	else:
		return None
	return temp_path

########################################


def find_in_path(filename, search_path=None, executable=False):
	"""
	Using the system PATH environment variable, search for a file

	If the flag executable is False, the file will be found using a
	simple path search. If the flag is True, the file will be searched
	for using the extensions in the PATHEXT environment variable in
	addition to use the filename as is.

	If search_path is a string, it will be seperated using os.pathsep. If
	not, it will be treated as an interable list of strings of full pathnames
	to search. If it is None, the PATH environment variable will be used.

	Examples:
		# Can return 'doxygen', 'doxygen.exe' or 'doxygen.com' depending
		# on what was found
		burger.find_in_path('doxygen', executable=True)

		# Will only find 'foo.txt'
		burger.find_in_path('foo.txt')

	Args:
		filename: File to locate
		search_path: Search paths to use instead of PATH
		executable: True to ensure it's an executable
	Return:
		None if not found, a full path if the file is found
	See:
		burger.buildutils.get_path_ext() or burger.buildutils.make_exe_path()
	"""

	# Set up for added standard extentions
	if executable:
		pathext = get_path_ext()
	else:
		pathext = []

	# Is there a search path override?
	if search_path is None:
		# Use the environment variable
		paths = os.getenv('PATH', [])
	else:
		paths = search_path

	if is_string(paths):
		# Break it up based on the path seperator
		paths = paths.split(os.pathsep)

	# Since PATH was used, also test the current working directory
	# first
	if search_path is None:
		paths.insert(0, os.getcwd())

	# Scan the list of paths to find the file
	for item in paths:
		# Get the full path
		temp_path = os.path.join(item, filename)

		# Perform the test as an exe
		if executable:
			temp_path = make_exe_path(temp_path, pathext=pathext)
			if temp_path:
				break
		# Test for just a file
		elif os.path.isfile(temp_path):
			break
	else:
		# Not found in the loops
		return None

	# Return the path
	return os.path.abspath(temp_path)

########################################


def expand_and_verify(file_string):
	"""
	Expand the input string with os.path.expandvars()

	After expanding the string, test for the existence of the file
	and return the expanded path if True. Otherwise, return None

	Examples:
		perforcepath = burger.expand_and_verify('${PERFORCE}\\p4.exe')
		if perforcepath is None:
			return

	Args:
		file_string: Pathname with environment variable tokens

	Returns:
		None if the string couldn't be expanded or if the file didn't exist,
			otherwise, return the expanded pathname

	"""

	result_path = os.path.expandvars(file_string)
	if result_path is not None:
		if not os.path.isfile(result_path):
			result_path = None
	return result_path

########################################


def where_is_doxygen(verbose=False, refresh=False, path=None):
	"""
	Return the location of Doxygen's executable

	Look for an environment variable DOXYGEN and
	determine if the executable resides there, if
	so, return the string to the path

	If running on a MacOSX client, look in the Applications
	folder for a copy of Doxygen.app and return the
	pathname to the copy of doxygen that resides within

	PATH is then searched for doxygen, and if it's not found,
	None is returned.

	Args:
		verbose: If True, print a message if doxygen was not found
		refresh: If True, reset the cache and force a reload.
		path: Path to doxygen to place in the cache

	Returns:
		A path to the Doxygen command line executable or None if not found.

	"""

	global _DOXYGEN_PATH				# pylint: disable=W0603

	# Clear the cache if needed
	if refresh:
		_DOXYGEN_PATH = None

	# Set the override, if found
	if path:
		_DOXYGEN_PATH = path

	# Is cached?
	if _DOXYGEN_PATH:
		return _DOXYGEN_PATH

	# Try the environment variable first
	if os.getenv('DOXYGEN', None):
		if get_windows_host_type():

			# Windows points to the base path
			doxygenpath = os.path.expandvars('${DOXYGEN}\\bin\\doxygen.exe')
		else:
			# Just append the exec name
			doxygenpath = os.path.expandvars('${DOXYGEN}/doxygen')

		# Valid?
		if is_exe(doxygenpath):
			_DOXYGEN_PATH = doxygenpath
			return doxygenpath

	# Scan the PATH for the exec
	doxygenpath = find_in_path('doxygen', executable=True)
	if doxygenpath:
		_DOXYGEN_PATH = doxygenpath
		return doxygenpath

	# List of the usual suspects
	full_paths = []

	# Check if it's installed but not in the path
	if get_windows_host_type():

		# Try the 'ProgramFiles' folders
		for item in _WINDOWS_ENV_PATHS:
			if os.getenv(item, None):
				full_paths.append(os.path.expandvars( \
					'${' + item + '}\\doxygen\\bin\\doxygen.exe'))

	elif get_mac_host_type():

		# MacOSX has it hidden in the application
		full_paths.append('/Applications/Doxygen.app/Contents/Resources/doxygen')
		full_paths.append('/opt/local/bin/doxygen')

	elif os.name == 'posix':
		# Posix / Linux
		full_paths.append('/usr/bin/doxygen')

	# Scan the list of known locations
	for doxygenpath in full_paths:
		if is_exe(doxygenpath):
			# Finally found it!
			_DOXYGEN_PATH = doxygenpath
			return doxygenpath

	# Oh, dear.
	if verbose:
		print('Doxygen not found!')
		if get_mac_host_type():
			print('Install the desktop application in the Applications folder or ' \
				'use brew or macports for the command line version')

	# Can't find it
	return None

########################################


def where_is_p4(verbose=False, refresh=False, path=None):

	"""
	Return the location of the p4 executable

	Look for an environment variable PERFORCE and
	determine if the executable resides there, if
	so, return the string to the path.

	PATH is then searched for p4, and if it's not found,
	None is returned.

	Args:
		verbose: If True, print a message if Perforce was not found
		refresh: If True, reset the cache and force a reload.
		path: Path to Perforce to place in the cache
	Returns:
		A path to the Perforce command line executable or None if not found.
	See:
		perforce_edit()
	"""

	global _PERFORCE_PATH				# pylint: disable=W0603

	# Clear the cache if needed
	if refresh:
		_PERFORCE_PATH = None

	# Set the override, if found
	if path:
		_PERFORCE_PATH = path

	# Is cached?
	if _PERFORCE_PATH:
		return _PERFORCE_PATH

	# Try the environment variable first
	if os.getenv('PERFORCE', None):
		if get_windows_host_type():

			# Windows points to the base path
			p4path = os.path.expandvars('${PERFORCE}\\p4.exe')
		else:
			# Just append the exec name
			p4path = os.path.expandvars('${PERFORCE}/p4')

		# Valid?
		if is_exe(p4path):
			_PERFORCE_PATH = p4path
			return p4path

	# Scan the PATH for the exec
	p4path = find_in_path('p4', executable=True)
	if p4path:
		_PERFORCE_PATH = p4path
		return p4path

	# List of the usual suspects
	full_paths = []

	# Check if it's installed but not in the path
	if get_windows_host_type():

		# Try the 'ProgramFiles' folders
		for item in _WINDOWS_ENV_PATHS:
			if os.getenv(item, None):
				full_paths.append(os.path.expandvars( \
					'${' + item + '}\\perforce\\p4.exe'))

	elif get_mac_host_type():

		# Installed here via brew
		full_paths.append('/opt/local/bin/p4')

	elif os.name == 'posix':
		# Posix / Linux
		full_paths.append('/usr/bin/p4')

	# Scan the list of known locations
	for p4path in full_paths:
		if is_exe(p4path):
			# Finally found it!
			_PERFORCE_PATH = p4path
			return p4path

	# Oh, dear.
	if verbose:
		print('Perforce "p4" not found!')
		if get_mac_host_type():
			print('Use brew or macports for the command line version')

	# Can't find it
	return None

########################################


def perforce_edit(files, verbose=False):

	"""
	Given a list of files, checkout (Edit) them in perforce

	Pass either a single string or a string list of pathnames
	of files to checkout in perforce using the 'p4 edit' command

	Args:
		files: list or string object of file(s) to checkout
		verbose: If True, print the command line and warnings

	Returns:
		Zero if no error, non-zero on error
	See:
		where_is_p4()
	"""

	# Get the p4 executable
	perforce_path = where_is_p4(verbose=verbose)

	# Not found?
	if perforce_path is None:
		return 10

	# Encapsulate the single string entry
	if is_string(files):
		file_list = (files,)
	else:
		file_list = files

	# Generate the command line and call
	from .strutils import encapsulate_path
	p4quoted = encapsulate_path(perforce_path)
	error = 0
	for item in file_list:
		cmd = '{} edit {}'.format(p4quoted, encapsulate_path(os.path.abspath(item)))
		if verbose:
			print(cmd)
		error = subprocess.call(cmd, shell=True)
		if error != 0:
			break
	return error

########################################


def compare_files(filename1, filename2):
	"""
	Compare text files for equality

	Check if two text files are the same length,
	and then test the contents to verify equality.

	Args:
		filename1: string object with the pathname of the file to test
		filename2: string object with the pathname of the file to test against

	Returns:
		True if the files are equal, False if not.

	See:
		compare_file_to_string()
	"""

	# Load in the two text files

	try:
		with open(filename1, 'r') as filep:
			file_one_lines = filep.read().splitlines()
		with open(filename2, 'r') as filep:
			file_two_lines = filep.read().splitlines()
	except IOError as error:
		# Only deal with file not found
		if error.errno != errno.ENOENT:
			raise
		# If not found, return "not equal"
		return False

	del filep

	# Compare the file contents

	if len(file_one_lines) == len(file_two_lines):
		for i, j in zip(file_one_lines, file_two_lines):
			if i != j:
				break
		else:
			# It's a match!
			return True
	return False

########################################


def compare_file_to_string(filename, data):

	"""
	Compare text file and a string for equality

	Check if a text file is the same as a string by loading the text file and
	testing line by line to verify the equality of the contents

	Args:
		filename: string object with the pathname of the file to test
		data: string object to test against

	Returns:
		True if the file and the string are the same, False if not

	See:
		compare_files()
	"""

	# Do a data compare as a text file

	try:
		with open(filename, 'r') as filep:
			file_one_lines = filep.read().splitlines()
	except IOError as error:
		# Only deal with file not found
		if error.errno != errno.ENOENT:
			raise
		# If not found, return "not equal"
		return False

	del filep

	# Compare the file contents taking into account
	# different line endings

	# Test if this is a StringIO object
	if hasattr(data, 'getvalue'):
		file_two_lines = data.getvalue().splitlines()
	else:
		file_two_lines = data.splitlines()

	# Compare the file contents

	if len(file_one_lines) == len(file_two_lines):
		for i, j in zip(file_one_lines, file_two_lines):
			if i != j:
				break
		else:
			# It's a match!
			return True
	return False

########################################


def run_command(args, working_dir=None, quiet=False):
	"""
	Execute a program and capture the return code and text output

	Pass a command line formatted for the current shell and then this
	function will execute that command and capture both stdout and stderr.

	Note:
		The first parameter is passed to subprocess.Popen() as is.

	Args:
		args: List of command line entries, starting with the program pathname
		working_dir: Directory to set before executing command
		quiet: Set to True if errors should not be printed

	Returns:
		The return code, stdout, stderr
	"""
	try:
		tempfp = subprocess.Popen(args, cwd=working_dir, stdout=subprocess.PIPE, \
			stderr=subprocess.PIPE, universal_newlines=True)
	except OSError as error:
		if not quiet:
			print('Command line "{}" generated error {}'.format(args, error))
		return (error.errno, '', '')

	stdoutstr, stderrstr = tempfp.communicate()
	return (tempfp.returncode, stdoutstr, stderrstr)

########################################


def make_version_header(working_dir, outputfilename, verbose=False):
	"""
	Create a C header with the perforce version

	This function assumes version control is with perforce!

	Get the last change list and create a header
	with this information (Only modify the output file if
	the contents have changed)

	C++ defines are declared for P4_CHANGELIST, P4_CHANGEDATE, P4_CHANGETIME,
	P4_CLIENT, and P4_USER

	Args:
		working_dir: string with the path of the folder to obtain the perforce
			version for
		outputfilename: string with the path of the generated header
		verbose: Print perforce commands and other informational messages

	Returns:
		Zero if no error, non-zero on error
	"""

	# Check if perforce is installed
	p4exe = where_is_p4()
	if p4exe is None:
		return 10

	# Create the header guard by taking the filename,
	# converting to upper case and replacing spaces and
	# periods with underbars.
	headerguard = os.path.basename(outputfilename).upper()
	headerguard = headerguard.replace(' ', '_')
	headerguard = '__{}__'.format(headerguard.replace('.', '_'))

	# Get the last change list
	# Parse "Change 3361 on 2012/05/15 13:20:12 by burgerbecky@burgeroctocore
	# 'Made a p4 change'"
	# -m 1 / Limit to one entry
	# -t / Display the time
	# -l / Print out the entire changelist description

	cmd = (p4exe, 'changes', '-m', '1', '-t', '-l', '...#have')
	if verbose:
		print(' '.join(cmd))
	error, tempdata = run_command(cmd, working_dir)[:2]
	if error != 0:
		return error

	# Parse out the output of the p4 changes command
	p4changes = tempdata.strip().split(' ')

	# Get the p4 client
	# Parse "P4CLIENT=burgeroctocore (config)"

	cmd = (p4exe, 'set', 'P4CLIENT')
	if verbose:
		print(' '.join(cmd))
	error, tempdata = run_command(cmd, working_dir)[:2]
	if error != 0:
		return error

	# Parse out the P4CLIENT query
	p4clients = tempdata.strip().split(' ')[0].split('=')

	# Get the p4 user
	# Parse "P4USER=burgerbecky (config)"

	cmd = (p4exe, 'set', 'P4USER')
	if verbose:
		print(' '.join(cmd))
	error, tempdata = run_command(cmd, working_dir)[:2]
	if error != 0:
		return error

	# Parse out the P4USER query
	p4users = tempdata.strip().split(' ')[0].split('=')

	# Write out the header

	filep = StringIO()
	filep.write( \
		'/***************************************\n'
		'\n'
		'\tThis file was generated by a call to\n'
		'\tburger.buildutils.make_version_header() from\n'
		'\tthe burger python package\n'
		'\n'
		'***************************************/\n'
		'\n'
		'#ifndef {0}\n'
		'#define {0}\n'
		'\n'.format(headerguard))

	if len(p4changes) > 4:
		filep.write('#define P4_CHANGELIST ' + p4changes[1] + '\n')
		filep.write('#define P4_CHANGEDATE "' + p4changes[3] + '"\n')
		filep.write('#define P4_CHANGETIME "' + p4changes[4] + '"\n')

	if len(p4clients) > 1:
		filep.write('#define P4_CLIENT "' + p4clients[1] + '"\n')

	if len(p4users) > 1:
		filep.write('#define P4_USER "' + p4users[1] + '"\n')

	filep.write('\n#endif\n')

	# Check if the data is different than what's already stored on
	# the drive

	filevalue = filep.getvalue()
	del filep

	if compare_file_to_string(outputfilename, filevalue) is not True:
		if verbose:
			print('Writing ' + outputfilename)
		try:
			with open(outputfilename, 'w') as filep:
				filep.write(filevalue)
		except IOError as error:
			print(error)
			return 2
	return 0

########################################


def is_codewarrior_mac_allowed():
	"""
	Return True if this machine can run Codewarrior for Mac OS Carbon

	Test first if the host platform is a mac, and if so, test if it's
	capable of running Mac OS Carbon Codewarrior 9 or 10

	Returns:
		True if CodeWarrior for Mac OS can be run on this Macintosh

	See:
		host_machine()
	"""

	# Test if a mac

	if get_mac_host_type():
		# Get the Mac OS version number
		mac_ver = platform.mac_ver()
		release = mac_ver[0]

		# Convert 10.5.8 to 10.5

		digits = release.split('.')

		# Snow Leopard (10.6) supports Rosetta
		# Lion (10.7) and Mountain Lion (10.8) do not

		if float(digits[0]) >= 10:
			if float(digits[1]) < 7:
				return True

	# Can't run, not a mac or Power PC native or emulation isn't supported
	return False

########################################


def import_py_script(file_name, module_name=None):
	"""
	Manually load in a python file

	Load in a python script from disk and parse it, creating
	a .pyc file if needed and reading from a .pyc file if it exists.

	Note:
		The module returned will not be present in the sys.modules cache, this
		is by design to allow python files with the same name to be loaded
		from different directories without creating a cache collision

	Args:
		file_name: Name of the file to load
		module_name: Name of the loaded module for ``__name__``
	Returns:
		The imported python script object
	See:
		run_py_script()
	"""

	# If there's no module name, glean one from the filename
	if not module_name:
		module_name = os.path.splitext(os.path.split(file_name)[-1])[0]

	if PY3_5_OR_HIGHER:

		# Python 3.5 and allows the loading of a module without
		# touching the cache
		# pylint: disable=E0611, E0401, E1101
		import importlib.util
		spec = importlib.util.spec_from_file_location(module_name, file_name)
		result = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(result)

	else:
		# First step, if there's a module already loaded by this
		# name, save it for restoration later

		saved = None
		if module_name in sys.modules:
			saved = sys.modules[module_name]
			del sys.modules[module_name]

		# Perform the load, throw exception on error
		try:
			if PY3_3_OR_HIGHER:
				# Python 3.3 and 3.4 prefers using the SourceFileLoader class
				# pylint: disable=E0611, E0401
				from importlib.machinery import SourceFileLoader
				result = SourceFileLoader(module_name, file_name).load_module()

			else:
				# Use the imp library for Python 2.x to 3.2
				import imp
				result = imp.load_source(module_name, file_name)

		# Wrap up by restoring the cache the way it was found
		finally:
			if saved:
				sys.modules[module_name] = saved
			else:
				# Remove the generated entry since load_source() added it

				# Note: Test before deletion, in case load_source threw
				# an exception before creating the entry
				if module_name in sys.modules:
					del sys.modules[module_name]

	return result

########################################


def run_py_script(file_name, function_name=None, arg=None):
	"""
	Manually load and run a function in a python file

	Load in a python script from disk and execute a specific function.
	Returns the value returned from the loaded script.

	Note:
		The script will not be added to the module cache.

	Args:
		file_name: Name of the file to load
		function_name: Name of the function in the file to call
		arg: Argument to pass to the function
	Returns:
		The value returned from the python script.
	See:
		import_py_script()
	"""

	# If a function name wasn't passed, assume it's ``main``
	if not function_name:
		function_name = 'main'

	# Load in the script
	module = import_py_script(file_name)

	# Find the function and execute it
	method = getattr(module, function_name)
	if arg is None:
		return method()
	return method(arg)
