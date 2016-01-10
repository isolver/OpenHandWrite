__author__ = 'Sol'
"""
Simple example of how to use the markwrite package to do batch
pen data input file -> markwrite report output file creation.
"""

# Ensure to import markwrite package before anything else
import markwrite

import os
from markwrite.project import MarkWriteProject
from markwrite.reports import PenSampleReportExporter

# list of data files to create reports for. relative or absolute
# paths can be used
data_file_paths=['test_data\\TXYP\\1.tab.txyp']

# for each pen data file ...
for dfp in data_file_paths:
    absdfp = os.path.abspath(dfp)
    _,dfname = os.path.split(absdfp)

    # Create a markwrite project class from the data file. This performs
    # all the same steps as loading the data file from within the MarkWrite GUI
    # including data filtering, sample grouping into series, runs, and strokes.
    mwp = MarkWriteProject(file_path=absdfp)

    # create the report output folder if needed
    outdirpath = os.path.abspath(os.path.join('.','test_output_reports'))
    if not os.path.exists(outdirpath):
        os.makedirs(outdirpath)
    outfilepath = os.path.join(outdirpath, dfname+'.txt')

    # Generate a PenSampleReport from the markwrite project
    PenSampleReportExporter.export(outfilepath, mwp)

    # cleanup before running the next report
    mwp.close()
    mwp = None