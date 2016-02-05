# -*- coding: utf-8 -*-
from __future__ import division
__version__ = "0.2.2.8"
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

# Need to import pyTables module before pyqt imports pyh5 or error occurs when
# openning an iohub datastore file.
import tables
import pyqtgraph
import sys
from appdirs import AppDirs
from file_io import readPickle, writePickle

appdirs = AppDirs("MarkWrite")
usersettings = readPickle(appdirs.user_config_dir,u'usersettings.pkl')

from pyqtgraph.Qt import QtGui
app = QtGui.QApplication(sys.argv)

from gui.projectsettings import ProjectSettingsDialog
_ = ProjectSettingsDialog(savedstate=usersettings)
from gui.projectsettings import SETTINGS
writePickle(appdirs.user_config_dir,u'usersettings.pkl', SETTINGS)
#print "Updated usersettings.pkl in:",appdirs.user_config_dir