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
import pyqtgraph.exporters
from pyqtgraph.Qt import QtGui, QtCore
from weakref import proxy,ProxyType
from markwrite.gui import X_FIELD, Y_FIELD
from markwrite.gui.projectsettings import SETTINGS
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.segment import PenDataSegment
from markwrite.gui.dialogs import fileSaveDlg

class PenDataTemporalPlotWidget(pg.GraphicsLayoutWidget):
    displayVelocityTrace = True
    displayStrokePoints = True
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

        self._lastselectedtimerange = None
        self._level1Segment = None

        self._enablePopupDisplay = True
        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)
        MarkWriteMainWindow.instance().sigActiveObjectChanged.connect(
            self.handleSelectedObjectChanged)

    def mouseDoubleClickEvent(self, event):
        """
        On double click, find closest pen sample to mouse pos and select 
        the sample's segment (if it has been assigned to one). 
        """
        if MarkWriteMainWindow.instance().project:
            pdat = self.getCurrentPenData()
            if len(pdat):
                streg = MarkWriteMainWindow.instance().project.selectedtimeregion
                if streg:
                    xmin, xmax = streg.getRegion()
                    data_pos = self.dataplots['xy_plot'].vb.mapSceneToView(event.pos())        
                    x = data_pos.x()
                    if x < xmin or x > xmax:
                        ptime_ix = len(pdat['time'][pdat['time']<=x])
                        if ptime_ix > 0:
                            seg_id = pdat[ptime_ix]['segment_id']
                            if seg_id > 0:
                                seg = PenDataSegment.id2obj[seg_id]    
                                if seg.l1seg==seg:
                                    # Do not select segment if it is an L1
                                    pass
                                else:
                                    MarkWriteMainWindow.instance().setActiveObject(seg)
                                
                        streg._ignore_events=True
                        super(PenDataTemporalPlotWidget,self).mouseDoubleClickEvent(event)
                        streg._ignore_events=False                       
                    else:
                        super(PenDataTemporalPlotWidget,self).mouseDoubleClickEvent(event)
                        

    def mouseMoveEvent(self, event):
        super(PenDataTemporalPlotWidget,self).mouseMoveEvent(event)
        if (self._enablePopupDisplay is True and event.buttons() and not 
                (event.buttons()&QtCore.Qt.LeftButton==QtCore.Qt.LeftButton)):
            self._enablePopupDisplay = False
        elif not event.buttons():
            self._enablePopupDisplay = True
            
    def contextMenuEvent(self, event):
        if self._enablePopupDisplay:
            menu = QtGui.QMenu(self)
            quitAction = menu.addAction("Save as Image")
            action = menu.exec_(self.mapToGlobal(event.pos()))
            if action == quitAction:
                exporter = pg.exporters.ImageExporter(self.ci)
                apath = fileSaveDlg(initFileName="timeline_view.png",
                            prompt=u"Save Timeline View as Image",
                            allowed="*.png")
                if apath:
                    exporter.export(apath)
        self._enablePopupDisplay=True
        
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
                if self.plotitems['velocity_plot'].get('boundary_points'):
                    del self.plotitems['velocity_plot']['boundary_points']   
                del self.plotitems['velocity_plot']
            if self.dataplots.get('velocity_plot'):
                del self.dataplots['velocity_plot']

    def removeAccelerationPlot(self):
        if not SETTINGS['display_timeplot_atrace']:
            delattr(self,'acceleration_plot')
            self.removeItem(self.dataplots['acceleration_plot'])
            if self.plotitems.get('acceleration_plot'):
                if self.plotitems['acceleration_plot'].get('boundary_points'):
                    del self.plotitems['acceleration_plot']['boundary_points']   
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
        try:
            if self._level1Segment:
                return self._level1Segment.pendata
        except:
            pass
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

    def addStrokeBoundaryPoints(self, strokeboundries, time_mask):
        ssize = SETTINGS['pen_stroke_boundary_size']
        scolor = SETTINGS['pen_stroke_boundary_color']        
        mpen = pg.mkPen(scolor, width=ssize)
        mbrush = pg.mkBrush(scolor)
        pcolor = SETTINGS['pen_stroke_pause_boundary_color']
        ppen = pg.mkPen(pcolor, width=ssize)
        pbrush = pg.mkBrush(pcolor)
        display_x = SETTINGS['display_timeplot_xtrace']
        display_y = SETTINGS['display_timeplot_ytrace']
        proj = MarkWriteMainWindow.instance().project
        stroke_type = proj.stroke_boundaries['stroke_type'][time_mask]
        mstroke_mask =  stroke_type==0
        pstroke_mask =  stroke_type==4
           
        def addBoundaryPointsToSubPlot(plot_name, point_fields):
            bpoints = self.plotitems[plot_name].get('boundary_points')
            if ssize == 0:
                if bpoints:
                    bpoints.clear()
                return
            if bpoints is None:
                bpoints = self.plotitems[plot_name]['boundary_points'] = pg.ScatterPlotItem(size=ssize, 
                                                                                            pen=mpen, 
                                                                                            brush=mbrush) 
                if hasattr(self, plot_name):
                    getattr(self, plot_name).addItem(bpoints)
            else:
                bpoints.clear()
            
            for fname in point_fields:             
                bpoints.addPoints(x=strokeboundries['time'][mstroke_mask],
                                                     y=strokeboundries[fname][mstroke_mask],
                                                     size=ssize, pen=mpen, brush=mbrush)
                bpoints.addPoints(x=strokeboundries['time'][pstroke_mask],
                                                     y=strokeboundries[fname][pstroke_mask],
                                                     size=ssize, pen=ppen, brush=pbrush)
        
        
        xy_fields=[]
        if display_x:
          xy_fields.append(X_FIELD)
        if display_y:
          xy_fields.append(Y_FIELD)
          
        addBoundaryPointsToSubPlot('xy_plot',xy_fields)    
        if hasattr(self, 'velocity_plot'):        
            addBoundaryPointsToSubPlot('velocity_plot', ['xy_velocity',])    
        if hasattr(self, 'acceleration_plot'):        
            addBoundaryPointsToSubPlot('acceleration_plot'  , ['xy_acceleration',])    

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
        self.plotitems['xy_plot']['x'].setVisible(SETTINGS['display_timeplot_xtrace'])
        
        penarray, brusharray = self.getPenBrush('timeplot_ytrace_color', 'timeplot_ytrace_size',penpoints, penarray,
                                                 brusharray)

        added = self.addPlotLineItem('xy_plot','y',x=penpoints['time'],
                                        y=penpoints[Y_FIELD],
                                        pen=None, symbol='o',
                                        symbolSize=SETTINGS[
                                            'timeplot_ytrace_size'],
                                        symbolPen=penarray,
                                        symbolBrush=brusharray)
        self.plotitems['xy_plot']['y'].setVisible(SETTINGS['display_timeplot_ytrace'])

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
                
            self.velocity_plot.setLimits(xMin=penpoints['time'][0],
                                     xMax=penpoints['time'][-1])

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

            self.acceleration_plot.setLimits(xMin=penpoints['time'][0],
                                     xMax=penpoints['time'][-1])

        if added:
            # Add a Selection Region that is used to create segments by user
            # The project class now creates the selection region item widget
            self.currentSelection = project.selectedtimeregion

            self.xy_plot.addItem(self.currentSelection)


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
        vms_times = proj.stroke_boundary_samples['time']
        vms_mask = (vms_times >= pstart) & (vms_times <= pend)
        self.addStrokeBoundaryPoints(proj.stroke_boundary_samples[vms_mask], vms_mask)

        self.xy_plot.setRange(xRange=(penpoints['time'][0], penpoints['time'][-1]),
                      yRange=self.fullPenValRange,
                      padding=None)


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

        if 'display_timeplot_xtrace' in updates.keys():
            self.plotitems['xy_plot']['x'].setVisible(SETTINGS['display_timeplot_xtrace'])
        if 'display_timeplot_ytrace' in updates.keys():
            self.plotitems['xy_plot']['y'].setVisible(SETTINGS['display_timeplot_ytrace'])

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
            if k.startswith('pen_stroke_boundary') or k.startswith('display_timeplot_xtrace') or k.startswith('display_timeplot_ytrace'):
                proj = MarkWriteMainWindow.instance().project
                pstart, pend = penpoints['time'][[0,-1]]
                vms_times = proj.stroke_boundary_samples['time']
                vms_mask = (vms_times >= pstart) & (vms_times <= pend)
                self.addStrokeBoundaryPoints(proj.stroke_boundary_samples[vms_mask], vms_mask)
                break
            
        self.xy_plot.getViewBox().setMouseEnabled(y=SETTINGS['timeplot_enable_ymouse'])
        if SETTINGS['timeplot_enable_ymouse'] is False:
            self.xy_plot.setRange(yRange=self.fullPenValRange)

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
                
    def getState(self):
        acceleration_plot_state = None
        velocity_plot_state = None
        if hasattr(self, 'acceleration_plot') and self.acceleration_plot:
            acceleration_plot_state = self.acceleration_plot.getViewBox().getState()
        if hasattr(self, 'velocity_plot') and self.velocity_plot:
            velocity_plot_state = self.velocity_plot.getViewBox().getState()
        return {'xy_plot': self.xy_plot.getViewBox().getState(),
                'acceleration_plot': acceleration_plot_state,
                'velocity_plot': velocity_plot_state
                }
        
    def setState(self, s):
        if s.get('xy_plot'):        
            self.xy_plot.getViewBox().setState(s['xy_plot'])
        if s.get('velocity_plot'):
            self.velocity_plot.getViewBox().setState(s['velocity_plot'])
        if s.get('acceleration_plot'):
            self.acceleration_plot.getViewBox().setState(s['acceleration_plot'])
            