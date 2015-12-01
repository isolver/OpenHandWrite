# Creates an exe for the MarkWrite application using cx_freeze.
# Build with `python freezeApp.py build_exe`
from cx_Freeze import setup, Executable

import shutil
from glob import glob
# Remove the build folder
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
import sys
import markwrite

includes = ['PyQt4.QtCore', 'PyQt4.QtGui', 'sip', 'pyqtgraph.graphicsItems',
            'numpy', 'atexit']
excludes = ['cvxopt','_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
    'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl','tables',
    'Tkconstants', 'Tkinter', 'zmq','PySide','pysideuic','scipy','matplotlib']

includefiles =['markwrite/resources','test_data', 'customreports.py']
if sys.version[0] == '2':
    # causes syntax error on py2
    excludes.append('PyQt4.uic.port_v3')

base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    'build_exe': 'build/MarkWrite',
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
      executables = [Executable(script="./markwrite/runapp.py", targetName='MarkWrite.exe',base=base)])


