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
import re

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')

class ReportExporter(object):
    '''
    To define a new report type that can be used by MarkWrite, a class that
    implements the ReportExporter interface must be created.

    ReportExporter is the parent class, or in this case more like a report
    class template, for creating tabular style reports. A report can have
    1 - C named columns, and 0 - R rows.  Each column represents a variable,
    each row provides the values for the C variables.

    Reports are saved as utf-8 encoded text files. The utf-8 encoding is done by
    the ReportExporter class when the report file is saved, so all string
    type values returned by a ReportExporter subclass should be unicode strings,
    i.e.

        # Good
        ustring = u'This is a unicode string'

        # Bad (maybe)
        astring = 'This is not a unicode string'

    If your strings only contain latin-1 characters, then the above will not
    really  matter.

    A report can have the following parts:

    1. Report Preamble: Any text that should be added to the start
         of a report file. This is optional.

    2. Header Row: A list containing the report column names.
         ReportExporter converts the column name list into a utf-8 string,
         with each column name separated by the ReportExporter.sep string.
         The default sep is a tab. The header row line is terminated by the
         ReportExporter.nl string, which is a '\n' by default. The header row
         is optional.

    3. Data Rows: Each data row is a list containing the report column values
         for a single entry in the report. The elements of a data row can be of
         any data type. ReportExporter converts each data row list it receives
         into a ReportExporter.sep separated line, ending with the
         ReportExporter.nl. A report must provide this section, otherwise what
         would be the point of the report? ;)

    To create a new report type, create a subclass of the ReportExporter
    class. At minimum, a ReportExporter subclass must implement the following
    parts of the ReportExporter interface. For the example, we will create a
    report type that simply saves out the pen point samples that were loaded
    into the project and converted into the project.pendata numpy rec array.

        class RawSampleDataReportExporter(ReportExporter):
            progress_dialog_title = "Saving the Raw Pen Point Sample Report .."
            def __init__(self):
                ReportExporter.__init__(self)

            @classmethod
            def columnnames(cls):
                # Return the name of each 'column' of the project.pendata
                # numpy array.
                # Note that the report cls has a 'project' attribute
                # that can be used to access the project in use when
                # generating the report

                return cls.project.pendata.dtype.names

            @classmethod
            def datarowcount(cls):
                # Return the number of pen samples that will be saved
                # in the report. Each sample will be a report data row.
                return cls.project.pendata.shape[0]

            @classmethod
            def datarows(cls):
                # Iterate through the pen data array, yielding each pen sample
                # as a list.
                for pensample in cls.project.pendata:
                    yield pensample.tolist()

    This example code has been saved to a file called 'customreports.py',
    which is in the same directory as the MarkWrite.exe. To add other
    custom reports, add the new report class to the same 'customreports.py'
    file. This file is read when MarkWrite.exe is started, and any custom
    report classes are loaded and added to the File->Export menu of the
    application.

    The name of the class is used to generate the name of the report that will
    appear in the MarkWrite application. The report class name to app report
    gui label conversion logic is:
        * Remove 'Exporter' from the end of the class name, if it is present.
        * For each upper case letter in the class name, insert a space char
          prior to it.
        * Add 'Report' to the end of the report label if it does not already
          exist.
    So for the RawSampleDataReportExporter example, the report label displayed
    in the File->Export menu of the MarkWrite application would be
    "Raw Sample Data Report".

    Users of the MarkWrite application will then be able to use the new
    report type.

    Review the doc strings for the full ReportExporter class to learn all the
    different options that can be changed for use in a ReportExporter subclass.
    '''

    # Text to display in the progress bar dialog that will appear during
    # report saving. If the report creation takes < ~ 0.5 seconds, the dialog
    # is not shown.
    progress_dialog_title = "Saving MarkWrite Report .."

    # After how many data rows are saved should the progress dialog be updated.
    # The default value of 1 means the dialog is updated for each data row.
    progress_update_rate=1

    # The separator to use between each column of the report file.
    sep=u'\t'

    # The new line character(s) that should be used to terminate each line of
    # the report.
    nl=u'\n'

    # Specifies the value to use for missing data in a report. This attribute
    # can be used within your own datarows() code for elements of a data row
    # array that should have a missing value.
    # The attribute is also used automatically during report creation to
    # pad the end of any data row list returned from .datarows() that has a
    # length < len(columnnames).
    missingval=u''

    # Optional. When a report is created, each element of a data row list is
    # converted to a string using the Python string .format() method. By
    # default, each value is converted using the default .format() conversion
    # logic. If you want the row data for one or more of the report columns
    # to use a formatter other than the default, add them to this dict.
    # Each key must be equal to one of the reports column names. The value
    # for a given key is the formatting string to use for values of the given
    # column.
    # Using the RawDataReportExporter example created above, to specify that
    # the time column data values should always be saved with six decimal
    # places:
    #
    #     class RawDataReportExporter(ReportExporter):
    #         formating=dict(time=u'{:.6f}')
    #
    # If using custom formatter, you must be sure that the value for the
    # column returned for each data row can be converted without raising an
    # error.
    # For details on all the possible field formatting string options,
    # see https://docs.python.org/2/library/string.html#formatspec
    formating={}


    #
    ## The remaining class attributes should not be reimplemented in a
    ## ReportExporter subclass.
    #

    # Can be used within your report code to access the project object,
    # usually the pendata and segmentset project attributes.
    project = None

    def __init__(self):
        pass

    @classmethod
    def columnnames(cls):
        """
        This class method must be implemented by the subclass being created.
        It must return a list of unicode strings, each being the name of a column
        to be used in the generated report.
        :return: list
        """
        return []

    @classmethod
    def datarowcount(cls):
        """
        This class method must be implemented by the subclass being created.
        It should return the number of data rows that the .datarows()
        generator will return in total.

        ReportExporter only uses this count so that the progress bar dialog
        can accurately report the % of the report generated. Therefore,
        unless your own code uses the count in a way that requires it
        to be completely accurate, the value returned can be an
        approximation if necessary;
        :return: int
        """
        return 0

    @classmethod
    def datarows(cls):
        """
        This class method must be implemented by the subclass being created.

        For each data row to be included in the report, yield a list
        containing a value for each report column. The list must have the
        same length as .columnnames(), i.e. one value for each column,
        in the order that the column names are specified.

        The method should be a generator, yielding one data row list at a time.
        See the .datarows() method of the sample and segment level report
        classes for examples  of how this is done if needed.
        :return: a yielded list for each data row
        """
        yield []

    @classmethod
    def preamble(cls):
        """
        Optional.
        This class method must be implemented by the subclass being created
        if the report format is to start with a preamble section at the start
        of the report.
        :return: unicode utf-8 encoded text.
        """
        return ''

    #
    ## The remaining class methods should not be reimplemented in a
    ## ReportExporter subclass.
    #

    @classmethod
    def columncount(cls):
        return len(cls.columnnames())

    @classmethod
    def reportlabel(cls):
        label = cls.__name__
        if label.endswith('Exporter'):
            label = label[:-8]
        if not label.endswith('Report'):
            label = label+'Report'

        s1 = first_cap_re.sub(r'\1 \2', label)
        return all_cap_re.sub(r'\1 \2', s1)

    @classmethod
    def outputfileprefix(cls):
        return cls.reportlabel().replace(' ','_')

    @classmethod
    def rowformat(cls):
        """
         :return: list of strings
        """
        rowformater=[]
        for cname in cls.columnnames():
            rowformater.append(cls.formating.get(cname,u"{}"))
        return cls.sep.join(rowformater)+cls.nl

    @classmethod
    def export(cls, file_path, project):
        """
        This method is called by the MarkWrite application to create and
        save a report. Subclasses should *not* have to override / change
        this method.

        Example usage:

            MyReportExporter.export(path_to_output_file, markwrite_app.project)

        :param file_path: Absolute file path to save the report to.
        :param project: The MarkWrite Project instance that will be used
                        for data and further calculations by the datarows
                        method.
        :return: None
        """
        cls.project = project
        try:
            import pyqtgraph
            with codecs.open(file_path, "w", "utf-8") as f:
                with pyqtgraph.ProgressDialog(cls.progress_dialog_title, 0,cls.datarowcount()) as dlg:

                    rp = cls.preamble()
                    if len(rp)>0:
                        # TODO: Should split into lines and prefix each line
                        # with a 'comment' character(s), like '#' is used in python

                        f.write(cls.preamble()+cls.nl)

                    if len(cls.columnnames())>0:
                        f.write(cls.sep.join(cls.columnnames())+cls.nl)

                    rowformatstr=cls.rowformat()
                    ri = 0
                    for row in cls.datarows():
                        row.extend([cls.missingval,]*(cls.columncount()-len(row)))
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

import importlib,inspect
custom_report_classes = [rctype for rcname, rctype in inspect.getmembers(importlib.import_module('customreports'), inspect.isclass) if rctype != ReportExporter]
