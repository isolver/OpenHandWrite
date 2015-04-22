import numpy as np
import pyqtgraph as pg
from markwrite.gui.projectsettings import SETTINGS
from markwrite.gui.mainwin import MarkWriteMainWindow
__author__ = 'Sol'


class PenDataSpatialPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)

        self.getPlotItem().invertY(True)
        self.getPlotItem().setAspectLocked(True, 1)

        self.allPlotDataItem = None  #self.getPlotItem().plot(pen=None,
        # symbol='o', symbolSize=1, symbolBrush=(255,255,255), symbolPen=(
        # 255,255,255))
        self.selectedPlotDataItem = None  #self.getPlotItem().plot(pen=None,
        # symbol='o', symbolSize=3, symbolBrush=(0,0,255), symbolPen=(0,0,255))

        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)
        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.connect(
            self.handlePenDataSelectionChanged)
        MarkWriteMainWindow.instance().sigSegmentRemoved.connect(
            self.handleSegmentRemoved)
        MarkWriteMainWindow.instance().sigSegmentCreated.connect(
            self.handleSegmentCreated)

    def createDefaultPenBrushForData(self, pdat):
        pen = pg.mkPen(SETTINGS['spatialplot_default_color'],
                       width=SETTINGS['spatialplot_default_point_size'])
        pen2 = pg.mkPen(SETTINGS['spatialplot_default_color'].lighter(),
                        width=SETTINGS['spatialplot_default_point_size'])
        brush = pg.mkBrush(SETTINGS['spatialplot_default_color'])
        brush2 = pg.mkBrush(SETTINGS['spatialplot_default_color'].lighter())
        penarray = np.empty(pdat.shape[0], dtype=object)
        penarray[:] = pen
        penarray[pdat['pressure'] == 0] = pen2
        brusharray = np.empty(pdat.shape[0], dtype=object)
        brusharray[:] = brush
        brusharray[pdat['pressure'] == 0] = brush2
        return brusharray, penarray

    def handleResetPenData(self, project):
        #print ">> PenDataSpatialPlotWidget.handleResetPenData:",project
        pdat = project.pendata

        if self.allPlotDataItem is None:
            brusharray,penarray = self.createDefaultPenBrushForData(pdat)

            self.allPlotDataItem = self.getPlotItem().plot(x=pdat['x'],
                                                           y=pdat['y'],
                                                           pen=None, symbol='o',
                                                           symbolSize=1,
                                                           symbolBrush=brusharray,
                                                           symbolPen=penarray)

            pen = pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'], width=SETTINGS['spatialplot_selectedpoint_size'])
            brush = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'])

            self.selectedPlotDataItem = self.getPlotItem().plot(pen=None,
                                                                symbol='o',
                                                                symbolSize=SETTINGS['spatialplot_selectedpoint_size'],
                                                                symbolPen=pen,
                                                                symbolBrush=brush)

        else:
            brusharray, penarray = self.createDefaultPenBrushForData(pdat)

            self.allPlotDataItem.setData(x=pdat['x'], y=pdat['y'],
                                         pen=None, symbol='o',
                                         symbolSize=1,
                                         symbolBrush=brusharray,
                                         symbolPen=penarray)

            self.getPlotItem().setLimits(xMin=pdat['x'].min(),
                                         yMin=pdat['y'].min(),
                                         xMax=pdat['x'].max(),
                                         yMax=pdat['y'].max())

            self.setRange(xRange=(pdat['x'].min(), pdat['x'].max()),
                          yRange=(pdat['y'].min(), pdat['y'].max()),
                          padding=None)
            #print "<< PenDataSpatialPlotWidget.handleResetPenData"


    def updateSelectedPenPointsGraphics(self, selectedpendata=None):
        if selectedpendata is None:
            selectedpendata = MarkWriteMainWindow.instance().project.selectedpendata
        if MarkWriteMainWindow.instance().project.isSelectedDataValidForNewSegment():
            pen = pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'],
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            brush = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'])
            self.selectedPlotDataItem.setData(x=selectedpendata['x'],
                                              y=selectedpendata['y'], pen=None,
                                              symbol='o', symbolSize=SETTINGS[
                    'spatialplot_selectedpoint_size'],
                                              symbolBrush=brush, symbolPen=pen)
        else:
            pen = pg.mkPen(SETTINGS['spatialplot_selectedinvalid_color'],
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            brush = pg.mkBrush(SETTINGS['spatialplot_selectedinvalid_color'])
            self.selectedPlotDataItem.setData(x=selectedpendata['x'],
                                              y=selectedpendata['y'], pen=None,
                                              symbol='o', symbolSize=SETTINGS[
                    'spatialplot_selectedpoint_size'],
                                              symbolBrush=brush, symbolPen=pen)

    def handleUpdatedSettingsEvent(self, updates, settings):
        selectedpendata = MarkWriteMainWindow.instance().project.selectedpendata
        pdat = MarkWriteMainWindow.instance().project.pendata

        for k in updates.keys():
            if k.startswith('spatialplot_default'):
                brusharray, penarray = self.createDefaultPenBrushForData(pdat)

                self.allPlotDataItem.setData(x=pdat['x'], y=pdat['y'],
                                             symbolBrush=brusharray,
                                             symbolPen=penarray)
                break

        for k in updates.keys():
            if k.startswith('spatialplot_selected'):
                self.updateSelectedPenPointsGraphics(selectedpendata)
            break

    def handleSegmentRemoved(self,*args, **kwags):
        self.updateSelectedPenPointsGraphics()

    def handleSegmentCreated(self,*args, **kwags):
        self.updateSelectedPenPointsGraphics()

    def handlePenDataSelectionChanged(self, timeperiod, selectedpendata):

        if self.allPlotDataItem is None:
            self.handleResetPenData(MarkWriteMainWindow.instance().project)

        self.updateSelectedPenPointsGraphics(selectedpendata)

        self.ensureSelectionIsVisible(timeperiod, selectedpendata)
        #print "<< PenDataSpatialPlotWidget.handlePenDataSelectionChanged"

    def zoomToPenData(self, pendata, lock_bounds=False):
        xpadding = self.getPlotItem().getViewBox().suggestPadding(0)
        ypadding = self.getPlotItem().getViewBox().suggestPadding(1)
        if lock_bounds:
            self.setLimits(yMin=max(0.0, pendata['y'].min() - ypadding),
                           yMax=pendata['y'].max() + ypadding,
                           xMin=max(0.0, pendata['x'].min() - xpadding),
                           xMax=pendata['x'].max() + xpadding)
        self.setRange(xRange=(pendata['x'].min(), pendata['x'].max()),
                      yRange=(pendata['y'].min(), pendata['y'].max()),
                      padding=None)

    def ensureSelectionIsVisible(self, timespan, selectedpendata):
        if len(selectedpendata) > 0:
            (vxmin, vxmax), (vymin, vymax) = self.viewRange()
            dxmin, dxmax, dymin, dymax = selectedpendata['x'].min(), \
                                         selectedpendata['x'].max(), \
                                         selectedpendata['y'].min(), \
                                         selectedpendata['y'].max()

            vxlength = vxmax - vxmin
            vylength = vymax - vymin
            dxlength = dxmax - dxmin
            dylength = dymax - dymin

            if dxlength > vxlength or dylength > vylength:
                #print "dlength > vlength:",dlength, vlength
                self.setRange(xRange=(dxmin, dxmax), yRange=(dymin, dymax),
                              padding=None)
                return

            xrange = None
            yrange = None

            if dxmin < vxmin:
                xrange = (dxmin, dxmin + vxlength)
            if dxmax > vxmax:
                xrange = (dxmax - vxlength, dxmax)

            if dymin < vymin:
                yrange = (dymin, dymin + vylength)
            if dymax > vymax:
                yrange = (dymax - vylength, dymax)

            if xrange:
                dxlength = xrange[1] - xrange[0]
            if yrange:
                dylength = yrange[1] - yrange[0]

            if dxlength > vxlength:
                xrange = (dxmin, dxmax)
            if dylength > vylength:
                yrange = (dymin, dymax)

            if xrange or yrange:
                self.setRange(xRange=xrange, yRange=yrange, padding=0)