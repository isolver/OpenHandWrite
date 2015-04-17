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
from markwrite.reports import ReportExporter
from weakref import proxy

class SegmentLevelReportExporter(ReportExporter):
    """
    Segment level report outputs one row per segment within the project.
    Columns are:
        * file: name of imported pen sample data file
        * seg_id: unique identifier assigned to segment.
        * category: The name of segment tree the root the segment is part of
        * level: Segment level in the segmentation tree.
        * segpath: tree branch path to segment, not including root of tree
        * name
        * start_time:
        * end_time:
        * duration:
        * start_index:
        * end_index:
        * sample_count:
        * subsegment_count:
        * prev_penpress_time
        * next_penpress_time
    """
    progress_dialog_title = "Saving Pen Data Segmentation Report .."
    progress_update_rate=1
    segpathsep=u'->'
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        column_names=['file','seg_id','category','level','segpath','name'
            ,'start_time','end_time','duration','start_index','end_index',
            'sample_count','subsegment_count','prev_penpress_time'
            ,'next_penpress_time']
        return column_names

    @classmethod
    def datarowcount(cls):
        return cls.project.segmentset.totalsegmentcount

    @classmethod
    def datarows(cls):
        pendata = cls.project.pendata
        pointcount=pendata.shape[0]
        nonzero_pressure_ixs = np.nonzero(pendata['pressure'])[0]
        segment_tree = cls.project.segmentset

        catname = segment_tree.name
        filename=catname=segment_tree.name

        for level_num, segment_list in cls.project.segmentset.getLeveledSegments().items():
            """


            * start_index:
            * end_index:
            * sample_count:
            *subsegment_count
            * prev_penpress_time
            * next_penpress_time
            """
            for segment in segment_list:
                #TODO: Segment path string
                segpath = cls.segpathsep.join(segment.path)

                stime, etime = segment.timerange
                start_index, end_index = segment_tree.calculateTrimmedSegmentIndexBoundsFromTimeRange(stime, etime)
                duration = etime - stime
                subsegment_count = len(segment.children)

                prev_penpress_time=''
                next_penpress_time=''

                if start_index>0:
                    prev_nonzero_ix = np.searchsorted(nonzero_pressure_ixs, start_index, side='left')-1
                    prev_penpress_time = pendata['time'][prev_nonzero_ix]
                if end_index < pointcount:
                    next_nonzero_ix = np.searchsorted(nonzero_pressure_ixs, end_index, side='left')+1
                    next_penpress_time = pendata['time'][next_nonzero_ix]

                yield [filename,
                           segment.id,
                           catname,
                           level_num,
                           segpath,
                           segment.name,
                           stime,
                           etime,
                           duration,
                           start_index,
                           end_index,
                           segment.pointcount,
                           subsegment_count,
                           prev_penpress_time,
                           next_penpress_time
                           ]

