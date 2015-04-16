# -*- coding: utf-8 -*-
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
from __future__ import division

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import string, os, sys, json

OK = QtGui.QDialogButtonBox.Ok

def fileSaveDlg(initFilePath="", initFileName="",
                prompt=u"Select file to save",
                allowed=None):
    """A simple dialogue allowing write access to the file system.

    :parameters:
        initFilePath: string
            default file path on which to open the dialog
        initFileName: string
            default file name, as suggested file
        prompt: string (default "Select file to open")
            can be set to custom prompts
        allowed: string
            a string to specify file filters.
            e.g. "Text files (*.txt) ;; Image files (*.bmp *.gif)"
            See http://pyqt.sourceforge.net/Docs/PyQt4/qfiledialog.html
            #getSaveFileName
            for further details

    If initFilePath or initFileName are empty or invalid then
    current path and empty names are used to start search.

    If user cancels the None is returned.
    """
    if allowed is None:
        allowed = "All files (*.*);;" \
                  "Text files (*.txt)"

    r = QtGui.QFileDialog.getSaveFileName(parent=None,
                                          caption=prompt,
                                          directory=os.path.join(initFilePath,
                                                                 initFileName),
                                          filter=allowed)
    if len(r) == 0:
        return None
    return unicode(r)


def fileOpenDlg(tryFilePath="",
                tryFileName="",
                prompt=u"Select file to open",
                allowed=None,
                allow_multiple_select=False):
    """A simple dialogue allowing read access to the file system.

    :parameters:
        tryFilePath: string
            default file path on which to open the dialog
        tryFileName: string
            default file name, as suggested file
        prompt: string (default "Select file to open")
            can be set to custom prompts
        allowed: string (available since v1.62.01)
            a string to specify file filters.
            e.g. "Text files (*.txt) ;; Image files (*.bmp *.gif)"
            See http://pyqt.sourceforge.net/Docs/PyQt4/qfiledialog.html
            #getOpenFileNames
            for further details

    If tryFilePath or tryFileName are empty or invalid then
    current path and empty names are used to start search.

    If user cancels, then None is returned.
    """

    if allowed is None:
        allowed = "Supported Input Files (*.txyp *.xml);;"
                  #"Data Files (*.txyp *.xml);;"
                  #"Project Files (*.mwp);;"
    fdlg = QtGui.QFileDialog.getOpenFileName
    if allow_multiple_select is True:
        fdlg = QtGui.QFileDialog.getOpenFileNames

    filesToOpen = fdlg(parent=None,
                       caption=prompt,
                       directory=os.path.join(tryFilePath,tryFileName),
                       filter=allowed)
    if allow_multiple_select is True:
        filesToOpen = [unicode(fpath) for fpath in filesToOpen if
                       os.path.exists(fpath)]
    else:
        filesToOpen = [unicode(filesToOpen),]

    if len(filesToOpen) == 0:
        return None

    return filesToOpen


def infoDlg(title=u"Information",
            prompt=u"No details provided. ('prompt' value not set)."):

    QtGui.QMessageBox.information(None,
                                  title,
                                  prompt)


def warnDlg(title=u"Warning",
            prompt=u"No details provided. ('prompt' value not set)."):

    QtGui.QMessageBox.warning(None,
                              title,
                              prompt)


def criticalDlg(title=u"Critical",
                prompt=u"No details provided. ('prompt' value not set)."):

    QtGui.QMessageBox.critical(None,
                               title,
                               prompt)


def aboutDlg(title=u"About App",
             prompt=u"No details provided. ('prompt' value not set)."):

    QtGui.QMessageBox.about(None,
                            title,
                            prompt)


class ConfirmAction(object):
    instance = None
    text = 'Action Confirmation Request'
    info_text = "Are you sure you want to perform the action?"

    @classmethod
    def display(cls):
        if cls.instance:
            return cls.instance.exec_()
        else:
            msgBox = QtGui.QMessageBox()
            cls.instance = msgBox
            msgBox.setWindowTitle('MarkWrite')
            msgBox.setText(cls.text)
            msgBox.setInformativeText(cls.info_text)
            msgBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No);
            msgBox.setDefaultButton(QtGui.QMessageBox.No)
            msgBox.setIcon(QtGui.QMessageBox.Information)
            r=msgBox.exec_()

            return r == QtGui.QMessageBox.Yes

class ErrorDialog(object):
    instance = None
    text = 'Error Occurred'
    info_text = "An error occurred while performing the action."

    @classmethod
    def display(cls):
        if cls.instance:
            return cls.instance.exec_()
        else:
            msgBox = QtGui.QMessageBox()
            cls.instance = msgBox
            msgBox.setWindowTitle('MarkWrite')
            msgBox.setText(cls.text)
            msgBox.setInformativeText(cls.info_text)
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
            msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
            msgBox.setIcon(QtGui.QMessageBox.Critical)
            return msgBox.exec_() == QtGui.QMessageBox.Ok

class NotSupportedFileType(ErrorDialog):
    instance = None
    text = 'Import Data Source File Error'
    info_text = "The selected file type cannot be imported by MarkWrite. Please selected another file."

class ExitApplication(ConfirmAction):
    instance = None
    text = 'Exit Application'
    info_text = "Are you sure you want to quit the application?"

#class SaveProjectChanges(ConfirmAction):
#    instance = None
#    text = 'Save Modified Project'
#    info_text = "Save the current project's changes?"
