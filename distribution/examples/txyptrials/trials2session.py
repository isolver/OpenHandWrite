# -*- coding: utf-8 -*-
"""
Merges several .txyp files into a single session level txyp file, adding
trial condition variable lines for use by MarkWrite.

@author: Sol
"""
import sys, os, glob, io

merge_file_dir = os.path.abspath('./test_data')
file_name_match = '*-w_*.txyp'
glob_pattern = merge_file_dir+os.path.sep+file_name_match

output_file_name = 'session.txyp'
output_path = os.path.join(merge_file_dir, output_file_name)

fname_token_sep = '_'
file_token_labels = (u'Part_ID', u'Trial_ID', u'Trial_Word')
order_inputs_by = 1  # Index of file_token_labels element to order inputs with.

trial_cv_labels = list(file_token_labels)
trial_cv_labels.extend([u"DV_TRIAL_START", u"DV_TRIAL_END"])


def fileNameTokens(file_path):
    fname = unicode(os.path.basename(file_path), "cp1252")
    return fname[:-len('.txyp')].split('_')


def sortInputFiles(in_files):
    fin_dict = {}
    for input_fname in in_files:
        fpath, fname = os.path.split(input_fname)
        fname_tokens = fileNameTokens(input_fname)
        fin_dict[int(fname_tokens[order_inputs_by])] = input_fname
    sorted_keys = fin_dict.keys()
    sorted_keys.sort()
    sorted_in_files = []
    for skey in sorted_keys:
        sorted_in_files.append(fin_dict[skey])
    return sorted_in_files

if __name__ == '__main__':
    file_matches = glob.glob(glob_pattern)
    input_file_paths = sortInputFiles(file_matches)

    print u"Reading trial input files from: ", merge_file_dir
    print
    session_time_offset = 0
    with io.open(output_path, 'w', encoding='utf8') as fout:
        fout.write(u'T	X	Y	P\n')
        fout.write(u"!TRIAL_CV_LABELS {}\n".format(u" ".join(trial_cv_labels)))
        for input_fname in input_file_paths:
            _, fname = os.path.split(input_fname)
            print u"Processing Input File: ", fname

            start_time = None
            end_time = None
            with io.open(input_fname, 'r', encoding='utf8') as fin:
                for lin in fin:
                    lin = lin.strip().replace("\t", " ")
                    T, X, Y, P = lin.split(u" ")
                    if T == u'T':
                        continue
                    T = float(T) + session_time_offset
                    if start_time is None:
                        start_time = T
                    fout.write(u"{}\t{}\t{}\t{}\t\n".format(T, X, Y, P))
                end_time = T

                fname_values = fileNameTokens(input_fname)
                trial_cv = fname_values + [u"%.3f"%start_time, u"%.3f"%end_time]
                trial_cv_line = u" ".join(trial_cv)
                fout.write(u"!TRIAL_CV_VALUES {}\n".format(trial_cv_line))

                session_time_offset = T
        print
        print u"Saved Merged File to:", output_path
