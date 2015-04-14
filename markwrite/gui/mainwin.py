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


from weakref import proxy,WeakValueDictionary
import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea,Dock
from pyqtgraph import TableWidget

from markwrite.util import getIconFilePath
from markwrite.file_io import loadPredefinedSegmentTagList,PenSampleReportExporter
from markwrite.segment import PenDataSegment
from markwrite.gui.segmenttree import SegmentTreeWidget
from dialogs import ExitApplication, fileOpenDlg, ErrorDialog, warnDlg, fileSaveDlg
from markwrite.project import MarkWriteProject
from markwrite.gui import ProjectSettingsDialog
DEFAULT_WIN_SIZE = (1200,800)

DEFAULT_DOCK_PLACEMENT={
            u"Markup Tree":('left',(.2,1.0)),
            u"Timeline":(['right',u"Markup Tree"],(.8,.35)),
            u"Spatial View":(['bottom',u"Timeline"],(.60,.65)),
            u"Selected Data":(['right',u"Spatial View"],(.2,.65)),
            }

ABOUT_DIALOG_TEXT = """
<b> MarkWrite</b> <br>
Copywrite 2015 COPYRIGHT_HOLDER_NAME<br>
This software is GLP v3 licensed.<br>
<br>
See licence.txt for license details.
"""

ABOUT_DIALOG_TITLE="About MarkWrite"


def showNotImplementedDialog(widget,title=None,msg=None,func_name=None):
    if func_name:
        if title is None:
            title = "Function '{0}' Not Implemented"
            title = title.format(func_name)
        if msg is None:
            msg = "The Function '{0}' Has Not Yet Been Implemented."
            msg = msg.format(func_name)
    else:
        if title is None:
            title="Action Not Implemented"
        if msg is None:
            msg = "The Selected Action Has Not Yet Been Implemented."
    QtGui.QMessageBox.information(widget,title,msg)

def not_implemented(wrapped_func):
    def func_wrapper(*args, **kwargs):
        showNotImplementedDialog(args[0],func_name=wrapped_func.__name__)
    return func_wrapper


def showSegmentNameDialog(tags, default = u""):
    return QtGui.QInputDialog.getItem(WRITEMARK_APP_INSTANCE,
        u"Segment Name (Tag)",
        u"Enter the desired pen segment tag, or selected one from the predefined tag list.",
        [default]+tags,
        current = 0,
        editable = True,
        )


class MarkWriteMainWindow(QtGui.QMainWindow):
    sigProjectChanged = QtCore.Signal(object)  # new_project
    sigResetProjectData = QtCore.Signal(object)  # project
    sigSelectedPenDataUpdate = QtCore.Signal(object, object)  # (smin,smax), segmentdata
    sigSegmentCreated = QtCore.Signal(object)  # new segment
    sigSegmentRemoved = QtCore.Signal(object, object)  # segment being removed, segment index in list
    def __init__(self, qtapp):
        global WRITEMARK_APP_INSTANCE

        QtGui.QMainWindow.__init__(self)
        WRITEMARK_APP_INSTANCE=self

        self._current_project = None
        self._activesegment=None

        self._predefinedtags=loadPredefinedSegmentTagList(u'default.tag')

        # create qt actions used by menu, toolbar, or both
        self.createGuiActions()

        # init GUI related stuff
        self.setupGUI(qtapp)

        self.sigProjectChanged.connect(self.handleProjectChange)
        self.sigSelectedPenDataUpdate.connect(self.handleSelectedPenDataUpdate)

    @property
    def project(self):
        return self._current_project

    @property
    def activesegment(self):
        return self._activesegment

    @activesegment.setter
    def activesegment(self, s):
        self._activesegment = s
        self.removeSegmentAction.setEnabled(s is not None and s.parent is not None)

    @property
    def predefinedtags(self):
        if self.project:
            return self.project.autodetected_segment_tags+self._predefinedtags
        return self._predefinedtags

    def createGuiActions(self):
        #
        # File Menu / Toolbar Related Actions
        #
        atext='Open an Existing MarkWrite Project or Digitized Pen Position File'
        aicon='folder&32.png'
        self.openFileAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'Open',
                                    self)
        self.openFileAction.setShortcut('Ctrl+O')
        self.openFileAction.setEnabled(True)
        self.openFileAction.setStatusTip(atext)
        self.openFileAction.triggered.connect(self.openFile)

        atext='Save Current Project.'
        aicon='save&32.png'
        self.saveProjectAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'Save',
                                    self)
        self.saveProjectAction.setShortcut('Ctrl+S')
        self.saveProjectAction.setEnabled(False)
        self.saveProjectAction.setStatusTip(atext)
        self.saveProjectAction.triggered.connect(self.saveProject)

        atext='Export Pen Sample Report File.'
        aicon='page&32.png'
        self.exportSampleReportAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'Export Pen Sample Report',
                                    self)
        #self.exportSampleReportAction.setShortcut('Ctrl+S')
        self.exportSampleReportAction.setEnabled(False)
        self.exportSampleReportAction.setStatusTip(atext)
        self.exportSampleReportAction.triggered.connect(self.createPenSampleLevelReportFile)


        atext='Open Application & Project Settings Dialog.'
        aicon='settings&32.png'
        self.showProjectSettingsDialogAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'Settings',
                                    self)
        self.showProjectSettingsDialogAction.setShortcut('Ctrl+ALT+S')
        self.showProjectSettingsDialogAction.setEnabled(True)
        self.showProjectSettingsDialogAction.setStatusTip(atext)
        self.showProjectSettingsDialogAction.triggered.connect(self.handleDisplayAppSettingsDialogEvent)



        atext='Exit Application'
        aicon='shut_down&32.png'
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

        atext='Create a Segment Using Currently Selected Pen Data.'
        aicon='accept&32.png'
        self.createSegmentAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'Create',
                                    self)
        self.createSegmentAction.setEnabled(False)
        self.createSegmentAction.setStatusTip(atext)
        self.createSegmentAction.triggered.connect(self.createSegment)

        atext='Remove the Active Segment.'
        aicon='delete&32.png'
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

        atext='Displays the MarkWrite About Dialog.'
        aicon='info&32.png'
        self.aboutAction = ContextualStateAction(
                                    QtGui.QIcon(getIconFilePath(aicon)),
                                    'About',
                                    self)
        self.aboutAction.setEnabled(True)
        self.aboutAction.setStatusTip(atext)
        self.aboutAction.triggered.connect(self.showAboutDialog)

    def setupGUI(self,app):
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

        self.toolbarExport = self.addToolBar('Export')
        self.toolbarExport.addAction(self.exportSampleReportAction)

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
            if isinstance(dpos,basestring):
                self._dockarea.addDock(Dock(name, size=[ww*dw,wh*dh]), dpos)
            else:
                self._dockarea.addDock(Dock(name, size=[ww*dw,wh*dh]), dpos[0], self._dockarea.docks[dpos[1]])

            if inner_widget:
                self._dockarea.docks[name].addWidget(inner_widget)

        addDock(u"Markup Tree", ProjectInfoDockArea())
        self._penDataTimeLineWidget=PenDataTemporalPlotWidget()
        self._penDataSpatialViewWidget=PenDataSpatialPlotWidget()
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
            fileName=self._current_project.name

            if self._current_project.modified:
                fileName = u'[{0}] : '.format(fileName)
            else:
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
            file_path=file_path[0]
            if len(file_path) > 0:
                try:
                    wmproj = MarkWriteProject(file_path=file_path)
                    self.createSegmentAction.setEnabled(True)
                    self.sigProjectChanged.emit(wmproj)
                    self.sigResetProjectData.emit(wmproj)
                except:
                    import traceback
                    traceback.print_exc()
                    ErrorDialog.info_text=u"An error occurred while opening:\n%s\nMarkWrite will now close."%(file_path)
                    ErrorDialog().display()
                    self.closeEvent(u'FORCE_EXIT')

    def saveProject(self,confirm_save=False):
        if self._current_project:
            self._current_project.save()
        self.updateAppTitle()
        self.saveProjectAction.setEnabled(self._current_project and self._current_project.modified)
        warnDlg(prompt=u"Project Saving is not Implemented Yet. Sorry.")

    def createPenSampleLevelReportFile(self):
        default_file_name = u"pen_samples_{0}.txt".format(self.project.name)
        file_path = fileSaveDlg(initFileName=default_file_name,prompt="Export Pen Sample Report")
        if file_path:
            PenSampleReportExporter().export(file_path,  self.project)

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
            selectedtimeperiod = self._penDataTimeLineWidget.currentSelection.getRegion()
            self._penDataTimeLineWidget.currentSelection.setRegion(self.project.selecteddatatimerange)
            tag, ok = showSegmentNameDialog(self.predefinedtags)
            tag = unicode(tag).strip().replace('\t',"#")
            if len(tag)>0 and ok:
                psid = self.project.getSelectedDataSegmentIDs()[0]
                new_segment = self.project.createPenDataSegment(tag,psid)
                self.sigSegmentCreated.emit(new_segment)
            else:
                # If segment creation was cancelled or failed, then reset
                # timeline selection region to original time period.
                self._penDataTimeLineWidget.currentSelection.setRegion(selectedtimeperiod)
        else:
            ErrorDialog.info_text=u"Segment Creation Failed.\nNo selected pen data."
            ErrorDialog().display()

    def removeSegment(self):

        segment = self.activesegment
        if segment and segment.parent is not None:
            seg_ix = segment.parent.getChildIndex(segment)

            # Decrement the pendata array 'segment_id' field for elements within
            # the segment being removed so that # of segments that contain each
            # pen point can be tracked
            allpendata = self.project.pendata
            segment_filter = (allpendata['time']>=segment.starttime) & (allpendata['time']<=segment.endtime)
            allpendata['segment_id'][segment_filter]=segment.parent.id
            self.sigSegmentRemoved.emit(segment, seg_ix)
            segment.parent.removeChild(segment)


    def handleProjectChange(self, project):
        if self._current_project:
            print "TODO: If current project has been modified, ask if it should be saved."
        self._current_project = project
        self.updateAppTitle()
        self.saveProjectAction.setEnabled(project.modified)
        self.exportSampleReportAction.setEnabled(True)

    def handleSelectedPenDataUpdate(self, timeperiod, pendata):
        #print '>> App.handleSelectedPenDataUpdate:',timeperiod
        self.createSegmentAction.setEnabled(self.project and self.project.isSelectedDataValidForNewSegment())
        #print '<< App.handleSelectedPenDataUpdate'

    def handleDisplayAppSettingsDialogEvent(self):
        projsettings, ok = ProjectSettingsDialog.getProjectSettings(self)
        print("{} {}".format(projsettings, ok))

    def closeEvent(self, event):
        if event == u'FORCE_EXIT':
            QtCore.QCoreApplication.instance().quit()
            return

        exitapp = ExitApplication.display()
        if exitapp:
            if self._current_project and self._current_project.modified:
                print "TODO: Since open project has been modified, ask if it should be saved before exiting app."
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
    def __init__(self,*args,**kwargs):
        QtGui.QAction.__init__(self,*args,**kwargs)
        self.enableActionsList=[]
        self.disableActionsList=[]

    def enableAndDisableActions(self):
        for ea in self.enableActionsList:
            ea.setEnabled(True)
        for da in self.disableActionsList:
            da.setDisabled(True)


#
## GraphicsWidgets
#

class PenDataTemporalPlotWidget(pg.PlotWidget):
    def __init__(self):
        global WRITEMARK_APP_INSTANCE
        pg.PlotWidget.__init__(self, enableMenu=False)
        # Create Pen Position Time Series Plot for All Data

        self.getPlotItem().setLabel('left', "Pen Position", units='pix')
        self.getPlotItem().setLabel('bottom', "Time", units='sec')
        self.xPenPosTrace = None
        self.yPenPosTrace = None
        self.currentSelection = None
        self._lastselectedtimerange=None
        self.sigRegionChangedProxy=None
        WRITEMARK_APP_INSTANCE.sigResetProjectData.connect(self.handleResetPenData)

    def handleResetPenData(self, project):
        '''

        :param self:
        :param project:
        :return:
        '''
        numpy_data = project.pendata
        penValRange = (min(numpy_data['x'].min(), numpy_data['y'].min()), max(numpy_data['x'].max(), numpy_data['y'].max()))
        self.getPlotItem().setLimits(yMin=penValRange[0], yMax=penValRange[1], xMin=numpy_data['time'][0], xMax=numpy_data['time'][-1])
        if self.xPenPosTrace is None:
            # Create DataItem objects
            pen = pg.mkPen((0,255,0), width=2)
            pen2 = pg.mkPen((0,255,255), width=2)
            penarray=np.empty(numpy_data.shape[0],dtype=object)
            penarray[:]=pen
            penarray[numpy_data['pressure']==0]=pen2

            brush=pg.mkBrush((0,255,0))
            brush2=pg.mkBrush((0,255,255))
            brusharray=np.empty(numpy_data.shape[0],dtype=object)
            brusharray[:]=brush
            brusharray[numpy_data['pressure']==0]=brush2

            self.xPenPosTrace = self.getPlotItem().plot(x=numpy_data['time'], y=numpy_data['x'],  pen=None, symbol='o', symbolSize=1, symbolPen=penarray, symbolBrush=brusharray, name="X Position") # pen=None, symbol='o', symbolSize=1, symbolPen='r', symbolBrush='r',


            pen = pg.mkPen((255,255,0), width=2)
            pen2 = pg.mkPen((255,128,0), width=2)
            penarray[:]=pen
            penarray[numpy_data['pressure']==0]=pen2

            brush=pg.mkBrush((255,255,0))
            brush2=pg.mkBrush((255,128,0))
            brusharray[:]=brush
            brusharray[numpy_data['pressure']==0]=brush2

            self.yPenPosTrace = self.getPlotItem().plot(x=numpy_data['time'], y=numpy_data['y'],  pen=None, symbol='o', symbolSize=1, symbolPen=penarray, symbolBrush=brusharray, name="Y Position") #symbol='o', symbolSize=1, symbolPen='g', symbolBrush='g', name="Y Position")

            # Add a Selection Region that is used to create segments by user
            self.currentSelection = pg.LinearRegionItem(values=[numpy_data['time'][0],numpy_data['time'][0]+1.0],movable=True)
            self.currentSelection.setBounds(bounds=(numpy_data['time'][0], numpy_data['time'][-1]))
            self.addItem(self.currentSelection)
            self.sigRegionChangedProxy=pg.SignalProxy(self.currentSelection.sigRegionChanged, rateLimit=30, slot=self.handlePenDataSelectionChanged)

        else:
            # Update DataItem objects
            pen = pg.mkPen((0,255,0), width=2)
            pen2 = pg.mkPen((0,255,255), width=2)
            brush=pg.mkBrush((0,255,0))
            brush2=pg.mkBrush((0,255,255))

            penarray=np.empty(numpy_data.shape[0],dtype=object)
            penarray[:]=pen
            penarray[numpy_data['pressure']==0]=pen2

            brusharray=np.empty(numpy_data.shape[0],dtype=object)
            brusharray[:]=brush
            brusharray[numpy_data['pressure']==0]=brush2

            self.xPenPosTrace.setData(x=numpy_data['time'], y=numpy_data['x'],symbolPen=penarray, symbolBrush=brusharray)


            pen = pg.mkPen((255,255,0), width=2)
            pen2 = pg.mkPen((255,128,0), width=2)
            brush=pg.mkBrush((255,255,0))
            brush2=pg.mkBrush((255,128,0))
            penarray[:]=pen
            penarray[numpy_data['pressure']==0]=pen2
            brusharray[:]=brush
            brusharray[numpy_data['pressure']==0]=brush2

            self.yPenPosTrace.setData(x=numpy_data['time'], y=numpy_data['y'],symbolPen=penarray, symbolBrush=brusharray)
            self.currentSelection.setRegion([numpy_data['time'][0],numpy_data['time'][0]+1.0])
            self.currentSelection.setBounds(bounds=(numpy_data['time'][0], numpy_data['time'][-1]))

        self.setRange(xRange=(numpy_data['time'][0],numpy_data['time'][-1]), padding=None)
        self.handlePenDataSelectionChanged()

    def handlePenDataSelectionChanged(self):
        self.currentSelection.setZValue(10)
        minT, maxT=self.currentSelection.getRegion()
        #print '>> Timeline.handlePenDataSelectionChanged:',( minT, maxT)
        selectedpendata = WRITEMARK_APP_INSTANCE.project.updateSelectedData(minT, maxT)
        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.emit((minT, maxT),selectedpendata)
        self.ensureSelectionIsVisible([minT, maxT], selectedpendata)
        #print '<< Timeline.handlePenDataSelectionChanged'

    def zoomToPenData(self, pendata, lock_bounds=False):
        if len(pendata)>0:
            penValRange = (min(pendata['x'].min()-20, pendata['y'].min()-20,0), max(pendata['x'].max()+20, pendata['y'].max()+20))
            #if lock_bounds:
            #    self.setLimits(xMin=pendata['time'][0], xMax=pendata['time'][-1]+0.01)
            self.setRange(xRange=(pendata['time'][0],pendata['time'][-1]), yRange=penValRange, padding=None)

    def ensureSelectionIsVisible(self, timespan, pendata):
        if len(pendata)>0:
            dxmin, dxmax =timespan
            dxlength = dxmax-dxmin
            (vxmin,vxmax),(vymin,vymax) = self.viewRange()
            vxlength = vxmax-vxmin
            vxborder=(vxlength-dxlength)/2.0
            dymin,dymax = (min(pendata['x'].min()-20, pendata['y'].min()-20,vymin), max(pendata['x'].max()+20, pendata['y'].max()+20, vymax))

            if dxlength > vxlength:
                ##print "dlength > vlength:",dlength, vlength
                self.setRange(xRange=(dxmin,dxmax), yRange=(dymin,dymax), padding=None)
                return

            if dxmin < vxmin:
                self.setRange(xRange=(dxmin,dxmin+vxlength),yRange=(dymin,dymax), padding=0)
                ##print 'dmin < vmin:',dmin,dmin+vlength,self.viewRange()[0]
                return

            if dxmax > vxmax:
                self.setRange(xRange=(dxmax-vxlength,dxmax),yRange=(dymin,dymax), padding=0)
                ##print 'dmax > vmax:',dmax-vlength,dmax,self.viewRange()[0]
                return




class PenDataSpatialPlotWidget(pg.PlotWidget):
    def __init__(self):
        global WRITEMARK_APP_INSTANCE
        pg.PlotWidget.__init__(self, enableMenu=False)

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)

        self.allPlotDataItem=None#self.getPlotItem().plot(pen=None, symbol='o', symbolSize=1, symbolBrush=(255,255,255), symbolPen=(255,255,255))
        self.selectedPlotDataItem=None#self.getPlotItem().plot(pen=None, symbol='o', symbolSize=3, symbolBrush=(0,0,255), symbolPen=(0,0,255))

        WRITEMARK_APP_INSTANCE.sigResetProjectData.connect(self.handleResetPenData)
        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.connect(self.handlePenDataSelectionChanged)

    def handleResetPenData(self, project):
        #print ">> PenDataSpatialPlotWidget.handleResetPenData:",project
        pdat = project.pendata

        if self.allPlotDataItem is None:
            pen = pg.mkPen((255,255,255), width=1)
            pen2 = pg.mkPen((255,0,255), width=1)
            brush=pg.mkBrush((255,255,255))
            brush2=pg.mkBrush((255,0,255))

            penarray=np.empty(pdat.shape[0],dtype=object)
            penarray[:]=pen
            penarray[pdat['pressure']==0]=pen2

            brusharray=np.empty(pdat.shape[0],dtype=object)
            brusharray[:]=brush
            brusharray[pdat['pressure']==0]=brush2

            self.allPlotDataItem=self.getPlotItem().plot(pen=None, symbol='o', symbolSize=1, symbolBrush=brusharray, symbolPen=penarray)
            self.selectedPlotDataItem=self.getPlotItem().plot(pen=None, symbol='o', symbolSize=3, symbolBrush=(0,0,255), symbolPen=(0,0,255))

        else:

            pen = pg.mkPen((255,255,255), width=1)
            pen2 = pg.mkPen((255,0,255), width=1)
            brush=pg.mkBrush((255,255,255))
            brush2=pg.mkBrush((255,0,255))

            penarray=np.empty(pdat.shape[0],dtype=object)
            penarray[:]=pen
            penarray[pdat['pressure']==0]=pen2

            brusharray=np.empty(pdat.shape[0],dtype=object)
            brusharray[:]=brush
            brusharray[pdat['pressure']==0]=brush2

            self.allPlotDataItem.setData(x=pdat['x'],y=pdat['y'],symbolBrush=brusharray, symbolPen=penarray)
            self.getPlotItem().setLimits(xMin=pdat['x'].min(), yMin=pdat['y'].min(),xMax=pdat['x'].max(), yMax=pdat['y'].max())
            self.setRange(xRange=(pdat['x'].min(), pdat['x'].max()), yRange=(pdat['y'].min(), pdat['y'].max()), padding=None)
            #print "<< PenDataSpatialPlotWidget.handleResetPenData"

    def handlePenDataSelectionChanged(self,timeperiod, selectedpendata):

        if self.allPlotDataItem is None:
            self.handleResetPenData(WRITEMARK_APP_INSTANCE.project)

        if WRITEMARK_APP_INSTANCE.createSegmentAction.isEnabled():
            self.selectedPlotDataItem.setData(x=selectedpendata['x'],y=selectedpendata['y'],symbolBrush=(0,0,255), symbolPen=(0,0,255))
        else:
            self.selectedPlotDataItem.setData(x=selectedpendata['x'],y=selectedpendata['y'],symbolBrush=(255,0,0), symbolPen=(255,0,0))

        self.ensureSelectionIsVisible(timeperiod, selectedpendata)
        #print "<< PenDataSpatialPlotWidget.handlePenDataSelectionChanged"

    def zoomToPenData(self, pendata, lock_bounds=False):
        xpadding = self.getPlotItem().getViewBox().suggestPadding(0)
        ypadding = self.getPlotItem().getViewBox().suggestPadding(1)
        if lock_bounds:
            self.setLimits(yMin=max(0.0,pendata['y'].min()-ypadding), yMax=pendata['y'].max()+ypadding, xMin=max(0.0,pendata['x'].min()-xpadding), xMax=pendata['x'].max()+xpadding)
        self.setRange(xRange=(pendata['x'].min(), pendata['x'].max()), yRange=(pendata['y'].min(), pendata['y'].max()), padding=None)

    def ensureSelectionIsVisible(self, timespan, selectedpendata):
        if len(selectedpendata)>0:
            (vxmin,vxmax),(vymin,vymax) = self.viewRange()
            dxmin,dxmax,dymin,dymax = selectedpendata['x'].min(), selectedpendata['x'].max(), selectedpendata['y'].min(), selectedpendata['y'].max()

            vxlength = vxmax-vxmin
            vylength = vymax-vymin
            dxlength = dxmax-dxmin
            dylength = dymax-dymin

            if dxlength > vxlength or dylength > vylength:
                #print "dlength > vlength:",dlength, vlength
                self.setRange(xRange=(dxmin,dxmax), yRange=(dymin,dymax), padding=None)
                return

            xrange = None
            yrange = None

            if dxmin < vxmin:
                xrange=(dxmin,dxmin+vxlength)
            if dxmax > vxmax:
                xrange=(dxmax-vxlength,dxmax)

            if dymin < vymin:
                yrange=(dymin,dymin+vylength)
            if dymax > vymax:
                yrange=(dymax-vylength,dymax)

            if xrange:
                dxlength =  xrange[1]-xrange[0]
            if yrange:
                dylength =  yrange[1]-yrange[0]

            if dxlength > vxlength:
                xrange=(dxmin,dxmax)
            if dylength > vylength:
                yrange=(dymin,dymax)

            if xrange or yrange:
                self.setRange(xRange=xrange, yRange=yrange, padding=0)


class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False, )

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)
        #self.getPlotItem().hideButtons()
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')
        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o', symbolSize=1, symbolBrush=(255,255,255), symbolPen=(255,255,255))

        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.connect(self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self.plotDataItem.setData(x=pendata['x'],y=pendata['y'],)
        self.getPlotItem().enableAutoRange(x=True, y=True)

class ProjectInfoDockArea(DockArea):
    segid2treenode=WeakValueDictionary()
    def __init__(self):
        DockArea.__init__(self)

        self.project_tree_dock = Dock(u"Project Tree", hideTitle=True)
        self.addDock(self.project_tree_dock, 'top')#'above', self.flowcharts_dock)

        self.project_tree = SegmentTreeWidget()

        self.project_tree_dock.addWidget(self.project_tree)

        self.properties_table = TableWidget(sortable=False, editable=False)
        self.properties_table.setColumnCount(1)
        self.properties_table.contextMenu.clear()
        self.properties_table.horizontalHeader().hide()

        self.properties_dock = Dock("Selected Object Properties", widget=self.properties_table, hideTitle=True)
        self.addDock(self.properties_dock, 'bottom')

        self.current_pydat_obj=None

        WRITEMARK_APP_INSTANCE.sigProjectChanged.connect(self.handleProjectChange)
        WRITEMARK_APP_INSTANCE.sigSegmentCreated.connect(self.handleSegmentCreated)
        WRITEMARK_APP_INSTANCE.sigSegmentRemoved.connect(self.handleSegmentRemoved)

        self.project_tree.currentItemChanged.connect(self.currentTreeItemChangedEvent)
        self.project_tree.itemDoubleClicked.connect(self.treeItemDoubleClickedEvent)
        self.project_tree.customContextMenuRequested.connect(self.rightClickTreeEvent)

    def updatePropertiesTableData(self,props):
        self.properties_table.clear()
        self.properties_table.setData(props)
        self.properties_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    #
    # Signal Handlers
    #

    def handleProjectChange(self, project):
        self.project_tree.clear()
        self.segid2treenode.clear()
        # Create Project Tree Node
        projecttreeitem=QtGui.QTreeWidgetItem([project.name])
        projecttreeitem._pydat=proxy(project.segmentset)
        self.segid2treenode[project.segmentset.id]=projecttreeitem
        self.project_tree.addTopLevelItem(projecttreeitem)
        projecttreeitem.setSelected(True)
        self.project_tree.setCurrentItem(projecttreeitem)
        self.current_pydat_obj=project.segmentset
        #TODO: UPDATE TO SUPPORT PROJECT REOPENNING WITH SEG. HEIRARCHY.
        # Current code assumes list on segments only
        for pds in project.segmentset.children:
            segtreeitem=QtGui.QTreeWidgetItem([pds.name])
            segtreeitem._pydat=proxy(pds)
            projecttreeitem.addChild(segtreeitem)

        self.updatePropertiesTableData(project.propertiesTableData())

    def handleSegmentCreated(self, segment):
        #print '>>TREE.handleSegmentCreated:',segment
        segindex = segment.parent.getChildIndex(segment)
        parent_tree_node = self.segid2treenode[segment.parent.id]
        #parent_tree_node = self.project_tree.topLevelItem(0)
        segtreeitem=QtGui.QTreeWidgetItem([segment.name])
        self.segid2treenode[segment.id]=segtreeitem
        segtreeitem._pydat=proxy(segment)
        parent_tree_node.insertChild(segindex,segtreeitem)
        for i in self.project_tree.selectedItems():
            i.setSelected(False)
        segtreeitem.setSelected(True)
        self.project_tree.setCurrentItem(segtreeitem)
        self.updatePropertiesTableData(segment.propertiesTableData())
        WRITEMARK_APP_INSTANCE.activesegment=segment
        #print '<< TREE.handleSegmentCreated'

    def handleSegmentRemoved(self, segment, segment_index):
        #print '>> TREE.handleSegmentRemoved:',segment,segment_index
        parent_tree_node = self.segid2treenode[segment.parent.id]#self.project_tree.topLevelItem(0)
        segmenttreeitem = parent_tree_node.child(segment_index)
        parent_tree_node.removeChild(segmenttreeitem)
        for i in self.project_tree.selectedItems():
            i.setSelected(False)
        parent_tree_node.setSelected(True)
        self.project_tree.setCurrentItem(parent_tree_node)
        WRITEMARK_APP_INSTANCE.activesegment=segment.parent
        #print '<< TREE.handleSegmentRemoved'

    def rightClickTreeEvent(self, *args, **kwargs):
        # Show Segment name editing dialog
        segment = WRITEMARK_APP_INSTANCE.activesegment
        ##print "rightClickTreeEvent:",segment
        if segment:
            if segment.parent is not None:
                tag, ok = showSegmentNameDialog(WRITEMARK_APP_INSTANCE.predefinedtags, default=segment.name)
                if len(tag)>0 and ok:
                    segment.name = tag
                    self.project_tree.selectedItems()[0].setText(0,segment.name)
                    self.updatePropertiesTableData(segment.propertiesTableData())
            else:
                print "TODO: SUPPORT RENAMING OF SEGMENT CATEGORY NODE."


    def currentTreeItemChangedEvent(self,*args,**kwargs):
        new_tree_widget, old_tree_widget=args

        try:
            if new_tree_widget is None or not hasattr(new_tree_widget, '_pydat'):
                self.current_pydat_obj=None
                self.properties_table.clear()
                WRITEMARK_APP_INSTANCE.activesegment=None
            else:
                self.current_pydat_obj=new_tree_widget._pydat
                self.updatePropertiesTableData(self.current_pydat_obj.propertiesTableData())
                activesegment=WRITEMARK_APP_INSTANCE.activesegment=self.current_pydat_obj
                temporalPlotWidget=WRITEMARK_APP_INSTANCE._penDataTimeLineWidget
                timelineselectionregionwidget = temporalPlotWidget.currentSelection
                if timelineselectionregionwidget:
                    if activesegment.parent:
                        timelineselectionregionwidget.setRegion(activesegment.timerange)
                        sreg=timelineselectionregionwidget.getRegion()
                        # If region did not change since last call to
                        # currentTreeItemChangedEvent, then calling setRegion
                        # does not trigger the region updated handler, so we
                        # need to force the data view widgets to check that
                        # the region is visible in the views.
                        if sreg == temporalPlotWidget._lastselectedtimerange:
                            temporalPlotWidget.ensureSelectionIsVisible(activesegment.timerange,activesegment.pendata)
                            WRITEMARK_APP_INSTANCE._penDataSpatialViewWidget.ensureSelectionIsVisible(activesegment.timerange,activesegment.pendata)
                        temporalPlotWidget._lastselectedtimerange = sreg
                    else:
                        # The segment category tree node (the root) has been selected,
                        # so zoom time and spatial views out to full data file,
                        # but do not change the selected region widget in the timeline view.
                        temporalPlotWidget.ensureSelectionIsVisible(activesegment.timerange,activesegment.pendata)
                        WRITEMARK_APP_INSTANCE._penDataSpatialViewWidget.ensureSelectionIsVisible(activesegment.timerange,activesegment.pendata)
        except Exception, e:
            import traceback
            traceback.print_exc()
            self.properties_table.clear()
            self.current_pydat_obj=None

    def treeItemDoubleClickedEvent(self,*args,**kwargs):
        item_tree_widget = args[0]
        if item_tree_widget and hasattr(item_tree_widget, '_pydat'):
            segment = item_tree_widget._pydat
            WRITEMARK_APP_INSTANCE._penDataTimeLineWidget.zoomToPenData(segment.pendata)
            WRITEMARK_APP_INSTANCE._penDataSpatialViewWidget.zoomToPenData(segment.pendata)
