import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from weakref import proxy,ProxyType
from markwrite.gui.projectsettings import SETTINGS
from markwrite.gui.mainwin import MarkWriteMainWindow

__author__ = 'Sol'




class PenDataTemporalPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)
        # Create Pen Position Time Series Plot for All Data

        self.getPlotItem().setLabel('left', "Pen Position", units='pix')
        self.getPlotItem().setLabel('bottom', "Time", units='sec')
        self.getPlotItem().getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
        self.xPenPosTrace = None
        self.yPenPosTrace = None
        self.currentSelection = None
        self.fullPenValRange=[0,1]
        self.maxTime=1
        self._lastselectedtimerange = None
        self.sigRegionChangedProxy = None
        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)

    def getPenBrushX(self, penpoints, penarray=None, brusharray=None):
        if penarray is None:
            penarray = np.empty(penpoints.shape[0], dtype=object)
            brusharray = np.empty(penpoints.shape[0], dtype=object)

        pen = pg.mkPen(SETTINGS['timeplot_xtrace_color'],
                       width=SETTINGS['timeplot_xtrace_size'])
        pen2 = pg.mkPen(SETTINGS['timeplot_xtrace_color'].darker(),
                        width=SETTINGS['timeplot_xtrace_size'])
        penarray[:] = pen
        penarray[penpoints['pressure'] == 0] = pen2

        brush = pg.mkBrush(SETTINGS['timeplot_xtrace_color'])
        brush2 = pg.mkBrush(SETTINGS['timeplot_xtrace_color'].darker())
        brusharray[:] = brush
        brusharray[penpoints['pressure'] == 0] = brush2

        return penarray, brusharray

    def updateTraceX(self, penpoints, penarray, brusharray):
        penarray, brusharray = self.getPenBrushX(penpoints, penarray,
                                                 brusharray)
        self.xPenPosTrace.setData(x=penpoints['time'], y=penpoints['x'],
                                  symbolPen=penarray,
                                  symbolBrush=brusharray)
        return penarray, brusharray

    def getPenBrushY(self, penpoints, penarray=None, brusharray=None):
        if penarray is None:
            penarray = np.empty(penpoints.shape[0], dtype=object)
            brusharray = np.empty(penpoints.shape[0], dtype=object)

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

        return penarray, brusharray

    def updateTraceY(self, penpoints, penarray, brusharray):
        penarray, brusharray = self.getPenBrushY(penpoints, penarray,
                                                 brusharray)
        self.xPenPosTrace.setData(x=penpoints['time'], y=penpoints['y'],
                                  symbolPen=penarray,
                                  symbolBrush=brusharray)
        return penarray, brusharray

    def handleResetPenData(self, project):
        '''

        :param self:
        :param project:
        :return:
        '''
        penpoints = project.pendata
        self.fullPenValRange = (min(penpoints['x'].min(), penpoints['y'].min()),
                       max(penpoints['x'].max(), penpoints['y'].max()))
        self.maxTime=penpoints['time'][-1]
        self.getPlotItem().setLimits(yMin=self.fullPenValRange[0], yMax=self.fullPenValRange[1],
                                     xMin=penpoints['time'][0],
                                     xMax=penpoints['time'][-1])

        penarray, brusharray = None, None

        if self.xPenPosTrace is None:
            # Create DataItem objects
            penarray, brusharray = self.getPenBrushX(penpoints, penarray,
                                                     brusharray)
            self.xPenPosTrace = self.getPlotItem().plot(x=penpoints['time'],
                                                        y=penpoints['x'],
                                                        pen=None, symbol='o',
                                                        symbolSize=SETTINGS[
                                                            'timeplot_xtrace_size'],
                                                        symbolPen=penarray,
                                                        symbolBrush=brusharray,
                                                        name="X Position")

            penarray, brusharray = self.getPenBrushY(penpoints, penarray,
                                                     brusharray)
            self.yPenPosTrace = self.getPlotItem().plot(x=penpoints['time'],
                                                        y=penpoints['y'],
                                                        pen=None, symbol='o',
                                                        symbolSize=SETTINGS[
                                                            'timeplot_ytrace_size'],
                                                        symbolPen=penarray,
                                                        symbolBrush=brusharray,
                                                        name="Y Position")

            # Add a Selection Region that is used to create segments by user
            # The project class now creates the selection region item widget
            self.currentSelection = project.selectedtimeregion

            self.addItem(self.currentSelection)
            self.sigRegionChangedProxy = pg.SignalProxy(
                self.currentSelection.sigRegionChanged, rateLimit=30,
                slot=self.handlePenDataSelectionChanged)

        else:
            # Update DataItem objects
            penarray, brusharray = self.updateTraceX(penpoints, penarray, brusharray)
            self.updateTraceY(penpoints, penarray, brusharray)

        self.setRange(xRange=(penpoints['time'][0], penpoints['time'][-1]),
                      padding=None)
        self.handlePenDataSelectionChanged()


    def handleUpdatedSettingsEvent(self, updates, settings):
        penarray, brusharray = None, None
        penpoints = MarkWriteMainWindow.instance().project.pendata
        for k in updates.keys():
            if k.startswith('timeplot_xtrace'):
                penarray, brusharray = self.updateTraceX(penpoints, penarray, brusharray)
            break

        for k in updates.keys():
            if k.startswith('timeplot_ytrace'):
                self.updateTraceY(penpoints, penarray, brusharray)
                break

        self.getPlotItem().getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
        if SETTINGS['timeplot_enable_ymouse'] is False:
            self.setRange(yRange=self.fullPenValRange)

    def handlePenDataSelectionChanged(self):
        self.currentSelection.setZValue(10)
        minT, maxT , selectedpendata= self.currentSelection.selectedtimerangeanddata
        # print '>> Timeline.handlePenDataSelectionChanged:',( minT, maxT)

        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.emit((minT, maxT),
                                                                     selectedpendata)

        self.ensureSelectionIsVisible([minT, maxT], selectedpendata)
        #print '<< Timeline.handlePenDataSelectionChanged'


    def zoomToPenData(self, pendata, lock_bounds=False):
        if len(pendata) > 0:
            if SETTINGS['timeplot_enable_ymouse']:
                penValRange = (min(pendata['x'].min() - 20, pendata['y'].min() - 20, 0),
                    max(pendata['x'].max() + 20, pendata['y'].max() + 20))
            else:
                penValRange = self.fullPenValRange
            # if lock_bounds:
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

            kwargs={}
            if SETTINGS['timeplot_enable_ymouse']:
                kwargs['yRange'] = (
                    min(pendata['x'].min() - 20, pendata['y'].min() - 20, vymin),
                    max(pendata['x'].max() + 20, pendata['y'].max() + 20, vymax))
            else:
                kwargs['yRange'] = self.fullPenValRange

            if dxlength > vxlength:
                # #print "dlength > vlength:",dlength, vlength
                kwargs['xRange']=(dxmin, dxmax)
                self.setRange(**kwargs)
                return

            if dxmin < vxmin:
                kwargs['xRange']=(dxmin, dxmin + vxlength)
                kwargs['padding']=0
                self.setRange(**kwargs)
                # #print 'dmin < vmin:',dmin,dmin+vlength,self.viewRange()[0]
                return

            if dxmax > vxmax:
                kwargs['xRange']=(dxmax - vxlength, dxmax)
                kwargs['padding']=0
                self.setRange(**kwargs)
                # #print 'dmax > vmax:',dmax-vlength,dmax,self.viewRange()[0]
                return