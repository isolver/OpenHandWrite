__author__ = 'Sol'
"""
Simple example of how to use the markwrite package to do batch
pen data input file -> markwrite report output file creation.
"""
# Ensure to import markwrite package before anything else
import markwrite
import os

#
## NEXT 2-3 VARIABLES NEED TO BE CHANGED BASED ON THE LOCATION AND TYPE
## OF THE INPUT FILES TO PROCESS.
#
# Set root path to use when scanning for input files
root_input_folder = os.path.abspath('test_data')
# Set file types to use as input files
input_extensions = "txyp", "xml", "hdf5", "mwp"
# If hdf5 files are being processed, and trials are to be parsed
# from the hdf5 file using trial condition variable columns, specify
# tuple containing (trial_start_col_name, trial_end_col_name),
hdf5_trial_parsing = ('DV_GO_START', 'DV_STOP_END')

from markwrite.project import MarkWriteProject
from markwrite.reports import PenSampleReportExporter

def getInputFiles(froot, exts):
    data_files=[]
    for path, dirs, files in os.walk(froot):
        for f in files:
            for ext in exts:
                if f.endswith(ext):
                    data_files.append(os.path.join(path, f))
                    break
    return data_files

data_file_paths = getInputFiles(root_input_folder, input_extensions)
# for each pen data file ...
for dfp in data_file_paths:
    _,dfname = os.path.split(dfp)
    print 'Processed',dfp,'->',
    # Create a markwrite project class from the data file. This performs
    # all the same steps as loading the data file from within the MarkWrite GUI
    # including data filtering, sample grouping into series, runs, and strokes.
    mwp = MarkWriteProject(file_path=dfp,
                           tstart_cond_name=hdf5_trial_parsing[0],
                           tend_cond_name=hdf5_trial_parsing[1])

    # create the report output folder if needed
    outdirpath = os.path.abspath(os.path.join('.','test_output_reports'))
    if not os.path.exists(outdirpath):
        os.makedirs(outdirpath)
    outfilepath = os.path.join(outdirpath, dfname+'.txt')

    # Generate a PenSampleReport from the markwrite project
    PenSampleReportExporter.export(outfilepath, mwp)

    print outfilepath
    # cleanup before running the next report
    mwp.close()
    mwp = None
print "Complete."