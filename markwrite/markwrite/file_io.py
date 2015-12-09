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
from util import getSegmentTagsFilePath
import codecs
import os

markwrite_pendata_format = [('time', np.float32),
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
                    ('segment_id', np.uint16)]


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
            for line_index, tab_line in enumerate(f):
                if line_index < cls.DATA_START_LINE_INDEX:
                    continue
                try:
                    line_tokens = tab_line.split(u'\t')

                    list_result.append(
                        (float(line_tokens[cls.TIME_COLUMN_IX].strip()),
                         int(line_tokens[cls.X_COLUMN_IX].strip()),
                         int(line_tokens[cls.Y_COLUMN_IX].strip()),
                         int(line_tokens[cls.PRESS_COLUMN_IX].strip()),
                         0, # state field, always 0
                         0, # x_filtered, filled in by markwrite runtime
                         0, # y_filtered, filled in by markwrite runtime
                         0, # pressure_filtered, filled in by markwrite runtime
                         0, # x_velocity, filled in by markwrite runtime
                         0, # y_velocity, filled in by markwrite runtime
                         0, # xy_velocity, filled in by markwrite runtime
                          0) #segment_id, filled in by markwrite runtime
                        )

                except IndexError:
                    print("Note: Skipping Line {0}. Contains {1} Tokens.".format(len(list_result), len(line_tokens)))

        return list_result
#
# ioHub HDF5 File Importer
#
from psychopy.iohub.datastore.util import ExperimentDataAccessUtility
from psychopy.iohub import EventConstants

class HubDatastoreImporter(DataImporter):
    hubdata = None
    exp_condvars = None
    condvars_names = None
    def __init__(self):
        DataImporter.__init__(self)

    @classmethod
    def _load(cls, file_path):
        try:
            if cls.hubdata:
                cls.hubdata.close()
                cls.hubdata = None
            dpath, dfile=os.path.split(file_path)
            cls.hubdata = ExperimentDataAccessUtility(dpath, dfile,
                                                      experimentCode=None,
                                                      sessionCodes=[])
            return cls.hubdata
        except:
            print "Error openning ioHub HDF5 file."
            import traceback
            traceback.print_exc()
        return None

    @classmethod
    def validate(cls, file_path):
        exp_data_util = cls._load(file_path)
        file_valid = False
        if exp_data_util:
            evt_table_mappings = cls.hubdata.getEventsByType()
            file_valid = evt_table_mappings.get(EventConstants.WINTAB_TABLET_SAMPLE,False)

        if cls.hubdata:
            cls.hubdata.close()
            cls.hubdata = None

        return file_valid

    @classmethod
    def parse(cls, file_path):
        exp_data_util = cls._load(file_path)
        if exp_data_util is None:
            return []

        wintab_samples = exp_data_util.getEventsByType().get(
                                EventConstants.WINTAB_TABLET_SAMPLE,None)
        list_result = []
        if wintab_samples:
            for r in wintab_samples:
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
                                 0) #segment_id, filled in by markwrite runtime
                                    )

            try:
                cls.exp_condvars = exp_data_util.getConditionVariablesTable().read()
                cls.condvars_names = cls.exp_condvars.dtype.names
            except:
                cls.exp_condvars = None
                cls.condvars_names = None

        if cls.hubdata:
            cls.hubdata.close()
            cls.hubdata = None

        return list_result

    def __del__(self):
        if self.hubdata:
            self.hubdata.close()
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
            return True
        except:
            pass
        return False

    @classmethod
    def parse(cls, file_path):
        list_result = []
        xml_root = ET.parse(file_path).getroot()
        for stroke_set in xml_root.iter(u'strokes'):
            pressure = 0
            for stroke in stroke_set.iter(u'stroke'):
                list_result.append((float(stroke.get("Time")),
                                stroke.get("X"),
                                stroke.get("Y"),
                                1, # pressure, always 1
                                0, # state field, always 0
                                0, # x_filtered, filled in by markwrite runtime
                                0, # y_filtered, filled in by markwrite runtime
                                0, # pressure_filtered, filled in by  runtime
                                0, # x_velocity, filled in by markwrite runtime
                                0, # y_velocity, filled in by markwrite runtime
                                0, # xy_velocity, filled in by markwrite runtime
                                0) #segment_id, filled in by markwrite runtime
                                )
            last_point = list(list_result[-1])
            last_point[-2] = 0  # Set pressure to 0 for last point
            list_result.pop(-1)
            list_result.append(tuple(last_point))
        return list_result

################################################################################

def loadPredefinedSegmentTagList(file_name=u'default.tag'):
    tag_file_path = getSegmentTagsFilePath(file_name)
    with codecs.open(tag_file_path, "r", "utf-8") as f:
        return [tag.strip() for tag in f if len(tag.strip())>0]

################################################################################

import cPickle
import os

def readPickle(file_path, file_name):
    abs_file_path = os.path.join(file_path,file_name)
    if os.path.isfile(abs_file_path):
        with open(abs_file_path, 'rb') as f:
            return cPickle.load(f)
    return None

def writePickle(file_path, file_name, dictobj):
    abs_file_path = os.path.join(file_path,file_name)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(abs_file_path, 'wb') as f:
        cPickle.dump(dictobj, f, cPickle.HIGHEST_PROTOCOL)

################################################################################

