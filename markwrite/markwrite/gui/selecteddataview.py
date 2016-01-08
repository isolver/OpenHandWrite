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
import pyqtgraph as pg
from markwrite.gui import X_FIELD, Y_FIELD
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.gui.projectsettings import SETTINGS
import numpy as np

class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False, )

        self._lastSelectedData=[]

        self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])
        self.getPlotItem().setAspectLocked(True, 1)
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')
        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o',
                                                    symbolSize=1,
                                                    symbolBrush=(255, 255, 255),
                                                    symbolPen=(255, 255, 255))

        self.strokeBoundaryPoints = None

        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.connect(
            self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self._lastSelectedData = pendata
        if len(pendata):
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

            penarray = np.empty(pendata.shape[0], dtype=object)
            penarray[:] = pen
            penarray[pendata['pressure'] == 0] = pen2
            brusharray = np.empty(pendata.shape[0], dtype=object)
            brusharray[:] = brush
            brusharray[pendata['pressure'] == 0] = brush2

            self.plotDataItem.setData(x=pendata[X_FIELD],
                                              y=pendata[Y_FIELD], pen=None,
                                              symbol='o', symbolSize=psize,
                                              symbolBrush=brusharray, symbolPen=penarray)

            if self.strokeBoundaryPoints is None:
                ssize = SETTINGS['pen_stroke_boundary_size']
                if ssize:
                    scolor = SETTINGS['pen_stroke_boundary_color']
                    pen = pg.mkPen(scolor,width=ssize)
                    brush = pg.mkBrush(scolor)
                    self.strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
                    self.getPlotItem().addItem(self.strokeBoundaryPoints)
            else:
                ssize = SETTINGS['pen_stroke_boundary_size']
                if ssize == 0:
                    self.strokeBoundaryPoints.clear()
                else:
                    scolor = SETTINGS['pen_stroke_boundary_color']
                    pen = pg.mkPen(scolor,width=ssize)
                    brush = pg.mkBrush(scolor)

                    proj = MarkWriteMainWindow.instance().project
                    pstart, pend = pendata['time'][[0,-1]]
                    vms_times = proj.velocity_minima_samples['time']
                    vmpoints = proj.velocity_minima_samples[(vms_times >= pstart) & (vms_times <= pend)]
                    self.strokeBoundaryPoints.setData(x=vmpoints[X_FIELD], y=vmpoints[Y_FIELD], size=ssize, pen=pen, brush=brush)

        else:
            self.plotDataItem.setData(x=[],y=[])

        self.getPlotItem().enableAutoRange(x=True, y=True)

    def handleUpdatedSettingsEvent(self, updates, settings):
        if 'spatialplot_invert_y_axis' in updates.keys():
            self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])

        for k in updates.keys():
            if k.startswith('pen_stroke_boundary'):
                self.handlePenDataSelectionChanged(None,self._lastSelectedData)