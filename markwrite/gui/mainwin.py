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

from weakref import proxy

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea,Dock
from pyqtgraph import TreeWidget, TableWidget

from markwrite.util import getIconFilePath
from markwrite.file_io import loadPredefinedSegmentTagList
from markwrite.segment import PenDataSegment
from dialogs import ExitApplication, fileOpenDlg, ErrorDialog, warnDlg
from markwrite.project import MarkWriteProject

DEFAULT_WIN_SIZE = (1200,800)

DEFAULT_DOCK_PLACEMENT={
            u"Project Details":('left',(.2,1.0)),
            u"Timeline":(['right',u"Project Details"],(.8,.35)),
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
    sigSelectedPenDataUpdate = QtCore.Signal(object)  # new selected data_this/is &
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
        self.removeSegmentAction.setEnabled(s is not None)

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

        self.toolbarsegment = self.addToolBar('&Segment')
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

        addDock(u"Project Details", ProjectInfoDockArea())
        self._penDataTemporalPlotWidget=PenDataTemporalPlotWidget()
        addDock(u"Timeline", self._penDataTemporalPlotWidget)
        addDock(u"Spatial View", PenDataSpatialPlotWidget())
        addDock(u"Selected Data", SelectedPointsPlotWidget())

        #
        ## Do Misc. GUI setup.
        #

        self.setWindowIcon(QtGui.QIcon(getIconFilePath('edit&32.png')))

        # Below does not work for some reason.
        #app_icon = QtGui.QIcon()
        #app_icon.addFile('edit&16.png', QtCore.QSize(16,16))
        #app_icon.addFile('edit&24.png', QtCore.QSize(24,24))
        #app_icon.addFile('edit&32.png', QtCore.QSize(32,32))
        #app_icon.addFile('edit&64.png', QtCore.QSize(64,64))
        #app_icon.addFile('edit&128.png', QtCore.QSize(128,128))
        #app.setWindowIcon(app_icon)
        #self.setWindowIcon(app_icon)


        self.updateAppTitle()
        self.resize(*DEFAULT_WIN_SIZE)

    @property
    def penDataTemporalPlotWidget(self):
        return self._penDataTemporalPlotWidget

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
                    self.sigProjectChanged.emit(wmproj)
                    self.sigResetProjectData.emit(wmproj)
                except:
                    #import traceback
                    #traceback.print_exc()
                    ErrorDialog.info_text=u"An error occurred while opening:\n%s\nMarkWrite will now close."%(file_path)
                    ErrorDialog().display()
                    self.closeEvent(u'FORCE_EXIT')

    def saveProject(self,confirm_save=False):
        if self._current_project:
            self._current_project.save()
        self.updateAppTitle()
        self.saveProjectAction.setEnabled(self._current_project and self._current_project.modified)
        warnDlg(prompt=u"Project Saving is not Implemented Yet. Sorry.")

    def createSegment(self):
        if self.project and len(self.project.selectedpendata) > 0:
            tag, ok = showSegmentNameDialog(self._predefinedtags)
            if len(tag)>0 and ok:
                new_segment = PenDataSegment(name=tag, pendata=self.project.selectedpendata)
                self.project.addSegment(new_segment)

                # Increment the pendata array 'segmented' field for elements within
                # the segment so that # of segments created that contain each
                # pen point can be tracked
                allpendata = self.project.pendata
                segment_filter = (allpendata['time']>=new_segment.starttime) & (allpendata['time']<=new_segment.endtime)
                allpendata['segmented'][segment_filter]+=1

                self.sigSegmentCreated.emit(new_segment)
        else:
            ErrorDialog.info_text=u"Segment Creation Failed.\nNo selected pen data."
            ErrorDialog().display()

    def removeSegment(self):
        segment = self.activesegment
        if segment:
            seg_ix = self.project.getSegmentIndex(segment)
            print 'removeSegment:', segment, seg_ix

            # Decrement the pendata array 'segmented' field for elements within
            # the segment being removed so that # of segments that contain each
            # pen point can be tracked
            allpendata = self.project.pendata
            segment_filter = (allpendata['time']>=segment.starttime) & (allpendata['time']<=segment.endtime)
            allpendata['segmented'][segment_filter]-=1

            self.project.removeSegment(segment)
            self.activesegment=None

            self.sigSegmentRemoved.emit(segment, seg_ix)

    def handleProjectChange(self, project):
        if self._current_project:
            print "TODO: If current project has been modified, ask if it should be saved."
        self._current_project = project
        self.updateAppTitle()
        self.saveProjectAction.setEnabled(project.modified)

    def handleSelectedPenDataUpdate(self, pendata):
        self.createSegmentAction.setEnabled(self.project and len(pendata)>0)

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
        self.getPlotItem().setLabel('bottom', "Time", units='msec')

        self.xPenPosTrace = None
        self.yPenPosTrace = None
        self.currentSelection = None
        self.sigRegionChangedProxy=None
        WRITEMARK_APP_INSTANCE.sigResetProjectData.connect(self.handleResetPenData)

    def handleResetPenData(self, project):
        '''

        :param self:
        :param project:
        :return:
        '''
        #print "PenDataTemporalPlotWidget.handleResetPenData:",project
        numpy_data = project.pendata
        penValRange = (min(numpy_data['x'].min(), numpy_data['y'].min()), max(numpy_data['x'].max(), numpy_data['y'].max()))
        self.getPlotItem().setLimits(yMin=penValRange[0], yMax=penValRange[1], xMin=numpy_data['time'][0], xMax=numpy_data['time'][-1])
        if self.xPenPosTrace is None:
            # Create DataItem objects
            self.xPenPosTrace = self.getPlotItem().plot(x=numpy_data['time'], y=numpy_data['x'], pen=None, symbol='+', symbolSize=1, symbolPen=(0,255,0), name="X Position")
            self.yPenPosTrace = self.getPlotItem().plot(x=numpy_data['time'], y=numpy_data['y'], pen=None, symbol='+', symbolSize=1, symbolPen=(0,0,255), name="Y Position")

            # Add a Selection Region that is used to create segments by user
            self.currentSelection = pg.LinearRegionItem(values=[numpy_data['time'][0],numpy_data['time'][0]+1000],movable=True)
            self.currentSelection.setBounds(bounds=(numpy_data['time'][0], numpy_data['time'][-1]))
            self.addItem(self.currentSelection)
            self.sigRegionChangedProxy=pg.SignalProxy(self.currentSelection.sigRegionChanged, rateLimit=60, slot=self.handlePenDataSelectionChanged)

        else:
            # Update DataItem objects
            self.xPenPosTrace.setData(x=numpy_data['time'], y=numpy_data['x'])
            self.yPenPosTrace.setData(x=numpy_data['time'], y=numpy_data['y'])
            self.currentSelection.setRegion([numpy_data['time'][0],numpy_data['time'][0]+1000])
            self.currentSelection.setBounds(bounds=(numpy_data['time'][0], numpy_data['time'][-1]))

        self.handlePenDataSelectionChanged()

    def handlePenDataSelectionChanged(self):
        self.currentSelection.setZValue(10)
        minT, maxT=self.currentSelection.getRegion()
        #print "PenDataTemporalPlotWidget.handlePenDataSelectionChanged:",(minT, maxT)
        WRITEMARK_APP_INSTANCE.project.selectedtimeperiod=minT, maxT
        numpy_data = WRITEMARK_APP_INSTANCE.project.pendata
        selectedpendata = numpy_data[(numpy_data['time'] >= minT) & (numpy_data['time'] <= maxT)]
        WRITEMARK_APP_INSTANCE.project.selectedpendata = selectedpendata
        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.emit(selectedpendata)

        #zoomedPointsDataItem.setData(x=currentlySelectedData['x'],y=currentlySelectedData['y'])

class PenDataSpatialPlotWidget(pg.PlotWidget):
    def __init__(self):
        global WRITEMARK_APP_INSTANCE
        pg.PlotWidget.__init__(self, enableMenu=False)

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)

        #self.currentSelectionROI = pg.ROI(pos=(0,0),size=(0,0),removable=True,movable=False, pen=[255,0,0])
        #self.getPlotItem().getViewBox().addItem(self.currentSelectionROI)

        self.allPlotDataItem=self.getPlotItem().plot(pen=None, symbol='o', symbolSize=1)
        self.selectedPlotDataItem=self.getPlotItem().plot(pen=None, symbol='o', symbolSize=2, symbolBrush=(0,0,255), symbolPen=(0,0,255))

        WRITEMARK_APP_INSTANCE.sigResetProjectData.connect(self.handleResetPenData)
        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.connect(self.handlePenDataSelectionChanged)
        #(minx,maxx),(miny,maxy) = self.getPlotItem().getViewBox().viewRange()
        #print 'allDataSpatialPlotItem:',(minx,maxx),(miny,maxy)

    def handleResetPenData(self, project):
        #print "PenDataSpatialPlotWidget.handleResetPenData:",project
        pdat = project.pendata
        self.getPlotItem().setLimits(xMin=pdat['x'].min(), yMin=pdat['y'].min(),xMax=pdat['x'].max(), yMax=pdat['y'].max())
        self.allPlotDataItem.setData(x=pdat['x'],y=pdat['y'])

    def handlePenDataSelectionChanged(self,selectedpendata):
        #print "PenDataSpatialPlotWidget.handlePenDataSelectionChanged: len=",len(selectedpendata)
        self.selectedPlotDataItem.setData(x=selectedpendata['x'],y=selectedpendata['y'])
        #if len(selectedpendata) > 0:
        #    xmin,ymin = selectedpendata['x'].min(),selectedpendata['y'].min()
        #    xmax,ymax = selectedpendata['x'].max(),selectedpendata['y'].max()
        #    sw=xmax-xmin
        #    sh=ymax-ymin
        #    self.currentSelectionROI.setPos((xmin-2,ymin-2))
        #    self.currentSelectionROI.setSize((sw+4,sh+4))
        #else:
        #    self.currentSelectionROI.setPos((0,0))
        #    self.currentSelectionROI.setSize((0,0))

class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)
        self.getPlotItem().hideButtons()
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')

        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o', symbolSize=1)

        WRITEMARK_APP_INSTANCE.sigSelectedPenDataUpdate.connect(self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self,selectedpendata):
        #print "SelectedPointsPlotWidget.handlePenDataSelectionChanged: len=",len(selectedpendata)
        self.plotDataItem.setData(x=selectedpendata['x'],y=selectedpendata['y'])


class ProjectInfoDockArea(DockArea):
    def __init__(self):
        DockArea.__init__(self)

        self.project_tree_dock = Dock(u"Project Tree", hideTitle=True)
        self.addDock(self.project_tree_dock, 'top')#'above', self.flowcharts_dock)

        self.project_tree = TreeWidget()
        self.project_tree.setColumnCount(1)
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.project_tree.setWindowTitle('MarkWrite Project')

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
        #self.project_tree.itemActivated.connect(self.itemActivatedEvent)
        #self.project_tree.itemChanged.connect(self.itemChangedEvent)
        self.project_tree.itemDoubleClicked.connect(self.treeItemDoubleClickedEvent)
        #self.project_tree.itemCollapsed.connect(self.itemCollapsedEvent)
        #self.project_tree.itemEntered.connect(self.itemEnteredEvent)
        #self.project_tree.itemExpanded.connect(self.itemExpandedEvent)
        #self.project_tree.itemPressed.connect(self.itemPressedEvent)
        #self.project_tree.itemSelectionChanged.connect(self.treeItemSelectionChangedEvent)

    def updatePropertiesTableData(self,props):
        self.properties_table.clear()
        self.properties_table.setData(props)
        self.properties_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    #
    # Signal Handlers
    #

    def handleProjectChange(self, project):
        self.project_tree.clear()

        # Create Project Tree Node
        projecttreeitem=QtGui.QTreeWidgetItem([project.name])
        projecttreeitem._pydat=proxy(project)
        self.project_tree.addTopLevelItem(projecttreeitem)
        projecttreeitem.setSelected(True)
        self.project_tree.setCurrentItem(projecttreeitem)

        for pds in project.segments:
            segtreeitem=QtGui.QTreeWidgetItem([pds.name])
            segtreeitem._pydat=proxy(pds)
            projecttreeitem.addChild(segtreeitem)

        self.updatePropertiesTableData(project.propertiesTableData())

    def handleSegmentCreated(self, segment):
        segindex = WRITEMARK_APP_INSTANCE.project.getSegmentIndex(segment)
        project_tree_node = self.project_tree.topLevelItem(0)
        segtreeitem=QtGui.QTreeWidgetItem([segment.name])
        segtreeitem._pydat=proxy(segment)
        project_tree_node.insertChild(segindex,segtreeitem)
        for i in self.project_tree.selectedItems():
            i.setSelected(False)
        segtreeitem.setSelected(True)
        self.project_tree.setCurrentItem(segtreeitem)
        self.updatePropertiesTableData(segment.propertiesTableData())
        WRITEMARK_APP_INSTANCE.activesegment=segment

    def handleSegmentRemoved(self, segment, segment_index):
        project_tree_node = self.project_tree.topLevelItem(0)
        segmenttreeitem = project_tree_node.child(segment_index)
        project_tree_node.removeChild(segmenttreeitem)

    def currentTreeItemChangedEvent(self,*args,**kwarg):
        new_tree_widget, old_tree_widget=args

        try:
            if new_tree_widget is None or not hasattr(new_tree_widget, '_pydat'):
                self.current_pydat_obj=None
                self.properties_table.clear()
            else:
                self.current_pydat_obj=new_tree_widget._pydat
                self.updatePropertiesTableData(new_tree_widget._pydat.propertiesTableData())
                if isinstance(self.current_pydat_obj,PenDataSegment):
                    activesegment=WRITEMARK_APP_INSTANCE.activesegment=self.current_pydat_obj
                    WRITEMARK_APP_INSTANCE.penDataTemporalPlotWidget.currentSelection.setRegion([activesegment.starttime,activesegment.endtime])
                else:
                    WRITEMARK_APP_INSTANCE.activesegment=None
        except Exception, e:
            print 'currentItemChangedEvent error:',e
            self.properties_table.clear()
            self.current_pydat_obj=None

    def treeItemDoubleClickedEvent(self,*args,**kwargs):
        item = args[0]
        if hasattr(item, '_pydat'):
            wmobj = item._pydat
            if isinstance(wmobj, PenDataSegment):
                print "PenDataSegment DoubleClickedEvent",wmobj
                tag, ok = showSegmentNameDialog(WRITEMARK_APP_INSTANCE._predefinedtags, default=wmobj.name)
                if len(tag)>0 and ok:
                    wmobj.name = tag
                    item.setText(0,wmobj.name)
                    self.updatePropertiesTableData(wmobj.propertiesTableData())

#void currentItemChanged (QTreeWidgetItem *,QTreeWidgetItem *)
#void itemActivated (QTreeWidgetItem *,int)
#void itemChanged (QTreeWidgetItem *,int)
#void itemClicked (QTreeWidgetItem *,int)
#void itemCollapsed (QTreeWidgetItem *)
#void itemDoubleClicked (QTreeWidgetItem *,int)
#void itemEntered (QTreeWidgetItem *,int)
#void itemExpanded (QTreeWidgetItem *)
#void itemPressed (QTreeWidgetItem *,int)
#void itemSelectionChanged ()