# -*- coding: utf-8 -*-
from __future__ import division
from markwrite.reports import ReportExporter
from markwrite.util import convertSampleStateValue
import numpy as np
#from weakref import proxy
#from time import time as time

#%%
class RawSampleDataReportExporter(ReportExporter):
    progress_dialog_title = "Saving the Raw Pen Point Sample Report .."
    formating=dict(time=u'{:.3f}')
    segpathsep=u'->'
    
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        # Return the name of each 'column' of the project.pendata
        # numpy array.
        # Note that the report cls has a 'project' attribute
        # that can be used to access the project in use when
        # generating the report
        r = ['index',]
        r.extend(cls.project.pendata.dtype.names)
        r.extend(('status','series_id','run_id','stroke_id'
                ))
        return r

    @classmethod
    def datarowcount(cls):
        # Return the number of pen samples that will be saved
        # in the report. Each sample will be a report data row.
        return cls.project.pendata.shape[0]

    @classmethod
    def datarows(cls):
        
        # Iterate through the pen data array, yielding each pen sample
        # as a list.
        getSeriesForSample = cls.project.getSeriesForSample
        getPressedRunForSample = cls.project.getPressedRunForSample
        getStrokeForSample = cls.project.getStrokeForSample

        for i, pensample in enumerate(cls.project.pendata):
            r = [i,]
            r.extend(pensample.tolist())
            r.extend((convertSampleStateValue(pensample['state']), 
                        getSeriesForSample(i),
                        getPressedRunForSample(i),
                        getStrokeForSample(i)
                        ))
            yield r

#%%
class DetailedSegmentReportExporter(ReportExporter):
  
    """
	Provides various segment-level measures.
	written rather quickly by mark.torrance@ntu.ac.uk, April 2016
	based on Sol's SegmentReport
	
	Although I have  done some testing, I recommend some thorough
	cross checking. Let me know any issues or, better, improve 
	the report yourself and let me have a copy!
	
	Note that this report does not yet include any measures related 
	to GetWrite (PsychoPy) events (e.g., time from stimulus onset
	to first press).
	
	
    Segment level report outputs one row per segment within the project.
    Columns are:
	variable name | description
	:----|:----
	seg_id | Name of file with segment data. This will be a markwrite peoject (wmp) file
	category | The name of the highest level segment in the current segment tree.
	level | Level of current segment if segment tree.
	segpath | Full path of segment.
	name | Name (tag) assigned to the segment
	start_time | Start time of the segment, in sec.msec format.
	end_time | End time of the segment, in sec.msec format.
	duration | Segment duration (end time - start time)
	start_index | The index of the segment's first pen sample point in the full sample array (0 based indexing)
	starts_with_press | First sample in segment is a pen press (i.e. pressure > 0)
	end_index | The index of the segment's last pen sample point in the full sample array (0 based indexing)
	sample_count | Number of samples in segment
	subsegment_count | Number of subsegment (children) embraced by this segment.
	prev_penpress_time | Time of the last pen-press (inking) sample 
	prev_pause | "Pause" prior to start of segment: start_time - prev_penpress_time
	prev_xy_displacement | length of straight line drawn between previous pen-press and location of first sample in segment (calculated regardless of whether or not the segment starts with a pen-press)
	prev_notpress_tracelength | Total "trace" length of pen tip between last pen-press and first sample of segment. This is the sum of straight-line distances between all hover samples, including cases where the pen goes out of range between samples.
	prev_trace_disp_ratio | prev_notpress_tracelength / prev_xy_displacement  Gives an indication of how much pen-waving occurred between during pen-lift prior to segment.
	next_penpress_time | Time of first pen-press immediately following segment.
	x_displacement | Distance in the x axis between first and final sample in segment (including non-press samples).
	y_displacement | Distance in the y axis between first and final sample in segment (including non-press samples).
	pentrace_length | total of distance moved by pen-tip between samples.
	hover_pentrace_len | total of straight-line distance between samples, when not pressed.
	press_pentrace_len | total of straight-line distance between samples, when pen is pressed. This therefore represents length of the inked lines of recorded by the digitiser).
	time_hover | Total time the pen was in the air but within range of the digitiser during the segment period.
	time_press | Total time pen was in contact with digitiser surface during segment period.
	time_notpress | duration - time_press: Total time in segment when the pen was not pressed on the digitiser surface.
	time_outrange | duration - time_press - time_hover: Total time in segment when pen was not recording.

    """
    progress_dialog_title = "Saving Pen Data Segmentation Report .."
    progress_update_rate=1
    segpathsep=u'->'
    
    def __init__(self):
        ReportExporter.__init__(self)
        self.pbs = (.05,.25),(.25,.75),(.75,2),(2,3),(3,10),(10,240) #pause boundaries
        
    @classmethod
    def datarowcount(cls):
        return cls.project.segmenttree.totalsegmentcount

    @classmethod
    def datarows(cls):
        
        sample_states = {1: 'FIRST_ENTER',
         2: 'FIRST_HOVER',
         4: 'HOVERING',
         8: 'FIRST_PRESS',
         16: 'PRESSED'}
        
        def sv2state(sv):
            return [v for k, v in sample_states.items() if sv&k==k]
        
        def in_state(x,state):
            return state in sv2state(x)
            
        vin_state = np.vectorize(in_state)         
        
        pendata = cls.project.pendata
        #pointcount=pendata.shape[0]
        nonzero_pressure_ixs = np.nonzero(pendata['pressure'])[0]
        
        ISIs = np.append(np.NAN,pendata['time'][1:]-pendata['time'][:-1])
        
        #pen moves (displacement) between samples
        y_disps = np.append(np.NAN,pendata['y_filtered'][1:]-pendata['y_filtered'][:-1])
        x_disps = np.append(np.NAN,pendata['x_filtered'][1:]-pendata['x_filtered'][:-1])
        xy_disps = (y_disps**2 + x_disps**2)**.5
        
        segment_tree = cls.project.segmenttree

        catname = segment_tree.name
        filename=catname=segment_tree.name

        for level_num, segment_list in cls.project.segmenttree.getLeveledSegments().items():
            for segment in segment_list:
                segpath = cls.segpathsep.join(segment.path)
                stime, etime = segment.timerange
                six, eix = segment_tree.calculateTrimmedSegmentIndexBoundsFromTimeRange(stime, etime)
                duration = round(etime - stime,4)
                subsegment_count = len(segment.children)
                
                SISIs = np.round(ISIs[six+1:eix+1],4) #segment ISI
                states = pendata['state'][six+1:eix+1]
                
                #times between penpress samples, ignoring all others
                #so the ISI for a press that follows a pen lift will be time to the previous
                #press sample
                ptimes = pendata['time'][six:eix][pendata['pressure'][six:eix] > 0]
                pressed_SISIs = ptimes[1:]-ptimes[:-1]
                
                
                #preceding pause variables
                prev_penpress_time=''
                next_penpress_time=''
                prev_pause=''
                prev_xy_disp=''
                prev_notpress_tracelength=''
                prev_trace_disp_ratio = ''
                
                #default values
                x_disp = cls.missingval
                y_disp = cls.missingval
                xy_disp = cls.missingval
                hover_xy_disp = cls.missingval
                press_xy_disp = cls.missingval
                pause_counts = []
                duration2 = cls.missingval             
                hovertime = cls.missingval 
                presstime = cls.missingval
                not_presstime = cls.missingval
                outrange_time = cls.missingval


                if six > 0:
                    try:
                        prev_penpress_time = pendata['time'][0:six][pendata['pressure'][0:six] > 0][-1]
                        prev_pause = round(stime - prev_penpress_time,4)
                    except: pass                        
                    
                    try:
                        x = (pendata['x_filtered'][six] 
                                - pendata['x_filtered'][np.where(pendata['time'] == prev_penpress_time)])
                        y = (pendata['y_filtered'][six]
                                - pendata['y_filtered'][np.where(pendata['time'] == prev_penpress_time)])
                        prev_xy_disp = int((x**2 + y**2)**.5)
                        prev_notpress_tracelength = (
                            int(sum(xy_disps[int(np.where(pendata['time'] == prev_penpress_time)[0])+1:six])))
                        prev_trace_disp_ratio = round(prev_notpress_tracelength / prev_xy_disp,4)
                    except: pass
                                              
                
                if eix < max(nonzero_pressure_ixs):
                    next_nonzero_ix = nonzero_pressure_ixs[np.searchsorted(nonzero_pressure_ixs, eix, side='left')+1]
                    next_penpress_time = round(pendata['time'][next_nonzero_ix],4)             
                
                starts_with_press = pendata['pressure'][six] > 0
                
                if eix > six:
                    x_disp = int(pendata['x_filtered'][eix]-pendata['x_filtered'][six])
                    y_disp = int(pendata['y_filtered'][eix]-pendata['y_filtered'][six])
                    xy_disp = int(sum(xy_disps[six+1:eix]))

                    hover_xy_disp = int(sum(xy_disps[six+1:eix]*vin_state(states,'HOVERING')[:-1]))
                    press_xy_disp = int(sum(xy_disps[six+1:eix]*vin_state(states,'PRESSED')[:-1]))                
                
                    duration2 = sum(SISIs)   #for checking against duration             
                    hovertime = sum(SISIs*vin_state(states,'HOVERING')) 
                    presstime = sum(SISIs*vin_state(states,'PRESSED'))
                    not_presstime = round(duration - presstime, 4)
                    outrange_time = round(duration - presstime - hovertime, 4)
                
                #get puase vars
                for mn,mx in DetailedSegmentReportExporter().pbs:
                    pause_counts.append(len(pressed_SISIs[(pressed_SISIs >= mn) & (pressed_SISIs < mx)]))             
                                                    
                rowdata = [filename,
                       segment.id,
                       catname,
                       level_num,
                       segpath,
                       segment.name,
                       round(stime,4),
                       round(etime,4),
                       round(duration,4),
                       duration2,
                       six,
                       starts_with_press,
                       eix,
                       segment.pointcount,
                       subsegment_count,
                       prev_penpress_time,
                       prev_pause,
                       prev_xy_disp,
                       prev_notpress_tracelength,
                       prev_trace_disp_ratio,
                       next_penpress_time,
                       x_disp,
                       y_disp,
                       xy_disp,
                       hover_xy_disp,
                       press_xy_disp,
                       hovertime,
                       presstime,
                       not_presstime,
                       outrange_time
                       ]
                
                rowdata.extend(pause_counts)
                
                yield rowdata

    @classmethod
    def columnnames(cls):
        column_names=['file',
                      'seg_id',
                      'category',
                      'level',
                      'segpath',
                      'name',
                      'start_time',
                      'end_time',
                      'duration',
                      'duration_check',
                      'start_index',
                      'starts_with_press',
                      'end_index',
                      'sample_count',
                      'subsegment_count',
                      'prev_penpress_time',
                      'prev_pause',
                      'prev_xy_displacement',
                      'prev_notpress_tracelength',
                      'prev_trace_disp_ratio',
                      'next_penpress_time',
                      'x_displacement',
                      'y_displacement',
                      'pentrace_length',
                      'hover_pentrace_len',
                      'press_pentrace_len',
                      'time_hover',
                      'time_press',
                      'time_notpress',
                      'time_outrange'
                      ]                      
        column_names.extend([str(p[0])+'-'+str(p[1])+'_count' for p in DetailedSegmentReportExporter().pbs])
                         
        return column_names

#%%       
class RawSampleDataReportPlusSegsExporter(ReportExporter):
    progress_dialog_title = "Saving the Raw Pen Point Sample Report .."
    formating=dict(time=u'{:.3f}')
    segpathsep=u'->'
    
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        # Return the name of each 'column' of the project.pendata
        # numpy array.
        # Note that the report cls has a 'project' attribute
        # that can be used to access the project in use when
        # generating the report
        r = ['index',]
        r.extend(cls.project.pendata.dtype.names)
        r.extend(('status','series_id','run_id','stroke_id',
                  'seg_level','seg_path','seg_name'
                ))
        return r

    @classmethod
    def datarowcount(cls):
        # Return the number of pen samples that will be saved
        # in the report. Each sample will be a report data row.
        return cls.project.pendata.shape[0]

    @classmethod
    def datarows(cls):
        # make segment dictionary
        segs = {}
        for level_num, segment_list in cls.project.segmenttree.getLeveledSegments().items():
            for segment in segment_list:
                segpath = cls.segpathsep.join([u'{}'.format(sp) for sp in segment.path])
                segs[segment.id] = (level_num,segpath,segment.name)
         
        # Iterate through the pen data array, yielding each pen sample
        # as a list.
        getSeriesForSample = cls.project.getSeriesForSample
        getPressedRunForSample = cls.project.getPressedRunForSample
        getStrokeForSample = cls.project.getStrokeForSample

        for i, pensample in enumerate(cls.project.pendata):
            r = [i,]
            r.extend(pensample.tolist())
            r.extend((convertSampleStateValue(pensample['state']), 
                        getSeriesForSample(i),
                        getPressedRunForSample(i),
                        getStrokeForSample(i),
                        segs.get(pensample['segment_id'],('','',''))[0],
                        segs.get(pensample['segment_id'],('','',''))[1],
                        segs.get(pensample['segment_id'],('','',''))[2]
                        ))
            yield r

#%%
class PenSampleReportExporter(ReportExporter):
    progress_dialog_title = "Saving Pen Point Sample Level Report .."
    progress_update_rate=10
    formating=dict(time=u'{:.3f}')
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        column_names=['file','index','time','x','y','pressure', 'status', 'cat1']
        ss = cls.project.segmenttree
        lvls = range(1,ss.getLevelCount()+1)
        column_names.extend([u'cat1.L%d'%l for l in lvls])
        
        if len(cls.project.trial_cond_vars):
            column_names.extend(cls.project.trial_cond_vars.dtype.names)
            
        return column_names

    @classmethod
    def datarowcount(cls):
        return cls.project.pendata.shape[0]

    @classmethod
    def datarows(cls):
        pendata = cls.project.pendata

        ss = cls.project.segmenttree
        sfile=ss.name

        lvls = range(1,ss.getLevelCount()+1)

        segs_by_lvl=ss.getLeveledSegments()
        catname = ss.name

        cvcolcount=0
        if len(cls.project.trial_cond_vars):
            cvcolcount=len(cls.project.trial_cond_vars.dtype.names)

        for i in xrange(pendata.shape[0]):
            dp=pendata[i]


            rowdata = [sfile,i,dp['time'],dp['x'],dp['y'],dp['pressure'],
                       convertSampleStateValue(dp['state']), catname]

            # Go through segment levels finding matching seg at each level for
            # current data point. Use '' for levels where no seg matched
            # data point time, otherwise use segment name.
            for l in lvls:
                dpsegname=cls.missingval
                for seg in segs_by_lvl[l]:
                    if seg.contains(time=dp['time']):
                        dpsegname=seg.name
                        break
                # If no seg was found at this level, none will exist at lower
                # levels for this point, so break the loop. Remaining col vals
                # will automatically be filled in by ReportExporter
                if dpsegname == cls.missingval:
                    break
                rowdata.append(dpsegname)

            if cvcolcount:
                tcv=cls.project.getTrialConditionsForSample(i)
                if tcv is not None:
                    rowdata.extend(list(tcv))
                else:
                    rowdata.extend([cls.missingval for i in range(cvcolcount)])
            yield rowdata