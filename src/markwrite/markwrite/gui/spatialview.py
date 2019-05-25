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
from markwrite.gui.projectsettings import SETTINGS
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.segment import PenDataSegment
from markwrite.gui import X_FIELD, Y_FIELD
from markwrite.gui.dialogs import fileSaveDlg

class PenDataSpatialPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False)
        self._level1Segment=None

        self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])
        self.getPlotItem().setAspectLocked(True, 1)
        self.getPlotItem().setContentsMargins(5, 5, 5, 5)
        self.allPlotDataItem = None
        self.selectedPlotDataItem = None
        self.strokeBoundaryPoints = None

        self._enablePopupDisplay = True
        
        MarkWriteMainWindow.instance().sigResetProjectData.connect(
            self.handleResetPenData)
        MarkWriteMainWindow.instance().sigSegmentRemoved.connect(
            self.handleSegmentRemoved)
        MarkWriteMainWindow.instance().sigSegmentCreated.connect(
            self.handleSegmentCreated)
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
                data_pos = self.getPlotItem().vb.mapSceneToView(event.pos())        
                dx = pdat[X_FIELD]-data_pos.x()
                dy = pdat[Y_FIELD]-data_pos.y()
                dxy = np.sqrt(dx*dx+dy*dy)
                min_ix = dxy.argmin()
                seg_id = pdat[min_ix]['segment_id']
                if seg_id:
                    seg = PenDataSegment.id2obj[seg_id]    
                    MarkWriteMainWindow.instance().setActiveObject(seg)
        super(PenDataSpatialPlotWidget,self).mouseDoubleClickEvent(event)
        
    def mouseMoveEvent(self, event):
        super(PenDataSpatialPlotWidget,self).mouseMoveEvent(event)
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
                exporter = pg.exporters.ImageExporter(self.plotItem)
                apath = fileSaveDlg(initFileName="spatial_view.png",
                            prompt=u"Save Spatial View as Image",
                            allowed="*.png")
                if apath:
                    exporter.export(apath)
        self._enablePopupDisplay = True
                
    def createDefaultPenBrushForData(self, pdat):
        pen = pg.mkPen(SETTINGS['spatialplot_default_color'],
                       width=SETTINGS['spatialplot_default_point_size'])
        pen2 = pg.mkPen(SETTINGS['spatialplot_default_color'].darker(300),
                        width=SETTINGS['spatialplot_default_point_size'])
        brush = pg.mkBrush(SETTINGS['spatialplot_default_color'])
        brush2 = pg.mkBrush(SETTINGS['spatialplot_default_color'].darker(300))
        penarray = np.empty(pdat.shape[0], dtype=object)
        penarray[:] = pen
        penarray[pdat['pressure'] == 0] = pen2
        brusharray = np.empty(pdat.shape[0], dtype=object)
        brusharray[:] = brush
        brusharray[pdat['pressure'] == 0] = brush2
        return brusharray, penarray

    def addStrokeBoundaryPoints(self, strokeboundries):
        proj = MarkWriteMainWindow.instance().project
        stroke_type = proj.stroke_boundaries['stroke_type']
        ssize = SETTINGS['pen_stroke_boundary_size']
        if ssize == 0:
            if self.strokeBoundaryPoints:
                self.strokeBoundaryPoints.clear()
            return
        pcolor = SETTINGS['pen_stroke_pause_boundary_color']
        scolor = SETTINGS['pen_stroke_boundary_color']
        pen = pg.mkPen(scolor,width=ssize)
        brush = pg.mkBrush(scolor)
        if self.strokeBoundaryPoints is None:
            self.strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
            self.getPlotItem().addItem(self.strokeBoundaryPoints)
        else:
            self.strokeBoundaryPoints.clear()

        mstrokes = stroke_type==0
        self.strokeBoundaryPoints.addPoints(x=strokeboundries[X_FIELD][mstrokes],
                                             y=strokeboundries[Y_FIELD][mstrokes],
                                             size=ssize, pen=pen, brush=brush)
        pen = pg.mkPen(pcolor,width=ssize)
        brush = pg.mkBrush(pcolor)
        pstrokes = stroke_type==4
        
        self.strokeBoundaryPoints.addPoints(x=strokeboundries[X_FIELD][pstrokes],
                                             y=strokeboundries[Y_FIELD][pstrokes],
                                             size=ssize, pen=pen, brush=brush)


    def handleSelectedObjectChanged(self, newobj, oldobj):
        if MarkWriteMainWindow.instance().project.autosegl1 is True:
            if isinstance(newobj, PenDataSegment):
                    l1seg=newobj.l1seg
                    if l1seg and l1seg != self._level1Segment:
                            #print ">> *** PenDataSpatialPlotWidget.handleSelectedObjectChanged:",l1seg

                            self._level1Segment=l1seg
                            self.handleResetPenData(None)
                            #print "<< *** PenDataSpatialPlotWidget.handleSelectedObjectChanged"
        else:
            self._level1Segment = None

    def getCurrentPenData(self):
        try:
            if self._level1Segment:
                return self._level1Segment.pendata
        except:
            pass
        return MarkWriteMainWindow.instance().project.pendata

    def handleResetPenData(self, project):
        #print ">> ### PenDataSpatialPlotWidget.handleResetPenData:",project
        #pdat = project.pendata
        pdat = self.getCurrentPenData()

        if self.allPlotDataItem is None:
            brusharray,penarray = self.createDefaultPenBrushForData(pdat)

            self.allPlotDataItem = self.getPlotItem().plot(x=pdat[X_FIELD],
                                                           y=pdat[Y_FIELD],
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

            self.allPlotDataItem.setData(x=pdat[X_FIELD], y=pdat[Y_FIELD],
                                         pen=None, symbol='o',
                                         symbolSize=1,
                                         symbolBrush=brusharray,
                                         symbolPen=penarray)

            self.getPlotItem().setLimits(xMin=pdat[X_FIELD].min(),
                                         yMin=pdat[Y_FIELD].min(),
                                         xMax=pdat[X_FIELD].max(),
                                         yMax=pdat[Y_FIELD].max())

            self.setRange(xRange=(pdat[X_FIELD].min(), pdat[X_FIELD].max()),
                          yRange=(pdat[Y_FIELD].min(), pdat[Y_FIELD].max()),
                          padding=None)

        proj = MarkWriteMainWindow.instance().project
        pstart, pend = pdat['time'][[0,-1]]
        vms_times = proj.stroke_boundary_samples['time']
        vms_mask = (vms_times >= pstart) & (vms_times <= pend)
        self.addStrokeBoundaryPoints(proj.stroke_boundary_samples[vms_mask])
        #print "<< ### PenDataSpatialPlotWidget.handleResetPenData"


    def updateSelectedPenPointsGraphics(self, selectedpendata=None):
        if selectedpendata is None:
            selectedpendata = MarkWriteMainWindow.instance().project.selectedpendata

        pen=pen2=None
        brush=brush2=None
        psize=SETTINGS['spatialplot_selectedpoint_size']

        if MarkWriteMainWindow.instance().project.isSelectedDataValidForNewSegment():
            pen = pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'],
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            pen2 = pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'].darker(300),
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            brush = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'])
            brush2 = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'].darker(300))
        else:
            pen = pg.mkPen(SETTINGS['spatialplot_selectedinvalid_color'],
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            brush = pg.mkBrush(SETTINGS['spatialplot_selectedinvalid_color'])
            pen2 = pg.mkPen(SETTINGS['spatialplot_selectedinvalid_color'].darker(300),
                           width=SETTINGS['spatialplot_selectedpoint_size'])
            brush2 = pg.mkBrush(SETTINGS['spatialplot_selectedinvalid_color'].darker(300))

        penarray = np.empty(selectedpendata.shape[0], dtype=object)
        penarray[:] = pen
        penarray[selectedpendata['pressure'] == 0] = pen2
        brusharray = np.empty(selectedpendata.shape[0], dtype=object)
        brusharray[:] = brush
        brusharray[selectedpendata['pressure'] == 0] = brush2

        self.selectedPlotDataItem.setData(x=selectedpendata[X_FIELD],
                                          y=selectedpendata[Y_FIELD], pen=None,
                                          symbol='o', symbolSize=psize,
                                          symbolBrush=brusharray, symbolPen=penarray)

    def handleUpdatedSettingsEvent(self, updates, settings):
        selectedpendata = MarkWriteMainWindow.instance().project.selectedpendata
        #pdat = MarkWriteMainWindow.instance().project.pendata
        pdat = self.getCurrentPenData()
        for k in updates.keys():
            if k.startswith('spatialplot_default'):
                brusharray, penarray = self.createDefaultPenBrushForData(pdat)

                self.allPlotDataItem.setData(x=pdat[X_FIELD], y=pdat[Y_FIELD],
                                             symbolBrush=brusharray,
                                             symbolPen=penarray)
                break

        for k in updates.keys():
            if k.startswith('spatialplot_selected'):
                self.updateSelectedPenPointsGraphics(selectedpendata)
            break

        for k in updates.keys():
            if k.startswith('pen_stroke_boundary'):
                proj = MarkWriteMainWindow.instance().project
                pstart, pend = pdat['time'][[0,-1]]
                vms_times = proj.stroke_boundary_samples['time']
                vms_mask = (vms_times >= pstart) & (vms_times <= pend)
                self.addStrokeBoundaryPoints(proj.stroke_boundary_samples[vms_mask])

        if 'spatialplot_invert_y_axis' in updates.keys():
            self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])

    def handleSegmentRemoved(self,*args, **kwags):
        self.updateSelectedPenPointsGraphics()

    def handleSegmentCreated(self,*args, **kwags):
        self.updateSelectedPenPointsGraphics()

    def handlePenDataSelectionChanged(self, timeperiod, selectedpendata):
        #print ">> PenDataSpatialPlotWidget.handlePenDataSelectionChanged",timeperiod,selectedpendata.shape
        if self.allPlotDataItem is None:
            self.handleResetPenData(MarkWriteMainWindow.instance().project)

        self.updateSelectedPenPointsGraphics(selectedpendata)

        self.ensureSelectionIsVisible(timeperiod, selectedpendata)
        #print "<< PenDataSpatialPlotWidget.handlePenDataSelectionChanged"

    def zoomToPenData(self, pendata, lock_bounds=False):
        xpadding = self.getPlotItem().getViewBox().suggestPadding(0)
        ypadding = self.getPlotItem().getViewBox().suggestPadding(1)
        if lock_bounds:
            self.setLimits(yMin=max(0.0, pendata[Y_FIELD].min() - ypadding),
                           yMax=pendata[Y_FIELD].max() + ypadding,
                           xMin=max(0.0, pendata[X_FIELD].min() - xpadding),
                           xMax=pendata[X_FIELD].max() + xpadding)
        self.setRange(xRange=(pendata[X_FIELD].min(), pendata[X_FIELD].max()),
                      yRange=(pendata[Y_FIELD].min(), pendata[Y_FIELD].max()),
                      padding=None)

    def ensureSelectionIsVisible(self, timespan, selectedpendata):
        if len(selectedpendata) > 0:
            (vxmin, vxmax), (vymin, vymax) = self.viewRange()
            dxmin, dxmax, dymin, dymax = selectedpendata[X_FIELD].min(), \
                                         selectedpendata[X_FIELD].max(), \
                                         selectedpendata[Y_FIELD].min(), \
                                         selectedpendata[Y_FIELD].max()

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
                
    def getState(self):
        return self.getPlotItem().getViewBox().getState()
        
    def setState(self, s):
        self.getPlotItem().getViewBox().setState(s)
