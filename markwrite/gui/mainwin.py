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

from markwrite.gui import ProjectSettingsDialog

from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

from markwrite.util import getIconFilePath
from markwrite.file_io import loadPredefinedSegmentTagList, readPickle, writePickle
from markwrite.reports import PenSampleReportExporter, SegmentLevelReportExporter
from markwrite.segment import PenDataSegment
from dialogs import ExitApplication, fileOpenDlg, ErrorDialog, warnDlg, \
    fileSaveDlg,ConfirmAction
from markwrite.project import MarkWriteProject

DEFAULT_WIN_SIZE = (1200, 800)

DEFAULT_DOCK_PLACEMENT = {
    u"Segment Tree": ('left', (.2, 1.0)),
    u"Timeline": (['right', u"Segment Tree"], (.8, .35)),
    u"Spatial View": (['bottom', u"Timeline"], (.60, .65)),
    u"Selected Data": (['right', u"Spatial View"], (.2, .65)),
}

ABOUT_DIALOG_TEXT = """
<b> MarkWrite</b> <br>
Copywrite 2015 COPYRIGHT_HOLDER_NAME<br>
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

        # create a temp ProjectSettingsDialog so that settings are loaded
        # even if ProjectSettingsDialog is not displayed


        self.sigProjectChanged.connect(self.handleProjectChange)
        self.sigSelectedPenDataUpdate.connect(self.handleSelectedPenDataUpdate)
        self.sigAppSettingsUpdated.connect(self._penDataTimeLineWidget.handleUpdatedSettingsEvent)
        self.sigAppSettingsUpdated.connect(self._penDataSpatialViewWidget.handleUpdatedSettingsEvent)

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
            self.removeSegmentAction.setEnabled(True)
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
        atext = 'Open an Existing MarkWrite Project or Digitized Pen Position ' \
                'File'
        aicon = 'folder&32.png'
        self.openFileAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Open',
            self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setEnabled(True)
        self.openFileAction.setStatusTip(atext)
        self.openFileAction.triggered.connect(self.openFile)

        #atext = 'Save Current Project.'
        #aicon = 'save&32.png'
        #self.saveProjectAction = ContextualStateAction(
        #    QtGui.QIcon(getIconFilePath(aicon)),
        #    'Save',
        #    self)
        #self.saveProjectAction.setShortcut('Ctrl+S')
        #self.saveProjectAction.setEnabled(False)
        #self.saveProjectAction.setStatusTip(atext)
        #self.saveProjectAction.triggered.connect(self.saveProject)

        atext = 'Export Pen Sample Report File.'
        aicon = 'sample_report&32.png'
        self.exportSampleReportAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Export Pen Sample Report',
            self)
        #self.exportSampleReportAction.setShortcut('Ctrl+S')
        self.exportSampleReportAction.setEnabled(False)
        self.exportSampleReportAction.setStatusTip(atext)
        self.exportSampleReportAction.triggered.connect(
            self.createPenSampleLevelReportFile)

        atext = 'Export Segment Level Report File.'
        aicon = 'segment_report&32.png'
        self.exportSegmentReportAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Export Segment Level Report',
            self)
        #self.exportSampleReportAction.setShortcut('Ctrl+S')
        self.exportSegmentReportAction.setEnabled(False)
        self.exportSegmentReportAction.setStatusTip(atext)
        self.exportSegmentReportAction.triggered.connect(
            self.createSegmentLevelReportFile)

        self.exportSampleReportAction.enableActionsList.append(self.exportSegmentReportAction)

        atext = 'Open Application & Project Settings Dialog.'
        aicon = 'settings&32.png'
        self.showProjectSettingsDialogAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Settings',
            self)
        self.showProjectSettingsDialogAction.setShortcut('Ctrl+ALT+S')
        self.showProjectSettingsDialogAction.setEnabled(True)
        self.showProjectSettingsDialogAction.setStatusTip(atext)
        self.showProjectSettingsDialogAction.triggered.connect(
            self.handleDisplayAppSettingsDialogEvent)

        atext = 'Exit Application'
        aicon = 'shut_down&32.png'
        self.exitAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Exit',
            self)
        self.exitAction.setEnabled(True)
        self.exitAction.setStatusTip(atext)
        self.exitAction.triggered.connect(self.closeEvent)

        #
        # Segment Menu / Toolbar Related Actions
        #

        atext = 'Create a Segment Using Currently Selected Pen Data.'
        aicon = 'accept&32.png'
        self.createSegmentAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Create',
            self)
        self.createSegmentAction.setEnabled(False)
        self.createSegmentAction.setStatusTip(atext)
        self.createSegmentAction.triggered.connect(self.createSegment)

        atext = 'Remove the Active Segment.'
        aicon = 'delete&32.png'
        self.removeSegmentAction = ContextualStateAction(
            QtGui.QIcon(getIconFilePath(aicon)),
            'Remove',
            self)
        self.removeSegmentAction.setEnabled(False)
        self.removeSegmentAction.setStatusTip(atext)
        self.removeSegmentAction.triggered.connect(self.removeSegment)

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
        #fileMenu.addAction(self.saveProjectAction)
        fileMenu.addAction(self.showProjectSettingsDialogAction)
        fileMenu.addSeparator()
        exportMenu = fileMenu.addMenu("&Export")
        exportMenu.addAction(self.exportSampleReportAction)
        exportMenu.addAction(self.exportSegmentReportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        segmentMenu = menubar.addMenu('&Segment')
        segmentMenu.addAction(self.createSegmentAction)
        segmentMenu.addAction(self.removeSegmentAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(self.aboutAction)

        self.toolbarFile = self.addToolBar('File')
        self.toolbarFile.addAction(self.openFileAction)
        #self.toolbarFile.addAction(self.saveProjectAction)
        self.toolbarFile.addAction(self.showProjectSettingsDialogAction)

        self.toolbarExport = self.addToolBar('Export')
        self.toolbarExport.addAction(self.exportSampleReportAction)
        self.toolbarExport.addAction(self.exportSegmentReportAction)


        self.toolbarsegment = self.addToolBar('Segment')
        self.toolbarsegment.addAction(self.createSegmentAction)
        self.toolbarsegment.addAction(self.removeSegmentAction)

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
        addDock(u"Selected Data", SelectedPointsPlotWidget())

        #
        ## Do Misc. GUI setup.
        #

        self.setWindowIcon(QtGui.QIcon(getIconFilePath('edit&32.png')))

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
                    wmproj = MarkWriteProject(file_path=file_path,mwapp=self)
                    self.createSegmentAction.setEnabled(True)
                    self.sigProjectChanged.emit(wmproj)
                    self.sigResetProjectData.emit(wmproj)
                except:
                    import traceback

                    traceback.print_exc()
                    ErrorDialog.info_text = u"An error occurred while " \
                                            u"opening:\n%s\nMarkWrite will " \
                                            u"now close." % (
                    file_path)
                    ErrorDialog().display()
                    self.closeEvent(u'FORCE_EXIT')

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

    def createSegment(self):
        """
        Displays the Create Segment dialog. If dialog is not cancelled and
        segment name length >0, then create a new segment and add to the
        projects segment list.

        TODO: 1.'Autotrim' segment time period and update View Widgets when
                the Create Segment dialog is first displayed. If no segment is
                actually created, reset selection region to previous state.
              2. If the selected / active node in the project tree gui widget
                is a Segment, then add the newly create segment as a child of
                currently selected segment, otherwise use current logic.
        :return:
        """
        if self.createSegmentAction.isEnabled():
            # Shrink timeline selection region to fit start and end time
            # of possible segment being created.
            selectedtimeperiod = self.project.selectedtimeperiod[:]


            pendata_ix_range = self.project.segmentset.calculateTrimmedSegmentIndexBoundsFromTimeRange(*selectedtimeperiod)
            segmenttimeperiod = self.project.pendata['time'][pendata_ix_range]
            self.project.selectedtimeregion.setRegion(segmenttimeperiod)

            tag, ok = showSegmentNameDialog(self.predefinedtags)
            tag = unicode(tag).strip().replace('\t', "#")
            if len(tag) > 0 and ok:
                psid = self.project.getSelectedDataSegmentIDs()[0]
                new_segment = self.project.createPenDataSegment(tag, psid)
                self.handleSelectedPenDataUpdate(None,None)
                self.sigSegmentCreated.emit(new_segment)
                self.setActiveObject(new_segment)
            else:
                # If segment creation was cancelled or failed, then reset
                # timeline selection region to original time period.
                self.project.selectedtimeregion.setRegion(selectedtimeperiod)
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

            segment.parent.removeChild(segment)
        else:
            print "   - Remove action IGNORED"
        print "<< removeSegment"

    def handleProjectChange(self, project):
        if self._current_project:
            pass
        self._current_project = project
        self.setActiveObject(self.project.selectedtimeregion)
        self.updateAppTitle()
        #self.saveProjectAction.setEnabled(project.modified)
        self.exportSampleReportAction.setEnabled(True)

    def handleSelectedPenDataUpdate(self, timeperiod, pendata):
        #print '>> App.handleSelectedPenDataUpdate:',timeperiod
        self.createSegmentAction.setEnabled(
            self.project and self.project.isSelectedDataValidForNewSegment())
        #print '<< App.handleSelectedPenDataUpdate'

    def handleDisplayAppSettingsDialogEvent(self):
        usersettings = readPickle(self._appdirs.user_config_dir,u'usersettings.pkl')

        updatedsettings, allsettings, savestate, ok = ProjectSettingsDialog.getProjectSettings(self, usersettings)
        if ok is True and len(updatedsettings)>0:
            writePickle(self._appdirs.user_config_dir,u'usersettings.pkl', savestate)
            if self.project:
                self.sigAppSettingsUpdated.emit(updatedsettings, allsettings)

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


