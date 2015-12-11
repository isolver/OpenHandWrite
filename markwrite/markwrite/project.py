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
from __future__ import division

from weakref import proxy,ProxyType
import time
import os
import glob
import numpy as np
import codecs

import pyqtgraph as pg
from pyqtgraph import OrderedDict
from pyqtgraph.Qt import QtGui

from file_io import EyePenDataImporter, XmlDataImporter, HubDatastoreImporter
from segment import PenDataSegment, PenDataSegmentCategory
from util import contiguous_regions
from gui.projectsettings import SETTINGS

selectedtimeperiod_properties=None

class SelectedTimePeriodItem(pg.LinearRegionItem):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        kwargs['movable']=True

        pg.LinearRegionItem.__init__(self,*args, **kwargs)

        self._project = None
        if project:
            self.project=project

    def mouseClickEvent(self, ev):
        self.project._mwapp.setActiveObject(self)
        pg.LinearRegionItem.mouseClickEvent(self, ev)

    def mouseDoubleClickEvent(self, event):
        pg.LinearRegionItem.mouseDoubleClickEvent(self, event)
        self.project._mwapp.setActiveObject(self)
        self.project._mwapp._penDataTimeLineWidget.zoomToPenData(
            self.selectedpendata)
        self.project._mwapp._penDataSpatialViewWidget.zoomToPenData(
            self.selectedpendata)

    def lineMoved(self):
        if self.blockLineSignal:
            return
        pg.LinearRegionItem.lineMoved(self)
        if self.project._mwapp._segmenttree.doNotSetActiveObject is False:
#            print 'lineMoved:',self.getRegion()
            self.project._mwapp.setActiveObject(self)

    def lineMoveFinished(self):
        pg.LinearRegionItem.lineMoveFinished(self)
        if self.project._mwapp._segmenttree.doNotSetActiveObject is False:
#            print 'lineMoveFinished:',self.getRegion()
            self.project._mwapp.setActiveObject(self)

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, p):
        if p is None:
            self._project = p
            self.setBounds(bounds=(0,0))
            self.setRegion([0,0])
        else:
            if isinstance(p,ProxyType):
                self._project=p
            else:
                self._project = proxy(p)

    @property
    def allpendata(self):
        return self.project.pendata

    @property
    def selectedpendata(self):
        minT, maxT = self.getRegion()
        allpendata = self.allpendata
        return allpendata[(allpendata['time'] >= minT) & (allpendata['time'] <= maxT)]

    @property
    def selectedtimerangeanddata(self):
        minT, maxT = self.getRegion()
        allpendata = self.allpendata
        return  minT, maxT, allpendata[(allpendata['time'] >= minT) & (allpendata['time'] <= maxT)]

    def propertiesTableData(self):
        """
        Return a dict of segment properties to display in the Selected Project
        Tree Node Object Properties Table.

        :return: dict of segmentcategory properties to display
        """
        global selectedtimeperiod_properties
        props= selectedtimeperiod_properties

        if selectedtimeperiod_properties is None:
            selectedtimeperiod_properties = OrderedDict()
            props= selectedtimeperiod_properties
            props['Name'] = ['']
            props['Start Time'] = ['']
            props['End Time'] = ['']
            props['Point Count'] = ['']

        props['Name'][0] = u"Selected Time Period"
        stime, etime = self.getRegion()
        props['Start Time'][0] = stime
        props['End Time'][0] = etime
        props['Point Count'][0] = self.selectedpendata.shape[0]

        return props

class MarkWriteProject(object):
    project_file_extension = u'mwp'
    input_file_loaders=dict(xml=XmlDataImporter,
                            txyp=EyePenDataImporter,
                            hdf5=HubDatastoreImporter)
    _selectedtimeregion=None
    def __init__(self, name=u"New", file_path=None, mwapp=None):
        """
        The MarkWriteProject class represents a MarkWrite project created using
        the MarkWrite Application. Information about imported data, etc. (TBD)
        is stored in the class for use while MarkWrite is running.

        A MarkWriteProject instance can be saved to a .wmpd file. The
        saved .wmpd file can be reopened from within the MarkWrite application
        at a later time to continue working on the project.

        The MarkWrite Application supports a single MarkWriteProject open
        at a time. To switch between different MarkWriteProject's, use File->Open
        and select the .wmpd file to open.

        :param name: str
        :param kwargs: dict
        :return: MarkWriteProject instance
        """
        self._pendata = []
        self.nonzero_pressure_mask = []
        self.nonzero_region_ix=[]
        self.sampling_interval = 0
        self.sample_dts = []
        self.series_boundaries = []
        self._segmentset=None
        self.autodetected_segment_tags=[]
        self._name = u"Unknown"
        self._original_timebase_offset=0
        self._autosegl1=False
        self._trialtimes = None
        self._expcondvars = []

        self._mwapp = None
        if mwapp:
            self._mwapp = proxy(mwapp)

        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
            dir_path, file_name = os.path.split(file_path)
            # Load raw data from file for use in project
            fname, fext=file_name.rsplit(u'.',1)
            fimporter = self.input_file_loaders.get(fext)
            if fimporter:
                self.autodetected_segment_tags=self.detectAssociatedSegmentTagsFile(dir_path,fname,fext)
                pdata = fimporter.asarray(file_path)

                # If file opened was an iohub hdf5 file, and had a
                # cond var table, get the cond var table as a ndarray.
                expcondvars = None
                try:
                    expcondvars = fimporter.exp_condvars
                except:
                    pass

                # If cond var table exists, give user option of selecting
                # a start and end time variable column to be used to
                # split data into trial segments and remove any between trial
                # data.

                tstartvar = None
                tendvar = None
                self._autosegl1 = SETTINGS['auto_generate_l1segments']

                if self._autosegl1:
                    if expcondvars is not None:
                        trial_start_var_select_filter = SETTINGS['hdf5_trial_start_var_select_filter'].strip()
                        trial_end_var_select_filter = SETTINGS['hdf5_trial_end_var_select_filter'].strip()

                        from gui.dialogs import DlgFromDict
                        tvarlists=OrderedDict()

                        def getFilteredVarList(vlist,fstr):
                            filter_tokens = fstr.split('*')
                            if len(filter_tokens) == 2:
                                vlist = [v for v in vlist if v.startswith(filter_tokens[0]) and v.endswith(filter_tokens[1])]
                            elif len(filter_tokens) == 1:
                                if fstr[0] == '*':
                                    vlist = [v for v in vlist if v.endswith(filter_tokens[1])]
                                elif fstr[-1] == '*':
                                    vlist = [v for v in vlist if v.startswith(filter_tokens[0])]
                                else:
                                    print "WARNING: UNHANDLED FILTER TOKENS:",filter_tokens
                            elif len(filter_tokens) > 2:
                                print "ERROR: FILTER CAN HAVE MAX 2 TOKENS:",filter_tokens
                            return vlist

                        tvarlists["Start Time Variable"]=list(expcondvars.dtype.names)
                        if trial_start_var_select_filter:
                            tvarlists["Start Time Variable"] = getFilteredVarList(tvarlists["Start Time Variable"], trial_start_var_select_filter)

                        tvarlists["End Time Variable"]=list(expcondvars.dtype.names)
                        if trial_end_var_select_filter:
                             tvarlists["End Time Variable"] = getFilteredVarList(tvarlists["End Time Variable"], trial_end_var_select_filter)

                        dictDlg = DlgFromDict(dictionary=tvarlists, title='Select Trial Time Conditions')
                        if dictDlg.OK:
                            tstartvar = tvarlists["Start Time Variable"]
                            tendvar = tvarlists["End Time Variable"]
                self.createNewProject(fname, pdata, expcondvars, tstartvar, tendvar, fext)
            else:
                print "Unsupported file type:",file_path
        else:
            raise IOError("Invalid File Path: %s"%(file_path))

    def detectAssociatedSegmentTagsFile(self,dir_path,fname,fext):
        tag_list=[]
        same_named_files = glob.glob(os.path.join(dir_path,fname+u'.*'))
        if len(same_named_files)<2:
            return tag_list

        same_named_files=[f for f in same_named_files if not f.endswith(fext)]
        if len(same_named_files)<1:
            return tag_list

        with codecs.open(same_named_files[0], "r", "utf-8") as f:
            for seg_line in f:
                seg_line=seg_line.splitlines()[-1].strip()
                if seg_line:
                    tag_list.append(seg_line)
        return tag_list

    def createNewProject(self, file_name, pen_data, condvars=None, stime_var=None, etime_var=None, file_type=None):
            PenDataSegmentCategory.clearSegmentCache()

            self._project_settings = None

            self._name = file_name
            self._filetype = file_type

            self._expcondvars = condvars
            self._stimevar = stime_var
            self._etimevar = etime_var

            # go through each trial, select only the samples within
            # the trial period, add the trials sample array to list of trial
            # sample data.
            samples_by_trial = []
            trial_times = None
            if self._expcondvars is not None and self._stimevar is not None and self._etimevar is not None:
                trial_times = []
                for t in self._expcondvars:
                    try:
                        trialstart = float(t[self._stimevar])
                        trialend = float(t[self._etimevar])
                        trial_times.append((trialstart,trialend))
                        trial_samples = pen_data[(pen_data['time'] >= trialstart) & (pen_data['time'] <= trialend)]
                        samples_by_trial.append(trial_samples)
                        #print "trial samples:",trial_samples.shape
                    except:
                        print("Error getting trial time period:")
                        import traceback
                        traceback.print_exc()

            if samples_by_trial:
                # make pen_data == concat'ed samples_by_trial
                pen_data = np.concatenate(samples_by_trial)

                # turn trial start, stop time list into np array
                trial_times = np.asarray(trial_times)

            # Normalize pen sample times so first sample starts at 0.0 sec.
            self._original_timebase_offset=pen_data[0]['time']
            pen_data['time']-=self._original_timebase_offset
            if trial_times is not None:
                trial_times-=self._original_timebase_offset
                self._trialtimes = trial_times

            # Change time stamps to sec.msec format, if needed
            if file_type != 'hdf5':
                # data from iohub hdf5 file is already in sec.msec format
                pen_data['time']=pen_data['time']/1000.0

            self._pendata = pen_data

            self.nonzero_pressure_mask=self._pendata['pressure']>0
            # nonzero_regions_ix will be a tuple of (starts, stops, lengths) arrays
            self.nonzero_region_ix=contiguous_regions(self.nonzero_pressure_mask)
            self._segmentset=PenDataSegmentCategory(name=self.name,project=self)
            self._pendata['segment_id']=self._segmentset.id

            # inter sample intervals, used for sampling rate calc and
            # vel / accell measures.
            self.sample_dts = self._pendata['time'][1:]-self._pendata['time'][:-1]

            # Calculate what the sampling interval (1000.0 / hz_rate) for the device was in sec.msec
            self.sampling_interval = np.percentile(self.sample_dts,5.0,interpolation='nearest')

            # Find pen sample series boundaries, using calculated
            # sampling_interval. Filtering and velocity alg's are applied to
            # the pen samples within each series.
            slist=[]
            series_starts_ix, series_stops_ix, series_lengths = contiguous_regions(self.sample_dts < 2.0*self.sampling_interval)
            for i in xrange(len(series_starts_ix)):
                slist.append((series_starts_ix[i],series_stops_ix[i]))
            series_dtype = np.dtype({'names':['start_ix','end_ix'], 'formats':[np.uint32,np.uint32,]})
            self.series_boundaries = np.asarray(slist,dtype=series_dtype)

            # filter data
            from sample_filter import filter_pen_sample_series
            from sample_va import calculate_velocity
            for series_bounds in self.series_boundaries:
                filter_pen_sample_series(self, self.pendata[
                        series_bounds['start_ix']:series_bounds['end_ix']+1])
                calculate_velocity(self, self.pendata[
                        series_bounds['start_ix']:series_bounds['end_ix']+1])

            if self._selectedtimeregion is None:
                MarkWriteProject._selectedtimeregion = SelectedTimePeriodItem(project=self)
            else:
                MarkWriteProject._selectedtimeregion.project = self

    def getSelectedDataSegmentIDs(self):
        if len(self.selectedpendata)>0:
            return np.unique(self.selectedpendata['segment_id'])
        return []

    def createSegmentFromSelectedPenData(self, tag, parent_id):
        """
        Only called if the currently selected pen data can make a valid segment.
        i.e. getSelectedDataSegmentIDs() returned a list of exactly 1 segment id

        Also ensure that self._selectedpendata has been trimmed as required
         based on enabled state of rules like the 0 pressure trim rule
        :param tag:
        :param parent_id:
        :return:
        """
        sparent = self._segmentset.id2obj[parent_id]
        new_segment = PenDataSegment(name=tag, pendata=self.selectedpendata, parent=sparent, fulltimerange=self.selectedtimeperiod)
        pendata = self.pendata
        mask = (pendata['time'] >= new_segment.starttime) & (pendata['time'] <= new_segment.endtime)
        self.pendata['segment_id'][mask]=new_segment.id
        return new_segment

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def pendata(self):
        return self._pendata

    @property
    def allpendata(self):
        return self._pendata

    @property
    def unsegmentedpendata(self):
        return self._pendata[self._pendata['segment_id']==0]

    @property
    def segmentedpendata(self):
        return self._pendata[self._pendata['segment_id']>0]

    @property
    def selectedtimeregion(self):
        return self._selectedtimeregion

    @property
    def selectedtimeperiod(self):
        return self._selectedtimeregion.getRegion()

    @property
    def selecteddatatimerange(self):
        if len(self.selectedpendata)>0:
            return self.selectedpendata['time'][[0,-1]]

    @property
    def selectedpendata(self):
        return self._selectedtimeregion.selectedpendata

    def isSelectedDataValidForNewSegment(self):
        if len(self.selectedpendata)>0:
            sids = self.getSelectedDataSegmentIDs()
            if len(sids)==1:
                if sids[0] == 0:
                    return True
                if self.segmentset.id2obj[sids[0]].pointcount > self.selectedpendata.shape[0]:
                    return True
        return False

    @property
    def segmentset(self):
        return self._segmentset

    def close(self):
        """
        Close the MarkWrite project, including closing any imported data files.
        Return a bool indicating if the close operation was successful or not.

        :return: bool
        """
        self._pendata = None
        self._selectedtimeregion = None
        return True

    def __del__(self):
        self.close()