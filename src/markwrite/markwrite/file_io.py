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
import numpy as np
from util import getSegmentTagsFilePath, SAMPLE_STATES, contiguous_regions
import codecs
import os
import traceback
from gui.projectsettings import SETTINGS
            
markwrite_pendata_format = [('time', np.float64),
                    ('x', np.int32),
                    ('y', np.int32),
                    ('pressure', np.int16),
                    ('state', np.uint8),
                    # Following are set by MarkWrite
                    ('x_filtered', np.float64),
                    ('y_filtered', np.float64),
                    ('pressure_filtered', np.float64),
                    ('x_velocity', np.float64),
                    ('y_velocity', np.float64),
                    ('xy_velocity', np.float64),
                    ('xy_acceleration', np.float64),
                    ('segment_id', np.uint16)]


class DataImporter(object):
    '''
    Parent class for all data import formatters. Each subclass must implement
    the .validate(file_path), .parse(file_path), and optionally 
    .setstatusdata(pendata)

    Use .asarray(file_path) to return the formatted input data as a numpy array
    with dtype markwrite_pendata_format
    
    The array returned by .asarray() will already have already had status data
    processed by the setstatusdata() implementaton. Default setstatusdata 
    is a direct pass through of the pendata array, with no changes made.
    '''
    _ADD_SAMPLE_COL_COUNT = 8
    def __init__(self):
        pass

    @classmethod
    def validate(cls, file_path):
        '''
        Checks that the file pointed to by file_path is formatted as expected
        by the DataImporter subclass being used.
        :param file_path: string providing path to file to open
        :return: bool
        '''
        return True

    @classmethod
    def parse(cls, file_path):
        '''
        Return a list of tuples, with each tuple representing a single data
        point parsed from the file. Each tuple must have 5 elements, with the
        following format:
            0,  'time', double
            1,  'x', int
            2,  'y', int
            3,  'pressure', int
            4,  'status', uint8

        For example, a list with three data points would look like:

            [(1111, 500, 250, 128, 0),
             (1115, 600, 190, 212, 0),
             (1119, 550, 210, 255, 0)]

        This method is only called if .validate(file_path) returns True.

        :param file_path:
        :return: list
        '''
        return []

    @classmethod
    def asarray(cls, file_path):
        '''
        Read the file pointed to by file_path, extract the pen digitizer data,
        and return the data as a numpy ndarray.

        :param file_path:
        :return:
        '''
        if cls.validate(file_path) is False:
            raise IOError("File could not be imported. Invalid format for DataImporter.")

        txyps_array = [s+(0,)*cls._ADD_SAMPLE_COL_COUNT for s in cls.parse(file_path)]        
        
        return cls.postprocess(np.asarray(txyps_array, markwrite_pendata_format))

    @classmethod
    def postprocess(cls, pendata):
        """
        Process the pendata array, updating sample data as needed. 
        
        Intended to be used to set the status column of the sample array 
        for data file types that do not provide status information, or can not
        set it within the .parse() method
        
        Default implementation is to return the pendata array unmodified.
        """
        return pendata
#
# E&P Syle Text File Importer (*.eptxyp)
#

class EyePenDataImporter(DataImporter):
    TIME_COLUMN_IX = 0
    X_COLUMN_IX = 1
    Y_COLUMN_IX = 2
    PRESS_COLUMN_IX = 3

    DATA_START_LINE_INDEX = 2

    def __init__(self):
        DataImporter.__init__(self)

    @classmethod
    def validate(cls, file_path):
        line1 = u'T	X	Y	P'
        with codecs.open(file_path, "r", "utf-8") as f:
            return f.readline().startswith(line1)
        return False

    @classmethod
    def parse(cls, file_path):
        list_result = []
        with codecs.open(file_path, "r", "utf-8") as f:
            last_sample=None
            for line_index, tab_line in enumerate(f):
                if line_index < cls.DATA_START_LINE_INDEX:
                    # skip hearer row and first row of 0's
                    continue
                try:
                    line_tokens = tab_line.split(u'\t')
                    xp = int(line_tokens[cls.X_COLUMN_IX].strip())
                    yp = int(line_tokens[cls.Y_COLUMN_IX].strip())
                    spress = int(line_tokens[cls.PRESS_COLUMN_IX].strip(u' \r\n'))

                    # All samples in txyp file are pressed samples
                    status = SAMPLE_STATES['PRESSED']

                    #skip any 0 pressure samples and set last_sample to None
                    if spress == 0:# and last_sample and last_sample[cls.X_COLUMN_IX] == xp and last_sample[cls.Y_COLUMN_IX] == yp:
                            # skip sample and set last_sample to None
                            last_sample = None
                            continue

                    if last_sample is None:
                        status += SAMPLE_STATES['FIRST_PRESS']

                    dsample = (float(line_tokens[cls.TIME_COLUMN_IX].strip())/1000.0,
                         xp,
                         yp,
                         spress,
                         status
                         ) 
                    last_sample=dsample
                    list_result.append(dsample)

                except IndexError:
                    print("Note: Skipping Line {0}. Contains {1} Tokens.".format(len(list_result), len(line_tokens)))

        return list_result
#
# Generic Tab Delimited File Importer  (*.txyp)
#
class TabDelimitedDataImporter(DataImporter):
    TIME_COLUMN_IX = 0
    X_COLUMN_IX = 1
    Y_COLUMN_IX = 2
    PRESS_COLUMN_IX = 3

    DATA_START_LINE_INDEX = 1

    exp_condvars = None
    condvars_names = None  
            
    def __init__(self):
        DataImporter.__init__(self)

    @classmethod
    def validate(cls, file_path):
        line1 = u'T	X	Y	P'
        with codecs.open(file_path, "r", "utf-8") as f:
            ffl1=f.readline().strip(u' \r\n')
            return ffl1.startswith(line1)
        return False

    @classmethod
    def parse(cls, file_path):
        list_result = []
        condvars_array=[]
        with codecs.open(file_path, "r", "utf-8") as f:
            cls.exp_condvars = None
            cls.condvars_names = None  
            for line_index, tab_line in enumerate(f):
                tab_line = tab_line.strip(u' \r\n')
                if line_index < cls.DATA_START_LINE_INDEX:
                    # skip hearer row
                    continue
                try:
                    tab_line = tab_line.replace(u'\t', u' ')
                    if tab_line.startswith(u'!TRIAL_CV_LABELS'):
                        if cls.condvars_names is None:
                            line_tokens = tab_line.split(u' ')
                            cls.condvars_names = [str(n) for n in line_tokens[1:]]
                        continue

                    if tab_line.startswith(u'!TRIAL_CV_VALUES'):
                        line_tokens = tab_line.split(u' ')
                        condvars_array.append(tuple(line_tokens[1:]))
                        continue
                    
                    line_tokens = tab_line.split(u' ')
                    list_result.append(
                    (float(line_tokens[cls.TIME_COLUMN_IX].strip())/1000.0,
                         int(line_tokens[cls.X_COLUMN_IX].strip()),
                         int(line_tokens[cls.Y_COLUMN_IX].strip()),
                         int(line_tokens[cls.PRESS_COLUMN_IX]),
                         0
                         ))

                except IndexError:
                    print("Note: Skipping Line {0}. Contains {1} Tokens.".format(len(list_result), len(line_tokens)))

            if cls.condvars_names and condvars_array:
                cvdtype=[]
                for i, lt in enumerate(condvars_array[0]):
                    etype = 'U16'
                    try:
                        lt = int(lt)
                        etype = np.int64
                    except:
                        try:
                            lt = float(lt)
                            etype = np.float64
                        except: 
                            pass
                    cvdtype.append((cls.condvars_names[i], etype))
                cvdtype = np.dtype(cvdtype)
                    
                temparray_ = []
                for cv_list in condvars_array:
                    temp_elem_=[]
                    for i, cv in enumerate(cv_list):
                        try:
                            cv = int(cv)
                        except:
                            try:
                                cv = float(cv)
                            except: 
                                pass
                        if cls.condvars_names[i].find("TRIAL_START")>=0:
                            cv = cv / 1000.0    
                        elif cls.condvars_names[i].find("TRIAL_END")>=0:
                            cv = cv / 1000.0    
                        temp_elem_.append(cv)                        
                    temparray_.append(tuple(temp_elem_))
                condvars_array = temparray_

                cls.exp_condvars = np.asarray(condvars_array, dtype=cvdtype)
        return list_result

    @classmethod
    def postprocess(cls,pendata):
        # Set initial sample state to HOVERING or PRESSED based on pressure
        pendata['state'][pendata['pressure']==0]=SAMPLE_STATES["HOVERING"]
        pendata['state'][pendata['pressure']>0]=SAMPLE_STATES["PRESSED"]

        # Calculate ISI value for samples 1-N
        sample_dts = pendata['time'][1:]-pendata['time'][:-1]
                
        # Handle non monotonic time stamped samples
        non_mono_ix = (sample_dts < 0.0).nonzero()[0]    
        if len(non_mono_ix)>0:
            non_mono_ix = non_mono_ix + 1
            print ">>>>>>>"
            print "WARNING: Non-monotonic Timestamps Detected."
            print "         Removing %d sample(s) with negative ISIs...."%(len(non_mono_ix))
            print "         Sample Indices:",non_mono_ix
            print "<<<<<<<"
            print
            # TODO: This code needs updating, it is a quick and dirty fix.
            #       Simply removes samples with negative ISI. In Guidos files,
            #       this seems to only occur within the first few samples
            #       of the file, if at all.
            pendata = np.delete(pendata,non_mono_ix)
            sample_dts = pendata['time'][1:]-pendata['time'][:-1]

        #
        # Detect Series Boundaries Using an ISI Threshold alg.
        #
        # Determine ISI threshold value to use
        if SETTINGS['series_detect_max_isi_msec'] > 0:
            series_isi_thresh = SETTINGS['series_detect_max_isi_msec']/1000.0
        else:
            try:
                series_isi_thresh = np.percentile(sample_dts,99.0,interpolation='nearest')*2.5
            except TypeError: 
                series_isi_thresh = np.percentile(sample_dts,99.0)*2.5
        print "series_isi_thresh:",series_isi_thresh
        print
        
        # Find sample array ix where ISI threshold is exceeded.
        # These are the series start ix
        series_start_ixs = (sample_dts > series_isi_thresh).nonzero()[0]
        if len(series_start_ixs)>0:
            series_start_ixs=series_start_ixs+1
        # First sample in data file is always a series start.
        series_start_ixs = np.insert(series_start_ixs, 0, 0)
        # Create list of series_start, series_end indexs for slicing
        series_bounds = []  # holds (series_start_ix, series_end_ix, 
                            # series_len, stime, etime, series_dur, series_dur/series_len)
        for i, start_ix in enumerate(series_start_ixs[:-1]):
            end_ix = series_start_ixs[i+1]
            stime, etime = pendata['time'][[start_ix,end_ix-1]]
            sdur = etime - stime 
            slen = end_ix-start_ix
            series_bounds.append((start_ix,end_ix,
                                  slen,stime, etime,sdur,sdur/slen))
        start_ix, end_ix = series_start_ixs[-1], len(pendata)
        stime, etime = pendata['time'][[start_ix,end_ix-1]]
        sdur = etime - stime 
        slen = end_ix-start_ix                         
        series_bounds.append((start_ix,end_ix,
                              slen,stime, etime,sdur,sdur/(slen-1)))

        # For each Sample Series in the data file,
        # 1) handle duplicate sample timestamps
        # 2) set FIRST_PRESS and FIRST_HOVER sample status as needed. 
        for i, sb in enumerate(series_bounds):
            # Cleanup duplicate timestamps after series bounds have been found
            # TODO: This code needs updating, it is a quick and dirty fix.
            #       A constant ISI across all series should really be used.
            dup_ix = (sample_dts[sb[0]:sb[1]] == 0.0).nonzero()[0]# + sb[0]    
            if len(dup_ix)>0:
                start_ix, end_ix, slen, stime, etime, sdur, sampling_interval = sb
                calc_sample_times, calc_isi = np.linspace(etime-slen*sampling_interval,etime,slen,retstep=True)
                print ">>>>>>>"
                print "Warning: Duplicate timestamps found in series", i+1, (stime, etime)
                print "         Sample / Duplicate Count:",slen,'/',len(dup_ix)
                print "         Calc. Series ISI:",calc_isi
                print "         Updating Series sample times......."
                print "<<<<<<<"
                print
                pendata['time'][start_ix:end_ix] = calc_sample_times[:]

            # Update sample state field to include FIRST_PRESS as needed
            run_start_ixs, _, _ = contiguous_regions(pendata['state'][sb[0]:sb[1]] == SAMPLE_STATES["PRESSED"])
            if len(run_start_ixs):
                run_start_ixs = np.array(run_start_ixs, dtype=np.uint32) + sb[0]
                pendata['state'][run_start_ixs]+= SAMPLE_STATES['FIRST_PRESS']        
            # Update sample state field to include FIRST_HOVER as needed
            hover_start_ixs, _, _ = contiguous_regions(pendata['state'][sb[0]:sb[1]] == SAMPLE_STATES["HOVERING"])
            if len(hover_start_ixs):
                hover_start_ixs = np.array(hover_start_ixs, dtype=np.uint32) + sb[0]
                pendata['state'][hover_start_ixs]+= SAMPLE_STATES['FIRST_HOVER']

        # For whole sample array, update series start sample's status
        # with FIRST_ENTER value.
        if len(series_start_ixs):
            pendata['state'][series_start_ixs] += SAMPLE_STATES['FIRST_ENTER']        
        
        # Return pendata array with sample state field populated.
        return pendata

#
# ioHub HDF5 File Importer  (*.hdf5)
#
from tables import openFile
from collections import namedtuple

class HubDatastoreImporter(DataImporter):
    hdfFile = None
    exp_condvars = None
    condvars_names = None
    WINTAB_TABLET_SAMPLE=91
    def __init__(self):
        DataImporter.__init__(self)


    @classmethod
    def _getEventMappingInformation(cls):
        """
        Returns details on how ioHub Event Types are mapped to tables within
        the given DataStore file.
        """
        if cls.hdfFile:
            eventMappings=dict()
            class_2_table=cls.hdfFile.root.class_table_mapping
            EventTableMapping=namedtuple('EventTableMapping',cls.hdfFile.root.class_table_mapping.colnames)
            for row in class_2_table[:]:
                eventMappings[row['class_id']]=EventTableMapping(*row)
            return eventMappings
        return None
        
    @classmethod
    def _getPenSampleEvents(cls, condition_str = None):
        """
        Get the Pen Sample Events from the iohub hdf5 file.
        Return value is a row iterator for events of that type.
        """
        event_mapping_info=cls._getEventMappingInformation().get(cls.WINTAB_TABLET_SAMPLE)
        if event_mapping_info:
            cond="(type == %d)"%(cls.WINTAB_TABLET_SAMPLE)
            if condition_str:
                cond+=" & "+condition_str
            return cls.hdfFile.getNode(event_mapping_info.table_path).where(cond).next()
        return []

    @classmethod
    def _close(cls):
        if cls.hdfFile:
            cls.hdfFile.close()
            cls.hdfFile = None
    
    @classmethod
    def _load(cls, file_path):
        try:
            cls._close()
            cls.hdfFile=openFile(file_path, 'r')
            return cls.hdfFile
        except:
            print "Error openning ioHub HDF5 file."
            traceback.print_exc()
        return None

    @classmethod
    def validate(cls, file_path):
        file_valid = False
        if cls._load(file_path):
            if cls._getPenSampleEvents():
                file_valid = True    
        cls._close()
        return file_valid

    @classmethod
    def parse(cls, file_path):
        list_result = []
        if cls._load(file_path) is None:
            return list_result

        for r in cls._getPenSampleEvents():
            list_result.append((
                             r['time'],
                             r['x'],
                             r['y'],
                             r['pressure'],
                             r['status'] # state field
                             ))

        try:
            cls.exp_condvars = None
            cls.condvars_names = None            
            cv_group = cls.hdfFile.root.data_collection.condition_variables
            if "EXP_CV_1" in cv_group._v_leaves:
                cls.exp_condvars = cv_group._v_leaves["EXP_CV_1"].read()
                cls.condvars_names = cls.exp_condvars.dtype.names
        except:
            cls.exp_condvars = None
            cls.condvars_names = None

        cls._close()
        return list_result

    def __del__(self):
        self._close()

#
# XML Format Importer (*.xml)
#
import xml.etree.ElementTree as ET

class XmlDataImporter(DataImporter):
    def __init__(self):
        DataImporter.__init__(self)

    @classmethod
    def validate(cls, file_path):
        try:
            xml_root = ET.parse(file_path)
            # TODO: Use element near start of file to verify that XML
            # file contains expected format. For example "xmlns:tns"
            return xml_root is not None
        except:
            pass
        return False

    @classmethod
    def parse(cls, file_path):
        list_result = []
        xml_root = ET.parse(file_path).getroot()
        for stroke_set in xml_root.iter(u'strokes'):
            si=0
            for stroke in stroke_set.iter(u'stroke'):
                status = SAMPLE_STATES['PRESSED']
                if si == 0:
                    status += SAMPLE_STATES['FIRST_PRESS']

                list_result.append((long(stroke.get("Time"))/1000.0,
                                int(stroke.get("X")),
                                int(stroke.get("Y")),
                                1, # pressure, always 1
                                status))
                si+=1

        return list_result

################################################################################

def loadPredefinedSegmentTagList(file_name=u'default.tag'):
    tag_file_path = getSegmentTagsFilePath(file_name)
    with codecs.open(tag_file_path, "r", "utf-8") as f:
        return [tag.strip() for tag in f if len(tag.strip())>0]

################################################################################

import cPickle

def readPickle(file_path, file_name):
    abs_file_path = os.path.join(file_path,file_name)
    dobj=None
    if os.path.isfile(abs_file_path):
        from pyqtgraph import mkColor
        with open(abs_file_path, 'rb') as f:
            dobj = cPickle.load(f)
        for k, v in dobj.items():
            if isinstance(v, tuple) and len(v)==3 and isinstance(v[0], (int, long, float)):
                #print "Creating color from:",k, v
                dobj[k] = mkColor(v)
    return dobj

def writePickle(file_path, file_name, dictobj):
    from pyqtgraph.Qt import QtGui
    abs_file_path = os.path.join(file_path,file_name)
    dobj=dict()
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    for k,v in dictobj.items():
        if isinstance(v, QtGui.QColor):
            dobj[k] = (v.red(), v.green(), v.blue())
        else:
            dobj[k]=v
    with open(abs_file_path, 'wb') as f:
        cPickle.dump(dobj, f, cPickle.HIGHEST_PROTOCOL)

################################################################################

