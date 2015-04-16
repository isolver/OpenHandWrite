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
from collections import OrderedDict

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType


flattenned_settings_dict = OrderedDict()
flattenned_settings_dict['new_segment_trim_0_pressure_points'] = {'name': 'Trim 0 Pressure Points', 'type': 'bool', 'value': True}
flattenned_settings_dict['plotviews_background_color'] = {'name': 'Background Color', 'type': 'color', 'value': (32,32,32), 'tip': "Application Plot's background color."}
flattenned_settings_dict['plotviews_foreground_color'] =  {'name': 'Foreground Color', 'type': 'color', 'value': (224,224,224), 'tip': "Application Plot's foreground color (axis lines / labels)."}

flattenned_settings_dict['timeplot_xtrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (170,255,127)}
flattenned_settings_dict['timeplot_xtrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['timeplot_ytrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (0,170,255)}
flattenned_settings_dict['timeplot_ytrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}

flattenned_settings_dict['spatialplot_default_color'] = {'name':'Default Point Color', 'type': 'color', 'value':(224,224,224)}
flattenned_settings_dict['spatialplot_validselected_color'] = {'name': 'Valid Segment Color', 'type': 'color', 'value':(0,160,0)}
flattenned_settings_dict['spatialplot_invalidselected_color'] ={'name': 'Invalid Segment Color', 'type': 'color', 'value': (160,0,0)}
flattenned_settings_dict['spatialplot_point_size'] = {'name': 'Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}

settings_params = [
        {'name': 'Segment Creation', 'type': 'group', 'children': [
            'new_segment_trim_0_pressure_points',
#            {'name': 'Suggest Default Segment Name', 'type': 'bool', 'value': False},
#            {'name': 'Autocomplete Segment Name', 'type': 'bool', 'value': True},
#            {'name': 'Allow Sibling Segments Temporal Overlap', 'type': 'bool', 'value': False},
#            {'name': 'Parent Segments Must Temporally Wrap Children', 'type': 'bool', 'value': True}

        ]},
        {'name': 'GUI Options', 'type': 'group', 'children': [
            'plotviews_background_color',
            'plotviews_foreground_color',
#            {'name': 'Auto Focus Selected Segment', 'type': 'bool', 'value': True, 'tip': "Timeline and Spatial Views automatically pan / zoom\nso pen data for a selected segment tree node is fully visible."},
#            {'name': 'Sort Category Tree by Segment Time', 'type': 'bool', 'value': True},
#
            {'name': 'TimeLine View', 'type': 'group', 'children': [
#                {'name': 'Selected Time Period Color', 'type': 'color', 'value': "FF0", 'tip': "Color of the time region selection bar."},
                {'name': 'Horizontal Pen Position Trace', 'type': 'group', 'children': [
#                    {'name': 'Point Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    'timeplot_xtrace_color',
                    'timeplot_xtrace_size',
                ]},
               {'name': 'Vertical Pen Position Trace', 'type': 'group', 'children': [
#                    {'name': 'Point Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    'timeplot_ytrace_color',
                    'timeplot_ytrace_size',
                 ]},
           ]},
            {'name': 'Spatial View', 'type': 'group', 'children': [
#                {'name': 'Background Color', 'type': 'color', 'value': "000", 'tip': "Spatial pen point plot's background color."},
#                {'name': 'Foreground Color', 'type': 'color', 'value': "FFF", 'tip': "Spatial pen point plot's foreground color (axis lines / labels)."},
#                {'name': 'Non Segmented Pen Points', 'type': 'group', 'children': [
#                    {'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
#                    {'name': 'Color', 'type': 'color', 'value': "0F0"},
#                    {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
#                ]},
#               {'name': 'Segmented Pen Points', 'type': 'group', 'children': [
#                    {'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
#                    {'name': 'Color', 'type': 'color', 'value': "0F0"},
#                    {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)},
#                ]},
                 {'name': 'Selected Pen Points', 'type': 'group', 'children': [
                    #{'name': 'Shape', 'type': 'list', 'values': {"Dot": 'o', "Cross": "x"}, 'value': 0},
                    'spatialplot_default_color',
                    'spatialplot_validselected_color',
                    'spatialplot_invalidselected_color',
                    'spatialplot_point_size',
                ]}
            ]},
             ]},
        ]


SETTINGS=dict()

path2key=dict()
def replaceGroupKeys(paramlist, parent_path=[]):
    for i,p in enumerate(paramlist):
        if isinstance(p,basestring):
            pdict=flattenned_settings_dict[p]
            paramlist[i]=pdict
            path2key['.'.join(parent_path+[pdict['name'],])]=p
        elif isinstance(p,dict):
            replaceGroupKeys(p.get('children'),parent_path+[p.get('name'),])
replaceGroupKeys(settings_params)
#print 'settings_params:',settings_params
paramdef = Parameter.create(name='params', type='group', children=settings_params)

class ProjectSettingsDialog(QtGui.QDialog):
    path2key=dict()
    cachedstate =  None#p.saveState()
    def __init__(self, parent = None):
        super(ProjectSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Application Settings")
        layout = QtGui.QVBoxLayout(self)

        self._settings = paramdef

        if ProjectSettingsDialog.cachedstate:
            self._settings.restoreState(ProjectSettingsDialog.cachedstate, addChildren=True, removeChildren=True)

        self._settings.sigTreeStateChanged.connect(self.handleSettingChange)

        self.initSettingsValues()
        #print 'settings_state:',self.settings_state

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

    def initSettingsValues(self, pgroup=None):
        global SETTINGS
        if pgroup is None:
            pgroup = self._settings
        for child in pgroup.children():
            if child.hasChildren():
                self.initSettingsValues(child)
            else:
                path = self._settings.childPath(child)
                if path is not None:
                    childName = '.'.join(path)
                else:
                    childName = child.name()
                SETTINGS[path2key[childName]]=child.value()

    ## If anything changes in the tree, print a message
    def handleSettingChange(self, param, changes):
        global SETTINGS
        for param, change, data in changes:
            path = self._settings.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            #print('  parameter: %s'% childName)
            #print('  key: %s'% self.path2key[childName])
            #print('  change:    %s'% change)
            #print('  data:      %s'% str(data))
            #print('  ----------')
            if change == 'value':
                SETTINGS[path2key[childName]]=data
                #print 'settings_state:',self.settings_state
    # get current date and time from the dialog
    @property
    def settings(self):
        return self._settings

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getProjectSettings(parent = None):
        dialog = ProjectSettingsDialog(parent)
        result = dialog.exec_()
        ProjectSettingsDialog.cachedstate=dialog.settings.saveState()
        return dialog.settings, result == QtGui.QDialog.Accepted

############### Unimplemented


def getSettingsForCurrentApplicationLaunch():
    """
    TODO: Either load default settings for app, or if a user saved settings
     state file exists, read it and load those as the settings to use for the
     application when run.
    :return:
    """
    pass

def loadUserSavedSettingsDict():
    """
    TODO: Implement ability to load a saved settings state dict so that they
    are used as the setting values for the application.
    :return:

    """
    pass

def saveSettingsDict():
    """
    TODO: Implement ability to save the current settings state so that they
    are used instead of the default settting values when the application starts
    again in the future.
    :return:

    """
    pass

def resetSettingsToDefault():
    """
    TODO: Resets the settings values back to the defaults, removing
          any user changes made.
    :return:
    """
    pass

if __name__ == '__main__':
    app = QtGui.QApplication([])
    projsettings, ok = ProjectSettingsDialog.getProjectSettings()
    print("{} {}".format(projsettings, ok))
    app.exec_()