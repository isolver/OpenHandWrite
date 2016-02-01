# Creates an exe for the MarkWrite GUI application using cx_freeze.
# Build with `python freezeApp.py build_exe`
# !!! Requires:
#      1. Must use my (Sol's) WinPython-32bit-2.7.6.0 python env. 
#      2. Use of psychopy_with_cx_freeze_needed_fixes.zip as psychopy folder in site-packages
#         so anytime psychopy source is rebuilt for WinPython-32bit-2.7.6.0
#           changes need to be reapplied. 

from cx_Freeze import setup, Executable

import numpy

from cx_Freeze import hooks

def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")

hooks.load_scipy = load_scipy_patched

import shutil
# Remove the build folder
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
import sys, os
import markwrite

includes = ['pyqtgraph','PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'pyqtgraph.graphicsItems',
            'numpy', 'atexit','scipy.special._ufuncs_cxx',
            'scipy.sparse.csgraph._validation',
            'scipy.integrate.vode',
            'scipy.integrate.lsoda']
excludes = ['cvxopt','_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 
            'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs', 
            'tcl','Tkconstants', 'Tkinter', 'zmq','PySide',
            'pysideuic','matplotlib','collections.abc']

includefiles =['../markwrite/markwrite/resources','../../distribution/MarkWrite/test_data']

if sys.version[0] == '2':
    # causes syntax error on py2
    excludes.append('PyQt4.uic.port_v3')    
base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    'build_exe': 'build_exe/MarkWrite',
    'excludes': excludes,
    'includes':includes,
    'include_msvcr':True,
    'compressed':True,
    'copy_dependent_files':True,
    'create_shared_zip':True,
    'include_files':includefiles,
    'include_in_shared_zip':True,
    'optimize':2}

setup(name = "MarkWrite",
      version = markwrite.__version__,
      description = "MarkWrite Application",
      options = {"build_exe": build_exe_options},
      executables = [Executable(script="./runapp.py", targetName='MarkWrite.exe',base=base)])

"""
import os
import shutil
import stat
def copytree(src, dst, symlinks = False, ignore = None):
  if not os.path.exists(dst):
    os.makedirs(dst)
    shutil.copystat(src, dst)
  lst = os.listdir(src)
  if ignore:
    excl = ignore(src, lst)
    lst = [x for x in lst if x not in excl]
  for item in lst:
    s = os.path.join(src, item)
    d = os.path.join(dst, item)
    if symlinks and os.path.islink(s):
      if os.path.lexists(d):
        os.remove(d)
      os.symlink(os.readlink(s), d)
      try:
        st = os.lstat(s)
        mode = stat.S_IMODE(st.st_mode)
        os.lchmod(d, mode)
      except:
        pass # lchmod not available
    elif os.path.isdir(s):
      copytree(s, d, symlinks, ignore)
    else:
      shutil.copy2(s, d)
      
#source_resources_dir = os.path.abspath(os.path.join('.', 'markwrite/resources'))
#target_resources_dir = os.path.abspath(os.path.join('.',build_exe_options['build_exe'],'resources'))
#print ("Copying folder {} to {}".format(source_resources_dir,target_resources_dir)) 
#copytree(source_resources_dir,target_resources_dir)

"""
