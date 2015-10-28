# -*- coding: utf-8 -*-
from __future__ import division
#
# This file is part of the open-source MarkWrite application.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
if sys.platform == 'win32':
    # Work around so that MarkWrite app icon is also used as task bar icon.
    # http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
    import ctypes
    myappid = u'isolver.markwrite.editor.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Need to import pyTables module before pyqt imports pyh5 or error occurs when
# openning an iohub datastore file.
import tables

import pyqtgraph as pg
# # Switch to using white background and black foreground

from pyqtgraph.Qt import QtGui
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.appdirs import AppDirs
from markwrite.file_io import readPickle

appdirs = AppDirs("MarkWrite")
usersettings = readPickle(appdirs.user_config_dir,u'usersettings.pkl')

app = QtGui.QApplication(sys.argv)

from markwrite.gui.projectsettings import ProjectSettingsDialog
_ = ProjectSettingsDialog(savedstate=usersettings)
from markwrite.gui.projectsettings import SETTINGS
pg.setConfigOption('background', SETTINGS['plotviews_background_color'])
pg.setConfigOption('foreground', SETTINGS['plotviews_foreground_color'])

wmwin = MarkWriteMainWindow(app)
MarkWriteMainWindow._appdirs = appdirs
wmwin.show()
status = app.exec_()
sys.exit(status)