__author__ = 'Sol'

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import TreeWidget

class SegmentTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        TreeWidget.__init__(self,parent)
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.setWindowTitle('MarkWrite Project')

#        self.itemActivated.connect(self.handleItemActivatedEvent)
#        self.itemChanged.connect(self.handleItemChangedEvent)
#        self.itemCollapsed.connect(self.handleItemCollapsedEvent)
#        self.itemEntered.connect(self.handleItemEnteredEvent)
#        self.itemExpanded.connect(self.handleItemExpandedEvent)
#        self.itemPressed.connect(self.handleItemPressedEvent)
#        self.itemSelectionChanged.connect(self.handleItemSelectionChangedEvent)
#        self.itemClicked.connect(self.handleItemSelectionChangedEvent)

    def itemMoving(self, item, parent, index):
        """Called when item has been dropped elsewhere in the tree.
        Return True to accept the move, False to reject."""
        return False

    def handleItemActivatedEvent(self, *args, **kwargs):
        print "handleItemActivatedEvent:", args, kwargs

    def handleItemChangedEvent(self, *args, **kwargs):
        print "handleItemChangedEvent:", args, kwargs

    def handleItemCollapsedEvent(self, *args, **kwargs):
        print "handleItemCollapsedEvent:", args, kwargs

    def handleItemEnteredEvent(self, *args, **kwargs):
        print "handleItemEnteredEvent:", args, kwargs

    def handleItemClickedEvent(self, *args, **kwargs):
        print "handleItemClickedEvent:", args, kwargs

    def handleItemExpandedEvent(self, *args, **kwargs):
        print "handleItemExpandedEvent:", args, kwargs

    def handleItemPressedEvent(self, *args, **kwargs):
        print "handleItemPressedEvent:", args, kwargs

    def handleItemSelectionChangedEvent(self, *args, **kwargs):
        print "handleItemSelectionChangedEvent:", args, kwargs
