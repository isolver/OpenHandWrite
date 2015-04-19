from _weakref import proxy
from weakref import WeakValueDictionary
from PyQt4 import QtGui
from pyqtgraph.dockarea import DockArea, Dock
from markwrite.gui.mainwin import showSegmentNameDialog, MarkWriteMainWindow

__author__ = 'Sol'

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import TreeWidget, TableWidget
from markwrite.segment import PenDataSegmentCategory
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

        MarkWriteMainWindow.instance().sigProjectChanged.connect(
            self.handleProjectChange)
        MarkWriteMainWindow.instance().sigSegmentCreated.connect(
            self.handleSegmentCreated)
        MarkWriteMainWindow.instance().sigSegmentRemoved.connect(
            self.handleSegmentRemoved)
        MarkWriteMainWindow.instance().sigActiveObjectChanged.connect(
            self.handleActiveObjectChanged)

        self.project_tree.currentItemChanged.connect(
            self.currentTreeItemChangedEvent)
        self.project_tree.itemDoubleClicked.connect(
            self.treeItemDoubleClickedEvent)
        self.project_tree.customContextMenuRequested.connect(
            self.rightClickTreeEvent)
 #       self.project_tree.itemSelectionChanged.connect(self.handleItemSelectionChanged)

        self.doNotSetActiveObject=False

    def updatePropertiesTableData(self, objwithprops, cleartable=False):
        if cleartable:
            self.properties_table.clear()
            self.properties_table.horizontalHeader().setResizeMode(
                QtGui.QHeaderView.Stretch)
            self.properties_table.setData(objwithprops.propertiesTableData())
        else:
            i=0
            for v in objwithprops.propertiesTableData().values():
                self.properties_table.setRow(i,v)
                i+=1

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

    def handleSegmentCreated(self, segment):
        #print '>>TREE.handleSegmentCreated:',segment
        self.doNotSetActiveObject = True
        segindex = segment.parent.getChildIndex(segment)
        parent_tree_node = self.segid2treenode[segment.parent.id]
        #parent_tree_node = self.project_tree.topLevelItem(0)
        segtreeitem = QtGui.QTreeWidgetItem([segment.name])
        self.segid2treenode[segment.id] = segtreeitem
        segtreeitem._pydat = proxy(segment)
        parent_tree_node.insertChild(segindex, segtreeitem)
        #for i in self.project_tree.selectedItems():
        #    i.setSelected(False)
        #segtreeitem.setSelected(True)
        self.project_tree.setCurrentItem(segtreeitem)
        #print '<< TREE.handleSegmentCreated'
        self.doNotSetActiveObject = False

    def handleSegmentRemoved(self, segment, segment_index):
        #print '>> TREE.handleSegmentRemoved:',segment,segment_index
        self.doNotSetActiveObject = True
        parent_tree_node = self.segid2treenode[
            segment.parent.id]  #self.project_tree.topLevelItem(0)
        segmenttreeitem = parent_tree_node.child(segment_index)
        #segmenttreeitem.setSelected(False)
        parent_tree_node.removeChild(segmenttreeitem)
        self.project_tree.setCurrentItem(None)
        self.project_tree.clearSelection()
        self.doNotSetActiveObject = False
        #print '<< TREE.handleSegmentRemoved'

    def handleActiveObjectChanged(self,activeobj, prevactiveobj):
        #if activeobj != prevactiveobj:
        #    print "Active Obj Changed:",activeobj, prevactiveobj
        if activeobj:
            self.updatePropertiesTableData(activeobj, activeobj!=prevactiveobj)

        if activeobj != prevactiveobj:
            if not isinstance(activeobj,PenDataSegmentCategory):
                #print "Deselecting Tree Node.."
                # set root node as current, otherwise if user tries to press on
                # prev selected segment, tree change event will not fire.
                if self.segid2treenode.has_key(0):
                    self.project_tree.setCurrentItem(self.segid2treenode[0])
                self.project_tree.clearSelection()
                #self.project_tree.setCurrentItem(None)
            else:
                #print "Settting tree node",activeobj,self.segid2treenode[activeobj.id]
                self.project_tree.setCurrentItem(self.segid2treenode[activeobj.id])

    def rightClickTreeEvent(self, *args, **kwargs):
        # Show Segment name editing dialog
        segment = MarkWriteMainWindow.instance().activeobject
        ##print "rightClickTreeEvent:",segment
        if segment:
            if segment.parent is not None:
                tag, ok = showSegmentNameDialog(
                    MarkWriteMainWindow.instance().predefinedtags, default=segment.name)
                if len(tag) > 0 and ok:
                    segment.name = tag
                    self.project_tree.selectedItems()[0].setText(0,
                                                                 segment.name)
            else:
                print "TODO: SUPPORT RENAMING OF SEGMENT CATEGORY NODE."


    def currentTreeItemChangedEvent(self, *args, **kwargs):
        current_tree_item, old_tree_widget = args
        #print ">> currentTreeItemChangedEvent:",current_tree_item, old_tree_widget
#        print "  selected items:",self.project_tree.selectedItems()
        try:
            if current_tree_item is None:
                #passing in not obj sets activeObject to project.selectedtimeregion
                MarkWriteMainWindow.instance().setActiveObject()
            elif self.doNotSetActiveObject is False:
                self.project_tree.setCurrentItem(current_tree_item)
                selectedsegment = current_tree_item._pydat
                if selectedsegment.isRoot():
                    ao=MarkWriteMainWindow.instance().setActiveObject()
                else:
                    ao=MarkWriteMainWindow.instance().setActiveObject(selectedsegment)
                #print "Set active object:",ao
        except Exception, e:
            import traceback
            traceback.print_exc()
            self.properties_table.clear()
#        print "<< currentTreeItemChangedEvent"

    def treeItemDoubleClickedEvent(self, *args, **kwargs):
        selectedsegment = args[0]._pydat
        MarkWriteMainWindow.instance()._penDataTimeLineWidget.zoomToPenData(
            selectedsegment.pendata)
        MarkWriteMainWindow.instance()._penDataSpatialViewWidget.zoomToPenData(
            selectedsegment.pendata)