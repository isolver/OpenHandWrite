from _weakref import proxy
from weakref import WeakValueDictionary
from PyQt4 import QtGui
from pyqtgraph.dockarea import DockArea, Dock
from markwrite.gui.mainwin import showSegmentNameDialog, MarkWriteMainWindow

__author__ = 'Sol'

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import TreeWidget, TableWidget

from markwrite.gui.mainwin import MarkWriteMainWindow

class SegmentTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        TreeWidget.__init__(self,parent)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
#        self.setWindowTitle('MarkWrite Project')

#        self.itemActivated.connect(self.handleItemActivatedEvent)
#        self.itemChanged.connect(self.handleItemChangedEvent)
#        self.itemCollapsed.connect(self.handleItemCollapsedEvent)
#        self.itemEntered.connect(self.handleItemEnteredEvent)
#        self.itemExpanded.connect(self.handleItemExpandedEvent)
#        self.itemPressed.connect(self.handleItemPressedEvent)
#        self.itemSelectionChanged.connect(self.handleItemSelectionChangedEvent)
#        self.itemClicked.connect(self.handleItemClickedEvent)

    def itemMoving(self, item, parent, index):
        """Called when item has been dropped elsewhere in the tree.
        Return True to accept the move, False to reject."""
        return False

    def handleItemActivatedEvent(self, *args, **kwargs):
        print "itemActivated:", args, kwargs

    def handleItemChangedEvent(self, *args, **kwargs):
        print "itemChanged:", args, kwargs

    def handleItemCollapsedEvent(self, *args, **kwargs):
        print "itemCollapsed:", args, kwargs

    def handleItemEnteredEvent(self, *args, **kwargs):
        print "itemEntered:", args, kwargs

    def handleItemClickedEvent(self, *args, **kwargs):
        print "itemClicked:", args, kwargs

    def handleItemExpandedEvent(self, *args, **kwargs):
        print "itemExpanded:", args, kwargs

    def handleItemPressedEvent(self, *args, **kwargs):
        print "itemPressed:", args, kwargs

#    def handleItemSelectionChangedEvent(self, *args, **kwargs):
#        print "itemSelectionChanged:", args, kwargs,self.selectedItems()
class SegmentInfoDockArea(DockArea):
    segid2treenode = WeakValueDictionary()

    def __init__(self):
        DockArea.__init__(self)

        self.project_tree_dock = Dock(u"Project Tree", hideTitle=True)
        self.addDock(self.project_tree_dock,
                     'top')  #'above', self.flowcharts_dock)

        self.project_tree = SegmentTreeWidget()

        self.project_tree_dock.addWidget(self.project_tree)

        self.properties_table = TableWidget(sortable=False, editable=False)
        self.properties_table.setColumnCount(1)
        self.properties_table.contextMenu.clear()
        self.properties_table.horizontalHeader().hide()

        self.properties_dock = Dock("Selected Object Properties",
                                    widget=self.properties_table,
                                    hideTitle=True)
        self.addDock(self.properties_dock, 'bottom')

        self.current_pydat_obj = None

        MarkWriteMainWindow.instance().sigProjectChanged.connect(
            self.handleProjectChange)
        MarkWriteMainWindow.instance().sigSegmentCreated.connect(
            self.handleSegmentCreated)
        MarkWriteMainWindow.instance().sigSegmentRemoved.connect(
            self.handleSegmentRemoved)

        self.project_tree.currentItemChanged.connect(
            self.currentTreeItemChangedEvent)
        self.project_tree.itemDoubleClicked.connect(
            self.treeItemDoubleClickedEvent)
        self.project_tree.customContextMenuRequested.connect(
            self.rightClickTreeEvent)

    def updatePropertiesTableData(self, props):
        self.properties_table.clear()
        self.properties_table.setData(props)
        self.properties_table.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

    #
    # Signal Handlers
    #

    def handleProjectChange(self, project):
        self.project_tree.clear()
        self.segid2treenode.clear()
        # Create Project Tree Node
        projecttreeitem = QtGui.QTreeWidgetItem([project.name])
        projecttreeitem._pydat = proxy(project.segmentset)
        self.segid2treenode[project.segmentset.id] = projecttreeitem
        self.project_tree.addTopLevelItem(projecttreeitem)
        projecttreeitem.setSelected(True)
        self.project_tree.setCurrentItem(projecttreeitem)
        self.current_pydat_obj = project.segmentset
        #TODO: UPDATE TO SUPPORT PROJECT REOPENNING WITH SEG. HEIRARCHY.
        # Current code assumes list on segments only
        #for pds in project.segmentset.children:
        #    segtreeitem = QtGui.QTreeWidgetItem([pds.name])
        #    segtreeitem._pydat = proxy(pds)
        #    projecttreeitem.addChild(segtreeitem)

        self.updatePropertiesTableData(project.segmentset.propertiesTableData())

    def handleSegmentCreated(self, segment):
        #print '>>TREE.handleSegmentCreated:',segment
        segindex = segment.parent.getChildIndex(segment)
        parent_tree_node = self.segid2treenode[segment.parent.id]
        #parent_tree_node = self.project_tree.topLevelItem(0)
        segtreeitem = QtGui.QTreeWidgetItem([segment.name])
        self.segid2treenode[segment.id] = segtreeitem
        segtreeitem._pydat = proxy(segment)
        parent_tree_node.insertChild(segindex, segtreeitem)
        for i in self.project_tree.selectedItems():
            i.setSelected(False)
        segtreeitem.setSelected(True)
        self.project_tree.setCurrentItem(segtreeitem)
        self.updatePropertiesTableData(segment.propertiesTableData())
        MarkWriteMainWindow.instance().activesegment = segment
        #print '<< TREE.handleSegmentCreated'

    def handleSegmentRemoved(self, segment, segment_index):
        #print '>> TREE.handleSegmentRemoved:',segment,segment_index
        parent_tree_node = self.segid2treenode[
            segment.parent.id]  #self.project_tree.topLevelItem(0)
        segmenttreeitem = parent_tree_node.child(segment_index)
        parent_tree_node.removeChild(segmenttreeitem)
        for i in self.project_tree.selectedItems():
            i.setSelected(False)
        parent_tree_node.setSelected(True)
        self.project_tree.setCurrentItem(parent_tree_node)
        MarkWriteMainWindow.instance().activesegment = segment.parent
        #print '<< TREE.handleSegmentRemoved'

    def rightClickTreeEvent(self, *args, **kwargs):
        # Show Segment name editing dialog
        segment = MarkWriteMainWindow.instance().activesegment
        ##print "rightClickTreeEvent:",segment
        if segment:
            if segment.parent is not None:
                tag, ok = showSegmentNameDialog(
                    MarkWriteMainWindow.instance().predefinedtags, default=segment.name)
                if len(tag) > 0 and ok:
                    segment.name = tag
                    self.project_tree.selectedItems()[0].setText(0,
                                                                 segment.name)
                    self.updatePropertiesTableData(
                        segment.propertiesTableData())
            else:
                print "TODO: SUPPORT RENAMING OF SEGMENT CATEGORY NODE."


    def currentTreeItemChangedEvent(self, *args, **kwargs):
        new_tree_widget, old_tree_widget = args

        try:
            if new_tree_widget is None or not hasattr(new_tree_widget,
                                                      '_pydat'):
                self.current_pydat_obj = None
                self.properties_table.clear()
                MarkWriteMainWindow.instance().activesegment = None
            else:
                self.current_pydat_obj = new_tree_widget._pydat
                self.updatePropertiesTableData(
                    self.current_pydat_obj.propertiesTableData())
                activesegment = MarkWriteMainWindow.instance().activesegment = self.current_pydat_obj
                temporalPlotWidget = MarkWriteMainWindow.instance()._penDataTimeLineWidget
                timelineselectionregionwidget = temporalPlotWidget.currentSelection
                if timelineselectionregionwidget:
                    if activesegment.parent:
                        timelineselectionregionwidget.setRegion(
                            activesegment.timerange)
                        sreg = timelineselectionregionwidget.getRegion()
                        # If region did not change since last call to
                        # currentTreeItemChangedEvent, then calling setRegion
                        # does not trigger the region updated handler, so we
                        # need to force the data view widgets to check that
                        # the region is visible in the views.
                        if sreg == temporalPlotWidget._lastselectedtimerange:
                            temporalPlotWidget.ensureSelectionIsVisible(
                                activesegment.timerange, activesegment.pendata)
                            MarkWriteMainWindow.instance()._penDataSpatialViewWidget.ensureSelectionIsVisible(
                                activesegment.timerange, activesegment.pendata)
                        temporalPlotWidget._lastselectedtimerange = sreg
                    else:
                        # The segment category tree node (the root) has been selected,
                        # so zoom time and spatial views out to full data file,
                        # but do not change the selected region widget in the timeline view.
                        temporalPlotWidget.ensureSelectionIsVisible(
                            activesegment.timerange, activesegment.pendata)
                        MarkWriteMainWindow.instance()._penDataSpatialViewWidget.ensureSelectionIsVisible(
                            activesegment.timerange, activesegment.pendata)
        except Exception, e:
            import traceback

            traceback.print_exc()
            self.properties_table.clear()
            self.current_pydat_obj = None

    def treeItemDoubleClickedEvent(self, *args, **kwargs):
        item_tree_widget = args[0]
        if item_tree_widget and hasattr(item_tree_widget, '_pydat'):
            segment = item_tree_widget._pydat
            MarkWriteMainWindow.instance()._penDataTimeLineWidget.zoomToPenData(
                segment.pendata)
            MarkWriteMainWindow.instance()._penDataSpatialViewWidget.zoomToPenData(
                segment.pendata)