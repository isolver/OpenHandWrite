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
import codecs

class ReportExporter(object):
    '''
    Parent class for all report export formats. Each subclass must implement
    the following methods:

    * columnnames()
    * datarowcount()
    * datarows()

    And optionally set the following class attribute:

    * progress_dialog_title
    * progress_update_rate
    * sep
    * nl
    * writepreamble
    * writeheader
    * formating

    and class methods:

    * preamble()

    For example, given a ReportExporter subclass called MyReportExporter,
    the specified report can be exxported / saved to disk using:

        MyReportExporter.export(path_to_output_file, markwrite_app.project)

    '''
    progress_dialog_title = "Saving MarkWrite Report .."
    progress_update_rate=1
    sep=u'\t'
    nl=u'\n'
    writepreamble=False
    writeheader=True
    formating={}
    project = None

    def __init__(self):
        pass

    @classmethod
    def columnnames(cls):
        """

        :return:
        """
        return []

    @classmethod
    def datarowcount(cls):
        """

        :return:
        """
        return 0

    @classmethod
    def datarows(cls):
        """

        :return:
        """
        return []

    @classmethod
    def preamble(cls):
        """

        :return:
        """
        return ''

    @classmethod
    def rowformat(cls):
        rowformater=[]
        for cname in cls.columnnames():
            rowformater.append(cls.formating.get(cname,u"{}"))
        return cls.sep.join(rowformater)+cls.nl

    @classmethod
    def export(cls, file_path, project):
        """

        :param cls:
        :param file_path:
        :param project:
        :return:
        """
        cls.project = project
        try:
            import pyqtgraph
            with codecs.open(file_path, "w", "utf-8") as f:
                with pyqtgraph.ProgressDialog(cls.progress_dialog_title, 0,cls.datarowcount()) as dlg:

                    if cls.writepreamble:
                        # TODO: Should split into lines and prefix each line
                        # with a 'comment' character(s), like '#' is used in python

                        f.write(cls.preamble()+cls.nl)

                    if cls.writeheader:
                        f.write(cls.sep.join(cls.columnnames())+cls.nl)

                    rowformatstr=cls.rowformat()
                    ri = 0
                    for row in cls.datarows():
                        f.write(rowformatstr.format(*row))

                        if ri%cls.progress_update_rate==0:
                            dlg.setValue(ri)
                        if dlg.wasCanceled():
                            # TODO: Should the incomplete report file be deleted
                            #       if dialog is cancelled?
                            break
                        ri+=1
            return ri
        except:
            import traceback
            traceback.print_exc()
        finally:
            cls.project = None
        return 0

from sample import PenSampleReportExporter
from segment import SegmentLevelReportExporter