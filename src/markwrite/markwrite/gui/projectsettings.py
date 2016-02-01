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

flattenned_settings_dict['auto_generate_l1segments'] = {'name': 'Enable Level 1 Auto Segmentation', 'type': 'bool', 'value': True}

flattenned_settings_dict['filter_imported_pen_data'] = {'name': 'Filter Imported Pen Data', 'type': 'bool', 'value': False}

flattenned_settings_dict['hdf5_trial_start_var_select_filter'] = {'name': 'Start Time Options Filter', 'type': 'str', 'value': "DV_*_START"}
flattenned_settings_dict['hdf5_trial_end_var_select_filter'] = {'name': 'End Time Options Filter', 'type': 'str', 'value':  "DV_*_END"}
flattenned_settings_dict['hdf5_apply_time_offset_var_select_filter'] = {'name': 'Exp. Time Condition Variables', 'type': 'str', 'value': "DV_*_START,DV_*_END"}

flattenned_settings_dict['new_segment_trim_0_pressure_points'] = {'name': 'Trim 0 Pressure Points', 'type': 'bool', 'value': True}
flattenned_settings_dict['plotviews_background_color'] = {'name': 'Background Color', 'type': 'color', 'value': (32,32,32), 'tip': "Application Plot's background color. Change will not take effect until the application is restarted."}
flattenned_settings_dict['plotviews_foreground_color'] =  {'name': 'Foreground Color', 'type': 'color', 'value': (224,224,224), 'tip': "Application Plot's foreground color (axis lines / labels)."}
flattenned_settings_dict['pen_stroke_boundary_size'] ={'name': 'Stroke Boundary Point Size', 'type': 'int', 'value': 2, 'limits': (0, 5)}
flattenned_settings_dict['pen_stroke_boundary_color'] =  {'name': 'Stroke Boundary Sample Color', 'type': 'color', 'value': (224,0,224)}

flattenned_settings_dict['timeplot_enable_ymouse'] = {'name': 'Enable Y Axis Pan / Scale with Mouse', 'type': 'bool', 'value': False}
flattenned_settings_dict['timeplot_xtrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (170,255,127)}
flattenned_settings_dict['timeplot_xtrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['timeplot_ytrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (0,170,255)}
flattenned_settings_dict['timeplot_ytrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}

flattenned_settings_dict['display_timeplot_vtrace'] = {'name': 'Display Plot', 'type': 'bool', 'value': False}
flattenned_settings_dict['timeplot_vtrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (255,170,100)}
flattenned_settings_dict['timeplot_vtrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['display_timeplot_atrace'] = {'name': 'Display Plot', 'type': 'bool', 'value': False}
flattenned_settings_dict['timeplot_atrace_color'] = {'name': 'Point Color', 'type': 'color', 'value': (100,170,255)}
flattenned_settings_dict['timeplot_atrace_size'] ={'name': 'Point Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['spatialplot_invert_y_axis'] = {'name': 'Invert Y Axis', 'type': 'bool', 'value': True}
flattenned_settings_dict['spatialplot_default_color'] = {'name':'Default Point Color', 'type': 'color', 'value':(224,224,224)}
flattenned_settings_dict['spatialplot_default_point_size'] = {'name': 'Size', 'type': 'int', 'value': 1, 'limits': (1, 5)}
flattenned_settings_dict['spatialplot_selectedvalid_color'] = {'name': 'Valid Segment Color', 'type': 'color', 'value':(0,160,0)}
flattenned_settings_dict['spatialplot_selectedinvalid_color'] ={'name': 'Invalid Segment Color', 'type': 'color', 'value': (160,0,0)}
flattenned_settings_dict['spatialplot_selectedpoint_size'] = {'name': 'Size', 'type': 'int', 'value': 2, 'limits': (1, 5)}

flattenned_settings_dict['stroke_detect_pressed_runs_only'] = {'name': 'Use Pressed Sample Runs Only', 'type': 'bool', 'value': True}
#flattenned_settings_dict['stroke_detect_min_value_threshold'] = {'name': 'Minimum Velocity Threshold', 'type': 'float', 'value': 0.0, 'step': 0.1, 'limits':(0.0, 500.0)}
flattenned_settings_dict['stroke_detect_min_p2p_sample_count'] = {'name': 'Minimum Stroke Sample Count', 'type': 'int', 'value': 7, 'limits': (1, 50)}
flattenned_settings_dict['stroke_detect_edge_type'] =  {'name': 'Detect Edge Type', 'type': 'list', 'values': ['none', 'rising', 'falling', 'both'], 'value': 'rising'}

#flattenned_settings_dict['series_detect_max_isi_msec'] = {'name': 'Maximum Series ISI (msec)', 'type': 'int', 'value': 0, 'limits': (0, 100)}


flattenned_settings_dict['kbshortcut_create_segment'] = {'name': 'Create Segment', 'type': 'str', 'value': QtGui.QKeySequence('Return').toString()}
flattenned_settings_dict['kbshortcut_delete_segment'] = {'name': 'Delete Segment', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+D').toString()}
flattenned_settings_dict['kbshortcut_timeplot_increase_mag'] = {'name': 'Increase Timeplot Magnification 2x', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl++').toString()}
flattenned_settings_dict['kbshortcut_timeplot_decrease_mag'] = {'name': 'Decrease Timeplot Magnification 2x', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+-').toString()}
flattenned_settings_dict['kbshortcut_move_plots_to_selection'] = {'name': 'Reposition Views on Selected Time Period', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Home').toString()}
flattenned_settings_dict['kbshortcut_selected_timeperiod_forward'] = {'name': 'Move Selected Time Period Forward', 'type': 'str', 'value': QtGui.QKeySequence('PgUp').toString()}
flattenned_settings_dict['kbshortcut_selected_timeperiod_backward'] = {'name': 'Move Selected Time Period Backward', 'type': 'str', 'value': QtGui.QKeySequence('PgDown').toString()}
#flattenned_settings_dict['kbshortcut_increase_selected_end_time'] = {'name': 'Increase Selected End Time', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+PgUp').toString()}
#flattenned_settings_dict['kbshortcut_decrease_selected_end_time'] = {'name': 'Decrease Selected End Time', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+PgDown').toString()}
#flattenned_settings_dict['kbshortcut_increase_selected_start_time'] = {'name': 'Increase Selected Start Time', 'type': 'str', 'value': QtGui.QKeySequence('Alt+PgUp').toString()}
#flattenned_settings_dict['kbshortcut_decrease_selected_start_time'] = {'name': 'Decrease Selected Start Time', 'type': 'str', 'value': QtGui.QKeySequence('Alt+PgDown').toString()}

#>>>TODO: Add default shortcut key values for below settings
flattenned_settings_dict['kbshortcut_select_next_series'] = {'name': 'Select Next Sample Series', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Up').toString()}
flattenned_settings_dict['kbshortcut_select_previous_series'] = {'name': 'Select Previous Sample Series', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Down').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_next_series_end'] = {'name': 'Move Selection End to Next Series End', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Right').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_prev_series_end'] = {'name': 'Move Selection End to Previous Series End', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Left').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_next_series_start'] = {'name': 'Move Selection Start to Next Series Start', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Shift+Right').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_prev_series_start'] = {'name': 'Move Selection Start to Previous Series Start', 'type': 'str', 'value': QtGui.QKeySequence('Alt+Shift+Left').toString()}

flattenned_settings_dict['kbshortcut_select_next_run'] = {'name': 'Select Next Sample Run', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Up').toString()}
flattenned_settings_dict['kbshortcut_select_previous_run'] = {'name': 'Select Previous Sample Run', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Down').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_next_run_end'] = {'name': 'Move Selection End to Next Run End', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Right').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_prev_run_end'] = {'name': 'Move Selection End to Previous Run End', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Left').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_next_run_start'] = {'name': 'Move Selection Start to Next Run Start', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Shift+Right').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_prev_run_start'] = {'name': 'Move Selection Start to Previous Run Start', 'type': 'str', 'value': QtGui.QKeySequence('Ctrl+Shift+Left').toString()}

flattenned_settings_dict['kbshortcut_select_next_stroke'] = {'name': 'Select Next Stroke', 'type': 'str', 'value': QtGui.QKeySequence('Up').toString()}
flattenned_settings_dict['kbshortcut_select_previous_stroke'] = {'name': 'Select Previous Stroke', 'type': 'str', 'value': QtGui.QKeySequence('Down').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_next_stroke_end'] = {'name': 'Move Selection End to Next Stroke End', 'type': 'str', 'value': QtGui.QKeySequence('Right').toString()}
flattenned_settings_dict['kbshortcut_selection_end_to_prev_stroke_end'] = {'name': 'Move Selection End to Previous Stroke End', 'type': 'str', 'value': QtGui.QKeySequence('Left').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_next_stroke_start'] = {'name': 'Move Selection Start to Next Stroke Start', 'type': 'str', 'value': QtGui.QKeySequence('Shift+Right').toString()}
flattenned_settings_dict['kbshortcut_selection_start_to_prev_stroke_start'] = {'name': 'Move Selection Start to Previous Stroke Start', 'type': 'str', 'value': QtGui.QKeySequence('Shift+Left').toString()}
#<<<


settings_params = [
        {'name': 'Loading Source Data', 'type': 'group', 'children': [
            #'series_detect_max_isi_msec',
            'filter_imported_pen_data',
            'auto_generate_l1segments',
               {'name': 'ioHub HDF5 Trial Segmentation', 'type': 'group', 'children': [
                    'hdf5_trial_start_var_select_filter',
                    'hdf5_trial_end_var_select_filter',
                    'hdf5_apply_time_offset_var_select_filter'
                 ]},
               {'name': 'Stoke Detection', 'type': 'group', 'children': [
                    'stroke_detect_pressed_runs_only',
#                    'stroke_detect_min_value_threshold',
                    'stroke_detect_min_p2p_sample_count',
                    'stroke_detect_edge_type',
                 ]},
        ]},
        {'name': 'Segment Creation', 'type': 'group', 'children': [
            'new_segment_trim_0_pressure_points',
        ]},
        {'name': 'GUI Options', 'type': 'group', 'children': [
            'plotviews_background_color',
            'plotviews_foreground_color',
            'pen_stroke_boundary_size',
            'pen_stroke_boundary_color',
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
               {'name': 'XY Velocity Trace', 'type': 'group', 'children': [
                    'display_timeplot_vtrace',
                    'timeplot_vtrace_color',
                    'timeplot_vtrace_size',
                 ]},
               {'name': 'Acceleration Trace', 'type': 'group', 'children': [
                    'display_timeplot_atrace',
                    'timeplot_atrace_color',
                    'timeplot_atrace_size',
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
        {'name': 'Keyboard Shortcuts', 'type': 'group', 'children': [
            'kbshortcut_create_segment',
            'kbshortcut_delete_segment',
            'kbshortcut_timeplot_increase_mag',
            'kbshortcut_timeplot_decrease_mag',
            'kbshortcut_move_plots_to_selection',
            'kbshortcut_selected_timeperiod_forward',
            'kbshortcut_selected_timeperiod_backward',
#            'kbshortcut_increase_selected_end_time',
#            'kbshortcut_decrease_selected_end_time',
#            'kbshortcut_increase_selected_start_time',
#            'kbshortcut_decrease_selected_start_time',

            'kbshortcut_select_next_series',
            'kbshortcut_select_previous_series',
            'kbshortcut_selection_end_to_next_series_end',
            'kbshortcut_selection_end_to_prev_series_end',
            'kbshortcut_selection_start_to_next_series_start',
            'kbshortcut_selection_start_to_prev_series_start',

            'kbshortcut_select_next_run',
            'kbshortcut_select_previous_run',
            'kbshortcut_selection_end_to_next_run_end',
            'kbshortcut_selection_end_to_prev_run_end',
            'kbshortcut_selection_start_to_next_run_start',
            'kbshortcut_selection_start_to_prev_run_start',

            'kbshortcut_select_next_stroke',
            'kbshortcut_select_previous_stroke',
            'kbshortcut_selection_end_to_next_stroke_end',
            'kbshortcut_selection_end_to_prev_stroke_end',
            'kbshortcut_selection_start_to_next_stroke_start',
            'kbshortcut_selection_start_to_prev_stroke_start',

            ]}
        ]


SETTINGS=dict()
class ProjectSettingsDialog(QtGui.QDialog):
    path2key=dict()
    def __init__(self, parent = None, savedstate=None):
        super(ProjectSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Application Settings")
        layout = QtGui.QVBoxLayout(self)
        self.setLayout(layout)

        if savedstate:
            for key,val in savedstate.items():
                if flattenned_settings_dict.get(key):
                    flattenned_settings_dict[key]['value'] = val

            #self._settings.restoreState(savedstate)

        self.initKeyParamMapping()
        self._settings = Parameter.create(name='params', type='group', children=settings_params)

        # Holds settings keys that have changed by the user when the
        # dialog is closed. Used to update any needed gui values..
        self._updated_settings={}

        self._invalid_settings={}

        self._settings.sigTreeStateChanged.connect(self.handleSettingChange)

        self.initSettingsValues()

        self.ptree = ParameterTree()
        self.ptree.setParameters(self._settings, showTop=False)
        self.ptree.setWindowTitle('MarkWrite Application Settings')

        layout.addWidget(self.ptree)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        wscreen = QtGui.QDesktopWidget().screenGeometry()
        if parent:
            wscreen = QtGui.QDesktopWidget().screenGeometry(parent)
        self.resize(min(500,int(wscreen.width()*.66)),min(700,int(wscreen.height()*.66)))
        # center dialog on same screen as is being used by markwrite app.
        qr = self.frameGeometry()
        cp = wscreen.center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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
                    child.orgvalue = child.value()

    ## If anything changes in the tree
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
                if setting_key.startswith('kbshortcut_'):
                    qks=QtGui.QKeySequence(data)
                    if (len(data)>0 and qks.isEmpty()) or qks.toString() in SETTINGS.values():
                        self._invalid_settings[setting_key]=param
                        continue
                    else:
                        data = u''+qks.toString()
                SETTINGS[setting_key]=data
                self._updated_settings[setting_key] = data
                param.orgvalue=data

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getProjectSettings(parent = None, usersettings = None):
        if usersettings is None:
            usersettings=SETTINGS
        dialog = ProjectSettingsDialog(parent, usersettings)
        result = dialog.exec_()
        for k, v in dialog._invalid_settings.items():
            v.setValue(v.orgvalue)
        dialog._invalid_settings.clear()
        usersettings=dialog._settings.saveState()
        return dialog._updated_settings,SETTINGS, usersettings, result == QtGui.QDialog.Accepted