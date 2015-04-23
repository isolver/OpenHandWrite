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

class PenSampleReportExporter(ReportExporter):
    progress_dialog_title = "Saving Pen Point Sample Level Report .."
    progress_update_rate=10
    formating=dict(time=u'{:.3f}')
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        column_names=['file','index','time','x','y','pressure','cat1']
        ss = cls.project.segmentset
        lvls = range(1,ss.getLevelCount()+1)
        column_names.extend([u'cat1.L%d'%l for l in lvls])

        return column_names

    @classmethod
    def datarowcount(cls):
        return cls.project.pendata.shape[0]

    @classmethod
    def datarows(cls):
        pendata = cls.project.pendata

        ss = cls.project.segmentset
        sfile=ss.name

        lvls = range(1,ss.getLevelCount()+1)

        segs_by_lvl=ss.getLeveledSegments()
        catname = ss.name

        for i in xrange(pendata.shape[0]):
            dp=pendata[i]


            rowdata = [sfile,i,dp['time'],dp['x'],dp['y'],dp['pressure'],catname]

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

            yield rowdata

