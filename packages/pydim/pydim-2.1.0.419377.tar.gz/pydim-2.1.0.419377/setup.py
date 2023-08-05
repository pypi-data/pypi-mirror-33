'''
\brief This is the configuration file that is also used to build the package.
It uses the standard distutils Python module to provide a platform independent
build mechanism
'''
from setuptools import setup, Extension
import setuptools
import os, sys
import os.path as path

# ###########################################################################
def getOS():
  if os.getenv('OS'):
      os_name = os.getenv('OS')
      '''Building DIM depends on $OS. If this is wrongly set then building DIM
  doesn't work and the installation will fail...
      '''
  else:
      os_name = os.uname()[0].lower()
  return os_name

# ###########################################################################

# The operating system (inherited from the environment if it exist). Possible
# variables include 'linux' and 'windows'
OS = getOS()


# With which libraries pydim should be linked
#LIBRARIES = ['dim', 'dl']
LIBRARIES = ['dim']
#
# Use the following variable if you need to pass any special options to the
# compiler.
#
COMPILE_ARGS = []
if OS.lower().find('win') > -1:
    # we have some sort of a windows machine
    COMPILE_ARGS += ['-DWIN32','-D__DEBUG', '-DDEBUG']
    #COMPILE_ARGS += ['-DWIN32']
    LIBRARIES.append('ws2_32')

else:
    LIBRARIES.append('dl')
#    COMPILE_ARGS += [ '-Wno-deprecated']
#    COMPILE_ARGS += ['-g', '-O0', '-D__DEBUG', '-DDEBUG', '-fno-inline', '-fno-default-inline']


# This can be used to build in debug mode and/or profiling. The internal debug
# of the DIM wrapper can be turned on using the -DDEBUG. For example:
#
#
# Additional compile flags can be set using the CFLAGS environment variable or
# by creating a Setup file with the complementary instructions:
#
# http://docs.python.org/install/index.html#tweaking-compiler-linker-flags
#

# ###########################################################################
# Although we should already have all the build info by this point we can
# still do a bit of guess work to find the DIM location(s). Building DIM
# usually creates some environment variables that we can search for.

# The expected location for the DIM.
dim_dir = None

# The expected location for the DIM headers is in DIM_HOME/dim.
dim_include_dirs = []

# The location where the DIM library (libdim.so on linux or dim.dll on Windows)
dim_library_dirs = []

# The following environment variables will be used looking for the Dim installation
dim_env_vars = ('DIMDIR', 'DIMHOME', 'DIM_HOME')
for dim_var in dim_env_vars:

    if os.getenv(dim_var):
      dim_dir = os.getenv(dim_var)
      dim_include_dirs = [dim_dir, os.path.join(dim_dir, 'dim')]
      dim_library_dirs = [dim_dir, os.path.join(dim_dir, 'bin'),os.path.join(dim_dir, OS)]

if not dim_include_dirs and not dim_library_dirs:
    dim_dir = path.join(os.getcwd(), '..', 'dim')
    if path.exists(dim_dir):
      dim_include_dirs = [dim_dir, os.path.join(dim_dir, OS)]
      dim_library_dirs = [dim_dir, os.path.join(dim_dir, 'dim')]
    else:
      dim_dir = None

#Adding the usual library and platform include paths
# Only for linux right now...
if not dim_include_dirs and os.sys.platform == 'linux2':
    dim_include_dirs = [ '/usr/local/include/dim' ]
if not dim_library_dirs and os.sys.platform == 'linxu2':
    if os.uname()[4] == 'x86_64':
        dim_library_dirs = [ '/usr/local/lib64/' ]
    else:
        dim_library_dirs = [ '/usr/local/lib' ]

#INCLUDE_DIRS = [ '/usr/local/include',
#                      '/usr/include/dim', '/usr/local/include/dim']

#LIBRARY_DIRS = [
#                      '/usr/lib/dim', '/usr/lib64/dim',
#                      '/usr/local/lib', '/usr/local/lib64',
#                      '/usr/local/lib/dim', '/usr/local/lib64/dim']

# ##############################################################################
# The final building parameters
cwd = os.getcwd()
include_dirs = dim_include_dirs# + INCLUDE_DIRS
include_dirs.append(os.path.join(cwd, 'src'))
include_dirs.append(os.path.join(cwd, 'dimbrowser'))
library_dirs = dim_library_dirs# + LIBRARY_DIRS
compile_args = COMPILE_ARGS
libraries = LIBRARIES
platform = sys.platform
version = open('./VERSION').read().strip()

################################################################################
#Printing the final variables and building the package
print 80*'-'
print 'Welcome to the DIM Python interface module (PyDIM) installer.'
print 80*'-'
print 'Using variables:'
print 'DIM dirs: %s' % dim_dir
print 'OS: %s' % OS
print 'Include dirs: %s' %include_dirs
print 'Library dirs: %s' %library_dirs
print 'Compile args: %s' %compile_args
print 80*'-'

dimmodule = Extension('dimc',
                      sources = ['src/dimmodule.cpp','src/pydim_utils.cpp'],
                      include_dirs = include_dirs,
                      libraries = libraries,
                      library_dirs = library_dirs,
                      extra_compile_args = compile_args
                     )
dimmodule_cpp = Extension('dimcpp',
                      sources = ['src/dimcppmodule.cpp', 'src/pydim_utils.cpp'],
                      include_dirs = include_dirs,
                      libraries = libraries,
                      library_dirs = library_dirs,
                      extra_compile_args = compile_args
                      )
dimbrowsermodule = Extension('dimbrowserwrappercpp',
                      sources = ['dimbrowser/dimbrowserwrapper.cpp'],
                      include_dirs = include_dirs,
                      libraries = libraries,
                      library_dirs = library_dirs,
                      extra_compile_args = compile_args
                      )


setup(name = 'pydim',
      version = version,
      description = 'Python interface package for DIM C and C++ interfaces.',
      long_description = 'The PyDIM package exposes the DIM C and C++ functions and classes in Python.',
      license='GPL',
      url = 'http://lhcbdoc.web.cern.ch/lhcbdoc/pydim/index.html',
      author = 'Niko Neufeld (originally by Radu Stoica)',
      author_email = 'niko.neufeld@cern.ch',
      py_modules = ['pydim/__init__', 'pydim/debug','dimbrowser/__init__','dimbrowser/dimbrowser'],
      ext_modules = [dimmodule_cpp, dimmodule,dimbrowsermodule],
      packages=setuptools.find_packages(),
      scripts = [],
      python_requires='<3'
     )
# And now we should have a happy user :-)
# ##############################################################################
