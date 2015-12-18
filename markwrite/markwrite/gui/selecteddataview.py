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

class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False, )

        self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])
        self.getPlotItem().setAspectLocked(True, 1)
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')
        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o',
                                                    symbolSize=1,
                                                    symbolBrush=(255, 255, 255),
                                                    symbolPen=(255, 255, 255))

        self.strokeBoundaryPoints = None
        ssize = SETTINGS['pen_stroke_boundary_size']
        if ssize:
            scolor = SETTINGS['pen_stroke_boundary_color']
            pen = pg.mkPen(scolor,width=ssize)
            brush = pg.mkBrush(scolor)
            self.strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=pen, brush=brush)
            self.getPlotItem().addItem(self.strokeBoundaryPoints)

        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.connect(
            self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self.plotDataItem.setData(x=pendata[X_FIELD], y=pendata[Y_FIELD], )

        if len(pendata) and self.strokeBoundaryPoints:
            proj = MarkWriteMainWindow.instance().project
            pstart, pend = pendata['time'][[0,-1]]
            vms_times = proj.velocity_minima_samples['time']
            vmpoints = proj.velocity_minima_samples[(vms_times >= pstart) & (vms_times <= pend)]
            self.strokeBoundaryPoints.setData(x=vmpoints[X_FIELD], y=vmpoints[Y_FIELD], )

        self.getPlotItem().enableAutoRange(x=True, y=True)

    def handleUpdatedSettingsEvent(self, updates, settings):
        if 'spatialplot_invert_y_axis' in updates.keys():
            self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])