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
import os
os.environ['HDF5_DISABLE_VERSION_CHECK']='2'
import shutil

import markwrite

import sys
if sys.platform == 'win32':
    # Work around so that MarkWrite app icon is also used as task bar icon.
    # http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
    import ctypes
    myappid = u'isolver.markwrite.editor.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    src_icon = os.path.abspath("./resources/icons")
    if not os.path.isdir(src_icon):
        src_icon=os.path.abspath("./MarkWrite/resources/icons")
    if os.path.isdir(src_icon):
        src_icon = os.path.join(src_icon,'markwrite_icon.ico')
        shutil.copy(src_icon, os.path.join(markwrite.appdirs.user_config_dir,'markwrite_icon.ico'))
    
import pyqtgraph as pg
from markwrite.gui.mainwin import MarkWriteMainWindow
# # Switch to using white background and black foreground
pg.setConfigOption('background', markwrite.SETTINGS['plotviews_background_color'])
pg.setConfigOption('foreground', markwrite.SETTINGS['plotviews_foreground_color'])

wmwin = MarkWriteMainWindow(markwrite.app)
MarkWriteMainWindow._appdirs = markwrite.appdirs
wmwin.show()
status = markwrite.app.exec_()