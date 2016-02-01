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
from util import getSegmentTagsFilePath
import codecs
import os

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


SAMPLE_STATES=dict()
# A sample that is the first sample following a time gap in the sample stream
SAMPLE_STATES['FIRST_ENTER'] = 1
# A sample that is the first sample with pressure == 0
# following a sample with pressure > 0
SAMPLE_STATES['FIRST_HOVER'] = 2
# A sample that has pressure == 0, and previous sample also had pressure  == 0
SAMPLE_STATES['HOVERING'] = 4
# A sample that is the first sample with pressure > 0
# following a sample with pressure == 0
SAMPLE_STATES['FIRST_PRESS'] = 8
#  A sample that has pressure > 0
# following a sample with pressure > 0
SAMPLE_STATES['PRESSED'] = 16
for k,v in SAMPLE_STATES.items():
    SAMPLE_STATES[v]=k

def convertSampleStateValue(sv):
    return [v for k, v in SAMPLE_STATES.items() if isinstance(k,int) and sv&k==k]

class DataImporter(object):
    '''
    Parent class for all data import formatters. Each subclass must implement
    the .validate(file_path) and .parse(file_path).

    Use .asarray(file_path) to return the formatted input data as a numpy array
    with dtype: [('time', np.int64),
                 ('x', np.int32),
                 ('y', np.int32),
                 ('pressure', np.int32),
                 ('tag_ix', np.uint32)]
    '''
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
            0,  'time', long
            1,  'x', int
            2,  'y', int
            3,  'pressure', int
            4,  0, int

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
        return np.asarray(cls.parse(file_path), markwrite_pendata_format)

#
# Tab Delimited File Importer
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
                         status, # state field
                         0, # x_filtered, filled in by markwrite runtime
                         0, # y_filtered, filled in by markwrite runtime
                         0, # pressure_filtered, filled in by markwrite runtime
                         0, # x_velocity, filled in by markwrite runtime
                         0, # y_velocity, filled in by markwrite runtime
                         0, # xy_velocity, filled in by markwrite runtime
                         0, # xy_accell, filled in by markwrite runtime
                         0) #segment_id, filled in by markwrite runtime

                    last_sample=dsample
                    list_result.append(dsample)

                except IndexError:
                    print("Note: Skipping Line {0}. Contains {1} Tokens.".format(len(list_result), len(line_tokens)))

        return list_result
#
# ioHub HDF5 File Importer
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
            import traceback
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
                             r['status'], # state field
                             0, # x_filtered, filled in by markwrite runtime
                             0, # y_filtered, filled in by markwrite runtime
                             0, # pressure_filtered, filled in by  runtime
                             0, # x_velocity, filled in by markwrite runtime
                             0, # y_velocity, filled in by markwrite runtime
                             0, # xy_velocity, filled in by markwrite runtime
                             0, # xy_accell, filled in by markwrite runtime
                             0) #segment_id, filled in by markwrite runtime
                                )

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
# XML Format Importer
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
                                status, # state field
                                0, # x_filtered, filled in by markwrite runtime
                                0, # y_filtered, filled in by markwrite runtime
                                0, # pressure_filtered, filled in by  runtime
                                0, # x_velocity, filled in by markwrite runtime
                                0, # y_velocity, filled in by markwrite runtime
                                0, # xy_velocity, filled in by markwrite runtime
                                0, # xy_accell, filled in by markwrite runtime
                                0) #segment_id, filled in by markwrite runtime
                                )
                si+=1
            #last_point = list(list_result[-1])
            #last_point[3] = 0  # Set pressure to 0 for last point
            #list_result[-1]=tuple(last_point)
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

