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

        MarkWriteMainWindow.instance().sigSelectedPenDataUpdate.connect(
            self.handlePenDataSelectionChanged)

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self.plotDataItem.setData(x=pendata[X_FIELD], y=pendata[Y_FIELD], )
        self.getPlotItem().enableAutoRange(x=True, y=True)

    def handleUpdatedSettingsEvent(self, updates, settings):
        if 'spatialplot_invert_y_axis' in updates.keys():
            self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])