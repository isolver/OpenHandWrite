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
import numpy as np
import pyqtgraph as pg

from markwrite.gui import ProjectSettingsDialog, SETTINGS,  X_FIELD, Y_FIELD

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

from markwrite.util import getIconFilePath
from markwrite.file_io import loadPredefinedSegmentTagList, readPickle, writePickle
from markwrite.reports import PenSampleReportExporter, SegmentLevelReportExporter, custom_report_classes
from markwrite.segment import PenDataSegment
from dialogs import ExitApplication, fileOpenDlg, ErrorDialog, warnDlg, \
    fileSaveDlg,ConfirmAction,infoDlg
from markwrite.project import MarkWriteProject

DEFAULT_WIN_SIZE = (1200, 800)

DEFAULT_DOCK_PLACEMENT = {
    u"Segment Tree": ('left', (.2, 1.0)),
    u"Timeline": (['right', u"Segment Tree"], (.8, .35)),
    u"Spatial View": (['bottom', u"Timeline"], (.60, .65)),
    u"Selected Pen Points": (['right', u"Spatial View"], (.2, .65)),
}

shortcutkey2action=dict()

ABOUT_DIALOG_TEXT = """
<b> MarkWrite v0.2.1</b> <br>
This software is GLP v3 licensed.<br>
<br>
See licence.txt for license details.
"""

ABOUT_DIALOG_TITLE = "About MarkWrite"


def showNotImplementedDialog(widget, title=None, msg=None, func_name=None):
    if func_name:
        if title is None:
            title = "Function '{0}' Not Implemented"
            title = title.format(func_name)
        if msg is None:
            msg = "The Function '{0}' Has Not Yet Been Implemented."
            msg = msg.format(func_name)
    else:
        if title is None:
            title = "Action Not Implemented"
        if msg is None:
            msg = "The Selected Action Has Not Yet Been Implemented."
    QtGui.QMessageBox.information(widget, title, msg)


def not_implemented(wrapped_func):
    def func_wrapper(*args, **kwargs):
        showNotImplementedDialog(args[0], func_name=wrapped_func.__name__)

    return func_wrapper


def showSegmentNameDialog(tags, default=u""):
    return QtGui.QInputDialog.getItem(MarkWriteMainWindow.instance(),
                                      u"Segment Name (Tag)",
                                      u"Enter the desired pen segment tag, "
                                      u"or selected one from the predefined "
                                      u"tag list.",
                                      [default] + tags,
                                      current=0,
                                      editable=True,
    )

class MarkWriteMainWindow(QtGui.QMainWindow):
    SAMPLE_XY_FIELDS = ['x_filtered', 'y_filtered']
    sigProjectChanged = QtCore.Signal(object)  # new_project
    sigResetProjectData = QtCore.Signal(object)  # project
    sigSelectedPenDataUpdate = QtCore.Signal(object,
                                             object)  # (smin,smax), segmentdata
    sigSegmentCreated = QtCore.Signal(object)  # new segment
    sigSegmentRemoved = QtCore.Signal(object,
                                      object)  # segment being removed,
                                      # segment index in list
    sigAppSettingsUpdated = QtCore.Signal(object, #dict of app settings that changed
                                          object,) #ful settings dict
    sigActiveObjectChanged = QtCore.Signal(object, object) #new, old active objects
    _mainwin_instance=None
    _appdirs = None
    def __init__(self, qtapp):
        global  SETTINGS
        QtGui.QMainWindow.__init__(self)
        MarkWriteMainWindow._mainwin_instance = self

        self._current_project = None
        self._activeobject = None

        self._predefinedtags = loadPredefinedSegmentTagList(u'default.tag')

        # create qt actions used by menu, toolbar, or both
        self.createGuiActions()

        # init GUI related stuff
        self.setupGUI(qtapp)

        self.sigProjectChanged.connect(self.handleProjectChange)
        self.sigSelectedPenDataUpdate.connect(self.handleSelectedPenDataUpdate)
        self.sigAppSettingsUpdated.connect(self._penDataTimeLineWidget.handleUpdatedSettingsEvent)
        self.sigAppSettingsUpdated.connect(self._penDataSpatialViewWidget.handleUpdatedSettingsEvent)
        self.sigAppSettingsUpdated.connect(self._selectedPenDataViewWidget.handleUpdatedSettingsEvent)
        self.sigAppSettingsUpdated.connect(self.handleUpdatedSettingsEvent)

    def handleUpdatedSettingsEvent(self, updates, settings):
        for k, v in updates.items():
            if k.startswith('kbshortcut_'):
                if shortcutkey2action.has_key(k):
                    shortcutkey2action[k].setShortcut(v)
                else:
                    print("{} is not found in shortcutkey2action. Keyboard shortcut has NOT been updated.".format(k))

    @staticmethod
    def instance():
        return MarkWriteMainWindow._mainwin_instance

    @property
    def project(self):
        return self._current_project

    @property
    def activeobject(self):
        return self._activeobject

    def setActiveObject(self, timeperioddatatype=None):
        prevactiveobj = self._activeobject

        self._activeobject = timeperioddatatype
        if timeperioddatatype is None:
            self._activeobject = self.project.selectedtimeregion
        #print "Settings active object:",self._activeobject
        if isinstance(self._activeobject,PenDataSegment):
            #print "**Setting region:",self._activeobject
            self._segmenttree.doNotSetActiveObject=True
            self.project.selectedtimeregion.setRegion(self._activeobject.timerange)
            self._segmenttree.doNotSetActiveObject=False
            self.removeSegmentAction.setEnabled(not self._activeobject.locked)
        else:
            self.removeSegmentAction.setEnabled(False)
        self.sigActiveObjectChanged.emit(self._activeobject,prevactiveobj)

        return self._activeobject

    @property
    def predefinedtags(self):
        if self.project:
            return self.project.autodetected_segment_tags + self._predefinedtags
        return self._predefinedtags

    def createGuiActions(self):
        #
        # File Menu / Toolbar Related Actions
        #
        atext = 'Open a supported pen data ' \
                'file format or previously saved MarkWrite project.'
        aicon = 'folder&32.png'
        self.openFileAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            '&Open',
            self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setEnabled(True)
        self.openFileAction.setStatusTip(atext)
        self.openFileAction.triggered.connect(self.openFile)

        atext = 'Save Project.'
        aicon = 'save&32.png'
        self.saveProjectAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            '&Save',
            self)
        self.saveProjectAction.setShortcut('Ctrl+S')
        self.saveProjectAction.setEnabled(False)
        self.saveProjectAction.setStatusTip(atext)
        self.saveProjectAction.triggered.connect(self.saveProject)

        atext = 'Export Pen Sample Level Report to a File.'
        aicon = 'sample_report&32.png'
        self.exportSampleReportAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Sample Report',
            self)
        #self.exportSampleReportAction.setShortcut('Ctrl+S')
        self.exportSampleReportAction.setEnabled(False)
        self.exportSampleReportAction.setStatusTip(atext)
        self.exportSampleReportAction.triggered.connect(
            self.createPenSampleLevelReportFile)

        atext = 'Export Segment Level Report to a File.'
        aicon = 'segment_report&32.png'
        self.exportSegmentReportAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Segment Report',
            self)
        self.exportSegmentReportAction.setEnabled(False)
        self.exportSegmentReportAction.setStatusTip(atext)
        self.exportSegmentReportAction.triggered.connect(
            self.createSegmentLevelReportFile)

        self.exportSampleReportAction.enableActionsList.append(self.exportSegmentReportAction)

        atext = 'Open the Application Settings Dialog.'
        aicon = 'settings&32.png'
        self.showProjectSettingsDialogAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            '&Settings',
            self)
        self.showProjectSettingsDialogAction.setShortcut('Alt+S')
        self.showProjectSettingsDialogAction.setEnabled(True)
        self.showProjectSettingsDialogAction.setStatusTip(atext)
        self.showProjectSettingsDialogAction.triggered.connect(
            self.handleDisplayAppSettingsDialogEvent)

        atext = 'Close the MarkWrite Application. Any data segmention will be lost!'
        aicon = 'shut_down&32.png'
        self.exitAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Exit',
            self)
        self.exitAction.setShortcut('Ctrl+Alt+Q')
        self.exitAction.setEnabled(True)
        self.exitAction.setStatusTip(atext)
        self.exitAction.triggered.connect(self.closeEvent)

        #
        # Selection Menu / Toolbar Related Actions
        #

        atext = 'Create a Segment Using Currently Selected Pen Data.'
        aicon = 'accept&32.png'
        self.createSegmentAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Create New',
            self)
        self.createSegmentAction.setShortcut(SETTINGS['kbshortcut_create_segment'])
        self.createSegmentAction.setEnabled(False)
        self.createSegmentAction.setStatusTip(atext)
        self.createSegmentAction.triggered.connect(self.createSegment)
        shortcutkey2action['kbshortcut_create_segment'] = self.createSegmentAction

        atext = 'Delete the Selected Segment and any of the segments children.'
        aicon = 'delete&32.png'
        self.removeSegmentAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Delete',
            self)
        self.removeSegmentAction.setShortcut(SETTINGS['kbshortcut_delete_segment'])
        self.removeSegmentAction.setEnabled(False)
        self.removeSegmentAction.setStatusTip(atext)
        self.removeSegmentAction.triggered.connect(self.removeSegment)
        shortcutkey2action['kbshortcut_delete_segment'] = self.removeSegmentAction

        #
        # Timeline Plot Zoom Related Actions
        #

        atext = 'Increase Timeplot Horizontal Magnification 2x'
        aicon = 'zoom_in&32.png'
        self.zoomInTimelineAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Zoom In 2x',
            self)
        self.zoomInTimelineAction.setShortcut(SETTINGS['kbshortcut_timeplot_increase_mag'])
        self.zoomInTimelineAction.setEnabled(False)
        self.zoomInTimelineAction.setStatusTip(atext)
        self.zoomInTimelineAction.triggered.connect(self.zoomInTimeline)
        shortcutkey2action['kbshortcut_timeplot_increase_mag'] = self.zoomInTimelineAction

        atext = 'Decrease Timeplot Horizontal Magnification 2x'
        aicon = 'zoom_out&32.png'
        self.zoomOutTimelineAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Zoom Out 2x',
            self)
        self.zoomOutTimelineAction.setShortcut(SETTINGS['kbshortcut_timeplot_increase_mag'])
        self.zoomOutTimelineAction.setEnabled(False)
        self.zoomOutTimelineAction.setStatusTip(atext)
        self.zoomOutTimelineAction.triggered.connect(self.zoomOutTimeline)
        shortcutkey2action['kbshortcut_timeplot_decrease_mag'] = self.zoomOutTimelineAction

        self.exportSampleReportAction.enableActionsList.append(self.zoomInTimelineAction)
        self.exportSampleReportAction.enableActionsList.append(self.zoomOutTimelineAction)

        atext = 'Reposition Views around Selected Time Period'
        aicon = 'target&32.png'
        self.gotoSelectedTimePeriodAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Go To Selected Time Period',
            self)
        self.gotoSelectedTimePeriodAction.setShortcut(SETTINGS['kbshortcut_move_plots_to_selection'])
        self.gotoSelectedTimePeriodAction.setEnabled(False)
        self.gotoSelectedTimePeriodAction.setStatusTip(atext)
        self.gotoSelectedTimePeriodAction.triggered.connect(self.gotoSelectTimelinePeriod)
        shortcutkey2action['kbshortcut_move_plots_to_selection'] = self.gotoSelectedTimePeriodAction

        atext = "Move selected time period forward, so that it's start time is one sample after the current selection's end time"
        aicon = 'move_selection_forward&32.png'
        self.forwardSelectionAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Jump Forward',
            self)
        self.forwardSelectionAction.setShortcut(SETTINGS['kbshortcut_selected_timeperiod_forward'])
        self.forwardSelectionAction.setEnabled(False)
        self.forwardSelectionAction.setStatusTip(atext)
        self.forwardSelectionAction.triggered.connect(self.jumpTimeSelectionForward)
        shortcutkey2action['kbshortcut_selected_timeperiod_forward'] = self.forwardSelectionAction

        atext = "Move selected time period backward, so that it's end time is one sample prior to the current selection's start time."
        aicon = 'move_selection_backward&32.png'
        self.backwardSelectionAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Jump Backward',
            self)
        self.backwardSelectionAction.setShortcut(SETTINGS['kbshortcut_selected_timeperiod_backward'])
        self.backwardSelectionAction.setEnabled(False)
        self.backwardSelectionAction.setStatusTip(atext)
        self.backwardSelectionAction.triggered.connect(self.jumpTimeSelectionBackward)
        shortcutkey2action['kbshortcut_selected_timeperiod_backward'] = self.backwardSelectionAction

        atext = 'Increase Timeline Selection End Time'
        aicon = 'increase_select_endtime&32.png'
        self.increaseSelectionEndPointAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Increase Selection End',
            self)
        self.increaseSelectionEndPointAction.setShortcut(SETTINGS['kbshortcut_increase_selected_end_time'])
        self.increaseSelectionEndPointAction.setEnabled(False)
        self.increaseSelectionEndPointAction.setStatusTip(atext)
        self.increaseSelectionEndPointAction.triggered.connect(self.increaseSelectionEndPointTime)
        shortcutkey2action['kbshortcut_increase_selected_end_time'] = self.increaseSelectionEndPointAction

        atext = 'Decrease Timeline Selection End Time'
        aicon = 'descrease_select_endtime&32.png'
        self.decreaseSelectionEndPointAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Decrease Selection End',
            self)
        self.decreaseSelectionEndPointAction.setShortcut(SETTINGS['kbshortcut_decrease_selected_end_time'])
        self.decreaseSelectionEndPointAction.setEnabled(False)
        self.decreaseSelectionEndPointAction.setStatusTip(atext)
        self.decreaseSelectionEndPointAction.triggered.connect(self.decreaseSelectionEndPointTime)
        shortcutkey2action['kbshortcut_decrease_selected_end_time'] = self.decreaseSelectionEndPointAction

        #======================================
        atext = 'Increase Timeline Selection Start Time'
        aicon = 'increase_select_starttime&32.png'
        self.increaseSelectionStartPointAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Increase Selection Start',
            self)
        self.increaseSelectionStartPointAction.setShortcut(SETTINGS['kbshortcut_increase_selected_start_time'])
        self.increaseSelectionStartPointAction.setEnabled(False)
        self.increaseSelectionStartPointAction.setStatusTip(atext)
        self.increaseSelectionStartPointAction.triggered.connect(self.increaseSelectionStartPointTime)
        shortcutkey2action['kbshortcut_increase_selected_start_time'] = self.increaseSelectionStartPointAction

        atext = 'Decrease Timeline Selection Start Time'
        aicon = 'decrease_select_starttime&32.png'
        self.decreaseSelectionStartPointAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Decrease Selection Start',
            self)
        self.decreaseSelectionStartPointAction.setShortcut(SETTINGS['kbshortcut_decrease_selected_start_time'])
        self.decreaseSelectionStartPointAction.setEnabled(False)
        self.decreaseSelectionStartPointAction.setStatusTip(atext)
        self.decreaseSelectionStartPointAction.triggered.connect(self.decreaseSelectionStartPointTime)
        shortcutkey2action['kbshortcut_decrease_selected_start_time'] = self.decreaseSelectionStartPointAction

        #
        # Next/Prev Sample Series Actions
        #
        atext = 'Select Next Sample Series'
        aicon = 'next_series&32.png'
        self.selectNextSampleSeriesAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Select Next Sample Series',
            self)
        self.selectNextSampleSeriesAction.setShortcut(SETTINGS['kbshortcut_select_next_series'])
        self.selectNextSampleSeriesAction.setEnabled(False)
        self.selectNextSampleSeriesAction.setStatusTip(atext)
        self.selectNextSampleSeriesAction.triggered.connect(self.selectNextSampleSeries)
        shortcutkey2action['kbshortcut_select_next_series'] = self.selectNextSampleSeriesAction

        atext = 'Select Previous Sample Series'
        aicon = 'prev_series&32.png'
        self.selectPrevSampleSeriesAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Select Previous Sample Series',
            self)
        self.selectPrevSampleSeriesAction.setShortcut(SETTINGS['kbshortcut_select_previous_series'])
        self.selectPrevSampleSeriesAction.setEnabled(False)
        self.selectPrevSampleSeriesAction.setStatusTip(atext)
        self.selectPrevSampleSeriesAction.triggered.connect(self.selectPrevSampleSeries)
        shortcutkey2action['kbshortcut_select_previous_series'] = self.selectPrevSampleSeriesAction

        atext = 'Move Selection End to Next Series End'
        aicon = 'selectend_to_next_seriesend&32.png'
        self.advanceSelectionEndToNextSeriesEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionEndToNextSeriesEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_next_series_end'])
        self.advanceSelectionEndToNextSeriesEndAction.setEnabled(False)
        self.advanceSelectionEndToNextSeriesEndAction.setStatusTip(atext)
        self.advanceSelectionEndToNextSeriesEndAction.triggered.connect(self.advanceSelectionEndToNextSeriesEnd)
        shortcutkey2action['kbshortcut_selection_end_to_next_series_end'] =self.advanceSelectionEndToNextSeriesEndAction

        atext = 'Move Selection End to Previous Series End'
        aicon = 'selectend_to_prev_seriesend&32.png'
        self.returnSelectionEndToPrevSeriesEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionEndToPrevSeriesEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_prev_series_end'])
        self.returnSelectionEndToPrevSeriesEndAction.setEnabled(False)
        self.returnSelectionEndToPrevSeriesEndAction.setStatusTip(atext)
        self.returnSelectionEndToPrevSeriesEndAction.triggered.connect(self.returnSelectionEndToPrevSeriesEnd)
        shortcutkey2action['kbshortcut_selection_end_to_prev_series_end'] = self.returnSelectionEndToPrevSeriesEndAction

        atext = 'Move Selection Start to Next Series Start'
        aicon = 'selectstart_to_next_seriesstart&32.png'
        self.advanceSelectionStartToNextSeriesStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionStartToNextSeriesStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_next_series_start'])
        self.advanceSelectionStartToNextSeriesStartAction.setEnabled(False)
        self.advanceSelectionStartToNextSeriesStartAction.setStatusTip(atext)
        self.advanceSelectionStartToNextSeriesStartAction.triggered.connect(self.advanceSelectionStartToNextSeriesStart)
        shortcutkey2action['kbshortcut_selection_start_to_next_series_start'] = self.advanceSelectionStartToNextSeriesStartAction

        atext = 'Move Selection Start to Previous Series Start'
        aicon = 'selectstart_to_prev_seriesstart&32.png'
        self.returnSelectionStartToPrevSeriesStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionStartToPrevSeriesStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_prev_series_start'])
        self.returnSelectionStartToPrevSeriesStartAction.setEnabled(False)
        self.returnSelectionStartToPrevSeriesStartAction.setStatusTip(atext)
        self.returnSelectionStartToPrevSeriesStartAction.triggered.connect(self.returnSelectionStartToPrevSeriesStart)
        shortcutkey2action['kbshortcut_selection_start_to_prev_series_start'] = self.returnSelectionStartToPrevSeriesStartAction

        #
        # Next/Prev Pen Pressed Run Actions
        #
        atext = 'Selected Next Pressed Sample Run'
        aicon = 'next_run&32.png'
        self.selectNextPressedRunAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.selectNextPressedRunAction.setShortcut(SETTINGS['kbshortcut_select_next_run'])
        self.selectNextPressedRunAction.setEnabled(False)
        self.selectNextPressedRunAction.setStatusTip(atext)
        self.selectNextPressedRunAction.triggered.connect(self.selectNextPressedRun)
        shortcutkey2action['kbshortcut_select_next_run'] =self.selectNextPressedRunAction

        atext = 'Selected Previous Pressed Sample Run'
        aicon = 'prev_run&32.png'
        self.selectPrevPressedRunAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.selectPrevPressedRunAction.setShortcut(SETTINGS['kbshortcut_select_previous_run'])
        self.selectPrevPressedRunAction.setEnabled(False)
        self.selectPrevPressedRunAction.setStatusTip(atext)
        self.selectPrevPressedRunAction.triggered.connect(self.selectPrevPressedRun)
        shortcutkey2action['kbshortcut_select_previous_run'] = self.selectPrevPressedRunAction

        atext = 'Move Selection End to Next Pressed Run End'
        aicon = 'selectend_to_next_runend&32.png'
        self.advanceSelectionEndToNextRunEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionEndToNextRunEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_next_run_end'])
        self.advanceSelectionEndToNextRunEndAction.setEnabled(False)
        self.advanceSelectionEndToNextRunEndAction.setStatusTip(atext)
        self.advanceSelectionEndToNextRunEndAction.triggered.connect(self.advanceSelectionEndToNextRunEnd)
        shortcutkey2action['kbshortcut_selection_end_to_next_run_end'] = self.advanceSelectionEndToNextRunEndAction

        atext = 'Move Selection End to Previous Pressed Run End'
        aicon = 'selectend_to_prev_runend&32.png'
        self.returnSelectionEndToPrevRunEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionEndToPrevRunEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_prev_run_end'])
        self.returnSelectionEndToPrevRunEndAction.setEnabled(False)
        self.returnSelectionEndToPrevRunEndAction.setStatusTip(atext)
        self.returnSelectionEndToPrevRunEndAction.triggered.connect(self.returnSelectionEndToPrevRunEnd)
        shortcutkey2action['kbshortcut_selection_end_to_prev_run_end'] = self.returnSelectionEndToPrevRunEndAction

        atext = 'Move Selection Start to Next Pressed Run Start'
        aicon = 'selectstart_to_next_runstart&32.png'
        self.advanceSelectionStartToNextRunStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionStartToNextRunStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_next_run_start'])
        self.advanceSelectionStartToNextRunStartAction.setEnabled(False)
        self.advanceSelectionStartToNextRunStartAction.setStatusTip(atext)
        self.advanceSelectionStartToNextRunStartAction.triggered.connect(self.advanceSelectionStartToNextRunStart)
        shortcutkey2action['kbshortcut_selection_start_to_next_run_start'] = self.advanceSelectionStartToNextRunStartAction

        atext = 'Move Selection Start to Previous Pressed Run Start'
        aicon = 'selectstart_to_prev_runstart&32.png'
        self.returnSelectionStartToPrevRunStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionStartToPrevRunStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_prev_run_start'])
        self.returnSelectionStartToPrevRunStartAction.setEnabled(False)
        self.returnSelectionStartToPrevRunStartAction.setStatusTip(atext)
        self.returnSelectionStartToPrevRunStartAction.triggered.connect(self.returnSelectionStartToPrevRunStart)
        shortcutkey2action['kbshortcut_selection_start_to_prev_run_start'] = self.returnSelectionStartToPrevRunStartAction

        #
        # Next/Prev Stroke Actions
        #
        atext = 'Select the Next Pen Stroke'
        aicon = 'next_stroke&32.png'
        self.selectNextStrokeAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Next Pen Stroke',
            self)
        self.selectNextStrokeAction.setShortcut(SETTINGS['kbshortcut_select_next_stroke'])
        self.selectNextStrokeAction.setEnabled(False)
        self.selectNextStrokeAction.setStatusTip(atext)
        self.selectNextStrokeAction.triggered.connect(self.selectNextStroke)
        shortcutkey2action['kbshortcut_select_next_stroke'] = self.selectNextStrokeAction

        atext = 'Select the Previous Pen Stroke'
        aicon = 'prev_stroke&32.png'
        self.selectPrevStrokeAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Previous Pen Stroke',
            self)
        self.selectPrevStrokeAction.setShortcut(SETTINGS['kbshortcut_select_previous_stroke'])
        self.selectPrevStrokeAction.setEnabled(False)
        self.selectPrevStrokeAction.setStatusTip(atext)
        self.selectPrevStrokeAction.triggered.connect(self.selectPrevStroke)
        shortcutkey2action['kbshortcut_select_previous_stroke'] = self.selectPrevStrokeAction

        atext = 'Move Selection End to Next Stroke End'
        aicon = 'selectend_to_next_strokeend&32.png'
        self.advanceSelectionEndToNextStrokeEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionEndToNextStrokeEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_next_stroke_end'])
        self.advanceSelectionEndToNextStrokeEndAction.setEnabled(False)
        self.advanceSelectionEndToNextStrokeEndAction.setStatusTip(atext)
        self.advanceSelectionEndToNextStrokeEndAction.triggered.connect(self.advanceSelectionEndToNextStrokeEnd)
        shortcutkey2action['kbshortcut_selection_end_to_next_stroke_end'] = self.advanceSelectionEndToNextStrokeEndAction

        atext = 'Move Selection End to Previous Stroke End'
        aicon = 'selectend_to_prev_strokeend&32.png'
        self.returnSelectionEndToPrevStrokeEndAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionEndToPrevStrokeEndAction.setShortcut(SETTINGS['kbshortcut_selection_end_to_prev_stroke_end'])
        self.returnSelectionEndToPrevStrokeEndAction.setEnabled(False)
        self.returnSelectionEndToPrevStrokeEndAction.setStatusTip(atext)
        self.returnSelectionEndToPrevStrokeEndAction.triggered.connect(self.returnSelectionEndToPrevStrokeEnd)
        shortcutkey2action['kbshortcut_selection_end_to_prev_stroke_end'] =self.returnSelectionEndToPrevStrokeEndAction

        atext = 'Move Selection Start to Next Stroke Start'
        aicon = 'selectstart_to_next_strokestart&32.png'
        self.advanceSelectionStartToNextStrokeStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.advanceSelectionStartToNextStrokeStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_next_stroke_start'])
        self.advanceSelectionStartToNextStrokeStartAction.setEnabled(False)
        self.advanceSelectionStartToNextStrokeStartAction.setStatusTip(atext)
        self.advanceSelectionStartToNextStrokeStartAction.triggered.connect(self.advanceSelectionStartToNextStrokeStart)
        shortcutkey2action['kbshortcut_selection_start_to_next_stroke_start'] = self.advanceSelectionStartToNextStrokeStartAction

        atext = 'Move Selection Start to Previous Stroke Start'
        aicon = 'selectstart_to_prev_strokestart&32.png'
        self.returnSelectionStartToPrevStrokeStartAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            atext,
            self)
        self.returnSelectionStartToPrevStrokeStartAction.setShortcut(SETTINGS['kbshortcut_selection_start_to_prev_stroke_start'])
        self.returnSelectionStartToPrevStrokeStartAction.setEnabled(False)
        self.returnSelectionStartToPrevStrokeStartAction.setStatusTip(atext)
        self.returnSelectionStartToPrevStrokeStartAction.triggered.connect(self.returnSelectionStartToPrevStrokeStart)
        shortcutkey2action['kbshortcut_selection_start_to_prev_stroke_start'] = self.returnSelectionStartToPrevStrokeStartAction

        #---

        self.exportSampleReportAction.enableActionsList.append(self.zoomInTimelineAction)
        self.exportSampleReportAction.enableActionsList.append(self.zoomOutTimelineAction)
        self.exportSampleReportAction.enableActionsList.append(self.gotoSelectedTimePeriodAction)
        self.exportSampleReportAction.enableActionsList.append(self.decreaseSelectionEndPointAction)
        self.exportSampleReportAction.enableActionsList.append(self.increaseSelectionEndPointAction)
        self.exportSampleReportAction.enableActionsList.append(self.decreaseSelectionStartPointAction)
        self.exportSampleReportAction.enableActionsList.append(self.increaseSelectionStartPointAction)
        self.exportSampleReportAction.enableActionsList.append(self.forwardSelectionAction)
        self.exportSampleReportAction.enableActionsList.append(self.backwardSelectionAction)

        self.exportSampleReportAction.enableActionsList.append(self.selectNextSampleSeriesAction)
        self.exportSampleReportAction.enableActionsList.append(self.selectPrevSampleSeriesAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionEndToNextSeriesEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionEndToPrevSeriesEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionStartToNextSeriesStartAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionStartToPrevSeriesStartAction)


        self.exportSampleReportAction.enableActionsList.append(self.selectNextPressedRunAction)
        self.exportSampleReportAction.enableActionsList.append(self.selectPrevPressedRunAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionEndToNextRunEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionEndToPrevRunEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionStartToNextRunStartAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionStartToPrevRunStartAction)


        self.exportSampleReportAction.enableActionsList.append(self.selectNextStrokeAction)
        self.exportSampleReportAction.enableActionsList.append(self.selectPrevStrokeAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionEndToNextStrokeEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionEndToPrevStrokeEndAction)
        self.exportSampleReportAction.enableActionsList.append(self.advanceSelectionStartToNextStrokeStartAction)
        self.exportSampleReportAction.enableActionsList.append(self.returnSelectionStartToPrevStrokeStartAction)
        #
        # Help Menu / Toolbar Related Actions
        #

        atext = 'Displays the MarkWrite About Dialog.'
        aicon = 'info&32.png'
        self.aboutAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'About',
            self)
        self.aboutAction.setEnabled(True)
        self.aboutAction.setStatusTip(atext)
        self.aboutAction.triggered.connect(self.showAboutDialog)

    def setupGUI(self, app):
        '''

        :return:
        '''

        #
        ## Create Main GUI Menu Bar
        #

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openFileAction)
        fileMenu.addAction(self.saveProjectAction)
        fileMenu.addAction(self.showProjectSettingsDialogAction)
        fileMenu.addSeparator()
        exportMenu = fileMenu.addMenu("&Export")
        exportMenu.addAction(self.exportSampleReportAction)
        exportMenu.addAction(self.exportSegmentReportAction)
        exportMenu.addSeparator()
        self.customReportActions=[]
        for custom_report in custom_report_classes:
            a = exportMenu.addAction(custom_report.reportlabel(), lambda: self.exportCustomReport(custom_report))
            a.setEnabled(False)
            self.customReportActions.append(a)
            self.exportSampleReportAction.enableActionsList.append(a)

        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        segmentMenu = menubar.addMenu('&Segment')
        segmentMenu.addAction(self.createSegmentAction)
        segmentMenu.addAction(self.removeSegmentAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(self.aboutAction)

        self.toolbarFile = self.addToolBar('File')
        self.toolbarFile.addAction(self.openFileAction)
        self.toolbarFile.addAction(self.saveProjectAction)
        self.toolbarFile.addAction(self.showProjectSettingsDialogAction)
        self.toolbarFile.addAction(self.exportSampleReportAction)
        self.toolbarFile.addAction(self.exportSegmentReportAction)


        self.toolbarsegment = self.addToolBar('Segment')
        self.toolbarsegment.addAction(self.createSegmentAction)
        self.toolbarsegment.addAction(self.removeSegmentAction)

        self.toolbarselecttimeperiod = self.addToolBar('Selected Time Period')
        self.toolbarselecttimeperiod.addAction(self.zoomInTimelineAction)
        self.toolbarselecttimeperiod.addAction(self.zoomOutTimelineAction)
        self.toolbarselecttimeperiod.addAction(self.gotoSelectedTimePeriodAction)
        self.toolbarselecttimeperiod.addAction(self.decreaseSelectionStartPointAction)
        self.toolbarselecttimeperiod.addAction(self.increaseSelectionStartPointAction)
        self.toolbarselecttimeperiod.addAction(self.backwardSelectionAction)
        self.toolbarselecttimeperiod.addAction(self.forwardSelectionAction)
        self.toolbarselecttimeperiod.addAction(self.decreaseSelectionEndPointAction)
        self.toolbarselecttimeperiod.addAction(self.increaseSelectionEndPointAction)

        self.toolbarseriesselect = self.addToolBar('Sample Series Selection')
        self.toolbarseriesselect.addAction(self.returnSelectionStartToPrevSeriesStartAction)
        self.toolbarseriesselect.addAction(self.advanceSelectionStartToNextSeriesStartAction)
        self.toolbarseriesselect.addAction(self.selectPrevSampleSeriesAction)
        self.toolbarseriesselect.addAction(self.selectNextSampleSeriesAction)
        self.toolbarseriesselect.addAction(self.returnSelectionEndToPrevSeriesEndAction)
        self.toolbarseriesselect.addAction(self.advanceSelectionEndToNextSeriesEndAction)

        self.toolbarrunselect = self.addToolBar('Pressed Run Selection')
        self.toolbarrunselect.addAction(self.returnSelectionStartToPrevRunStartAction)
        self.toolbarrunselect.addAction(self.advanceSelectionStartToNextRunStartAction)
        self.toolbarrunselect.addAction(self.selectPrevPressedRunAction)
        self.toolbarrunselect.addAction(self.selectNextPressedRunAction)
        self.toolbarrunselect.addAction(self.returnSelectionEndToPrevRunEndAction)
        self.toolbarrunselect.addAction(self.advanceSelectionEndToNextRunEndAction)


        self.toolbarstrokeselect = self.addToolBar('Pen Stroke Selection')
        self.toolbarstrokeselect.addAction(self.returnSelectionStartToPrevStrokeStartAction)
        self.toolbarstrokeselect.addAction(self.advanceSelectionStartToNextStrokeStartAction)
        self.toolbarstrokeselect.addAction(self.selectPrevStrokeAction)
        self.toolbarstrokeselect.addAction(self.selectNextStrokeAction)
        self.toolbarstrokeselect.addAction(self.returnSelectionEndToPrevStrokeEndAction)
        self.toolbarstrokeselect.addAction(self.advanceSelectionEndToNextStrokeEndAction)

        self.toolbarHelp = self.addToolBar('Help')
        self.toolbarHelp.addAction(self.aboutAction)

        #
        ## Create App Dock Area
        #

        self._dockarea = DockArea()
        self.setCentralWidget(self._dockarea)

        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)


        # Create Docking Layout
        def addDock(name, inner_widget=None):
            ww, wh = DEFAULT_WIN_SIZE

            dpos, (dw, dh) = DEFAULT_DOCK_PLACEMENT[name]
            if isinstance(dpos, basestring):
                self._dockarea.addDock(Dock(name, size=[ww * dw, wh * dh]),
                                       dpos)
            else:
                self._dockarea.addDock(Dock(name, size=[ww * dw, wh * dh]),
                                       dpos[0], self._dockarea.docks[dpos[1]])

            if inner_widget:
                self._dockarea.docks[name].addWidget(inner_widget)

        from markwrite.gui.selecteddataview import SelectedPointsPlotWidget
        from markwrite.gui.spatialview import PenDataSpatialPlotWidget
        from markwrite.gui.timelineplot import PenDataTemporalPlotWidget
        from markwrite.gui.segmenttree import SegmentInfoDockArea

        self._segmenttree = SegmentInfoDockArea()
        addDock(u"Segment Tree", self._segmenttree)
        self._penDataTimeLineWidget = PenDataTemporalPlotWidget()
        self._penDataSpatialViewWidget = PenDataSpatialPlotWidget()
        addDock(u"Timeline", self._penDataTimeLineWidget)
        addDock(u"Spatial View", self._penDataSpatialViewWidget)
        self._selectedPenDataViewWidget = SelectedPointsPlotWidget()
        addDock(u"Selected Pen Points", self._selectedPenDataViewWidget)

        #
        ## Do Misc. GUI setup.
        #

        self.setWindowIcon(QtGui.QIcon(getIconFilePath('edit&32.png')))

        self.statusBar().showMessage('Ready')
        self.updateAppTitle()

        self.resize(*DEFAULT_WIN_SIZE)

    @property
    def penDataTemporalPlotWidget(self):
        return self._penDataTimeLineWidget

    def updateAppTitle(self):
        if self._current_project is None:
            fileName = u''
        else:
            fileName = self._current_project.name
            fileName = u'{0} : '.format(fileName)

        app_title = u'MarkWrite'
        full_title = u'{0}{1}'.format(fileName, app_title)

        self.setWindowTitle(full_title)

    def showAboutDialog(self):
        QtGui.QMessageBox.about(self, ABOUT_DIALOG_TITLE, ABOUT_DIALOG_TEXT)
        self.sender().enableAndDisableActions()


    def openFile(self):
        file_path = fileOpenDlg()
        if file_path:
            file_path = file_path[0]
            if len(file_path) > 0:

                try:
                    import os
                    _, fname = os.path.split(file_path)
                    with pg.ProgressDialog("Loading Pen Data from: {}".format(fname), 0, maximum=100, parent=self, busyCursor=False) as dlg:
                        self._progressdlg=dlg
                        wmproj = MarkWriteProject(file_path=file_path, mwapp=self)

                        wmproj.selectedtimeregion.setBounds(bounds=(wmproj.pendata['time'][0], wmproj.pendata['time'][-1]))


                        self.sigProjectChanged.emit(wmproj)
                        self.sigResetProjectData.emit(wmproj)

                        if wmproj.autosegl1 is True:
                            for i, atrial in enumerate(wmproj.trial_boundaries):
                                self.createSegmentAction.setEnabled(True)
                                self.project.selectedtimeregion.setRegion((atrial['start_time'], atrial['end_time']))
                                seg = self.createSegment("Trial%d"%(i+1),trim_time_region=False)
                                if seg:
                                    seg.locked = True
                                else:
                                    print("!! Error: Unable to create segment for trial %d, with time period [%.3f, %.3f]."%(i,atrial['start_time'], atrial['end_time']))
                            self.setActiveObject(self.project.segmenttree.children[0])
                        else:
                            wmproj.selectedtimeregion.setRegion([wmproj.pendata['time'][0], wmproj.pendata['time'][0] + 1.0])

                        dlg.setValue(dlg.maximum())
                        dlg.hide()
                except:
                    import traceback

                    traceback.print_exc()
                    ErrorDialog.info_text = u"An error occurred while " \
                                            u"opening:\n%s\nMarkWrite will " \
                                            u"now close." % (
                    file_path)
                    ErrorDialog().display()
                    self.closeEvent(u'FORCE_EXIT')
                finally:
                    self._progressdlg=None

    def saveProject(self):
        if self.project is None:
            return

        print "TODO: Implement save project action."

        save_to_path=fileSaveDlg(initFilePath="",
                    initFileName=u"%s.%s"%(self.project.name,
                                           self.project.project_file_extension),
                        prompt=u"Save MarkWrite Project",
                        allowed="MarkWrite Project files "
                                "(*.%s)"%self.project.project_file_extension,
                        parent=self)

        if save_to_path:
            self.project.save(save_to_path)

    def createPenSampleLevelReportFile(self):
        default_file_name = u"pen_samples_{0}.txt".format(self.project.name)
        file_path = fileSaveDlg(initFileName=default_file_name,
                                prompt="Export Pen Sample Report")
        if file_path:
            PenSampleReportExporter().export(file_path, self.project)

    def createSegmentLevelReportFile(self):
        default_file_name = u"segments_{0}.txt".format(self.project.name)
        file_path = fileSaveDlg(initFileName=default_file_name,
                                prompt="Export Segment Level Report")
        if file_path:
            SegmentLevelReportExporter().export(file_path, self.project)

    def exportCustomReport(self,reportcls):
        default_file_name = u"{}_{}.txt".format(reportcls.outputfileprefix(),self.project.name)
        file_path = fileSaveDlg(initFileName=default_file_name,
                                prompt="Export %s"%(reportcls.reportlabel()))
        if file_path:
            reportcls().export(file_path, self.project)

    def createSegment(self, name=None, trim_time_region = True):
        """
        Displays the Create Segment dialog. If dialog is not cancelled and
        segment name length >0, then create a new segment and add to the
        projects segment list.
        :return:
        """
        if self.createSegmentAction.isEnabled():
            # Shrink timeline selection region to fit start and end time
            # of possible segment being created.
            orgval = SETTINGS['new_segment_trim_0_pressure_points']

            timeperiod = self.project.selectedtimeperiod[:]
            if trim_time_region is False:
                SETTINGS['new_segment_trim_0_pressure_points']=False

            pendata_ix_range = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(*timeperiod)
            new_segment = None
            if len(pendata_ix_range)>0:
                if trim_time_region:
                    segmenttimeperiod = self.project.pendata['time'][pendata_ix_range]
                    self.project.selectedtimeregion.setRegion(segmenttimeperiod)

                ok = True
                if not name:
                    name, ok = showSegmentNameDialog(self.predefinedtags)
                name = unicode(name).strip().replace('\t', "#")

                if len(name) > 0 and ok:
                    psid = self.project.getSelectedDataSegmentIDs()[0]
                    new_segment = self.project.createSegmentFromSelectedPenData(name, psid)
                    self.handleSelectedPenDataUpdate(None,None)
                    self.sigSegmentCreated.emit(new_segment)
                    self.setActiveObject(new_segment)
                else:
                    # If segment creation was cancelled or failed, then reset
                    # timeline selection region to original time period.
                    self.project.selectedtimeregion.setRegion(timeperiod)

            SETTINGS['new_segment_trim_0_pressure_points'] = orgval
            return new_segment

        else:
            ErrorDialog.info_text = u"Segment Creation Failed.\nNo selected " \
                                    u"pen data."
            ErrorDialog().display()

    def removeSegment(self):
        ConfirmAction.text = 'Delete Segment Confirmation'
        ConfirmAction.info_text = "Are you sure you want to <b>permanently deleted</b> the currently selected segment?" \
                                  "<br><br>" \
                                  "Any children of this segment will also be deleted."
        yes = ConfirmAction.display()
        if not yes:
            return
        segment = self.activeobject
        if segment and segment.parent is not None:
            seg_ix = segment.parent.getChildIndex(segment)
            # Decrement the pendata array 'segment_id' field for elements within
            # the segment being removed so that # of segments that contain each
            # pen point can be tracked
            allpendata = self.project.pendata
            segment_filter = (allpendata['time'] >= segment.starttime) & (
            allpendata['time'] <= segment.endtime)
            allpendata['segment_id'][segment_filter] = segment.parent.id
            self.setActiveObject(self.project.selectedtimeregion)
            self.handleSelectedPenDataUpdate(None,None)
            self.sigSegmentRemoved.emit(segment, seg_ix)
            self.project.modified = True

            segment.parent.removeChild(segment)
        else:
            print "   - Remove action IGNORED"
       #print "<< removeSegment"

    def handleProjectChange(self, project):
        if self._current_project:
            pass
        self._current_project = project
        self.setActiveObject(self.project.selectedtimeregion)
        self.updateAppTitle()
        self.saveProjectAction.setEnabled(project.modified)
        self.exportSampleReportAction.setEnabled(True)

    def zoomInTimeline(self):
        # TODO: Move method to _penDataTimeLineWidget
        self._penDataTimeLineWidget.scaleBy(x=0.5)

    def zoomOutTimeline(self):
        # TODO: Move method to _penDataTimeLineWidget
        self._penDataTimeLineWidget.scaleBy(x=2.0)#,center=(xmin+xmax)/2)

    def gotoSelectTimelinePeriod(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax , selpendat= self._penDataTimeLineWidget.currentSelection.selectedtimerangeanddata
        xpad = (xmax-xmin)/2
        pdat=self.project.pendata
        rx=(max(0,xmin-xpad),min(xmax+xpad,self._penDataTimeLineWidget.maxTime))
        if SETTINGS['timeplot_enable_ymouse']:
            ry = (
                    min(selpendat[X_FIELD].min(), selpendat[Y_FIELD].min()),
                    max(selpendat[X_FIELD].max(), selpendat[Y_FIELD].max()))
        else:
            ry = (0, max(pdat[X_FIELD].max(),pdat[Y_FIELD].max()))
        self._penDataTimeLineWidget.setPlotRange(xrange=rx, yrange=ry)

    def jumpTimeSelectionForward(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax = self.project.selectedtimeregion.getRegion()
        pendata_ix_range = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
        if len(pendata_ix_range):
            nix_min = pendata_ix_range[1]+1
            if self.project.pendata['pressure'][nix_min]==0.0:
                start_ixs,stop_ixs,lengths=self.project.nonzero_region_ix
                next_starts = start_ixs[start_ixs>nix_min]
                if len(next_starts)>0:
                    nix_min=next_starts[0]
                else:
                    infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be moved forward.<br>Reason: NTs index not available.")
                    return
            nxmin = self.project.pendata['time'][nix_min]
            nxmax = min(nxmin +(xmax-xmin), self.project.pendata['time'][-1])
            if nxmin >= nxmax:
                infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be moved forward.<br>Reason: End of data reached.")
                return
            self.project.selectedtimeregion.setRegion([nxmin,nxmax])

            (vmin,vmax),(_,_)=self._penDataTimeLineWidget.getViewRange()
            if nxmax >= vmax:
                self._penDataTimeLineWidget.translateViewBy(x=(nxmax-vmax)*1.25)

    def jumpTimeSelectionBackward(self):
        # TODO: Move method to _penDataTimeLineWidget
        if 0:
            xmin, xmax = self.project.selectedtimeregion.getRegion()
            nxmax =xmin-0.001
            nxmin = max(nxmax-(xmax-xmin),0.0)
            pendata_ix_range = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(nxmin,nxmax)
            if len(pendata_ix_range):
                segmenttimeperiod = self.project.pendata['time'][pendata_ix_range]
                self.project.selectedtimeregion.setRegion(segmenttimeperiod)

                (vmin,vmax),(_,_)=self._penDataTimeLineWidget.getViewRange()
                if nxmin < vmin:
                    self._penDataTimeLineWidget.translateViewBy(x=(nxmin-vmin)*1.25)
        else:
            xmin, xmax = self.project.selectedtimeregion.getRegion()
            pendata_ix_range = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
            if len(pendata_ix_range):
                nix_max = pendata_ix_range[0]-1
                if nix_max<=0:
                    infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be moved backward.<br>Reason: NTe index out of bounds.")
                    return
                if self.project.pendata['pressure'][nix_max]==0.0:
                    start_ixs,stop_ixs,lengths=self.project.nonzero_region_ix
                    prev_stops = stop_ixs[stop_ixs<=nix_max]
                    if len(prev_stops)>0:
                        nix_max=prev_stops[-1]
                    else:
                        infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be moved backward.<br>Reason: NTe index not available.")
                        return
                nxmax = self.project.pendata['time'][nix_max]
                nxmin = max(nxmax -(xmax-xmin), 0.0)
                if nxmin >= nxmax:
                    infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be moved backward.<br>Reason: End of data reached.")
                    return
                self.project.selectedtimeregion.setRegion([nxmin,nxmax])

                (vmin,vmax),(_,_)=self._penDataTimeLineWidget.getViewRange()
                if nxmin <= vmin:
                    self._penDataTimeLineWidget.translateViewBy(x=(nxmin-vmin)*1.25)

    def increaseSelectionEndPointTime(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax = self.project.selectedtimeregion.getRegion()
        ix_bounds = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
        if len(ix_bounds)>0:
            min_ix, max_ix = ix_bounds
            start_ixs,stop_ixs,lengths=self.project.nonzero_region_ix
            next_max_ix = stop_ixs[stop_ixs>(max_ix+1)][0]
            #print "org_max_ix, new_max_ix",max_ix,next_max_ix
            #print 'new start , end samples: ',self.project.pendata[[min_ix, next_max_ix]]
            if next_max_ix < self.project.pendata.shape[0]:
                segmenttimeperiod = self.project.pendata['time'][[min_ix, next_max_ix]]
                min_ix, next_max_ix = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(*segmenttimeperiod)
                self.project.selectedtimeregion.setRegion(self.project.pendata['time'][[min_ix, next_max_ix]])
                _,nxmax=segmenttimeperiod
                (vmin,vmax),(_,_)=self._penDataTimeLineWidget.getViewRange()
                if nxmax >= vmax:
                    self._penDataTimeLineWidget.translateViewBy(x=(nxmax-vmax)*1.25)
            else:
                 infoDlg(title=u"Action Aborted", prompt=u"The selected time period can not be extended<br>as it is at the end of the data samples.")


    def decreaseSelectionEndPointTime(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax = self.project.selectedtimeregion.getRegion()
        ix_bounds = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
        if len(ix_bounds)>0:
            min_ix, max_ix = ix_bounds
            if np.all(self.project.nonzero_pressure_mask[min_ix:max_ix]):
                self.project.selectedtimeregion.setRegion(self.project.pendata['time'][[min_ix, max_ix]])
                return
            start_ixs, stop_ixs, lengths=self.project.nonzero_region_ix
            prev_maxs = stop_ixs[stop_ixs<max_ix]
            if prev_maxs.shape[0]>0:
                if prev_maxs[-1] > min_ix:
                    prev_max_ix = prev_maxs[-1]
                    segmenttimeperiod = self.project.pendata['time'][[min_ix, prev_max_ix]]
                    min_ix, max_ix = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(*segmenttimeperiod)
                    self.project.selectedtimeregion.setRegion(self.project.pendata['time'][[min_ix, max_ix]])
                else:
                    infoDlg(title=u"Action Aborted", prompt=u"The end time of the selected time period can not be decreased further<br>without it being equal to the selected periods start time.")

    def increaseSelectionStartPointTime(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax = self.project.selectedtimeregion.getRegion()
        ix_bounds = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
        if len(ix_bounds)>0:
            min_ix, max_ix = ix_bounds
            if np.all(self.project.nonzero_pressure_mask[min_ix:max_ix]):
                self.project.selectedtimeregion.setRegion(self.project.pendata['time'][[min_ix, max_ix]])
                return
            start_ixs,stop_ixs,lengths=self.project.nonzero_region_ix
            higher_starts=start_ixs[start_ixs>(min_ix)]
            if len(higher_starts)==0:
                infoDlg(title=u"Action Aborted", prompt=u"The start time of the selected time period can not be increased<br> any further; it is the last IPS run of the file.")
            elif higher_starts[0]>=max_ix-1:
                infoDlg(title=u"Action Aborted", prompt=u"The start time of the selected time period can not be further increased<br> without it exceeding the selected periods end time.")
            else:
                segmenttimeperiod = self.project.pendata['time'][[higher_starts[0], max_ix]]
                self.project.selectedtimeregion.setRegion(segmenttimeperiod)

    def decreaseSelectionStartPointTime(self):
        # TODO: Move method to _penDataTimeLineWidget
        xmin, xmax = self.project.selectedtimeregion.getRegion()
        ix_bounds = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(xmin, xmax)
        if len(ix_bounds)>0:
            min_ix, max_ix = ix_bounds
            start_ixs, stop_ixs, lengths=self.project.nonzero_region_ix
            prev_starts = start_ixs[start_ixs<min_ix]
            if len(prev_starts)>0 and prev_starts[-1] >= 0:
                    prev_start_ix = prev_starts[-1]
                    segmenttimeperiod = self.project.pendata['time'][[prev_start_ix, max_ix]]
                    min_ix, max_ix = self.project.segmenttree.calculateTrimmedSegmentIndexBoundsFromTimeRange(*segmenttimeperiod)
                    self.project.selectedtimeregion.setRegion(self.project.pendata['time'][[min_ix, max_ix]])
                    nxmin,_=segmenttimeperiod
                    (vmin,vmax),(_,_)=self._penDataTimeLineWidget.getViewRange()
                    if nxmin < vmin:
                        self._penDataTimeLineWidget.translateViewBy(x=(nxmin-vmin)*1.25)

    def handleSelectedPenDataUpdate(self, timeperiod, pendata):
        #print '>> App.handleSelectedPenDataUpdate:',timeperiod
        self.createSegmentAction.setEnabled(
            self.project and self.project.isSelectedDataValidForNewSegment())
        #print '<< App.handleSelectedPenDataUpdate'

    def handleDisplayAppSettingsDialogEvent(self):
        updatedsettings, allsettings, savestate, ok = ProjectSettingsDialog.getProjectSettings(self)
        if ok is True:
            if len(updatedsettings)>0:
                writePickle(self._appdirs.user_config_dir,u'usersettings.pkl', SETTINGS)
                #print "MAINWIN.writePickle called:",SETTINGS
            if self.project:
                self.sigAppSettingsUpdated.emit(updatedsettings, allsettings)

    # >>>>>>
    # Generic Unit based selection region actions
    def advanceSelectionEndToNextUnitEnd(self, unit_lookup_table):
        selection_start, selection_end = self.project.selectedtimeregion.getRegion()
        new_selection_end = self.project.getNextUnitEndTime(unit_lookup_table,selection_end)
        if new_selection_end:
            self.project.selectedtimeregion.setRegion((selection_start,new_selection_end))

    def returnSelectionEndToPrevUnitEnd(self, unit_lookup_table):
        selection_start, selection_end = self.project.selectedtimeregion.getRegion()
        new_selection_end = self.project.getPrevUnitEndTime(unit_lookup_table,selection_end)
        if new_selection_end and new_selection_end > selection_start:
            self.project.selectedtimeregion.setRegion((selection_start,new_selection_end))

    def advanceSelectionStartToNextUnitStart(self, unit_lookup_table):
        selection_start, selection_end = self.project.selectedtimeregion.getRegion()
        new_selection_start = self.project.getNextUnitStartTime(unit_lookup_table, selection_start)
        if new_selection_start and new_selection_start < selection_end:
            self.project.selectedtimeregion.setRegion((new_selection_start, selection_end))

    def returnSelectionStartToPrevUnitStart(self, unit_lookup_table):
        selection_start, selection_end = self.project.selectedtimeregion.getRegion()
        new_selection_start = self.project.getPrevUnitStartTime(unit_lookup_table, selection_start)
        if new_selection_start:
            self.project.selectedtimeregion.setRegion((new_selection_start, selection_end))
    # <<<<<<

    # >>>>>>
    # SERIES based selection region actions
    def selectNextSampleSeries(self):
        seriestimerange = self.project.getNextUnitTimeRange(self.project.series_boundaries)
        if seriestimerange:
            self.project.selectedtimeregion.setRegion(seriestimerange)

    def selectPrevSampleSeries(self):
        seriestimerange = self.project.getPreviousUnitTimeRange(self.project.series_boundaries)
        if seriestimerange:
            self.project.selectedtimeregion.setRegion(seriestimerange)

    def advanceSelectionEndToNextSeriesEnd(self):
        self.advanceSelectionEndToNextUnitEnd(self.project.series_boundaries)

    def returnSelectionEndToPrevSeriesEnd(self):
        self.returnSelectionEndToPrevUnitEnd(self.project.series_boundaries)

    def advanceSelectionStartToNextSeriesStart(self):
        self.advanceSelectionStartToNextUnitStart(self.project.series_boundaries)

    def returnSelectionStartToPrevSeriesStart(self):
        self.returnSelectionStartToPrevUnitStart(self.project.series_boundaries)
    # <<<<<<

    # >>>>>>
    # RUN based selection region actions
    def selectNextPressedRun(self):
        runtimerange = self.project.getNextUnitTimeRange(self.project.press_period_boundaries)
        if runtimerange:
            self.project.selectedtimeregion.setRegion(runtimerange)

    def selectPrevPressedRun(self):
        runtimerange = self.project.getPreviousUnitTimeRange(self.project.press_period_boundaries)
        if runtimerange:
            self.project.selectedtimeregion.setRegion(runtimerange)

    def advanceSelectionEndToNextRunEnd(self):
        self.advanceSelectionEndToNextUnitEnd(self.project.press_period_boundaries)

    def returnSelectionEndToPrevRunEnd(self):
        self.returnSelectionEndToPrevUnitEnd(self.project.press_period_boundaries)

    def advanceSelectionStartToNextRunStart(self):
        self.advanceSelectionStartToNextUnitStart(self.project.press_period_boundaries)

    def returnSelectionStartToPrevRunStart(self):
        self.returnSelectionStartToPrevUnitStart(self.project.press_period_boundaries)
    # <<<<<<

    # >>>>>>
    # STROKE based selection region actions
    def selectNextStroke(self):
        stroketimerange = self.project.getNextUnitTimeRange(self.project.stroke_boundaries)
        if stroketimerange:
            self.project.selectedtimeregion.setRegion(stroketimerange)

    def selectPrevStroke(self):
        stroketimerange = self.project.getPreviousUnitTimeRange(self.project.stroke_boundaries)
        if stroketimerange:
            self.project.selectedtimeregion.setRegion(stroketimerange)

    def advanceSelectionEndToNextStrokeEnd(self):
        self.advanceSelectionEndToNextUnitEnd(self.project.stroke_boundaries)

    def returnSelectionEndToPrevStrokeEnd(self):
        self.returnSelectionEndToPrevUnitEnd(self.project.stroke_boundaries)

    def advanceSelectionStartToNextStrokeStart(self):
        self.advanceSelectionStartToNextUnitStart(self.project.stroke_boundaries)

    def returnSelectionStartToPrevStrokeStart(self):
        self.returnSelectionStartToPrevUnitStart(self.project.stroke_boundaries)
    # <<<<<<

    def closeEvent(self, event):
        if event == u'FORCE_EXIT':
            QtCore.QCoreApplication.instance().quit()
            return

        exitapp = ExitApplication.display()
        if exitapp:
            pass
            if event:
                event.accept()
            else:
                QtCore.QCoreApplication.instance().quit()
        else:
            if event:
                event.ignore()

    def __del__(self):
        pass

    def displayAllDataChannelsTimePlot(self):
            pw = pg.plot()
            pw.setWindowTitle('All Pen Samples')
            pw = pw.plotItem
            pw.setLabels(left='Pen Position')

            pw.addLegend()
            pdata=self.project.pendata


            def getPenBrushForAxis(axis, penpoints, penarray=None, brusharray=None):
                if penarray is None:
                    penarray = np.empty(penpoints.shape[0], dtype=object)
                    brusharray = np.empty(penpoints.shape[0], dtype=object)

                pen = pg.mkPen(SETTINGS['timeplot_%strace_color'%(axis)],
                               width=SETTINGS['timeplot_%strace_size'%(axis)])
                pen2 = pg.mkPen(SETTINGS['timeplot_%strace_color'%(axis)].darker(),
                                width=SETTINGS['timeplot_%strace_size'%(axis)])
                penarray[:] = pen
                penarray[penpoints['pressure'] == 0] = pen2

                brush = pg.mkBrush(SETTINGS['timeplot_%strace_color'%(axis)])
                brush2 = pg.mkBrush(SETTINGS['timeplot_%strace_color'%(axis)].darker())
                brusharray[:] = brush
                brusharray[penpoints['pressure'] == 0] = brush2

                return penarray, brusharray


#            left_axis = ('x','y')
#            penarray=None
#            brusharray=None
#            for axis  in left_axis:
#                penarray, brusharray = getPenBrushForAxis(axis,pdata,penarray,brusharray)
#                left_plot.plot(x=pdata['time'], y=pdata['%s_filtered'%(axis)],
#                                pen=None, symbol='o',
#                                symbolSize=SETTINGS[
#                                    'timeplot_%strace_size'%(axis)],
#                                symbolPen=penarray,
#                                symbolBrush=brusharray,
#                                name = "%s"%(axis))



            left_axis = ('v','a')
            axis2data=dict(v='xy_velocity',a='xy_acceleration')

            ssize= SETTINGS['pen_stroke_boundary_size']
            scolor = SETTINGS['pen_stroke_boundary_color']
            pen = pg.mkPen(scolor, width=ssize)
            brush = pg.mkBrush(scolor)
            strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
            pw.addItem(strokeBoundaryPoints)
            strokeboundries=self.project.velocity_minima_samples
            for axis in left_axis:
                strokeBoundaryPoints.addPoints(x=strokeboundries['time'],
                                               y=strokeboundries[axis2data[axis]])


            penarray=None
            brusharray=None
            for axis  in left_axis:
                penarray, brusharray = getPenBrushForAxis(axis,pdata,penarray, brusharray)
                pw.addItem(pg.PlotCurveItem(x=pdata['time'],
                                                    y=pdata[axis2data[axis]],
                                                    pen=None, symbol='o',
                                                    symbolSize=SETTINGS[
                                                        'timeplot_%strace_size'%(axis)],
                                                    symbolPen=penarray,
                                                    symbolBrush=brusharray,
                                                    name = "%s"%(axis)))

#
## Main App Helpers
#

class ContextualStateAction(QtGui.QAction):
    def __init__(self, *args, **kwargs):
        QtGui.QAction.__init__(self, *args, **kwargs)
        self.enableActionsList = []
        self.disableActionsList = []

    def enableAndDisableActions(self):
        for ea in self.enableActionsList:
            ea.setEnabled(True)
        for da in self.disableActionsList:
            da.setDisabled(True)

    def setEnabled(self, b):
        QtGui.QAction.setEnabled(self, b)
        self.enableAndDisableActions()
#
## GraphicsWidgets
#


