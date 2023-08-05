#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains the code for the command line "buildme"
"""

## \package makeprojects.buildme

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import argparse
import subprocess
import burger

## List of watcom platforms to build
WATCOM_PLATFORM_LIST = [
	'dos4gw',
	'dosx32',
	'win32'
]

## List of default configurations to build

DEFAULT_CONFIGURATION_LIST = [
	'Debug',
	'Internal',
	'Release'
]

########################################


def build_rez_script(full_pathname, verbose):
	"""
	Build a rezfile using 'makerez'

	Execute the program 'makerez' to build the script.

	Args:
		full_pathname: Pathname to the *.rezscript to build
		verbose: True if verbose output
	Returns:
		0 if no error, non-zero on error

	"""
	# Create the build command
	cmd = ['makerez', burger.encapsulate_path(full_pathname)]
	if verbose:
		cmd.insert(1, '-v')
		print(' '.join(cmd))
	return subprocess.call(cmd, cwd=os.path.dirname(full_pathname), shell=True)

########################################


def build_slicer_script(full_pathname, verbose):
	"""
	Build slicer data

	Args:
		full_pathname: Pathname to the *.slicer to build
		verbose: True if verbose output
	Returns:
		0 if no error, non-zero on error
	"""
	# Create the build command
	cmd = ['slicer', burger.encapsulate_path(full_pathname)]
	if verbose:
		print(' '.join(cmd))
	return subprocess.call(cmd, cwd=os.path.dirname(full_pathname), shell=True)

########################################


def builddoxygen(fullpathname, verbose):
	"""
	Build Doxygen docs
	Return 0 if no error, non-zero on error
	"""
	# Is Doxygen installed?

	doxygenpath = burger.where_is_doxygen(verbose=verbose)
	if doxygenpath is None:
		return 0

	# Make the output folder for errors (If needed)

	tempdir = os.path.join(os.path.dirname(fullpathname), 'temp')
	burger.create_folder_if_needed(tempdir)
	bindir = os.path.join(os.path.dirname(fullpathname), 'bin')
	burger.create_folder_if_needed(bindir)
	# Location of the log file
	errorsfile = os.path.join(bindir, 'doxygenerrors.txt')

	# Create the build command
	if burger.get_windows_host_type():
		cmd = [doxygenpath, burger.encapsulate_path(fullpathname), \
			'2>', burger.encapsulate_path(errorsfile)]
		if verbose:
			print(' '.join(cmd))
		error = subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)
	else:
		with open(fullpathname, 'r') as filep:
			file_one_lines = filep.read().splitlines()
		tempdox = fullpathname + '.tempfile'
		with open(tempdox, 'w') as filep:
			filep.write('\n'.join(file_one_lines))

		# The mac version requires the file to have Linux line feeds!!!
		cmd = [doxygenpath, burger.encapsulate_path(tempdox), \
			'2>', burger.encapsulate_path(errorsfile)]
		if verbose:
			print(' '.join(cmd))
		error = subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)
		os.remove(tempdox)

	# If the error log has nothing, delete it
	if os.stat(errorsfile).st_size == 0:
		os.remove(errorsfile)

	return error

########################################


def buildwatcommakefile(results, fullpathname, verbose, fatal):
	"""
	Build Watcom MakeFile
	Return 0 if no error, non-zero on error
	"""

	# Is Watcom installed?
	watcompath = os.getenv('WATCOM')
	if watcompath is None:
		print(fullpathname + ' requires Watcom to be installed to build!')
		results.append((0, fullpathname))
		return 0

	# Create the build commands

	erroroccurred = 0
	oldpath = os.environ['PATH']
	os.environ['PATH'] = os.path.join(watcompath, 'binnt') + ';' + \
		os.path.join(watcompath, 'binw') + ';' + oldpath

	if fullpathname.endswith('.wmk'):
		cmd = '"' + os.path.join(watcompath, 'binnt', 'wmake') + '" -e -h -f "' + \
			fullpathname + '" all'
		if verbose:
			print(cmd)
		error = subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)
		results.append((error, fullpathname, 'all'))
		if error != 0:
			erroroccurred = 1
			if fatal:
				os.environ['PATH'] = oldpath
				return error

	else:
		for platform in WATCOM_PLATFORM_LIST:
			for target in DEFAULT_CONFIGURATION_LIST:

				cmd = '"' + os.path.join(watcompath, 'binnt', 'wmake') + \
					'" -e -h -f "' + fullpathname + \
					'" Target=' + target + ' Platform=' + platform
				if verbose:
					print(cmd)
				error = subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)
				results.append((error, fullpathname, platform + '|' + target))
				if error != 0:
					erroroccurred = 1
					if fatal:
						os.environ['PATH'] = oldpath
						return error

	os.environ['PATH'] = oldpath
	return erroroccurred

########################################


def parseslnfile(fullpathname):
	"""
	Given a .sln file for Visual Studio 8, 9 or 10
	locate and extract all of the build targets
	available and return the list
	It will also determine which version of Visual
	Studio this solution file requires
	"""
	# Start with an empty list

	visualstudio = 0
	secondtest = False
	targetlist = []

	filep = open(fullpathname)
	for line in filep:

		# Secondary version number

		if secondtest and '# Visual Studio' in line:
			# The number is in the last part of the line
			lineparts = line.rsplit()
			versionstring = lineparts[len(lineparts) - 1]
			# Use the version string to determine which visual studio to launch
			if versionstring == '2012':
				visualstudio = 12
			elif versionstring == '2013':
				visualstudio = 13
			elif versionstring == '14':
				visualstudio = 15
			elif versionstring == '15':
				visualstudio = 17
			secondtest = False

		# Get the version number

		if 'Microsoft Visual Studio Solution File' in line:

			# The number is in the last part of the line
			lineparts = line.rsplit()
			versionstring = lineparts[len(lineparts) - 1]
			# Use the version string to determine which visual studio to launch
			if versionstring == '8.00':
				visualstudio = 7
			elif versionstring == '9.00':
				visualstudio = 8
			elif versionstring == '10.00':
				visualstudio = 9
			elif versionstring == '11.00':
				visualstudio = 10
			elif versionstring == '12.00':
				visualstudio = 12
				secondtest = True

		# Look for this section. Immediately after it
		# has the targets
		if 'GlobalSection(SolutionConfigurationPlatforms)' in line:
			for item in filep:
				# Once the end of the section is reached, end
				if 'EndGlobalSection' in item:
					break
				# They are seperated by spaces
				lineparts = item.rsplit('=')
				# The first entry is the data needed
				targetlist.append(lineparts[0].strip())

	# Clean up and exit with the results
	filep.close()
	if visualstudio == 0:
		print('The visual studio solution file ' + fullpathname + \
			' is corrupt or an unknown version!')
	return (targetlist, visualstudio)

########################################


def buildvisualstudio(results, fullpathname, verbose, fatal):
	"""
	Build a visual studio .sln file
	Return 0 if no error or error ignored, non-zero if a fatal error
	"""

	# Get the list of build targets
	(targetlist, visualstudio) = parseslnfile(fullpathname)

	# Was the file corrupted?
	if visualstudio == 0:
		results.append((10, fullpathname))
		# The error message about corruption was already printed
		return 10

	vstudioenv = None
	if visualstudio == 7:
		# Is Visual studio 7 installed?
		vstudioenv = 'VS71COMNTOOLS'
	elif visualstudio == 8:
		# Is Visual studio 8 installed?
		vstudioenv = 'VS80COMNTOOLS'
	elif visualstudio == 9:
		# Is Visual studio 9 installed?
		vstudioenv = 'VS90COMNTOOLS'
	elif visualstudio == 10:
		# Is Visual studio 10 installed?
		vstudioenv = 'VS100COMNTOOLS'
	elif visualstudio == 12:
		# Is Visual studio 11 (2012) installed?
		vstudioenv = 'VS110COMNTOOLS'
	elif visualstudio == 13:
		# Is Visual studio 12 (2013) installed?
		vstudioenv = 'VS120COMNTOOLS'
	elif visualstudio == 15:
		# Is Visual studio 14 (2015) installed?
		vstudioenv = 'VS140COMNTOOLS'
	elif visualstudio == 17:
		# Is Visual studio 15 (2017) installed?
		vstudioenv = 'VS150COMNTOOLS'
	else:
		print(fullpathname + ' requires Visual Studio version ' + \
			str(visualstudio) + ' which is unsupported!')
		results.append((0, fullpathname))
		return 0

	# Is Visual studio installed?
	vstudiopath = os.getenv(vstudioenv)
	if vstudiopath is None:
		print(fullpathname + ' requires Visual Studio version ' + \
			str(visualstudio) + ' to be installed to build!')
		print('Environment variable ' + vstudioenv + ' error')
		results.append((0, fullpathname))
		return 0

	# Locate the launcher

	vstudiopath = os.path.abspath(vstudiopath + r'\..\ide\devenv')
	# Build each and every target
	xboxfail = False
	xbox360fail = False
	ps3fail = False
	ps4fail = False
	shieldfail = False
	androidfail = False
	erroroccurred = 0
	for target in targetlist:

		# Certain targets require an installed SDK
		# verify that the SDK is installed before trying to build

		targettypes = target.rsplit('|')

		# PS3
		if targettypes[1] == 'PS3':
			if os.getenv('SCE_PS3_ROOT') is None:
				ps3fail = True
				continue

		# PS4
		if targettypes[1] == 'ORBIS':
			if os.getenv('SCE_ORBIS_SDK_DIR') is None:
				ps4fail = True
				continue

		# Xbox 360
		if targettypes[1] == 'Xbox 360':
			if os.getenv('XEDK') is None:
				xbox360fail = True
				continue

		# Xbox Classic
		if targettypes[1] == 'Xbox':
			if os.getenv('XDK') is None:
				xboxfail = True
				continue

		# Android
		if targettypes[1] == 'Android':
			if os.getenv('ANDROID_NDK') is None:
				androidfail = True
				continue

		# nVidia Shield
		if targettypes[1] == 'Tegra-Android':
			if os.getenv('NV') is None:
				shieldfail = True
				continue

		# Create the build command
		cmd = '"' + vstudiopath + '" "' + fullpathname + '" /Build "' + target + '"'
		if verbose:
			print(cmd)
		sys.stdout.flush()
		error = subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)
		results.append((error, fullpathname, target))
		if error != 0:
			erroroccurred = 1
			if fatal:
				return error

	if xboxfail:
		print('Xbox classic project detected but XDK was not installed')

	if xbox360fail:
		print('Xbox 360 project detected but XEDK was not installed')

	if ps3fail:
		print('PS3 project detected but SCE_PS3_ROOT was not found')

	if ps4fail:
		print('PS4 project detected but SCE_ORBIS_SDK_DIR was not found')

	if shieldfail:
		print('nVidia Shield project detected but NV was not found')

	if androidfail:
		print('Android project detected but ANDROID_NDK was not found')

	return erroroccurred

########################################


def buildcodewarriormac(file_name, verbose):
	"""
	Build a Metrowerks Codewarrior file on MacOS
	Return 0 if no error, 1 if an error, 2 if
	Code Warrior was not found
	"""

	file_name_lower = file_name.lower()
	# Codewarrior version was not detected for Mac OSX
	if 'wii' in file_name_lower:
		return 0
	if 'nds' in file_name_lower:
		return 0
	if 'gcn' in file_name_lower:
		return 0

	if 'c10' in file_name_lower or 'c58' in file_name_lower:
		cwfile = '/Applications/Metrowerks CodeWarrior 10.0/' + \
			'Metrowerks CodeWarrior/CodeWarrior IDE 10'
	elif 'cw9' in file_name_lower or 'c50' in file_name_lower:
		cwfile = '/Applications/Metrowerks CodeWarrior 9.0/' + \
			'Metrowerks CodeWarrior/CodeWarrior IDE 9.6'
	else:
		print('Codewarrior version was not detected')
		return 0

	mytempdir = os.path.join(os.path.dirname(file_name), 'temp')
	error_file = os.path.basename(file_name)
	error_list = os.path.splitext(error_file)
	error_file = os.path.join(mytempdir, error_list[0] + '.err')

	# Make the output folder for errors (If needed)

	burger.create_folder_if_needed(mytempdir)

	# Create the build command

	cmd = 'cmdide -proj -bcwef "' + error_file + '" -y "' + cwfile + \
		'" -z Everything "' + file_name + '"'
	if verbose:
		print(cmd)
	sys.stdout.flush()
	error = subprocess.call(cmd, cwd=os.path.dirname(file_name), shell=True)
	return error

########################################


def buildcodewarriorwindows(file_name, verbose):
	"""
	Build a Metrowerks Codewarrior file on MacOS
	Return 0 if no error, 1 if an error, 2 if
	Code Warrior was not found
	"""

	file_name_lower = file_name.lower()
	# Don't use Codewarrior for Mac
	if 'mac' in file_name_lower:
		return 0

	# These targets build on Windows hosts
	if 'wii' in file_name_lower:
		print('Can\'t build ' + file_name + ' yet!')
		return 0
	elif 'nds' in file_name_lower:
		print('Can\'t build ' + file_name + ' yet!')
		return 0
	elif 'gcn' in file_name_lower:
		print('Can\'t build ' + file_name + ' yet!')
		return 0
	elif 'w32' in file_name_lower or 'win' in file_name_lower:
		cwfile = os.getenv('CWFolder')
		if cwfile is None:
			print('Can\'t build ' + file_name + \
				'! CWFolder not set to Codewarrior 9.4 for Windows!')
			return 0
		# Note: CmdIDE is preferred, however, Codewarrior 9.4 has a bug
		# that it will die horribly if the pathname to it
		# has a space, so ide is used instead.
		cwfile = os.path.join(cwfile, 'Bin', 'ide')
	else:
		print('Codewarrior version was not detected for ' + file_name)
		return 0

	mytempdir = os.path.join(os.path.dirname(file_name), 'temp')
	error_file = os.path.basename(file_name)
	error_list = os.path.splitext(error_file)
	error_file = os.path.join(mytempdir, error_list[0] + '.err')

	# Make the output folder for errors (If needed)

	burger.create_folder_if_needed(mytempdir)

	# Create the build command
	# /s New instance
	# /t Project name
	# /b Build
	# /c close the project after completion
	# /q Close Codewarrior on completion

	cmd = '"' + cwfile + '" "' + file_name + '" /t Everything /s /c /q /b'
	if verbose:
		print(cmd)
	sys.stdout.flush()
	error = subprocess.call(cmd, cwd=os.path.dirname(file_name), shell=True)
	return error

########################################


def parsexcodeprojdir(file_name):
	"""
	Given a .xcodeproj directory for XCode for MacOSX
	locate and extract all of the build targets
	available and return the list
	"""

	# Start with an empty list

	targetlist = []
	filep = open(os.path.join(file_name, 'project.pbxproj'))
	projectfile = filep.read().splitlines()
	filep.close()
	configurationfound = False
	for line in projectfile:
		# Look for this section. Immediately after it
		# has the targets
		if configurationfound is False:
			if 'buildConfigurations' in line:
				configurationfound = True
		else:
			# Once the end of the section is reached, end
			if ');' in line:
				break
			# Format 1DEB923608733DC60010E9CD /* Debug */,
			lineparts = line.rsplit()
			# The third entry is the data needed
			targetlist.append(lineparts[2])

	# Exit with the results
	return targetlist

########################################


def buildxcode(results, file_name, verbose, ignoreerrors):
	"""
	Build a Mac OS X XCode file
	Return 0 if no error, 1 if an error, 2 if
	XCode was not found
	"""

	# Get the list of build targets
	targetlist = parsexcodeprojdir(file_name)
	file_name_lower = file_name.lower()
	# Use XCode 3 off the root
	if 'xc3' in file_name_lower:
		# On OSX Lion and higher, XCode 3.1.4 is a separate folder
		xcodebuild = '/Xcode3.1.4/usr/bin/xcodebuild'
		if not os.path.isfile(xcodebuild):
			# Use the pre-Lion folder
			xcodebuild = '/Developer/usr/bin/xcodebuild'
	# Invoke XCode 4 or higher from the app store
	else:
		xcodebuild = '/Applications/Xcode.app/Contents/Developer/usr/bin/xcodebuild'

	# Is this version of XCode installed?
	if os.path.isfile(xcodebuild) is not True:
		print('Can\'t build ' + file_name + \
			', the proper version of XCode is not installed')
		results.append((0, file_name))
		return 0

	# Build each and every target
	for target in targetlist:
		# Create the build command
		cmd = xcodebuild + ' -project "' + os.path.basename(file_name) + \
			'" -alltargets -parallelizeTargets -configuration "' + target + '"'
		if verbose:
			print(cmd)
		sys.stdout.flush()
		error = subprocess.call(cmd, cwd=os.path.dirname(file_name), shell=True)
		results.append((error, file_name, target))
		if error != 0:
			if ignoreerrors is False:
				return error

	return 0

########################################


def buildcodeblocks(fullpathname, verbose):
	"""
	Build a Codeblocks project

	Commands available as of 13.12
	--safe-mode
	--no-check-associations
	--no-dde
	--no-splash-screen
	--multiple-instance
	--debug-log
	--no-crash-handler
	--verbose
	--no-log
	--log-to-file
	--debug-log-to-file
	--rebuild
	--build
	--clean
	--target=
	--no-batch-window-close
	--batch-build-notify
	--script=
	--file=
	"""

	if burger.get_windows_host_type() is not False:
		if fullpathname.endswith('osx.cbp'):
			return 0
		# Is Codeblocks installed?
		codeblockspath = os.getenv('CODEBLOCKS')
		if codeblockspath is None:
			print(fullpathname + ' requires Codeblocks to be installed to build!')
			return 0
		codeblockspath = os.path.join(codeblockspath, 'codeblocks')
		codeblocksflags = '--no-check-associations --no-dde --no-batch-window-close'
	else:
		if not fullpathname.endswith('osx.cbp'):
			return 0

		codeblockspath = '/Applications/Codeblocks.app/Contents/MacOS/CodeBlocks'
		codeblocksflags = '--no-ipc'
	# Create the build command
	cmd = '"' + codeblockspath + '" ' + codeblocksflags + \
		' --no-splash-screen --build "' + \
		fullpathname + '" --target=Everything'
	if verbose:
		print(cmd)
	print(cmd)
	print('Codeblocks is currently broken. Disabled for now')
	return 0
	# return subprocess.call(cmd, cwd=os.path.dirname(fullpathname), shell=True)

########################################


def addproject(projects, file_name):

	"""
	Detect the project type and add it to the list
	"""
	# Only process project files

	base_name = os.path.basename(file_name)
	base_name_lower = base_name.lower()
	projecttype = None
	priority = 50
	if base_name_lower == 'prebuild.py':
		projecttype = 'python'
		priority = 1
	elif base_name_lower.endswith('.slicerscript'):
		projecttype = 'slicer'
		priority = 20
	elif base_name_lower.endswith('.rezscript'):
		projecttype = 'makerez'
		priority = 25
	elif base_name_lower == 'custombuild.py':
		projecttype = 'python'
		priority = 40
	elif base_name_lower.endswith('.sln'):
		projecttype = 'visualstudio'
		priority = 45
	elif base_name_lower.endswith('.mcp'):
		projecttype = 'codewarrior'
	elif base_name_lower == 'makefile' or base_name_lower.endswith('.wmk'):
		projecttype = 'watcommakefile'
	elif base_name_lower.endswith('.xcodeproj'):
		projecttype = 'xcode'
	elif base_name_lower.endswith('.cbp'):
		projecttype = 'codeblocks'
	elif base_name_lower == 'doxyfile':
		projecttype = 'doxygen'
		priority = 90
	elif base_name_lower == 'postbuild.py':
		projecttype = 'python'
		priority = 99

	if projecttype is not None:
		projects.append((file_name, projecttype, priority))
		return True
	return False

########################################


def getprojects(projects, working_dir):
	"""
	Scan a folder for files that need to be 'built'
	"""
	#
	# Get the list of files in this directory
	#

	for base_name in os.listdir(working_dir):
		file_name = os.path.join(working_dir, base_name)
		addproject(projects, file_name)

########################################


def recursivegetprojects(projects, working_dir):
	"""
	Recursively scan a folder and look for any project files than need to
	be built. Returns all files in the list "projects"
	"""
	# Iterate through this folder and build the contents

	getprojects(projects, working_dir)

	for base_name in os.listdir(working_dir):
		base_name_lower = base_name.lower()

		# Skip known folders that contain temp files and not potential projects
		if base_name_lower == 'temp':
			continue
		if base_name_lower == 'bin':
			continue
		if base_name_lower == 'appfolder':
			continue
		# Xcode folders don't have subprojects inside
		if base_name_lower.endswith('.xcodeproj'):
			continue
		# Codewarrior droppings (Case sensitive)
		if base_name.endswith('_Data'):
			continue
		if base_name.endswith(' Data'):
			continue
		file_name = os.path.join(working_dir, base_name)

		# Handle the directories found
		if os.path.isdir(file_name):
			recursivegetprojects(projects, file_name)

########################################


def main(working_dir=None):
	"""
	Command line shell
	"""

	if working_dir is None:
		working_dir = os.getcwd()
	# Don't clutter my system with pyc files
	sys.dont_write_bytecode = True

	# Was Burgerlib already installed?

	# sdks = burger.get_sdks_folder()

	# Where is perforce?

	# perforce = burger.where_is_p4()

	# Failsafe to make sure clean is only run from within
	# the Burgerlib projects folder

	# if (not working_dir.lower().startswith(rootPath.lower())):
	# print 'build can only be run from within the "' + rootPath + '" folder'
	# return -1

	# Parse the command line

	parser = argparse.ArgumentParser( \
		description='Build project files. Copyright by Rebecca Ann Heineman. ' + \
		'Builds *.sln, *.mcp, *.cbp, *.rezscript, *.slicerscript, doxyfile, ' + \
		'makefile and *.xcodeproj files')
	parser.add_argument('-r', dest='recursive', action='store_true', \
		default=False, help='Perform a recursive build.')
	parser.add_argument('-f', dest='fatal', action='store_true', \
		default=False, help='Quit immediately on any error.')
	parser.add_argument('-d', dest='directories', action='append', \
		help='List of directories to build in.')
	parser.add_argument('-docs', dest='documentation', action='store_true', \
		default=False, help='Compile Doxyfile files.')
	parser.add_argument('-v', '-verbose', dest='verbose', action='store_true', \
		default=False, help='Verbose output.')
	parser.add_argument('args', nargs=argparse.REMAINDER, \
		help='project filenames')

	args = parser.parse_args()

	verbose = args.verbose

	#
	# List of files to build
	#

	projects = []

	#
	# Get the list of directories to process
	#

	directories = args.directories
	if not directories:
		# Use the current working directory instead
		directories = [working_dir]
		if args.recursive is not False:

			#
			# If any filenames were passed, add them to the possible projects list
			#

			if args.args:
				for file_name in args.args:
					projectname = os.path.join(working_dir, file_name)
					if addproject(projects, os.path.join(working_dir, projectname)) is False:
						print('Error: ' + projectname + ' is not a known project file')
						return 10

	#
	# Create the list of projects that need to be built
	#

	if not projects:
		for my_dir_name in directories:
			if not args.recursive:
				getprojects(projects, my_dir_name)
			else:
				recursivegetprojects(projects, my_dir_name)

	#
	# If the list is empty, just exit now
	#

	if not projects:
		print('Nothing to build')
		return 0

	#
	# Sort the list by priority (The third parameter is priority from 1-99
	#
	projects = sorted(projects, key=lambda entry: entry[2])

	#
	# Let's process each and every file
	#

	#
	# args.documentation exists because building Doxygen files
	# are very time consuming
	#

	results = []
	anerroroccured = False
	for project in projects:
		fullpathname = project[0]
		projecttype = project[1]
		error = 0

		# Is it a python script?

		if projecttype == 'python':
			if os.path.isfile(fullpathname):
				if verbose:
					print('Invoking ' + fullpathname)
				error = burger.run_py_script(fullpathname, 'main', os.path.dirname(fullpathname))
				results.append((error, fullpathname))

		# Is it a slicer script?

		elif projecttype == 'slicer':
			if os.path.isfile(fullpathname):
				error = build_slicer_script(fullpathname, verbose)
				results.append((error, fullpathname))

		# Is it a makerez script?

		elif projecttype == 'makerez':
			if os.path.isfile(fullpathname):
				error = build_rez_script(fullpathname, verbose)
				results.append((error, fullpathname))

		# Is this a doxygen file?

		elif projecttype == 'doxygen':
			if args.documentation is True:
				if os.path.isfile(fullpathname):
					error = builddoxygen(fullpathname, verbose)
					results.append((error, fullpathname))

		# Is this a Watcom Makefile?

		elif projecttype == 'watcommakefile':
			if burger.get_windows_host_type() is not False:
				if os.path.isfile(fullpathname):
					error = buildwatcommakefile(results, fullpathname, verbose, args.fatal)

		# Visual studio solution files?

		elif projecttype == 'visualstudio':
			if burger.get_windows_host_type() is not False:
				if os.path.isfile(fullpathname):
					error = buildvisualstudio(results, fullpathname, verbose, args.fatal)

		# Metrowerks Codewarrior files?

		elif projecttype == 'codewarrior':
			if os.path.isfile(fullpathname):
				if burger.get_windows_host_type() is not False:
					error = buildcodewarriorwindows(fullpathname, verbose)
					results.append((error, fullpathname, 'Everything'))
				elif burger.is_codewarrior_mac_allowed():
					error = buildcodewarriormac(fullpathname, verbose)
					results.append((error, fullpathname, 'Everything'))

		# XCode project file?
		elif projecttype == 'xcode':
			if burger.get_mac_host_type() is not False:
				if os.path.isdir(fullpathname):
					error = buildxcode(results, fullpathname, verbose, True)

		# Codeblocks project file?
		elif projecttype == 'codeblocks':
			if os.path.isfile(fullpathname):
				error = buildcodeblocks(fullpathname, verbose)
				results.append((error, fullpathname, 'Everything'))

		# Abort on error?
		if error != 0:
			anerroroccured = True
			if args.fatal:
				break

	# List all the projects that failed

	if not anerroroccured:
		print('Build successful!')
		error = 0
	else:
		print('Errors detected in the build.')
		for entry in results:
			# Only print entries that failed
			if entry[0] != 0:
				output = 'Error %d in file %s' % (entry[0], entry[1])
				if len(entry) == 3:
					output = output + ' target ' + entry[2]
				print(output)
		if error == 0:
			error = 10
	return error


# If called as a function and not a class,
# call my main

if __name__ == "__main__":
	sys.exit(main())
