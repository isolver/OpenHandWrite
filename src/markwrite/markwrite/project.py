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
import os
import glob
import codecs

import numpy as np
import pyqtgraph as pg
from pyqtgraph import OrderedDict

from file_io import EyePenDataImporter, XmlDataImporter, HubDatastoreImporter, readPickle, writePickle,SAMPLE_STATES
from segment import PenDataSegment, PenDataSegmentCategory
from util import contiguous_regions, getFilteredStringList
from gui.projectsettings import SETTINGS
from .sigproc import filter_pen_sample_series, calculate_velocity, detect_peaks


selectedtimeperiod_properties=None

class SelectedTimePeriodItem(pg.LinearRegionItem):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        kwargs['movable']=True
        pg.LinearRegionItem.__init__(self,*args, **kwargs)
        for l in self.lines:
            l.pen.color()
            l.setPen(l.pen.color(),
                       width=2)
            l.setHoverPen(l.hoverPen.color(),width=2)
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

    def getBounds(self):
        return self.lines[0].maxRange

    @property
    def project(self):
        return self._project

    #def setBounds(self, bounds):
    #    super.setBounds(self, bounds)

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
        _, _, spendata = self.selectedtimerangeanddata
        return spendata

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
        props['Start Time'][0] = '%.3f'%stime
        props['End Time'][0] = '%.3f'%etime
        props['Point Count'][0] = self.selectedpendata.shape[0]
        mwapp = self._project._mwapp
        trialname=None
        if mwapp:
            if mwapp.activetrial:
                trialname = mwapp.activetrial.name
        if trialname:
            props.setdefault('Current Trial',[''])[0] = '%s'%(trialname)
        elif props.has_key('Current Trial'):
            del props['Current Trial']

        return props

    def toDict(self):
        return dict(timerange=self.getRegion())

def updateDataFileLoadingProgressDialog(mwapp, inc_val=2):
    if mwapp:
        progressdlg = mwapp._progressdlg
        if progressdlg.value()+inc_val >= progressdlg.maximum():
            progressdlg.setValue(progressdlg.minimum())
        else:
            mwapp._progressdlg += inc_val
        if mwapp._progressdlg.wasCanceled():
            # TODO: close out incomplete project load...
            pass

class MarkWriteProject(object):
    project_file_extension = u'mwp'
    serialize_attributes = (
                            'name',
                            'pendatafileinfo',
                            'schema_version',
                            'timebase_offset',
                            'autosegl1',
                            '_stimevar',
                            '_etimevar',
                            '_expcondvars',
                            'trial_boundaries',
                            'autodetected_segment_tags',
                            'pendata',
                            'nonzero_pressure_mask',
                            'nonzero_region_ix',
                            'series_boundaries',
                            'run_boundaries',
                            'velocity_minima_samples',
                            'stroke_boundaries',
                            'segmenttree'
                            )
    input_file_loaders=dict(xml=XmlDataImporter,
                            txyp=EyePenDataImporter,
                            hdf5=HubDatastoreImporter,
                            mwp=readPickle)
    _selectedtimeregion=None
    schema_version = "0.1"
    def __init__(self, name=u"New", file_path=None, mwapp=None, tstart_cond_name=None, tend_cond_name=None):
        """
        The MarkWriteProject class represents a MarkWrite project created using
        the MarkWrite Application. Information about imported data, etc.,
        is stored in the class for use while MarkWrite is running.

        A MarkWriteProject instance can be saved to a .mwp file. The
        saved .mwp file can be reopened from within the MarkWrite application
        at a later time to continue working on the project.

        The MarkWrite Application supports a single MarkWriteProject open
        at a time. To switch between different MarkWriteProject's, use File->Open
        and select the .mwp file to open.

        :param name: str
        :param kwargs: dict
        :return: MarkWriteProject instance
        """

        #
        ## >>> Attributes to save to serialized project file are all
        ## listed in MarkWriteProject.serialize_attributes
        #

        self.name = u"Unknown"
        self.projectfileinfo = dict(saved=False,
                                   abspath=None,
                                   folder=None,
                                   name=None,
                                   shortname=None,
                                   extension=None)

        self.pendatafileinfo = dict(abspath=None,
                                   folder=None,
                                   name=None,
                                   extension=None,
                                   utcdateloaded=None)

        self.timebase_offset=0
        self.autosegl1=False
        self._stimevar = tstart_cond_name
        self._etimevar = tend_cond_name
        self._expcondvars = []
        self.trial_boundaries = []

        self.autodetected_segment_tags=[]
        self.pendata = []
        self.nonzero_pressure_mask = []
        self.nonzero_region_ix=[]
        #self.sampling_interval = 0
        self.series_boundaries = []
        self.run_boundaries=[]
        self.velocity_minima_samples = None
        self.stroke_boundaries = []
        self.segmenttree=None

        self._velocity_minima_ixs=[]
        self._mwapp = None
        self._modified = True

        if mwapp:
            self._mwapp = proxy(mwapp)
            self._mwapp._current_project = self

        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):

            fext=file_path.rsplit(u'.',1)[-1]
            fimporter = self.input_file_loaders.get(fext)
            if fimporter:
                updateDataFileLoadingProgressDialog(self._mwapp, inc_val=1)
                if fext != self.project_file_extension:
                    #print fext, self.project_file_extension, self.project_file_extension == fext
                    # Load raw data from file for use in project
                    self.createNewProject(file_path, fimporter)
                else:
                    self.openFromProjectFile(file_path, fimporter)
            else:
                print "Unsupported file type:",file_path
        else:
            raise IOError("Invalid File Path: %s"%(file_path))

    def toDict(self):
        # check that all attributes to include in dict actually exist
        projdict = dict()
        for a in self.serialize_attributes:
            if hasattr(self, a):
                pa = getattr(self,a)
                if callable(pa):
                    pa = pa()
                if hasattr(pa, 'toDict'):
                    pa = pa.toDict()
                projdict[a] = pa
            else:
                print "### MarkWriteProject.toDict Error: %s is not a member of the project class"%a
        return projdict

    @classmethod
    def fromDict(cls, d):
        print cls, ".fromDict not yet implemented."

    def _detectAssociatedSegmentTagsFile(self,dir_path,fname,fext):
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

    def updateProjectFileInfo(self, file_path, saved=True):
            self.projectfileinfo['saved']= saved
            self.projectfileinfo['abspath'] = file_path
            self.projectfileinfo['folder'], self.projectfileinfo['name'] = os.path.split(file_path)
            self.projectfileinfo['shortname'], fext =  self.projectfileinfo['name'].rsplit(u'.',1)
            self.projectfileinfo['extension'] = self.project_file_extension
            self.name = self.projectfileinfo['shortname']

    def updatePenDataFileInfo(self, file_path):
            self.pendatafileinfo['abspath'] = file_path
            self.pendatafileinfo['folder'], self.pendatafileinfo['name'] = os.path.split(file_path)
            _, fext =  self.projectfileinfo['name'].rsplit(u'.',1)
            self.projectfileinfo['extension'] = fext
            import datetime
            self.pendatafileinfo['utcdateloaded'] = datetime.datetime.utcnow()

    def _detectTrialPeriodConditionVariables(self, fimporter):
        # If file opened was an iohub hdf5 file, and had a
        # cond var table, get the cond var table as a ndarray.
        try:
            self._expcondvars = fimporter.exp_condvars
        except:
            self._expcondvars = None

        # If cond var table exists, give user option of selecting
        # a start and end time variable column to be used to
        # split data into trial segments and remove any between trial
        # data.
        self.autosegl1 = SETTINGS['auto_generate_l1segments']
        if self.autosegl1 and self._expcondvars is not None and (self._stimevar is None and self._etimevar is None):
            trial_start_var_select_filter = SETTINGS['hdf5_trial_start_var_select_filter'].strip()
            trial_end_var_select_filter = SETTINGS['hdf5_trial_end_var_select_filter'].strip()

            tvarlists=OrderedDict()
            tvarlists["Start Time Variable"]=list(self._expcondvars.dtype.names)
            if trial_start_var_select_filter:
                tvarlists["Start Time Variable"] = getFilteredStringList(tvarlists["Start Time Variable"], trial_start_var_select_filter)
            tvarlists["End Time Variable"]=list(self._expcondvars.dtype.names)
            if trial_end_var_select_filter:
                 tvarlists["End Time Variable"] = getFilteredStringList(tvarlists["End Time Variable"], trial_end_var_select_filter)

            from gui.dialogs import DlgFromDict
            dictDlg = DlgFromDict(dictionary=tvarlists, title='Select Trial Time Conditions')
            if dictDlg.OK:
                self._stimevar = tvarlists["Start Time Variable"]
                self._etimevar = tvarlists["End Time Variable"]

    def _parsePenDataByTrials(self, pen_data):
        trials=[]   #list of tuples; each being (cvrow_index, start_sample_ix, start_sample_time, end_sample_ix, end_sample_time)
        if self._expcondvars is not None and self._stimevar is not None and self._etimevar is not None:
            # go through each trial, select only the samples within
            # the trial period, add the trials sample array to list of trial
            # sample data.
            samples_by_trial = []
            trialsamplecount = 0
            lastrialendix = -1

            CVROW_IX = 0
            TS_IX_IX = 1
            TS_TIME_IX = 2
            TE_IX_IX = 3
            TE_TIME_IX = 4

            for tix, t in enumerate(self._expcondvars):
                tbounds=[tix, 0, 0.0, 0, 0.0]
                try:
                    trialstart = float(t[self._stimevar])
                    trialend = float(t[self._etimevar])

                    if trialend - trialstart <= 0:
                        raise ValueError("Trial end time must be greater than trial start time: [{}, {}]".format(trialstart,trialend))

                    trial_time_mask = (pen_data['time'] >= trialstart) & (pen_data['time'] < trialend)
                    start_ix, end_ix, trial_length = contiguous_regions(trial_time_mask)
                    start_ix, end_ix = start_ix[0], end_ix[0]

                    # check for trial overlap
                    if not (end_ix > start_ix and start_ix >= lastrialendix):
                            raise ValueError("Trial sample range overlaps with existing trial: current=[{}, {}], last_trial_end_ix= {}".format(start_ix, end_ix, lastrialendix))

                    lastrialendix = end_ix

                    trial_samples = pen_data[trial_time_mask]

                    if len(trial_samples)>0:
                        tbounds[TS_IX_IX] = trialsamplecount
                        trialsamplecount += len(trial_samples)
                        tbounds[TE_IX_IX] = trialsamplecount-1
                        samples_by_trial.append(trial_samples)

                    # Normalize pen sample times so first sample starts at 0.0 sec.
                    if tix == 0:
                        self.timebase_offset = trialstart
                        tbounds[TS_TIME_IX] = 0.0
                    else:
                        tbounds[TS_TIME_IX] = trialstart-self.timebase_offset
                    tbounds[TE_TIME_IX] = trialend-self.timebase_offset

                except:
                    print("Error getting trial time period: [{}, {}] = [{}, {}]".format(self._stimevar, self._etimevar, t[self._stimevar], t[self._etimevar]))
                    import traceback
                    traceback.print_exc()
                finally:
                    trials.append(tuple(tbounds))

            # make pendata == concat'ed samples_by_trial
            pen_data = np.concatenate(samples_by_trial)

        else:
            # Normalize pen sample times so first sample starts at 0.0 sec.
            self.timebase_offset = pen_data['time'][0]
            self.autosegl1 = False

        # Normalize pen sample times so first sample starts at 0.0 sec.
        pen_data['time']-=self.timebase_offset

        trial_dtype = np.dtype({'names':['cvrow_ix','start_ix','start_time','end_ix','end_time'], 'formats':[np.int32,np.uint32,np.float64,np.uint32,np.float64]})
        self.trial_boundaries=np.asarray(trials,dtype=trial_dtype)
        return pen_data


    def _normalizeConditionVariableTimes(self):
        """
        Normalizes the time values for user specified condition variables.

        Using the app setting hdf5_apply_time_offset_var_select_filter,
        select matching condition variables and subtract the projects
        time offset from the cv values.
        :return:
        """
        if self._expcondvars is None:
            return
        cvnfilter = SETTINGS['hdf5_apply_time_offset_var_select_filter'].strip()
        if cvnfilter:
            normvarnames = getFilteredStringList(
                                    [unicode(cvn) for cvn in self._expcondvars.dtype.names],
                                    cvnfilter)
            for vn in normvarnames:
                # self._stimevar and self._etimevar values have already
                # been normalized, so skip any names that match either of those.
                if vn != self._stimevar and vn != self._etimevar:
                    self._expcondvars[vn]-=self.timebase_offset

    def _parsePenSampleSeries(self):
        """
        Find pen sample Series boundaries, using status
        field state FIRST_ENTER.
        If none exist, create a single Series that covers whole file.
        :return: ndarray with element dtype of ['id','start_ix','start_time','end_ix','end_time']
        """
        slist=[]
        festatus = SAMPLE_STATES['FIRST_ENTER']
        series_starts_ix =  list(*(self.pendata['state'] & festatus == festatus).nonzero())

        if len(series_starts_ix) == 0 or series_starts_ix[0]!=0:
            series_starts_ix.insert(0,0)
        series_stops_ix=series_starts_ix[1:]
        series_stops_ix.append(len(self.pendata))

        for i in range(len(series_starts_ix)):
            si, ei = series_starts_ix[i], series_stops_ix[i]
            ei=ei-1
            st, et = self.pendata['time'][[si, ei]]
            slist.append((i,si,st,ei,et))

        series_dtype = np.dtype({'names':['id','start_ix','start_time','end_ix','end_time'], 'formats':[np.uint16,np.uint32,np.float64,np.uint32,np.float64]})
        return np.asarray(slist,dtype=series_dtype)

    def createNewProject(self, file_path, fimporter):#, condvars=None, stime_var=None, etime_var=None):
            PenDataSegmentCategory.clearSegmentCache()

            self.updateProjectFileInfo(file_path, saved=False)
            self.updatePenDataFileInfo(file_path)

            self.autodetected_segment_tags=self._detectAssociatedSegmentTagsFile(self.projectfileinfo['folder'],self.projectfileinfo['shortname'], self.projectfileinfo['extension'])

            pen_data = fimporter.asarray(file_path)
            updateDataFileLoadingProgressDialog(self._mwapp)

            self._detectTrialPeriodConditionVariables(fimporter)
            updateDataFileLoadingProgressDialog(self._mwapp)

            self.pendata = self._parsePenDataByTrials(pen_data)
            updateDataFileLoadingProgressDialog(self._mwapp,10)

            self._normalizeConditionVariableTimes()

            self.nonzero_pressure_mask=self.pendata['pressure']>0
            # nonzero_regions_ix will be a tuple of (starts, stops, lengths) arrays
            self.nonzero_region_ix=contiguous_regions(self.nonzero_pressure_mask)
            updateDataFileLoadingProgressDialog(self._mwapp)

            self.segmenttree=PenDataSegmentCategory(name=self.name,project=self)
            self.pendata['segment_id']=self.segmenttree.id
            updateDataFileLoadingProgressDialog(self._mwapp)

            self.series_boundaries = self._parsePenSampleSeries()
            updateDataFileLoadingProgressDialog(self._mwapp)

            # 1) Filter each sample Series
            # 2) Calculate pen sample velocity and acceleration data.
            # 3) Detect Sample Runs within each Series.
            # 4) Detect pen stroke boundaries within
            #      a) full sample Series
            #      b) each sample Run within the Series
            self.run_boundaries=[]
            self._velocity_minima_ixs=[]
            self.velocity_minima_samples = None
            self.stroke_boundaries = []
            press_run_count=0
            for series_bounds in self.series_boundaries:
                # get sample array for current series
                pseries = self.pendata[
                        series_bounds['start_ix']:series_bounds['end_ix']+1]
                psb_start_ix = series_bounds['start_ix']

                # 1) Filter each sample Series
                filter_pen_sample_series(pseries)
                # 2) Calculate pen sample velocity and acceleration data.
                calculate_velocity(pseries)

                if SETTINGS['stroke_detect_pressed_runs_only'] is False:
                    # 4a) Detect pen stroke boundaries within current Series
                    self.findstrokes(pseries, psb_start_ix, series_bounds['id'])

                updateDataFileLoadingProgressDialog(self._mwapp)

                # 3) Detect Sample Runs within the Series.
                #    First attempt to use FIRST_PRESS pen sample state.
                fpstatus = SAMPLE_STATES['FIRST_PRESS']
                press_starts = list(*(pseries['state'] & fpstatus == fpstatus).nonzero())
                if len(press_starts) != 0:
                    if pseries['pressure'][0] > 0 and press_starts[0] != 0:
                        press_starts.insert(0,0)
                    press_stops=press_starts[1:]
                    press_stops.append(len(pseries))
                    # Add pressed period boundaries array for current series to
                    # the list of series pen pressed boundaries.
                    for i in range(len(press_starts)):
                        si = press_starts[i]
                        pressed_run_ixs = (pseries[si:press_stops[i]]['pressure']>0).nonzero()[0]
                        if len(pressed_run_ixs):
                            ei=si+pressed_run_ixs[-1]
                            st, et = pseries['time'][[si, ei]]
                            curr_press_series_id = press_run_count
                            press_run_count+=1
                            self.run_boundaries.append((curr_press_series_id,series_bounds['id'],psb_start_ix+si,st,psb_start_ix+ei,et))

                            if len(pressed_run_ixs) > 1 and SETTINGS['stroke_detect_pressed_runs_only'] is True:
                                # 4b) Detect pen stroke boundaries within each sample Run
                                self.findstrokes(pseries[si:ei+1], psb_start_ix+si, curr_press_series_id)
                        updateDataFileLoadingProgressDialog(self._mwapp)
                else:
                    # If no FIRST_PRESS pen sample states are found,
                    # use pen pressed periods (pressure > 0) to find Runs.
                    press_starts, press_stops, press_lenths = contiguous_regions(pseries['pressure'] > 0)
                    # Add pressed period boundaries array for current series to
                    # the list of series pen pressed boundaries.
                    for i in xrange(len(press_starts)):
                        si, ei = press_starts[i], press_stops[i]
                        try:
                            st, et = pseries['time'][[si, ei]]
                        except IndexError, err:
                            ei = ei-1
                            st, et = pseries['time'][[si, ei]]
                            press_stops[i]=ei
                        curr_press_series_id = press_run_count
                        press_run_count+=1
                        self.run_boundaries.append((curr_press_series_id,series_bounds['id'],psb_start_ix+si,st,psb_start_ix+ei,et))
                        if SETTINGS['stroke_detect_pressed_runs_only'] is True:
                            # 4b) Detect pen stroke boundaries within each sample Run
                            self.findstrokes(pseries[si:ei+1], psb_start_ix+si, curr_press_series_id)
                        updateDataFileLoadingProgressDialog(self._mwapp)

            # Convert run_boundaries list of lists into an ndarray
            run_dtype = np.dtype({'names':['id','parent_id','start_ix','start_time','end_ix','end_time'], 'formats':[np.uint16,np.uint16,np.uint32,np.float64,np.uint32,np.float64]})
            self.run_boundaries = np.asarray(self.run_boundaries, dtype=run_dtype)
            # Convert stroke_boundaries list of lists into an ndarray
            self.stroke_boundaries = np.asarray(self.stroke_boundaries, dtype=run_dtype)

            # Create ndarray of pen samples that are the detected stroke
            # boundary points.
            self.velocity_minima_samples = self.pendata[self._velocity_minima_ixs]

            if self._mwapp:
                # If project is being created via MarkWrite GUI, create
                # SelectedTimePeriodItem widget.
                if self._selectedtimeregion is None:
                    MarkWriteProject._selectedtimeregion = SelectedTimePeriodItem(project=self)
                else:
                    MarkWriteProject._selectedtimeregion.project = self
            else:
                # Otherwise, project is being created via custom script using
                # markwrite api, so create segments for any detected
                # trial periods.
                for t, tbounds in enumerate(self.trial_boundaries):
                    self.createSegmentForTimePeriod(u"Trial%d"%(t+1), self.segmenttree.id, tbounds['start_time'], tbounds['end_time'], update_segid_field=True)
            updateDataFileLoadingProgressDialog(self._mwapp,5)


    def findstrokes(self, searchsamplearray, obsolute_offset, parent_id):
        edge_type = SETTINGS['stroke_detect_edge_type']
        if edge_type == 'none':
            edge_type=None
        ppp_minima = detect_peaks(searchsamplearray['xy_velocity'],
                                  mph=None,
                                  mpd=SETTINGS['stroke_detect_min_p2p_sample_count'],
                                  edge=edge_type,
                                  valley=True)
        if len(ppp_minima)>1:
            for s,vmin_ix in enumerate(ppp_minima[:-1]):
                if s == 0:
                    vmin_ix = ppp_minima[0] = 0
                abs_vmin_ix = obsolute_offset+vmin_ix

                if ppp_minima[s+1] == ppp_minima[-1]:
                    next_abs_vmin_ix = obsolute_offset+len(searchsamplearray)-1
                else:
                    next_abs_vmin_ix = obsolute_offset+ppp_minima[s+1]
                if next_abs_vmin_ix >= len(self.pendata):
                    next_abs_vmin_ix=len(self.pendata)-1
                st, et = self.pendata['time'][[abs_vmin_ix, next_abs_vmin_ix]]
                self.stroke_boundaries.append((len(self.stroke_boundaries),parent_id,abs_vmin_ix,st,next_abs_vmin_ix,et))
                self._velocity_minima_ixs.append(abs_vmin_ix)
            next_abs_vmin_ix = obsolute_offset+len(searchsamplearray)-1
            if next_abs_vmin_ix >= len(self.pendata):
                next_abs_vmin_ix=len(self.pendata)-1
            self._velocity_minima_ixs.append(next_abs_vmin_ix)
        else:
            # add full run as one stroke
            self._velocity_minima_ixs.append(obsolute_offset)
            self._velocity_minima_ixs.append(obsolute_offset+len(searchsamplearray)-1)
            self.stroke_boundaries.append((len(self.stroke_boundaries),parent_id,
                                           obsolute_offset,
                                           searchsamplearray['time'][0],
                                           obsolute_offset+len(searchsamplearray)-1,
                                           searchsamplearray['time'][-1]))

    def getSeriesPeriodForTime(self, atime, positions='current'):
        """
        :param atime: the time to find the series for (if any)
        :param position: 'all', 'current', 'previous', or 'next'
        :return:
        """
        sb_start_times = self.series_boundaries['start_time']
        sb_end_times = self.series_boundaries['end_time']

        if positions == 'all':
            positions = ['previous', 'current', 'next']
        elif isinstance(positions, basestring):
            positions =[positions,]

        result = {}

        if 'current' in positions:
            result['current'] = None
            current = self.series_boundaries[(atime >= sb_start_times) & (atime <= sb_end_times)]
            if len(current)>0:
                result['current'] = current[0]

        nstime = pstime = atime
        current = result.get('current',None)
        if current:
            nstime = current['end_time']
            pstime = current['start_time']

        if 'next' in positions:
            result['next'] = None
            nexts = self.series_boundaries[sb_start_times >= nstime]
            if len(nexts)>0:
                result['next'] = nexts

        if 'previous' in positions:
            result['previous'] = None
            prevs = self.series_boundaries[sb_end_times <= pstime]
            if len(prevs)>0:
                result['previous'] = prevs

        return result

    def getNextUnitStartTime(self,unit_lookup_table, current_time):
        next_unit_ends = unit_lookup_table[unit_lookup_table['start_time'] > current_time]
        try:
            return next_unit_ends[0]['start_time']
        except:
            return None

    def getNextUnitEndTime(self,unit_lookup_table, current_time, adjust_end_time = False):
        next_unit_ends = unit_lookup_table[unit_lookup_table['end_time'] > current_time]
        try:
            if adjust_end_time is True:
                return self.pendata['time'][next_unit_ends[0]['end_ix']-1]
            return next_unit_ends[0]['end_time']
        except:
            return None

    def getPrevUnitStartTime(self,unit_lookup_table, current_time):
        prev_unit_starts = unit_lookup_table[unit_lookup_table['start_time'] < current_time]
        try:
            return prev_unit_starts[-1]['start_time']
        except:
            return None

    def getPrevUnitEndTime(self,unit_lookup_table, current_time, adjust_end_time = False):
        prev_unit_ends = unit_lookup_table[unit_lookup_table['end_time'] < current_time]
        try:
            if adjust_end_time is True:
                return self.pendata['time'][prev_unit_ends[-1]['end_ix']-1]
            return prev_unit_ends[-1]['end_time']
        except:
            return None

    def getNextUnitTimeRange(self, unit_lookup_table, adjust_end_time=False):
        if self.selectedtimeregion:
            selection_start, selection_end = self.selectedtimeregion.getRegion()
            mint, maxt = self.selectedtimeregion.getBounds()
            next_units = unit_lookup_table[unit_lookup_table['start_time'] > selection_start]
            try:
                if adjust_end_time is True:
                    st, et = max(next_units[0]['start_time'],mint), min(self.pendata['time'][next_units[0]['end_ix']-1], maxt)
                else:
                    st, et = max(next_units[0]['start_time'], mint), min(next_units[0]['end_time'], maxt)
                if st >= et:
                    return None
                return st, et
            except:
                return None

    def getPreviousUnitTimeRange(self, unit_lookup_table, adjust_end_time=False):
        if self.selectedtimeregion:
            selection_start, selection_end = self.selectedtimeregion.getRegion()
            mint, maxt = self.selectedtimeregion.getBounds()
            prev_units = unit_lookup_table[unit_lookup_table['start_time'] < selection_start]
            try:
                if adjust_end_time is True:
                    st, et = max(prev_units[-1]['start_time'], mint), min(self.pendata['time'][prev_units[-1]['end_ix']-1], maxt)
                else:
                    st, et = max(prev_units[-1]['start_time'], mint), min(prev_units[-1]['end_time'], maxt)
                if st >= et:
                    return None
                return st, et
            except:
                return None

    def getSeriesForSample(self, sample_index):
        starts = self.series_boundaries['start_ix']
        ends = self.series_boundaries['end_ix']
        series = self.series_boundaries[(sample_index >= starts) & (sample_index <= ends)]
        if len(series)>1:
            print "Error, > 1 stroke found:",sample_index, series
        elif len(series)==1:
            return series['id'][0]+1
        return 0

    def getPressedRunForSample(self, sample_index):
        starts = self.run_boundaries['start_ix']
        ends = self.run_boundaries['end_ix']
        run = self.run_boundaries[(sample_index >= starts) & (sample_index <= ends)]
        if len(run)>1:
            print "Error, > 1 stroke found:",sample_index, run
        elif len(run)==1:
            return run['id'][0]+1
        return 0

    def getStrokeForSample(self, sample_index):
        starts = self.stroke_boundaries['start_ix']
        ends = self.stroke_boundaries['end_ix']-1
        stroke = self.stroke_boundaries[(sample_index >= starts) & (sample_index <= ends)]
        if len(stroke)>1:
            print ">>>>>>>>\nError, %d strokes found for sample ix %d:"%(len(stroke), sample_index)
            for i, s in enumerate(stroke):
                print "\tSelected Stroke %d: "%(i), s
            print "Using last detected stroke for report.\n<<<<<<<"

        if len(stroke)>0 and len(stroke)<=2:
            return stroke['id'][-1]+1
        return 0

    def getSelectedDataSegmentIDs(self):
        if len(self.selectedpendata)>0:
            return np.unique(self.selectedpendata['segment_id'])
        return []

    def getPenDataForTimePeriod(self,tstart, tend, pendata=None):
        if pendata is None:
            pendata = self.pendata
        return pendata[(pendata['time'] >= tstart) & (pendata['time'] <=tend)]

    def createSegmentForTimePeriod(self, tag, parent_id, tstart, tend, id=None,
                                   update_segid_field = False):
        """

        :param tag:
        :param parent_id:
        :param tstart:
        :param tend:
        :return:
        """
        sparent = self.segmenttree.id2obj[parent_id]
        spendata = self.getPenDataForTimePeriod(tstart, tend)
        new_segment = PenDataSegment(name=tag, pendata=spendata, parent=sparent, fulltimerange=(tstart, tend), id=id)

        if update_segid_field is True:
            pendata = self.pendata
            mask = (pendata['time'] >= new_segment.starttime) & (pendata['time'] <= new_segment.endtime)
            self.pendata['segment_id'][mask]=new_segment.id
        self.modified = True
        return new_segment


    def createSegmentFromSelectedPenData(self, tag, parent_id):
        """
        **Only usable by MarkWrite GUI app.**

        Called if the currently selected pen data can make a valid segment.
        i.e. getSelectedDataSegmentIDs() returned a list of exactly 1 segment id

        Also ensure that self._selectedpendata has been trimmed as required
        based on enabled state of rules like the 0 pressure trim rule
        :param tag:
        :param parent_id:
        :return:
        """
        sparent = self.segmenttree.id2obj[parent_id]
        new_segment = PenDataSegment(name=tag, pendata=self.selectedpendata, parent=sparent, fulltimerange=self.selectedtimeperiod)

        pendata = self.pendata
        mask = (pendata['time'] >= new_segment.starttime) & (pendata['time'] <= new_segment.endtime)
        self.pendata['segment_id'][mask]=new_segment.id
        self.modified = True
        return new_segment

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, v):
        self._modified = bool(v)

    @property
    def allpendata(self):
        return self.pendata

    @property
    def unsegmentedpendata(self):
        return self.pendata[self.pendata['segment_id']==0]

    @property
    def segmentedpendata(self):
        return self.pendata[self.pendata['segment_id']>0]

    @property
    def selectedtimeregion(self):
        return self._selectedtimeregion

    @property
    def selectedtimeperiod(self):
        if self._selectedtimeregion:
            return self._selectedtimeregion.getRegion()
        return [0.0,0.0]

    @property
    def selecteddatatimerange(self):
        if len(self.selectedpendata)>0:
            return self.selectedpendata['time'][[0,-1]]

    @property
    def selectedpendata(self):
        if self._selectedtimeregion:
            return self._selectedtimeregion.selectedpendata
        return []

    def isSelectedDataValidForNewSegment(self):
        if len(self.selectedpendata)>0:
            sids = self.getSelectedDataSegmentIDs()
            if len(sids)==1:
                if sids[0] == 0:
                    return True
                if self.segmenttree.id2obj[sids[0]].pointcount > self.selectedpendata.shape[0]:
                    return True
        return False

    def save(self):
        if os.path.exists(self.projectfileinfo['abspath']):
            return self.saveAs(self.projectfileinfo['abspath'])
        return False


    def saveAs(self, tofile):
        try:
            self.updateProjectFileInfo(tofile, saved=True)
            projdict = self.toDict()
            pdir, pfile = os.path.split(tofile)
            writePickle(pdir, pfile, projdict)
            self.modified = False
            return True
        except:
            return False

    def openFromProjectFile(self, proj_file_path, fimporter):
        PenDataSegmentCategory.clearSegmentCache()
        projdict = fimporter(*os.path.split(proj_file_path))
        projattrnames = projdict.keys()

        self.updateProjectFileInfo(proj_file_path)

        # Handle segment tree specially
        segmenttree = projdict.get('segmenttree')
        projattrnames.remove('segmenttree')

        for aname in projattrnames:
            aval = projdict[aname]
            setattr(self,aname,aval)
            projdict[aname]=None
        del projdict

        self.segmenttree = PenDataSegmentCategory.fromDict(segmenttree, self, None)

        if self._mwapp:
            if self._selectedtimeregion is None:
                MarkWriteProject._selectedtimeregion = SelectedTimePeriodItem(project=self)
            else:
                MarkWriteProject._selectedtimeregion.project = self
        self.modified = False

    def close(self):
        """
        Close the MarkWrite project, including closing any imported data files.
        Return a bool indicating if the close operation was successful or not.

        :return: bool
        """
        self._selectedtimeregion = None
        for a in self.serialize_attributes:
            setattr(self,a,None)
        return True

    def __del__(self):
        self.close()