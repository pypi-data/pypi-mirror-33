#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package that contains file manipulation functions
"""

## \package burger.fileutils

from __future__ import absolute_import, print_function, unicode_literals

import errno
import os
import shutil
import stat
from .strutils import is_string, encapsulate_path
from .buildutils import perforce_edit, host_machine, get_windows_host_type


########################################


def is_write_protected(path_name):
	"""
	Test if a file is write protected

	If the file/directory exists, it is tested if it's
	write protected. If it exists and is write protected,
	True is returned, otherwise False is returned.

	Args:
		path_name: Path name to the file/directory

	Returns:
		True if the file exists and is write protected
	"""

	try:
		# Get the status of the file
		path_mode = os.stat(path_name).st_mode

		# Return True if write protected
		return not path_mode & stat.S_IWRITE

	# Don't throw if the file didn't exist
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise
	return False

########################################


def make_executable(exe_path):
	"""
	Set the executable flag to true on a file

	Args:
		exe_path: Pathname to the executable to fix up.

	"""

	# Get the Read access bits and copy them to the X flags
	exe_mode = os.stat(exe_path).st_mode
	exe_mode |= (exe_mode & 0x124) >> 2
	os.chmod(exe_path, exe_mode)

########################################


def create_folder_if_needed(path):
	"""
	Given a pathname to a folder, detect if the folder exists, if not, create it.

	Call os.makedirs(path) but does not throw an
	exception if the directory already exists. All other exceptions
	are passed through with raise.

	Args:
		path: A string object with the pathname.

	See:
		delete_directory()
	"""

	try:
		os.makedirs(path)
	except OSError as error:
		if error.errno != errno.EEXIST:
			raise

########################################


def delete_file(filename):
	"""
	Given a pathname to a file, delete it.

	If the file doesn't exist, it will return without raising
	an exception.

	Args:
		filename: A string object with the filename
	See:
		delete_directory()
	"""

	try:
		os.remove(filename)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise

########################################


def is_source_newer(source, destination):
	"""
	Return False if the source file is older then the destination file

	Check the modification times of both files to determine if the
	source file is newer. If the destination file is older or doesn't exist
	True is returned.

	Return False if destination is newer, not False if not.

	Examples:
		result = burger.fileutils.is_source_newer('file.c', 'file.obj')

		if result == 2:
			build_file_c()

		if result:
			compile('file.c', 'file.obj')
		else:
			print('Already built')

	Note:
		If the source file does not exist, the function will return 2.
		This is to allow proper error checking if the source is required
		to exist.

	Args:
		source: string pathname of the file to test
		destination: string pathname of the file to test against

	Returns:
		False if not newer, True if newer, 2 if there is no source file
	"""

	# Get the source file's modification time, If there's no source file, return 2
	try:
		srctime = os.path.getmtime(source)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise
		return 2

	# Get the destination file's modification time, if missing return True
	try:
		desttime = os.path.getmtime(destination)
	except OSError as error:
		if error.errno != errno.ENOENT:
			raise
		return True

	# Is the source older or equal? Return False to not update the destination
	if srctime <= desttime:
		return False
	return True

########################################


def copy_file_if_needed(source, destination, verbose=True, perforce=False):
	"""
	Copy a file only if newer than the destination.

	Copy a file only if the destination is missing or is older than the source
	file.

	Args:
		source: string pathname of the file to copy from
		destination: string pathname of the file to copy to
		verbose: True if print output is desired
		perforce: True if Perforce 'p4 edit' should be done on the destination.

	Returns:
		Zero if no error otherwise IOError.errno

	See:
		is_source_newer()
	"""

	# If there is a destination file, check the modification times
	# and check with 'is True' to ensure source exists

	if is_source_newer(source, destination) is True:

		# Alert perforce that the file is to be modified
		if perforce and is_write_protected(destination):
			perforce_edit(destination, verbose=verbose)

		# Copy the file
		if verbose:
			print('Copying {0} -> {1}'.format(source, destination))
		try:
			shutil.copyfile(source, destination)
		except IOError as error:
			print(error)
			return error.errno
	return 0

########################################


def copy_directory_if_needed(source, destination, exception_list=None, \
	verbose=True):

	"""
	Copy all of the files in a directory into a new directory

	Creating any necessary directories in the process, and it
	will skip files with specific extensions

	Note:
		This is a recursive function

	Args:
		source: string pathname of the directory to copy from
		destination: string pathname of the directory to copy to
		exception_list: optional list of file extensions to ignore during copy
		verbose: True if print output is desired

	Returns:
		Zero if no error, non-zero on error

	See:
		copy_file_if_needed(), create_folder_if_needed()
	"""

	# Ensure there is an exception list, even if empty
	if exception_list is None:
		exception_list = []

	# Make sure the output folder exists
	create_folder_if_needed(destination)

	# Iterate over the directory list
	for base_name in os.listdir(source):
		for item in exception_list:
			if base_name.endswith(item):
				break
		else:

			# Perform the copy of the entry
			file_name = os.path.join(source, base_name)

			# Handle the directories found
			if os.path.isdir(file_name):
				# Recursive!
				error = copy_directory_if_needed(file_name, \
					os.path.join(destination, base_name), exception_list, verbose=verbose)
			else:
				error = copy_file_if_needed(file_name, os.path.join( \
					destination, base_name), verbose=verbose)

			# Exit immediately on error
			if error != 0:
				return error
	return 0

########################################


def shutil_readonly_cb(func, path, exception_info):

	"""
	Subroutine for shutil.rmtree() to delete read only files

	shutil.rmtree() raises an exception if there are read
	only files in the directory being deleted. Use this
	callback to allow read only files to be disposed of.

	Examples:
		import burger
		import shutil

		shutil.rmtree(PATH_TO_DIRECTORY,onerror = burger.shutil_readonly_cb)

	Note:
		This is a callback function

	Args:
		func: Not used
		path: pathname of the file that is read only
		exception_info: Information about the exception

	See:
		delete_directory()
	"""

	# File not found? Ignore
	value = exception_info[1]
	if value.args[0] == errno.ENOENT:
		return

	# Read only?
	# EACCESS for Linux/MacOSX, EIO for Windows

	if value.args[0] == errno.EACCES or value.args[0] == errno.EIO:

		# Mark as writable and try again to delete the file
		os.chmod(path, stat.S_IWRITE)
		os.unlink(path)

########################################


def delete_directory(path, delete_read_only=False):
	"""
	Recursively delete a directory

	Delete a directory and all of the files and directories within.

	Args:
		path: Pathname of the directory to delete
		delete_read_only: True if read only files are to be deleted as well

	See:
		shutil_readonly_cb() or create_folder_if_needed()
	"""

	if delete_read_only:
		shutil.rmtree(path, onerror=shutil_readonly_cb)
	else:
		shutil.rmtree(path, ignore_errors=True)

########################################


def get_tool_path(tool_folder, tool_name, encapsulate=False):

	"""
	Find executable tool directory

	For allowing builds on multiple operating system hosts under the Burgerlib
	way of project management, it's necessary to query what is the host
	operating system and glean out which folder to find a executable compiled
	for that specific host

	Args:
		tool_folder: Pathname to the folder that contains the executables
		tool_name: Bare name of the tool (Windows will append '.exe')
		encapsulate: False if a path is requested, True if it's quoted to be
			used as a string to be sent to command line shell

	Returns:
		Full pathname to the tool to execute
	"""

	host = host_machine()

	# Macosx uses fat binaries
	if host == 'macosx':
		exename = os.path.join(tool_folder, 'macosx', tool_name)

	# Linux is currently just 64 bit Intel, will have to update
	# as more platforms are supported
	elif host == 'linux':
		exename = os.path.join(tool_folder, 'linux', tool_name)

	# Windows supports 32 and 64 bit Intel
	elif host == 'windows':
		exename = os.path.join(tool_folder, 'windows_' + get_windows_host_type(), \
			tool_name + '.exe')
	else:

		# On unknown platforms, assume the tool is in the path for the fallback
		exename = tool_name

	# Encase in quotes to handle spaces in filenames

	if encapsulate:
		return encapsulate_path(exename)
	return exename

########################################


def traverse_directory( \
	working_dir, filename_list, terminate=False, find_directory=False):

	"""
	Create a list of all copies of a file following a directory

	Starting with a working directory, test if a file exists
	and if so, insert it into a list. The list will be
	starting from the root with the last entry
	being at the working directory

	Args:
		working_dir: string with the path of the folder to start the search
		filename_list: string or an iterable of strings with the name(s)
			of the file(s) to find in the scanned folders
		terminate: True if searching will end on the first found file
		find_directory: True if searching for directories instead of files.
	Returns:
		List of pathnames (With filename appended)
	"""

	# Ensure that if the input was a string, that it becomes
	# an iterable to work below
	if is_string(filename_list):
		filename_list = (filename_list,)

	# Convert into a unpacked pathname
	tempdir = os.path.abspath(working_dir)

	dirlist = []

	# Loop
	while 1:
		# Iterate over the list and detect if these files are present
		for item in filename_list:
			temppath = os.path.join(tempdir, item)
			if find_directory:
				if os.path.isdir(temppath):
					# Insert at the beginning
					dirlist.insert(0, temppath)
					if terminate:
						return dirlist

			elif os.path.isfile(temppath):
				# Insert at the beginning
				dirlist.insert(0, temppath)
				if terminate:
					return dirlist

		# Pop a folder
		tempdir2 = os.path.dirname(tempdir)
		# Already at the top of the directory?
		if tempdir2 is None or tempdir2 == tempdir:
			break
		# Use the new folder
		tempdir = tempdir2

	# Return the list of files
	return dirlist

########################################


def unlock_files(working_dir, recursive=False):
	"""
	Iterate over a directory and unlock all read-only files.

	This function will generate a list of fully qualified pathnames
	of every file that was unlocked. Directories will be skipped.

	Examples:
		# Any file that is read only in this directory is now unlocked
		lock_list = unlock_files("~/projects/lockedfiles")

		# Do stuff on the files
		do_code_on_unlocked_files()

		# Re-lock all the files that were unlocked.
		lock_files(lock_list)

	Args:
		working_dir: Pathname to the directory to traverse for read-only files
		recursive: False (default) don't recurse through folders, True, recurse
	Returns:
		A list object with the name of every file that was unlocked.

	See:
		lock_files()

	"""

	# Ensure the pathname is unmangled
	abs_dir = os.path.abspath(working_dir)

	# Iterate over the directory
	result = []
	for item in os.listdir(abs_dir):
		path_name = os.path.join(abs_dir, item)

		# Get the status of the file
		path_mode = os.stat(path_name).st_mode

		# Process files
		if path_mode & stat.S_IFREG:

			# Only care about write protected files
			if not path_mode & stat.S_IWRITE:

				# Remove write protection while retaining the other flags
				os.chmod(path_name, path_mode + stat.S_IWRITE + \
					stat.S_IWGRP + stat.S_IWOTH)
				result.append(path_name)
		else:
			# Process recursion
			if recursive and path_mode & stat.S_IFDIR:
				result += unlock_files(path_name, True)
	return result


########################################


def lock_files(lock_list):
	"""
	Iterate over the input list and mark all files as read-only

	Args:
		lock_list: Iterable object containing a list of path names to files
			or directories to mark as "read-only"
	See:
		unlock_files()
	"""
	for item in lock_list:

		# Get the status of the file
		path_mode = os.stat(item).st_mode

		# Mark it write protected for Perforce
		os.chmod(item, path_mode & \
			(~(stat.S_IWRITE + stat.S_IWGRP + stat.S_IWOTH)))
