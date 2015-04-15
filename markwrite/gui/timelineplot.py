import numpy as np
import pyqtgraph as pg

from markwrite.gui.projectsettings import SETTINGS

from markwrite.gui.mainwin import MarkWriteMainWindow
__author__ = 'Sol'


class PenDataTemporalPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)
        # Create Pen Position Time Series Plot for All Data

        self.getPlotItem().setLabel('left', "Pen Position", units='pix')
        self.getPlotItem().setLabel('bottom', "Time", units='sec')
        self.xPenPosTrace = None
        self.yPenPosTrace = None
        self.currentSelection = None
        self._lastselectedtimerange = None
        self.sigRegionChangedProxy = None
        MarkWriteMainWindow.instance().sigResetProjectData.connect(
        self.handleResetPenData)

    def handleResetPenData(self, project):
        '''

        :param self:
        :param project:
        :return:
        '''
        penpoints = project.pendata
        penValRange = (min(penpoints['x'].min(), penpoints['y'].min()),
                       max(penpoints['x'].max(), penpoints['y'].max()))
        self.getPlotItem().setLimits(yMin=penValRange[0], yMax=penValRange[1],
                                     xMin=penpoints['time'][0],
                                     xMax=penpoints['time'][-1])
        if self.xPenPosTrace is None:
            # Create DataItem objects
            pen = pg.mkPen(SETTINGS['timeplot_xtrace_color'],
                           width=SETTINGS['timeplot_xtrace_size'])
            pen2 = pg.mkPen(SETTINGS['timeplot_xtrace_color'].darker(),
                            width=SETTINGS['timeplot_xtrace_size'])
            penarray = np.empty(penpoints.shape[0], dtype=object)
            penarray[:] = pen
            penarray[penpoints['pressure'] == 0] = pen2

            brush = pg.mkBrush(SETTINGS['timeplot_xtrace_color'])
            brush2 = pg.mkBrush(SETTINGS['timeplot_xtrace_color'].darker())
            brusharray = np.empty(penpoints.shape[0], dtype=object)
            brusharray[:] = brush
            brusharray[penpoints['pressure'] == 0] = brush2

            self.xPenPosTrace = self.getPlotItem().plot(x=penpoints['time'],
                                                        y=penpoints['x'],
                                                        pen=None, symbol='o',
                                                        symbolSize=1,
                                                        symbolPen=penarray,
                                                        symbolBrush=brusharray,
                                                        name="X Position")  #
                                                        #  pen=None,
                                                        # symbol='o',
                                                        # symbolSize=1,
                                                        # symbolPen='r',
                                                        # symbolBrush='r',

            pen = pg.mkPen(SETTINGS['timeplot_ytrace_color'],
                           width=SETTINGS['timeplot_ytrace_size'])
            pen2 = pg.mkPen(SETTINGS['timeplot_ytrace_color'].darker(),
                            width=SETTINGS['timeplot_ytrace_size'])
            penarray[:] = pen
            penarray[penpoints['pressure'] == 0] = pen2

            brush = pg.mkBrush(SETTINGS['timeplot_ytrace_color'])
            brush2 = pg.mkBrush(SETTINGS['timeplot_ytrace_color'].darker())
            brusharray[:] = brush
            brusharray[penpoints['pressure'] == 0] = brush2

            self.yPenPosTrace = self.getPlotItem().plot(x=penpoints['time'],
                                                        y=penpoints['y'],
                                                        pen=None, symbol='o',
                                                        symbolSize=1,
                                                        symbolPen=penarray,
                                                        symbolBrush=brusharray,
                                                        name="Y Position")
                                                        #symbol='o',
                                                        # symbolSize=1,
                                                        # symbolPen='g',
                                                        # symbolBrush='g',
                                                        # name="Y Position")

            # Add a Selection Region that is used to create segments by user
            self.currentSelection = pg.LinearRegionItem(
                values=[penpoints['time'][0], penpoints['time'][0] + 1.0],
                movable=True)
            self.currentSelection.setBounds(
                bounds=(penpoints['time'][0], penpoints['time'][-1]))
            self.addItem(self.currentSelection)
            self.sigRegionChangedProxy = pg.SignalProxy(
                self.currentSelection.sigRegionChanged, rateLimit=30,
                slot=self.handlePenDataSelectionChanged)

        else:
            # Update DataItem objects
            pen = pg.mkPen(SETTINGS['timeplot_xtrace_color'],
                           width=SETTINGS['timeplot_xtrace_size'])
            pen2 = pg.mkPen(SETTINGS['timeplot_xtrace_color'].darker(),
                            width=SETTINGS['timeplot_xtrace_size'])
            penarray = np.empty(penpoints.shape[0], dtype=object)
            penarray[:] = pen
            penarray[penpoints['pressure'] == 0] = pen2

            brush = pg.mkBrush(SETTINGS['timeplot_xtrace_color'])
            brush2 = pg.mkBrush(SETTINGS['timeplot_xtrace_color'].darker())
            brusharray = np.empty(penpoints.shape[0], dtype=object)
            brusharray[:] = brush
            brusharray[penpoints['pressure'] == 0] = brush2

            self.xPenPosTrace.setData(x=penpoints['time'], y=penpoints['x'],
                                      symbolPen=penarray,
                                      symbolBrush=brusharray)

            pen = pg.mkPen(SETTINGS['timeplot_ytrace_color'],
                           width=SETTINGS['timeplot_ytrace_size'])
            pen2 = pg.mkPen(SETTINGS['timeplot_ytrace_color'].darker(),
                            width=SETTINGS['timeplot_ytrace_size'])
            penarray[:] = pen
            penarray[penpoints['pressure'] == 0] = pen2

            brush = pg.mkBrush(SETTINGS['timeplot_ytrace_color'])
            brush2 = pg.mkBrush(SETTINGS['timeplot_ytrace_color'].darker())
            brusharray[:] = brush
            brusharray[penpoints['pressure'] == 0] = brush2

            self.yPenPosTrace.setData(x=penpoints['time'], y=penpoints['y'],
                                      symbolPen=penarray,
                                      symbolBrush=brusharray)
            self.currentSelection.setRegion(
                [penpoints['time'][0], penpoints['time'][0] + 1.0])
            self.currentSelection.setBounds(
                bounds=(penpoints['time'][0], penpoints['time'][-1]))

        self.setRange(xRange=(penpoints['time'][0], penpoints['time'][-1]),
                      padding=None)
        self.handlePenDataSelectionChanged()

    def handlePenDataSelectionChanged(self):
        self.currentSelection.setZValue(10)
        minT, maxT = self.currentSelection.getRegion()
        #print '>> Timeline.handlePenDataSelectionChanged:',( minT, maxT)
        selectedpendata = MarkWriteMainWindow.instance().project.updateSelectedData(
            minT, maxT)
        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.emit((minT, maxT),
                                                             selectedpendata)
        self.ensureSelectionIsVisible([minT, maxT], selectedpendata)
        #print '<< Timeline.handlePenDataSelectionChanged'

    def zoomToPenData(self, pendata, lock_bounds=False):
        if len(pendata) > 0:
            penValRange = (
            min(pendata['x'].min() - 20, pendata['y'].min() - 20, 0),
            max(pendata['x'].max() + 20, pendata['y'].max() + 20))
            #if lock_bounds:
            #    self.setLimits(xMin=pendata['time'][0], xMax=pendata[
            # 'time'][-1]+0.01)
            self.setRange(xRange=(pendata['time'][0], pendata['time'][-1]),
                          yRange=penValRange, padding=None)

    def ensureSelectionIsVisible(self, timespan, pendata):
        if len(pendata) > 0:
            dxmin, dxmax = timespan
            dxlength = dxmax - dxmin
            (vxmin, vxmax), (vymin, vymax) = self.viewRange()
            vxlength = vxmax - vxmin
            vxborder = (vxlength - dxlength) / 2.0
            dymin, dymax = (
            min(pendata['x'].min() - 20, pendata['y'].min() - 20, vymin),
            max(pendata['x'].max() + 20, pendata['y'].max() + 20, vymax))

            if dxlength > vxlength:
                ##print "dlength > vlength:",dlength, vlength
                self.setRange(xRange=(dxmin, dxmax), yRange=(dymin, dymax),
                              padding=None)
                return

            if dxmin < vxmin:
                self.setRange(xRange=(dxmin, dxmin + vxlength),
                              yRange=(dymin, dymax), padding=0)
                ##print 'dmin < vmin:',dmin,dmin+vlength,self.viewRange()[0]
                return

            if dxmax > vxmax:
                self.setRange(xRange=(dxmax - vxlength, dxmax),
                              yRange=(dymin, dymax), padding=0)
                ##print 'dmax > vmax:',dmax-vlength,dmax,self.viewRange()[0]
                return