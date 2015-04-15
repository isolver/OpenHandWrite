import pyqtgraph as pg

__author__ = 'Sol'

from markwrite.gui.mainwin import MarkWriteMainWindow
class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False, )

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)
        #self.getPlotItem().hideButtons()
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')
        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o',
                                                    symbolSize=1,
                                                    symbolBrush=(255, 255, 255),
                                                    symbolPen=(255, 255, 255))

        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.connect(
            self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self.plotDataItem.setData(x=pendata['x'], y=pendata['y'], )
        self.getPlotItem().enableAutoRange(x=True, y=True)