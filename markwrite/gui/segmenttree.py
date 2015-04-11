__author__ = 'Sol'

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import TreeWidget

class SegmentTreeWidget(TreeWidget):
    def __init__(self, parent=None):
        TreeWidget.__init__(self,parent)

    def itemMoving(self, item, parent, index):
        """Called when item has been dropped elsewhere in the tree.
        Return True to accept the move, False to reject."""
        return False