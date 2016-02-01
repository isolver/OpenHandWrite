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
from collections import OrderedDict
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import string, os, sys, json

OK = QtGui.QDialogButtonBox.Ok

def fileSaveDlg(initFilePath="", initFileName="",
                prompt=u"Save MarkWrite Project",
                allowed=None, parent=None):
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

    r = QtGui.QFileDialog.getSaveFileName(parent=parent,
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
        allowed = "Supported files (*.txyp *.xml *.hdf5 *.mwp);;"
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

def singleSelectDialog(items, parent=None, title=u'singleSelectDialog', text='Select:'):
    var, ok = QtGui.QInputDialog.getItem(parent, title, text, items, editable=False)
    if ok:
        return unicode(var)
    return None

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


class Dlg(QtGui.QDialog):
    """A simple dialogue box. You can add text or input boxes
    (sequentially) and then retrieve the values.
    """

    def __init__(self, title='MarkWrite Dialog',
                 pos=None, size=None, style=None,
                 labelButtonOK="OK",
                 labelButtonCancel="Cancel",
                 screen=-1):

        QtGui.QDialog.__init__(self, None, QtCore.Qt.WindowTitleHint)

        self.inputFields = []
        self.inputFieldTypes = []
        self.inputFieldNames = []
        self.data = []
        self.irow = 0

        #QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))

        #add buttons for OK and Cancel
        self.buttonBox = QtGui.QDialogButtonBox(QtCore.Qt.Horizontal, parent=self)
        self.okbutton = QtGui.QPushButton(labelButtonOK, parent=self)
        self.cancelbutton = QtGui.QPushButton(labelButtonCancel, parent=self)
        self.buttonBox.addButton(self.okbutton,
                                 QtGui.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.cancelbutton,
                                 QtGui.QDialogButtonBox.ActionRole)
        self.okbutton.clicked.connect(self.accept)
        self.cancelbutton.clicked.connect(self.reject)

        if style:
            raise RuntimeWarning(
                "Dlg does not currently support the stype kwarg.")

        self.pos = pos
        self.size = size
        self.screen = screen
        #self.labelButtonOK = labelButtonOK
        #self.labelButtonCancel = labelButtonCancel

        self.layout = QtGui.QGridLayout()
        self.layout.setColumnStretch(1, 1)
        self.layout.setSpacing(10)
        self.layout.setColumnMinimumWidth(1, 250)

        self.setLayout(self.layout)

        self.setWindowTitle(title)


    def addText(self, text, color='', isFieldLabel=False):
        textLabel = QtGui.QLabel(text, parent=self)

        if len(color):
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Foreground, QtGui.QColor(color))
            textLabel.setPalette(palette)

        if isFieldLabel is True:
            self.layout.addWidget(textLabel, self.irow, 0, 1, 1)
        else:
            self.layout.addWidget(textLabel, self.irow, 0, 1, 2)
            self.irow += 1

        return textLabel


    def addField(self, label='', initial='', color='', choices=None, tip='',
                 enabled=True):
        """
        Adds a (labelled) input field to the dialogue box, optional text color
        and tooltip.

        If 'initial' is a bool, a checkbox will be created.
        If 'choices' is a list or tuple, a dropdown selector is created.
        Otherwise, a text line entry box is created.

        Returns a handle to the field (but not to the label).
        """
        self.inputFieldNames.append(label)
        if choices:
            self.inputFieldTypes.append(str)
        else:
            self.inputFieldTypes.append(type(initial))
        if type(initial) == np.ndarray:
            initial = initial.tolist()  #convert numpy arrays to lists

        #create label
        inputLabel = self.addText(label, color, isFieldLabel=True)

        #create input control
        if type(initial) == bool and not choices:
            self.data.append(initial)
            inputBox = QtGui.QCheckBox(parent=self)
            inputBox.setChecked(initial)

            def handleCheckboxChange(new_state):
                ix = self.inputFields.index(inputBox)
                self.data[ix] = inputBox.isChecked()

            inputBox.stateChanged.connect(handleCheckboxChange)
        elif not choices:
            self.data.append(initial)
            inputBox = QtGui.QLineEdit(unicode(initial), parent=self)

            def handleLineEditChange(new_text):
                ix = self.inputFields.index(inputBox)
                thisType = self.inputFieldTypes[ix]

                try:
                    if thisType in (str, unicode):
                        self.data[ix] = unicode(new_text)
                    elif thisType == tuple:
                        jtext = "[" + unicode(new_text) + "]"
                        self.data[ix] = json.loads(jtext)[0]
                    elif thisType == list:
                        jtext = "[" + unicode(new_text) + "]"
                        self.data[ix] = json.loads(jtext)[0]
                    elif thisType == float:
                        self.data[ix] = string.atof(str(new_text))
                    elif thisType == int:
                        self.data[ix] = string.atoi(str(new_text))
                    elif thisType == long:
                        self.data[ix] = string.atol(str(new_text))
                    elif thisType == dict:
                        jtext = "[" + unicode(new_text) + "]"
                        self.data[ix] = json.loads(jtext)[0]
                    elif thisType == np.ndarray:
                        self.data[ix] = np.array(
                            json.loads("[" + unicode(new_text) + "]")[0])
                    else:
                        self.data[ix] = new_text

                except Exception as e:
                    self.data[ix] = unicode(new_text)
            inputBox.textEdited.connect(handleLineEditChange)
        else:
            inputBox = QtGui.QComboBox(parent=self)
            choices = list(choices)
            for i, option in enumerate(choices):
                inputBox.addItem(unicode(option))
                #inputBox.addItems([unicode(option) for option in choices])
                inputBox.setItemData(i, (option,))

            if isinstance(initial, (int, long)) and len(choices) > initial >= 0:
                pass
            elif initial in choices:
                initial = choices.index(initial)
            else:
                initial = 0
            inputBox.setCurrentIndex(initial)

            self.data.append(choices[initial])

            def handleCurrentIndexChanged(new_index):
                ix = self.inputFields.index(inputBox)
                # Some versions of pyqt require using toPyObject(), 
                # others do not. Try both.
                try:
                    self.data[ix] = inputBox.itemData(new_index).toPyObject()[0]
                except:
                    self.data[ix] = inputBox.itemData(new_index)[0]
            inputBox.currentIndexChanged.connect(handleCurrentIndexChanged)

        if len(color):
            inputBox.setPalette(inputLabel.palette())
        if len(tip):
            inputBox.setToolTip(tip)
        inputBox.setEnabled(enabled)
        self.layout.addWidget(inputBox, self.irow, 1)

        self.inputFields.append(inputBox)  #store this to get data back on OK
        self.irow += 1

        return inputBox

    def addFixedField(self, label='', initial='', color='', choices=None,
                      tip=''):
        """Adds a field to the dialog box (like addField) but the field cannot
        be edited. e.g. Display experiment version.
        """
        return self.addField(label, initial, color, choices, tip, enabled=False)

    def display(self):
        """
        Presents the dialog and waits for the user to press either OK or CANCEL.

        If user presses OK button, function returns a list containing the
        updated values coming from each of the input fields created.
        Otherwise, None is returned.

        :return: self.data
        """
        return self.exec_()

    def show(self):
        """
        ** QDialog already has a show() method. So this method calls
           QDialog.show() and then exec_(). This seems to not cause issues,
           however we need to keep an eye out for any issues.

        ** Deprecated: Use dlg.display() instead. This method will be removed
           in a future version of psychopy.

        Presents the dialog and waits for the user to press either OK or CANCEL.

        If user presses OK button, function returns a list containing the
        updated values coming from each of the input fields created.
        Otherwise, None is returned.

        :return: self.data
        """
        return self.display()

    def exec_(self):
        """
        Presents the dialog and waits for the user to press either OK or CANCEL.

        If user presses OK button, function returns a list containing the
        updated values coming from each of the input fields created.
        Otherwise, None is returned.
        """

        self.layout.addWidget(self.buttonBox, self.irow, 0, 1, 2)

        # Center Dialog on appropriate screen
        frameGm = self.frameGeometry()
        desktop = QtGui.QApplication.desktop()
        qtscreen = self.screen
        if self.screen <= 0:
            qtscreen = desktop.primaryScreen()
        centerPoint = desktop.screenGeometry(qtscreen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

        QtGui.QDialog.show(self)
        self.raise_()
        self.activateWindow()

        self.OK = False
        if QtGui.QDialog.exec_(self) == QtGui.QDialog.Accepted:
            self.OK = True
            return self.data

class DlgFromDict(Dlg):
    """Creates a dialogue box that represents a dictionary of values.
    Any values changed by the user are change (in-place) by this
    dialogue box.
    """
    def __init__(self, dictionary, title='',fixed=[], order=[], tip={}, screen=-1):
        Dlg.__init__(self, title, screen=screen)
        self.dictionary = dictionary
        keys = self.dictionary.keys()
        if not isinstance(self.dictionary, OrderedDict):
            keys.sort()
        if len(order):
            keys = order + list(set(keys).difference(set(order)))
        types=dict([])
        for field in keys:
            types[field] = type(self.dictionary[field])
            tooltip = ''
            if field in tip.keys():
                tooltip = tip[field]
            if field in fixed:
                self.addFixedField(field, self.dictionary[field], tip=tooltip)
            elif type(self.dictionary[field]) in [list, tuple]:
                self.addField(field,choices=self.dictionary[field], tip=tooltip)
            else:
                self.addField(field, self.dictionary[field], tip=tooltip)

        ok_data = self.exec_()
        if ok_data:
            for n,thisKey in enumerate(keys):
                self.dictionary[thisKey]=ok_data[n]


