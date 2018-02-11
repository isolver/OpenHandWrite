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
import pyqtgraph.exporters
from pyqtgraph.Qt import QtGui, QtCore
from markwrite.gui.dialogs import fileSaveDlg
from markwrite.gui import X_FIELD, Y_FIELD
from markwrite.gui.mainwin import MarkWriteMainWindow
from markwrite.gui.projectsettings import SETTINGS
import numpy as np

class SelectedPointsPlotWidget(pg.PlotWidget):
    def __init__(self):
        pg.PlotWidget.__init__(self, enableMenu=False, )

        self._lastSelectedData=[]

        self.qtpenbrushs = dict()
        self.createPenBrushCache()

        self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])
        self.getPlotItem().setAspectLocked(True, 1)
        self.getPlotItem().hideAxis('left')
        self.getPlotItem().hideAxis('bottom')
        self.plotDataItem = self.getPlotItem().plot(pen=None, symbol='o',
                                                    symbolSize=1,
                                                    symbolBrush=(255, 255, 255),
                                                    symbolPen=(255, 255, 255))

        self.strokeBoundaryPoints = None

        self._enablePopupDisplay = True


    def mouseMoveEvent(self, event):
        super(SelectedPointsPlotWidget,self).mouseMoveEvent(event)
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
                apath = fileSaveDlg(initFileName="selected_data_view.png",
                            prompt=u"Save Selected Data View as Image",
                            allowed="*.png")
                if apath:
                    exporter.export(apath)
        self._enablePopupDisplay = True

    def createPenBrushCache(self):
        self.qtpenbrushs.clear()
        self.qtpenbrushs['selected_valid_pressed_pen']=pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'],
                               width=SETTINGS['spatialplot_selectedpoint_size'])
        self.qtpenbrushs['selected_valid_hover_pen']=pg.mkPen(SETTINGS['spatialplot_selectedvalid_color'].darker(300),
                               width=SETTINGS['spatialplot_selectedpoint_size'])
        self.qtpenbrushs['selected_valid_pressed_brush'] = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'])
        self.qtpenbrushs['selected_valid_hover_brush'] = pg.mkBrush(SETTINGS['spatialplot_selectedvalid_color'].darker(300))

        self.qtpenbrushs['selected_invalid_pressed_pen']=pg.mkPen(SETTINGS['spatialplot_selectedinvalid_color'],
                               width=SETTINGS['spatialplot_selectedpoint_size'])
        self.qtpenbrushs['selected_invalid_hover_pen']=pg.mkPen(SETTINGS['spatialplot_selectedinvalid_color'].darker(300),
                               width=SETTINGS['spatialplot_selectedpoint_size'])
        self.qtpenbrushs['selected_invalid_pressed_brush'] = pg.mkBrush(SETTINGS['spatialplot_selectedinvalid_color'])
        self.qtpenbrushs['selected_invalid_hover_brush'] = pg.mkBrush(SETTINGS['spatialplot_selectedinvalid_color'].darker(300))
        if SETTINGS['pen_stroke_boundary_size'] > 0:
            self.qtpenbrushs['stroke_boundary_pen']=pg.mkPen(SETTINGS['pen_stroke_boundary_color'],
                               width=SETTINGS['pen_stroke_boundary_size'])
            self.qtpenbrushs['stroke_boundary_brush'] = pg.mkBrush(SETTINGS['pen_stroke_boundary_color'])

    def handlePenDataSelectionChanged(self, timeperiod, pendata):
        self._lastSelectedData = pendata
        if len(pendata):

            psize=SETTINGS['spatialplot_selectedpoint_size']

            penarray = np.empty(pendata.shape[0], dtype=object)
            brusharray = np.empty(pendata.shape[0], dtype=object)

            if MarkWriteMainWindow.instance().project.isSelectedDataValidForNewSegment():
                penarray[:] = self.qtpenbrushs['selected_valid_pressed_pen']
                penarray[pendata['pressure'] == 0] = self.qtpenbrushs['selected_valid_hover_pen']
                brusharray[:] = self.qtpenbrushs['selected_valid_pressed_brush']
                brusharray[pendata['pressure'] == 0] = self.qtpenbrushs['selected_valid_hover_brush']
            else:
                penarray[:] = self.qtpenbrushs['selected_invalid_pressed_pen']
                penarray[pendata['pressure'] == 0] = self.qtpenbrushs['selected_invalid_hover_pen']
                brusharray[:] = self.qtpenbrushs['selected_invalid_pressed_brush']
                brusharray[pendata['pressure'] == 0] = self.qtpenbrushs['selected_invalid_hover_brush']

            self.plotDataItem.setData(x=pendata[X_FIELD],
                                              y=pendata[Y_FIELD], pen=None,
                                              symbol='o', symbolSize=psize,
                                              symbolBrush=brusharray, symbolPen=penarray)

            ssize = SETTINGS['pen_stroke_boundary_size']
            if self.strokeBoundaryPoints is None:
                if ssize > 0:
                    self.strokeBoundaryPoints = pg.ScatterPlotItem(size=ssize, pen=self.qtpenbrushs['stroke_boundary_pen'], brush=self.qtpenbrushs['stroke_boundary_brush'])
                    self.getPlotItem().addItem(self.strokeBoundaryPoints)
            else:
                if ssize == 0:
                    self.strokeBoundaryPoints.clear()
                else:
                    proj = MarkWriteMainWindow.instance().project
                    pstart, pend = pendata['time'][[0,-1]]
                    vms_times = proj.stroke_boundary_samples['time']
                    vmpoints = proj.stroke_boundary_samples[(vms_times >= pstart) & (vms_times <= pend)]
                    self.strokeBoundaryPoints.setData(x=vmpoints[X_FIELD], y=vmpoints[Y_FIELD], size=ssize, pen=self.qtpenbrushs['stroke_boundary_pen'], brush=self.qtpenbrushs['stroke_boundary_brush'])

        else:
            self.plotDataItem.clear()#setData(x=[],y=[],pen='black', brush='')

        self.getPlotItem().enableAutoRange(x=True, y=True)

    def handleUpdatedSettingsEvent(self, updates, settings):
        if 'spatialplot_invert_y_axis' in updates.keys():
            self.getPlotItem().invertY(SETTINGS['spatialplot_invert_y_axis'])

        for k in updates.keys():
            if k.startswith('pen_stroke_boundary') or k.startswith('spatialplot_selected'):
                self.createPenBrushCache()
                self.handlePenDataSelectionChanged(None,self._lastSelectedData)
                break
                            
    def getState(self):
        return self.getPlotItem().getViewBox().getState()
        
    def setState(self, s):
        self.getPlotItem().getViewBox().setState(s)