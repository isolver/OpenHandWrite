# Creates an exe for the MarkWrite GUI application using cx_freeze.
# Build with `python freezeApp.py build_exe`

import numpy
import glob

from cx_Freeze import setup, Executable
from cx_Freeze import hooks
def load_scipy_patched(finder, module):
    """the scipy module loads items within itself in a way that causes
        problems without the entire package and a number of other subpackages
        being present."""
    finder.IncludePackage("scipy._lib")  # Changed include from scipy.lib to scipy._lib
    finder.IncludePackage("scipy.misc")
hooks.load_scipy = load_scipy_patched

import markwrite
import shutil
import sys, os

build_folder="MarkWrite_v%s/MarkWrite"%markwrite.__version__

# Remove the build folder
shutil.rmtree(build_folder, ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

includes = ['numpy',
            'pyqtgraph',
            'PyQt4.QtCore',
            'PyQt4.QtGui',
            'sip',
            'pyqtgraph.graphicsItems',
            'atexit',
            'scipy.special._ufuncs_cxx',
            'scipy.sparse.csgraph._validation',
            'scipy.integrate.vode',
            'scipy.integrate.lsoda'
            ]
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
    'build_exe': build_folder,
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
      executables = [Executable(script="./runapp.py", targetName='MarkWrite.exe',base=base, icon = os.path.abspath("../markwrite/markwrite/resources/icons/markwrite_icon.ico"))])

#
## Copy extra files into MarkWrite_v exe folder
#

# Copy link to MarkWrite_v0.x.x.x.x/MarkWrite/MarkWrite.exe       
shutil.copy("./MarkWrite.lnk", os.path.join(build_folder,'..','MarkWrite.lnk'))

# Copy numpy dll's that cx_freeze seems to miss.....       
SRC_DLL_DIR = r"D:\DropBox\OpenHandWriteDistribution\OpenHandWrite\WinPython\python-2.7.10.amd64\Lib\site-packages\numpy\core"
DST_DIR = os.path.abspath(build_folder)
numpy_dlls = glob.glob(r"{}\*.dll".format(SRC_DLL_DIR))
print
for dllpath in numpy_dlls:
    shutil.copy2(dllpath,DST_DIR)
    print "Copying {} to {}".format(dllpath,DST_DIR)
print