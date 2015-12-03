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

flattenned_settings_dict['hdf5_create_trial_segments'] = {'name': 'Enable', 'type': 'bool', 'value': True}
flattenned_settings_dict['hdf5_trial_start_var_select_filter'] = {'name': 'Start Time Options Filter', 'type': 'str', 'value': "DV_*_START"}
flattenned_settings_dict['hdf5_trial_end_var_select_filter'] = {'name': 'End Time Options Filter', 'type': 'str', 'value':  "DV_*_END"}

flattenned_settings_dict['new_segment_trim_0_pressure_points'] = {'name': 'Trim 0 Pressure Points', 'type': 'bool', 'value': True}
flattenned_settings_dict['plotviews_background_color'] = {'name': 'Background Color', 'type': 'color', 'value': (32,32,32), 'tip': "Application Plot's background color. Change will not take effect until the application is restarted."}
flattenned_settings_dict['plotviews_foreground_color'] =  {'name': 'Foreground Color', 'type': 'color', 'value': (224,224,224), 'tip': "Application Plot's foreground color (axis lines / labels)."}

flattenned_settings_dict['timeplot_enable_ymouse'] = {'name': 'Enable Y Axis Pan / Scale with Mouse', 'type': 'bool', 'value': False}
flattenned_settings_dict['timeplot_xtrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (170,255,127)}
flattenned_settings_dict['timeplot_xtrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['timeplot_ytrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (0,170,255)}
flattenned_settings_dict['timeplot_ytrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}

flattenned_settings_dict['spatialplot_invert_y_axis'] = {'name': 'Invert Y Axis', 'type': 'bool', 'value': True}
flattenned_settings_dict['spatialplot_default_color'] = {'name':'Default Point Color', 'type': 'color', 'value':(224,224,224)}
flattenned_settings_dict['spatialplot_default_point_size'] = {'name': 'Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['spatialplot_selectedvalid_color'] = {'name': 'Valid Segment Color', 'type': 'color', 'value':(0,160,0)}
flattenned_settings_dict['spatialplot_selectedinvalid_color'] ={'name': 'Invalid Segment Color', 'type': 'color', 'value': (160,0,0)}
flattenned_settings_dict['spatialplot_selectedpoint_size'] = {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)}

settings_params = [
        {'name': 'Loading Source Data', 'type': 'group', 'children': [
               {'name': 'ioHub HDF5 Trial Segmentation', 'type': 'group', 'children': [
                    'hdf5_create_trial_segments',
                    'hdf5_trial_start_var_select_filter',
                    'hdf5_trial_end_var_select_filter',
                 ]},
        ]},
        {'name': 'Segment Creation', 'type': 'group', 'children': [
            'new_segment_trim_0_pressure_points',
        ]},
        {'name': 'GUI Options', 'type': 'group', 'children': [
            'plotviews_background_color',
            'plotviews_foreground_color',
            {'name': 'TimeLine View', 'type': 'group', 'children': [
                'timeplot_enable_ymouse',
                {'name': 'Horizontal Pen Position Trace', 'type': 'group', 'children': [
                    'timeplot_xtrace_color',
                    'timeplot_xtrace_size',
                ]},
               {'name': 'Vertical Pen Position Trace', 'type': 'group', 'children': [
                    'timeplot_ytrace_color',
                    'timeplot_ytrace_size',
                 ]},
           ]},
            {'name': 'Spatial View', 'type': 'group', 'children': [
                'spatialplot_invert_y_axis',
                'spatialplot_default_color',
                'spatialplot_default_point_size',
                 {'name': 'Selected Pen Points', 'type': 'group', 'children': [
                    'spatialplot_selectedvalid_color',
                    'spatialplot_selectedinvalid_color',
                    'spatialplot_selectedpoint_size',
                ]}
            ]},
             ]},
        ]


SETTINGS=dict()
class ProjectSettingsDialog(QtGui.QDialog):
    path2key=dict()
    def __init__(self, parent = None, savedstate=None):
        super(ProjectSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Application Settings")
        layout = QtGui.QVBoxLayout(self)

        self.initKeyParamMapping()
        self._settings = Parameter.create(name='params', type='group', children=settings_params)

        if savedstate:
            self._settings.restoreState(savedstate)

        # Holds settings keys that have changed by the user when the
        # dialog is closed. Used to update any needed gui values..
        self._updated_settings={}

        self._settings.sigTreeStateChanged.connect(self.handleSettingChange)

        self.initSettingsValues()

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

    def initKeyParamMapping(self):
        if len(self.path2key)==0:
            def replaceGroupKeys(paramlist, parent_path=[]):
                for i,p in enumerate(paramlist):
                    if isinstance(p,basestring):
                        pdict=flattenned_settings_dict[p]
                        paramlist[i]=pdict
                        self.path2key['.'.join(parent_path+[pdict['name'],])]=p
                    elif isinstance(p,dict):
                        replaceGroupKeys(p.get('children'),parent_path+[p.get('name'),])
            replaceGroupKeys(settings_params)

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
                if self.path2key.has_key(childName):
                    SETTINGS[self.path2key[childName]]=child.value()

    ## If anything changes in the tree, print a message
    def handleSettingChange(self, param, changes):
        global SETTINGS
        for param, change, data in changes:
            path = self._settings.childPath(param)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            if change == 'value':
                setting_key = self.path2key[childName]
                SETTINGS[setting_key]=data
                self._updated_settings[setting_key] = data
                #print 'settings_state:',self.settings_state

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getProjectSettings(parent = None, usersettings = None):
        dialog = ProjectSettingsDialog(parent, usersettings)
        result = dialog.exec_()
        usersettings=dialog._settings.saveState()
        return dialog._updated_settings,SETTINGS, usersettings, result == QtGui.QDialog.Accepted