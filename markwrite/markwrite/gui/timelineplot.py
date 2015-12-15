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

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from weakref import proxy,ProxyType
from markwrite.gui import X_FIELD, Y_FIELD
from markwrite.gui.projectsettings import SETTINGS
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.segment import PenDataSegment

class PenDataTemporalPlotWidget(pg.PlotWidget):
    displayVelocityTrace = True
    displayStrokePoints = True
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)
        # Create Pen Position Time Series Plot for All Data

        self.getPlotItem().setLabel('left', "Pen Position", units='raw')
        self.getPlotItem().setLabel('bottom', "Time", units='sec')
        self.getPlotItem().getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])

#       self.velocityPlot = None
#        self.velocityTrace = None
#        self.velocityPlot = pg.ViewBox()
#        self.getPlotItem().showAxis('right')
#        self.getPlotItem().scene().addItem(self.velocityPlot)
#        self.getPlotItem().getAxis('right').linkToView(self.velocityPlot)
#        self.velocityPlot.setXLink(self.getPlotItem())
#        self.getPlotItem().getAxis('right').setLabel('Absolute Velocity', color='#0000ff')

#        self.updateTwoAxisViews()
#        self.getPlotItem().vb.sigResized.connect(self.updateTwoAxisViews)

#        ssize = SETTINGS['timeplot_xtrace_size']
#        self.velocityTrace = pg.PlotCurveItem(
#                                symbolPen=pg.mkPen([255,255,255],width=ssize),
#                                symbolBrush=pg.mkBrush([255,255,255]),
#                                pen=None, symbol='-',
#                                symbolSize=ssize,
#                                name="Absolute Velocity")
#        self.velocityPlot.addItem(self.velocityTrace)

        self.xPenPosTrace = None
        self.yPenPosTrace = None

        self.strokeBoundaryPoints = None
        self.currentSelection = None
        self.fullPenValRange=[0,1]
        self.maxTime=1
        self._lastselectedtimerange = None
        self.sigRegionChangedProxy = None
        self._level1Segment = None
        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)
        MarkWriteMainWindow.instance().sigActiveObjectChanged.connect(
            self.handleSelectedObjectChanged)

#    ## Handle view resizing
#    def updateTwoAxisViews(self):
#        ## view has resized; update auxiliary views to match
#        self.velocityPlot.setGeometry(self.getPlotItem().vb.sceneBoundingRect())

        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
#        self.velocityPlot.linkedViewChanged(self.getPlotItem().vb, self.velocityPlot.XAxis)

    def handleSelectedObjectChanged(self, newobj, oldobj):
        if MarkWriteMainWindow.instance().project._autosegl1 is True:
            if isinstance(newobj, PenDataSegment):
                    l1seg=newobj.l1seg
                    if l1seg and l1seg != self._level1Segment:
                            #print ">> *** PenDataTemporalPlotWidget.handleSelectedObjectChanged:",l1seg

                            self._level1Segment=l1seg
                            self.handleResetPenData(None)
                            #print "<< *** PenDataTemporalPlotWidget.handleSelectedObjectChanged"
        else:
            self._level1Segment = None

    def getCurrentPenData(self):
        if self._level1Segment:
            return self._level1Segment.pendata
        return MarkWriteMainWindow.instance().project.pendata

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
        self.xPenPosTrace.setData(x=penpoints['time'], y=penpoints[X_FIELD],
                                  symbolPen=penarray,
                                  symbolBrush=brusharray,
                                  pen=None, symbol='o',
                                    symbolSize=SETTINGS[
                                        'timeplot_xtrace_size'])
        return penarray, brusharray

    def addStrokeBoundaryPoints(self, strokeboundries):
        if self.strokeBoundaryPoints is None:
            ssize = SETTINGS['timeplot_xtrace_size']*2
            pen = pg.mkPen([255, 0, 255],
                           width=ssize)
            brush = pg.mkBrush([255, 0, 255])
            self.strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
            self.getPlotItem().addItem(self.strokeBoundaryPoints)
        else:
            self.strokeBoundaryPoints.clear()
        self.strokeBoundaryPoints.addPoints(x=strokeboundries['time'],
                                             y=strokeboundries[X_FIELD])
        self.strokeBoundaryPoints.addPoints(x=strokeboundries['time'],
                                             y=strokeboundries[Y_FIELD],
                                            )

#    def updateVelocityTrace(self, penpoints):
#        if self.displayVelocityTrace:
#            print "updateVelocityTrace called:",penpoints.shape,penpoints['time'].min(),penpoints['time'].max(),penpoints['xy_velocity'].min(),penpoints['xy_velocity'].max()
#            self.velocityTrace.setData(x=penpoints['time'],
#                                           y=penpoints['xy_velocity'],
#                                           )
#        elif self.velocityTrace is not None:
#            print"TODO: Remove Velocity trace from plot."

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
        self.yPenPosTrace.setData(x=penpoints['time'], y=penpoints[Y_FIELD],
                                  symbolPen=penarray,
                                  symbolBrush=brusharray,
                                    pen=None, symbol='o',
                                    symbolSize=SETTINGS[
                                        'timeplot_ytrace_size'],
                                    name="Y Position")
        return penarray, brusharray

    def handleResetPenData(self, project):
        '''

        :param self:
        :param project:
        :return:
        '''
        #penpoints = project.pendata
        penpoints = self.getCurrentPenData()

        self.fullPenValRange = (min(penpoints[X_FIELD].min(), penpoints[Y_FIELD].min()),
                       max(penpoints[X_FIELD].max(), penpoints[Y_FIELD].max()))
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
                                                        y=penpoints[X_FIELD],
                                                        pen=None, symbol='o',
                                                        symbolSize=SETTINGS[
                                                            'timeplot_xtrace_size'],
                                                        symbolPen=penarray,
                                                        symbolBrush=brusharray,
                                                        name="X Position")

            penarray, brusharray = self.getPenBrushY(penpoints, penarray,
                                                     brusharray)
            self.yPenPosTrace = self.getPlotItem().plot(x=penpoints['time'],
                                                        y=penpoints[Y_FIELD],
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
            self.getPlotItem().getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
            # Update DataItem objects
            penarray, brusharray = self.updateTraceX(penpoints, penarray, brusharray)
            self.updateTraceY(penpoints, penarray, brusharray)

        proj = MarkWriteMainWindow.instance().project
        pstart, pend = penpoints['time'][[0,-1]]
        vms_times = proj.velocity_minima_samples['time']
        vms_mask = (vms_times >= pstart) & (vms_times <= pend)
        self.addStrokeBoundaryPoints(proj.velocity_minima_samples[vms_mask])

#        self.updateVelocityTrace(penpoints)

        self.setRange(xRange=(penpoints['time'][0], penpoints['time'][-1]),
                      yRange=self.fullPenValRange,
                      padding=None)
        self.handlePenDataSelectionChanged()


    def handleUpdatedSettingsEvent(self, updates, settings):
        penarray, brusharray = None, None
        #penpoints = MarkWriteMainWindow.instance().project.pendata
        penpoints = self.getCurrentPenData()

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
                penValRange = (min(pendata[X_FIELD].min() - 20, pendata[Y_FIELD].min() - 20, 0),
                    max(pendata[X_FIELD].max() + 20, pendata[Y_FIELD].max() + 20))
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
                    min(pendata[X_FIELD].min() - 20, pendata[Y_FIELD].min() - 20, vymin),
                    max(pendata[X_FIELD].max() + 20, pendata[Y_FIELD].max() + 20, vymax))
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