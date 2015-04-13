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
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

#
## IMPORTANT:
## THE CODE IN THIS FILE IS TOTALLY MADE-UP, INCOMPLETE, ETC....
## JUST SETTING BASE SETTINGS FRAMEWORK UP FOR NOW....
#

params = [
        {'name': 'GUI Options', 'type': 'group', 'children': [
            {'name': 'Auto Focus Selected Segment', 'type': 'bool', 'value': True, 'tip': "Timeline and Spatial Views automatically pan / zoom\nso pen data for a selected segment tree node is fully visible."},

            {'name': 'TimeLine View', 'type': 'group', 'children': [
                {'name': 'Background Color', 'type': 'color', 'value': "000", 'tip': "Timeline plot's background color."},
                {'name': 'Foreground Color', 'type': 'color', 'value': "FFF", 'tip': "Timeline plot's foreground color (axis lines / labels)."},
                {'name': 'Selected Time Period Color', 'type': 'color', 'value': "FF0", 'tip': "Color of the time region selection bar."},
                {'name': 'Horizontal Pen Position Trace', 'type': 'group', 'children': [
                    {'name': 'Point Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    {'name': 'Point Color', 'type': 'color', 'value': "0F0"},
                    {'name': 'Point Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
                ]},
                {'name': 'Vertical Pen Position Trace', 'type': 'group', 'children': [
                    {'name': 'Point Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    {'name': 'Point Color', 'type': 'color', 'value': "0F0"},
                    {'name': 'Point Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
                 ]},
            ]},

            {'name': 'Spatial View', 'type': 'group', 'children': [
                {'name': 'Background Color', 'type': 'color', 'value': "000", 'tip': "Spatial pen point plot's background color."},
                {'name': 'Foreground Color', 'type': 'color', 'value': "FFF", 'tip': "Spatial pen point plot's foreground color (axis lines / labels)."},
                {'name': 'Non Segmented Pen Points', 'type': 'group', 'children': [
                    {'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    {'name': 'Color', 'type': 'color', 'value': "0F0"},
                    {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
                ]},
                 {'name': 'Segmented Pen Points', 'type': 'group', 'children': [
                    {'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    {'name': 'Color', 'type': 'color', 'value': "0F0"},
                    {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
                ]},
                 {'name': 'Selected Pen Points', 'type': 'group', 'children': [
                    {'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    {'name': 'Color', 'type': 'color', 'value': "0F0"},
                    {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
                ]}
            ]},

        ]},
        {'name': 'Segment Creation', 'type': 'group', 'children': [
            {'name': 'Temporal Overlap', 'type': 'bool', 'value': False},
            {'name': 'Parent Segments Must Temporally Wrap Children', 'type': 'bool', 'value': True}
        ]}
        ]





class ProjectSettingsDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(ProjectSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Application Settings")
        layout = QtGui.QVBoxLayout(self)


        self._settings = Parameter.create(name='params', type='group', children=params)
        self._settings.sigTreeStateChanged.connect(self.handleSettingChange)

        self.ptree = ParameterTree()
        self.ptree.setParameters(self._settings, showTop=False)
        self.ptree.setWindowTitle('MarkWrite Application Settings')
        layout.addWidget(self.ptree)
        self.ptree.adjustSize()
        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.resize(500,700)


    ## If anything changes in the tree, print a message
    def handleSettingChange(self, param, changes):
        print("tree changes:")
        for param, change, data in changes:
            path = self._settings.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print('  parameter: %s'% childName)
            print('  change:    %s'% change)
            print('  data:      %s'% str(data))
            print('  ----------')

    # get current date and time from the dialog
    @property
    def settings(self):
        return self._settings

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getProjectSettings(parent = None):
        dialog = ProjectSettingsDialog(parent)
        result = dialog.exec_()
        return dialog.settings, result == QtGui.QDialog.Accepted

if __name__ == '__main__':
    app = QtGui.QApplication([])
    projsettings, ok = ProjectSettingsDialog.getProjectSettings()
    print("{} {}".format(projsettings, ok))
    app.exec_()