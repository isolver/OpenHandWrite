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

class PenDataTemporalPlotWidget(pg.GraphicsLayoutWidget):
    displayVelocityTrace = True
    displayStrokePoints = True

    def addSubPlot(self,name, row, **kwargs):
        if name in self.dataplots.keys():
            return None
        self.dataplots[name] = self.addPlot(name=name, row=row, col=0)
        for k,v in kwargs.items():
            a = getattr(self.dataplots[name], k, None)#, v)
            if a is None:
                a = getattr(self.dataplots[name].getViewBox(), k, None)

            if a and callable(a):
                if isinstance(v, dict):
                    a(**v)
                else:
                    a(v)
            else:
                setattr(a, k, v)

        # Add an attribute to the class that allows access to the
        # newly added plot item.

        setattr(self, name, self.dataplots[name])
        return self.dataplots[name]

    def addPlotLineItem(self,plot_name, item_name, **kwargs):
        plot = self.dataplots.get(plot_name,None)
        if plot:
            aplotsitems = self.plotitems.setdefault(plot_name,{})
            plotitem = aplotsitems.get(item_name)
            if plotitem is None:
                aplotsitems[item_name]=plot.plot(**kwargs)
                return True
            else:
                plotitem.setData(**kwargs)
                return False

    def __init__(self):
        pg.GraphicsLayoutWidget.__init__(self)
        # Create Pen Position Time Series Plot for All Data

        self.dataplots=dict()
        self.plotitems=dict()

        ylabel = dict(axis='left', text="Position")
        mouseenabled = {'y':SETTINGS['timeplot_enable_ymouse']}
        last_plot = self.addSubPlot("xy_plot", 0, setMenuEnabled=False,
                        setMouseEnabled=mouseenabled, hideAxis='bottom',
                        setLabel=ylabel)
        self.nextRow()
        last_plot = self.createVelocityPlot(mouseenabled)
        self.nextRow()
        self.createAccelerationPlot(mouseenabled)

        self.bottom_plot.setLabel('bottom', text="Time", units='sec')

        self.currentSelection = None
        self.fullPenValRange=[0,1]
        self.maxTime=1
        self.sigRegionChangedProxy = None

        self._lastselectedtimerange = None
        self._level1Segment = None

        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)
        MarkWriteMainWindow.instance().sigActiveObjectChanged.connect(
            self.handleSelectedObjectChanged)

    @property
    def bottom_plot(self):
        if hasattr(self,'acceleration_plot'):
            return self.acceleration_plot
        if hasattr(self,'velocity_plot'):
            return self.velocity_plot
        return self.xy_plot

    def createVelocityPlot(self, mouseenabled):
        if SETTINGS['display_timeplot_vtrace']:
            ylabel = dict(axis='left', text="Velocity")
            return self.addSubPlot("velocity_plot", 1, setMenuEnabled=False, setXLink="xy_plot",
                            setMouseEnabled=mouseenabled, hideAxis='bottom',
                            setLabel=ylabel)

    def createAccelerationPlot(self, mouseenabled):
        if SETTINGS['display_timeplot_atrace']:
            ylabel = dict(axis='left', text="Acceleration")
            return self.addSubPlot("acceleration_plot", 2, setMenuEnabled=False, setXLink="xy_plot",
                            setMouseEnabled=mouseenabled, setLabel=ylabel)

    def removeVelocityPlot(self):
        if not SETTINGS['display_timeplot_vtrace']:
            delattr(self,'velocity_plot')
            self.removeItem(self.dataplots['velocity_plot'])
            if self.plotitems.get('velocity_plot'):
                del self.plotitems['velocity_plot']
            if self.dataplots.get('velocity_plot'):
                del self.dataplots['velocity_plot']

    def removeAccelerationPlot(self):
        if not SETTINGS['display_timeplot_atrace']:
            delattr(self,'acceleration_plot')
            self.removeItem(self.dataplots['acceleration_plot'])
            if self.plotitems.get('acceleration_plot'):
                del self.plotitems['acceleration_plot']
            if self.dataplots.get('acceleration_plot'):
                del self.dataplots['acceleration_plot']

    def handleSelectedObjectChanged(self, newobj, oldobj):
        if MarkWriteMainWindow.instance().project.autosegl1 is True:
            if isinstance(newobj, PenDataSegment):
                    l1seg=newobj.l1seg
                    if l1seg and l1seg != self._level1Segment:
                            self._level1Segment=l1seg
                            self.handleResetPenData(None)
        else:
            self._level1Segment = None

    def getCurrentPenData(self):
        if self._level1Segment:
            return self._level1Segment.pendata
        return MarkWriteMainWindow.instance().project.pendata

    def getPenBrush(self, colorkey, sizekey, penpoints,
                    penarray=None, brusharray=None):
        if penarray is None:
            penarray = np.empty(penpoints.shape[0], dtype=object)
            brusharray = np.empty(penpoints.shape[0], dtype=object)

        pen = pg.mkPen(SETTINGS[colorkey],
                       width=SETTINGS[sizekey])
        pen2 = pg.mkPen(SETTINGS[colorkey].darker(300),
                        width=SETTINGS[sizekey])
        penarray[:] = pen
        penarray[penpoints['pressure'] == 0] = pen2
        brush = pg.mkBrush(SETTINGS[colorkey])
        brush2 = pg.mkBrush(SETTINGS[colorkey].darker(300))
        brusharray[:] = brush
        brusharray[penpoints['pressure'] == 0] = brush2

        return penarray, brusharray


    def updateTrace(self, plotname, axisname, colorkey, sizekey, penpoints, penarray, brusharray):
        penarray, brusharray = self.getPenBrush(colorkey,sizekey, penpoints, penarray,
                                                 brusharray)
        self.addPlotLineItem(plotname, axisname, x=penpoints['time'], y=penpoints[axisname],
                                  symbolPen=penarray,
                                  symbolBrush=brusharray,
                                    pen=None, symbol='o',
                                    symbolSize=SETTINGS[sizekey])
        return penarray, brusharray

    def addStrokeBoundaryPoints(self, strokeboundries):
        ssize = SETTINGS['pen_stroke_boundary_size']
        bpoints = self.plotitems['xy_plot'].get('boundary_points')
        if ssize == 0:
            if bpoints:
                bpoints.clear()
            return
        scolor = SETTINGS['pen_stroke_boundary_color']
        pen = pg.mkPen(scolor, width=ssize)
        brush = pg.mkBrush(scolor)
        if bpoints is None:
            bpoints = self.plotitems['xy_plot']['boundary_points'] = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
            self.xy_plot.addItem(bpoints)
        else:
            bpoints.clear()
        bpoints.addPoints(x=strokeboundries['time'],
                                             y=strokeboundries[X_FIELD],
                                             size=ssize, pen=pen, brush=brush)
        bpoints.addPoints(x=strokeboundries['time'],
                                             y=strokeboundries[Y_FIELD],
                                             size=ssize, pen=pen, brush=brush
                                            )


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
        self.xy_plot.setLimits(yMin=self.fullPenValRange[0], yMax=self.fullPenValRange[1],
                                     xMin=penpoints['time'][0],
                                     xMax=penpoints['time'][-1])

        penarray, brusharray = None, None

        # Create DataItem objects
        penarray, brusharray = self.getPenBrush('timeplot_xtrace_color', 'timeplot_xtrace_size',penpoints, penarray,
                                                 brusharray)

        self.addPlotLineItem('xy_plot','x',x=penpoints['time'],
                                    y=penpoints[X_FIELD],
                                    symbolPen=penarray,
                                    symbolBrush=brusharray,
                                    pen=None, symbol='o',
                                    symbolSize=SETTINGS['timeplot_xtrace_size'])

        penarray, brusharray = self.getPenBrush('timeplot_ytrace_color', 'timeplot_ytrace_size',penpoints, penarray,
                                                 brusharray)

        added = self.addPlotLineItem('xy_plot','y',x=penpoints['time'],
                                        y=penpoints[Y_FIELD],
                                        pen=None, symbol='o',
                                        symbolSize=SETTINGS[
                                            'timeplot_ytrace_size'],
                                        symbolPen=penarray,
                                        symbolBrush=brusharray)

        if hasattr(self, 'velocity_plot'):
            penarray, brusharray = self.getPenBrush('timeplot_vtrace_color', 'timeplot_vtrace_size',penpoints, penarray,
                                                     brusharray)

            added = self.addPlotLineItem('velocity_plot','xy_velocity',x=penpoints['time'],
                                            y=penpoints['xy_velocity'],
                                            pen=None, symbol='o',
                                            symbolSize=SETTINGS[
                                                'timeplot_vtrace_size'],
                                            symbolPen=penarray,
                                            symbolBrush=brusharray)

        if hasattr(self, 'acceleration_plot'):
            penarray, brusharray = self.getPenBrush('timeplot_atrace_color', 'timeplot_atrace_size',penpoints, penarray,
                                                     brusharray)

            added = self.addPlotLineItem('acceleration_plot','xy_acceleration',x=penpoints['time'],
                                            y=penpoints['xy_acceleration'],
                                            pen=None, symbol='o',
                                            symbolSize=SETTINGS[
                                                'timeplot_atrace_size'],
                                            symbolPen=penarray,
                                            symbolBrush=brusharray)

        if added:
            # Add a Selection Region that is used to create segments by user
            # The project class now creates the selection region item widget
            self.currentSelection = project.selectedtimeregion

            self.xy_plot.addItem(self.currentSelection)
            self.sigRegionChangedProxy = pg.SignalProxy(
                self.currentSelection.sigRegionChanged, rateLimit=30,
                slot=self.handlePenDataSelectionChanged)

        else:
            self.xy_plot.getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
            # Update DataItem objects
            penarray, brusharray = self.updateTrace('xy_plot','x','timeplot_xtrace_color', 'timeplot_xtrace_size', penpoints, penarray, brusharray)
            penarray, brusharray = self.updateTrace('xy_plot','y','timeplot_ytrace_color', 'timeplot_ytrace_size',penpoints, penarray, brusharray)
            if hasattr(self, 'velocity_plot'):
                penarray, brusharray = self.updateTrace('velocity_plot','xy_velocity','timeplot_vtrace_color', 'timeplot_vtrace_size',penpoints, penarray, brusharray)
            if hasattr(self, 'acceleration_plot'):
                penarray, brusharray = self.updateTrace('acceleration_plot','xy_acceleration','timeplot_atrace_color', 'timeplot_atrace_size',penpoints, penarray, brusharray)

        proj = MarkWriteMainWindow.instance().project
        pstart, pend = penpoints['time'][[0,-1]]
        vms_times = proj.velocity_minima_samples['time']
        vms_mask = (vms_times >= pstart) & (vms_times <= pend)
        self.addStrokeBoundaryPoints(proj.velocity_minima_samples[vms_mask])

        self.xy_plot.setRange(xRange=(penpoints['time'][0], penpoints['time'][-1]),
                      yRange=self.fullPenValRange,
                      padding=None)
        self.handlePenDataSelectionChanged()


    def handleUpdatedSettingsEvent(self, updates, settings):
        penarray, brusharray = None, None
        penpoints = self.getCurrentPenData()

        for k in updates.keys():
            if k.startswith('timeplot_xtrace'):
                penarray, brusharray = self.updateTrace('xy_plot', 'x', 'timeplot_xtrace_color', 'timeplot_xtrace_size', penpoints, penarray, brusharray)
            break

        for k in updates.keys():
            if k.startswith('timeplot_ytrace'):
                self.updateTrace('xy_plot', 'y', 'timeplot_ytrace_color', 'timeplot_ytrace_size', penpoints, penarray, brusharray)
                break

        prev_bottom_plot = self.bottom_plot

        if 'display_timeplot_atrace' in updates.keys():
            plot_currently_displayed = hasattr(self,'acceleration_plot') and self.acceleration_plot is not None
            if plot_currently_displayed and updates['display_timeplot_atrace'] is False:
                self.removeAccelerationPlot()
            elif not plot_currently_displayed and updates['display_timeplot_atrace'] is True:
                self.createAccelerationPlot(SETTINGS['timeplot_enable_ymouse'])
                penarray, brusharray = self.updateTrace('acceleration_plot', 'xy_acceleration', 'timeplot_atrace_color', 'timeplot_atrace_size', penpoints, penarray, brusharray)
        else:
            if hasattr(self,'acceleration_plot'):
                for k in updates.keys():
                    if k.startswith('timeplot_atrace'):
                        penarray, brusharray = self.updateTrace('acceleration_plot', 'xy_acceleration', 'timeplot_atrace_color', 'timeplot_atrace_size', penpoints, penarray, brusharray)
                    break

        if 'display_timeplot_vtrace' in updates.keys():
            plot_currently_displayed = hasattr(self,'velocity_plot') and self.velocity_plot is not None
            if plot_currently_displayed and updates['display_timeplot_vtrace'] is False:
                self.removeVelocityPlot()
            elif not plot_currently_displayed and updates['display_timeplot_vtrace'] is True:
                self.createVelocityPlot(SETTINGS['timeplot_enable_ymouse'])
                penarray, brusharray = self.updateTrace('velocity_plot', 'xy_velocity', 'timeplot_vtrace_color', 'timeplot_vtrace_size', penpoints, penarray, brusharray)
        else:
            if hasattr(self,'velocity_plot'):
                for k in updates.keys():
                    if k.startswith('timeplot_vtrace'):
                        penarray, brusharray = self.updateTrace('velocity_plot', 'xy_velocity', 'timeplot_vtrace_color', 'timeplot_vtrace_size', penpoints, penarray, brusharray)
                    break

        if self.bottom_plot != prev_bottom_plot:
            prev_bottom_plot.hideAxis('bottom')
        self.bottom_plot.setLabel('bottom', text="Time", units='sec')

        for k in updates.keys():
            if k.startswith('pen_stroke_boundary'):
                proj = MarkWriteMainWindow.instance().project
                pstart, pend = penpoints['time'][[0,-1]]
                vms_times = proj.velocity_minima_samples['time']
                vms_mask = (vms_times >= pstart) & (vms_times <= pend)
                self.addStrokeBoundaryPoints(proj.velocity_minima_samples[vms_mask])

        self.xy_plot.getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
        if SETTINGS['timeplot_enable_ymouse'] is False:
            self.xy_plot.setRange(yRange=self.fullPenValRange)

    def handlePenDataSelectionChanged(self):
        self.currentSelection.setZValue(10)
        minT, maxT , selectedpendata= self.currentSelection.selectedtimerangeanddata
        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.emit((minT, maxT),
                                                                     selectedpendata)
        self.ensureSelectionIsVisible([minT, maxT], selectedpendata)

    def scaleBy(self, x=None,y=None):
        for pi in self.dataplots.values():
            pi.getViewBox().scaleBy(x=x)

    def setPlotRange(self, xrange=None, yrange=None):
        for pi in self.dataplots.values():
            pi.setRange(xRange=xrange, yRange=yrange)

    def getViewRange(self):
        return self.xy_plot.getViewBox().viewRange()

    def translateViewBy(self, x=None):
        for pi in self.dataplots.values():
            pi.getViewBox().translateBy(x=x)

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
            self.xy_plot.setRange(xRange=(pendata['time'][0], pendata['time'][-1]),
                          yRange=penValRange, padding=None)


    def ensureSelectionIsVisible(self, timespan, pendata):
        if len(pendata) > 0:
            dxmin, dxmax = timespan
            dxlength = dxmax - dxmin
            (vxmin, vxmax), (vymin, vymax) = self.xy_plot.viewRange()
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
                kwargs['xRange']=(dxmin, dxmax)
                self.xy_plot.setRange(**kwargs)
                return

            if dxmin < vxmin:
                kwargs['xRange']=(dxmin, dxmin + vxlength)
                kwargs['padding']=0
                self.xy_plot.setRange(**kwargs)
                return

            if dxmax > vxmax:
                kwargs['xRange']=(dxmax - vxlength, dxmax)
                kwargs['padding']=0
                self.xy_plot.setRange(**kwargs)
                return