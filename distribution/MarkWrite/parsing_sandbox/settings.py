# -*- coding: utf-8 -*-
"""
Created on Fri May 17 08:57:04 2019

@author: sol
"""

input_file_name = './input/5101_New.txt'
output_file_name = './output/5101_New_parsed.txt'

# List of series indices to plot during analysis.
plot_series_ix = [0, 1]#,1,2,3,4,5,6,7,8,9,10]

## Device resolution information....
spatial_resolution = 100.0/3.0  # lines or units / cm
temporal_resolution = 133.0  # sampling rate device data in Hz

# Minimum series size critera
min_series_length = 10  # Minimum length of a series; i.e. sample count 
min_pressed_count = 3   # Minimum number of > 0 pressure samples in a series
                        # must be <= min_series_length


# dalpha calculation settings
inter_sample_distance = 0.1    # cm
abs_dalpha_thresh = 40.0   # degrees


# Series stroke merging and clasification settings 
min_stroke_length = 0.05 # cm
#min_stroke_duration = 0.03 # minimum number samples in a stroke
min_stroke_velocity = 0.5 # cm / sec

# Output fields
add_fields =  ['x.fc10', 'y.fc10', 'x.fc5', 'y.fc5', 'vx.fc10',
               'vy.fc10', 'vxy.fc10', 'vx.fc5', 'vy.fc5', 'vxy.fc5',
               'vxy.fc10.extrema', 'vxy.fc5.extrema',
               'vxy.fc10.minima.dalpha','series_sample_index','vxy.fc10.minima.pre','vxy.fc10.minima.post',
               'stroke_id', 'stroke_state']
