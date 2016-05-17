# -*- coding: utf-8 -*-
"""
Allows selection of an Experiment Template .hdf5 results file.

User then selects the start end trial condition variable names to use
for selecting tablet sample events for each trial.

Saves a tab delimited .txt file with each row being a wintab sample event.
Each row has columns for session meta data, trial condition variables, and
tablet event fields.

@author: Sol
"""
import sys, os
from psychopy.core import getTime
from psychopy import gui
from psychopy.iohub.datastore.util import displayDataFileSelectionDialog, \
                                            ExperimentDataAccessUtility
from psychopy.iohub.constants import EventConstants
from psychopy.iohub import _DATA_STORE_AVAILABLE, module_directory
from collections import OrderedDict

if _DATA_STORE_AVAILABLE is False:
    raise ImportError("DataStore module could not be imported. "
                      "(Likely that pyTables hdf5dll could not be found). "
                      "Exiting demo...")
    sys.exit(1)

def displayTimeRangeVariableSelectionDialog(dataAccessUtil):
    try:
        cv_names = [cvname for cvname in dataAccessUtil.getConditionVariableNames()
                    if cvname.startswith('DV_')]
        dlg_info =  OrderedDict()
        dlg_info["Start Trial Time"] = [cvname for cvname in cv_names
                                        if cvname.endswith('START')]
        dlg_info["End Trial Time"] = [cvname for cvname in cv_names
                                      if cvname.endswith('END')]
        infoDlg = gui.DlgFromDict(dictionary=dlg_info,
                                           title="Trial Event Time Range Variables",
                                           order=dlg_info.keys())
        if not infoDlg.OK:
            return None
        return dlg_info.values()
    except:
        pass

def writeOutputFileHeader(output_file, *args):
    """
    Writes the header line at the top of the Log file.
    Currently uses format:

    session_meta_data_cols [session_user_variable_columns] [event_table_cols][3:]

    Session data is associated with each log entry row using the session_id field.
    """
    allcols=[]
    for cnlist in args:
        allcols.extend(cnlist)
    output_file.write('\t'.join(allcols))
    output_file.write('\n')
    return allcols

def writeDataRow(output_file,*args):
    """
    Save a row of data to the output file, in tab delimited format. See comment
    for writeOutputFileHeader function for order of saved columns.
    """
    all_data=[]
    for cvals in args:
        all_data.extend([str(cv) for cv in cvals])
    output_file.write('\t'.join(all_data))
    output_file.write('\n')

if __name__ == '__main__':
    # Select the hdf5 file to process.
    data_file_path= displayDataFileSelectionDialog(
                                        starting_dir=os.path.join(
                                            module_directory(
                                                writeOutputFileHeader),
                                            'results'))
    if data_file_path is None:
        print("File Selection Cancelled, exiting...")
        sys.exit(0)

    dpath,dfile=os.path.split(data_file_path)

    # Lets time how long it takes to read and save to .txt format
    #
    start_time=getTime()

    # Create an instance of the ExperimentDataAccessUtility class
    # for the selected DataStore file. This allows us to access data
    # in the file based on Device Event names and attributes, as well
    # as access the experiment session metadata saved with each session run.
    dataAccessUtil=ExperimentDataAccessUtility(dpath,dfile,
                                               experimentCode=None,
                                               sessionCodes=[])

    duration=getTime()-start_time

    dvs_selected = displayTimeRangeVariableSelectionDialog(dataAccessUtil)

    # restart processing time calculation...
    #
    start_time=getTime()

    # Read the session metadata table for all sessions saved to the file.
    #
    session_metadata=dataAccessUtil.getSessionMetaData()
    sesion_meta_data_dict=dict()
    # Create a session_id -> session metadata mapping for use during
    # file writing.
    #
    if len(session_metadata):
        session_metadata_columns = list(session_metadata[0]._fields[:-1] )
        session_uservar_columns=list(session_metadata[0].user_variables.keys())
        for s in session_metadata:
            sesion_meta_data_dict[s.session_id]=s

    # Get the experiment conditions table for the session reference...
    try:
        cv_table = dataAccessUtil.getConditionVariablesTable()
    except:
        cv_table = None

    # Get the WintabTabletSample evvents table reference....
    tablet_sample_table = dataAccessUtil.getEventTable(
                                            EventConstants.WINTAB_TABLET_SAMPLE)

    # Open a file to save the tab delimited output to.
    #
    log_file_name="%s.txt"%(dfile[:-5])

    scount = 0

    with open(log_file_name,'w') as output_file:

        # write column header
        #
        args = [output_file,session_metadata_columns,]
        if cv_table:
            args.append(cv_table.colnames[2:])
        args.append(tablet_sample_table.colnames[3:])
        writeOutputFileHeader(*args)

        print('Writing Data to %s:\n'%(os.path.abspath(log_file_name)))

        if cv_table:
            for trial_vars in cv_table.iterrows():
                evt_win_start_time, evt_win_end_time = trial_vars[dvs_selected[0]],\
                                                       trial_vars[dvs_selected[1]]
                sys.stdout.write("Saving Events for Trial {}.".format(
                                                        trial_vars['DV_TRIAL_ID']))
                if evt_win_start_time >= evt_win_end_time:
                    print "WARNING: Trial start time >= end_time:" \
                          " {}, {}. Skipping output for trial {}".format(
                                                        evt_win_start_time,
                                                        evt_win_end_time,
                                                        trial_vars['DV_TRIAL_ID'])
                    continue
                event_iterator_for_output = tablet_sample_table.where(
                                            "(time > {}) & (time <= {})".format(
                                                                evt_win_start_time,
                                                                evt_win_end_time))
                for i,event in enumerate(event_iterator_for_output):
                    # write out each row of the event data with session
                    # and condition variable data as prepended columns.....
                    #
                    writeDataRow(output_file,
                                 sesion_meta_data_dict[event['session_id']][:-1],
                                 trial_vars[:][2:],
                                 event[:][3:])
                    if i%100==0:
                        sys.stdout.write('.')
                    scount = scount + 1
                sys.stdout.write('\n')
        else:
            for i,event in enumerate(tablet_sample_table.iterrows()):
                # write out each row of the event data with session
                # and condition variable data as prepended columns.....
                #
                writeDataRow(output_file,
                             sesion_meta_data_dict[event['session_id']][:-1],
                             event[3:])
                if i%100==0:
                    sys.stdout.write('.')
                scount = scount + 1

    dataAccessUtil.close()

    if scount > 0:
        duration=duration+(getTime()-start_time)
        print('\nOutput Complete. '
              '%d Events Saved to %s in %.3f seconds '
              '(%.2f events/seconds).\n'%(scount,os.path.abspath(log_file_name),duration,scount/duration))
    else:
        print("The selected file does not have any Pen Sample Events "
              "within the chosen trial start and end times.")