# Creates an exe for the MarkWrite GUI application using cx_freeze.
# Build with `python freezeApp.py build_exe`

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

import markwrite
import shutil
import sys, os

build_folder="MarkWrite v%s/MarkWrite"%markwrite.__version__

# Remove the build folder
shutil.rmtree(build_folder, ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)


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
      
shutil.copy("./MarkWrite.lnk", os.path.join(build_folder,'..','MarkWrite.lnk'))
