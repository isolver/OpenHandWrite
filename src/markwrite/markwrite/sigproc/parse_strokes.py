# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:44:42 2019

@author: sol
"""
from __future__ import division

import numpy as np
from numpy import (sqrt, square, diff, cumsum, append, sign, vectorize,
                   arctan2, pi, where, abs, hypot)                   
from scipy import signal
from ..gui.projectsettings import SETTINGS
from . import detect_peaks

def parse_using_sample_field(pen_samples):
    """
    Find stroke boundary positions within pen_samples array. 
    
    pen_samples only contains the sample data for a single sample run
    (as defined by associated settings), not all the pen data.
    """
    ppp_minima = None
    
    edge_type = SETTINGS['stroke_detect_edge_type']
    if edge_type == 'none':
        edge_type = None
    vtype = SETTINGS['stroke_detect_peak_or_valley']
    # vtype 'Minima' == True        
    valley_types = [True,]
    if vtype == 'Maxima':
        valley_types = [False,]
    elif vtype == 'Minima & Maxima':
        valley_types = [True, False]
        
    for vt in valley_types:
        if ppp_minima is None:
            ppp_minima = detect_peaks(pen_samples[SETTINGS['stroke_detect_algorithm']],
                              mph=None,
                              mpd=SETTINGS[
                                  'stroke_detect_min_p2p_sample_count'],
                              edge=edge_type,
                              valley=vt)
        else:
            ppp_minima2 = detect_peaks(pen_samples[SETTINGS['stroke_detect_algorithm']],
                              mph=None,
                              mpd=SETTINGS[
                                  'stroke_detect_min_p2p_sample_count'],
                              edge=edge_type,
                              valley=vt)
                              
            ppp_minima = np.append(ppp_minima, ppp_minima2)
            ppp_minima.sort()

    return ppp_minima
    

_dat = dict()
temporal_resolution = 0.0
spatial_resolution = 0.0

def parse_velocity_and_curvature(series, all_series_dat=None, series_id=None):
    """
    Find stroke boundary positions within series pen samples array. 
    
    series only contains the sample data for a single sample series / run
    (as defined by associated settings), not all the pen data.
    """
    global _dat, temporal_resolution, spatial_resolution
    _dat = dict()
    if all_series_dat is not None and series_id is not None:
        all_series_dat[series_id]=_dat
    spatial_resolution = SETTINGS['device_spatial_resolution']
    temporal_resolution = SETTINGS['device_temporal_resolution']

    if temporal_resolution == 0.0:
        misi = diff(series['time']).mean()
        temporal_resolution = 1.0 / misi
        if np.isnan(temporal_resolution) or np.isnan(misi):
            print "Warning: Setting resolution to default:", 1.0 / 0.01, len(series)
            misi = 0.01
            temporal_resolution = 1.0 / misi
    _dat['x.fc5'] = butter_it(series['x'], 5, temporal_resolution)
    _dat['x.fc10'] = butter_it(series['x'], 10, temporal_resolution)
    _dat['y.fc5'] = butter_it(series['y'], 5, temporal_resolution)
    _dat['y.fc10'] = butter_it(series['y'], 10, temporal_resolution)
    
    _dat['series_sample_index'] = np.arange(len(series['time'])) 
    # Calculate velocity data
    # NOTE: velocity array index -1 is a copy of index -2 so velocity array 
    # == input array size.
    (_dat['vx.fc5'], 
     _dat['vy.fc5'], 
     _dat['vxy.fc5']) = get_velocity(series['time'], _dat['x.fc5'], _dat['y.fc5'])
     
    (_dat['vx.fc10'],
     _dat['vy.fc10'],
     _dat['vxy.fc10']) = get_velocity(series['time'], _dat['x.fc10'], _dat['y.fc10'])

    # Calculate local minima / maxima for xy velocity fc5 and fc10
    # Extrema are stored as index lists that can be used to access xy_fc*
    extrema = diff(sign(diff(_dat['vxy.fc10'])))
    _dat['vxy.fc10.minima'] = (extrema > 0).nonzero()[0] + 1
    _dat['vxy.fc10.maxima'] = (extrema < 0).nonzero()[0] + 1 
    extrema = diff(sign(diff(_dat['vxy.fc5'])))
    _dat['vxy.fc5.minima'] = (extrema > 0).nonzero()[0] + 1
    _dat['vxy.fc5.maxima'] = (extrema < 0).nonzero()[0] + 1 
    del extrema
    
    # Assign the first and the last element of a series as an extreme. 
    fixup_extrema(10)
    fixup_extrema(5)
    
    # Build _dat[vxy.fc*.extrema] arrays,
    # where -1 = minima, +1 = maxima, all other elements = 0.
    _dat['vxy.fc10.extrema'] = np.zeros(len(_dat['vxy.fc10']))
    _dat['vxy.fc10.extrema'][_dat['vxy.fc10.minima']] = -1
    _dat['vxy.fc10.extrema'][_dat['vxy.fc10.maxima']] = 1

    _dat['vxy.fc5.extrema'] = np.zeros(len(_dat['vxy.fc5']))
    _dat['vxy.fc5.extrema'][_dat['vxy.fc5.minima']] = -1
    _dat['vxy.fc5.extrema'][_dat['vxy.fc5.maxima']] = 1

    # Get nearest fc10_max to each fc5_max
    def find_nearest_maxfc10(value):
        return find_nearest(_dat['vxy.fc10.maxima'], value)

    # Any indices MISSING from NN are supernumerous maxima vxy.fc10 point.
    #NN = vectorize(find_nearest_maxfc10)(_dat['vxy.fc5.maxima'])

    ## Calculate DAlpha Extrema

    # Approximate dalpha for fc10
    dalpha = get_dalpha(10)

    _dat['vxy.fc10.minima.dalpha'] = np.zeros(len(series['time']), dtype=np.float64)
    _dat['vxy.fc10.minima.dalpha'][_dat['vxy.fc10.minima']] = dalpha
    
    pre_ix = _dat['vxy.fc10.minima.pre']
    _dat['vxy.fc10.minima.pre'] = np.zeros(len(series['time']), dtype=np.int)
    _dat['vxy.fc10.minima.pre'][_dat['vxy.fc10.minima']] = pre_ix

    post_ix = _dat['vxy.fc10.minima.post']
    _dat['vxy.fc10.minima.post'] = np.zeros(len(series['time']), dtype=np.int)
    _dat['vxy.fc10.minima.post'][_dat['vxy.fc10.minima']] = post_ix
    
    # Get candidate stroke_minima boundaries that pass abs_dalpha_thresh.        
    filtered_series_minima = _dat['vxy.fc10.minima'][abs(dalpha) > SETTINGS['stroke_detect_abs_dalpha_thresh']]
    #filtered_series_maxima = _dat['vxy.fc10.maxima'][NN]

    _dat['stroke_id'] = np.zeros(len(series['time']), dtype=np.uint32)
    _dat['stroke_state'] = np.zeros(len(series['time']), dtype=np.int8)
    _dat['stroke_state'][:] = -1
   
    stroke_bounds = assign_stroke_boundaries(series, filtered_series_minima)       


    keep_dat_cols = ['x.fc10', 'y.fc10', 'x.fc5', 'y.fc5', 'vxy.fc10', 'vxy.fc5',
                     'vxy.fc10.extrema', 'vxy.fc5.extrema', 'vxy.fc10.minima.dalpha',
                     'series_sample_index', 'vxy.fc10.minima.pre',
                     'vxy.fc10.minima.post']

    for dk in _dat.keys():
        if dk not in keep_dat_cols:
            _dat[dk] = None
            del _dat[dk]
            
    return stroke_bounds

# Butterworth filter
def butter_it(samples, frequency, sampling_rate):
    """
    """
    # Pad input array with reflection of first and last [temporal_resolution] 
    # elements. e.g. 133, for 133 hz. This way we pad using about 1 second 
    # worth of data at each end of the series.
    pad_len = min(len(samples), int(temporal_resolution))
    padding = samples[:pad_len][::-1] #reverse  order
    padded_data = append(padding, samples)
    padding = samples[-pad_len:][::-1] #reverse  order
    padded_data = append(padded_data, padding)
    
    w = 2.0 * (frequency/sampling_rate)#frequency / (sampling_rate / 2.0) # Normalize the frequency
    #print 'w:',w    
    try:
        b, a  = signal.butter(4, w, 'low') 
        return signal.filtfilt(b, a, padded_data, padtype=None)[pad_len:-pad_len]
    except:
        print 'Warning: Exception filtering samples. Sample length:', samples.shape
        return samples

# Calculate velocity of given series
def get_velocity(t, x, y):
    dx = (x[1:] - x[:-1]) / spatial_resolution
    dx = append(dx, dx[-1])
    dy = (y[1:] - y[:-1]) / spatial_resolution
    dy = append(dy, dy[-1])
    dxy = hypot(dx, dy)

    # NOTE: Using a fixed dt based on the specified temporal_resolution
    # instead of t[1:] - t[:-1], as example data file has a very 
    # variable ISI that cause occolations in velocity calc.
    dt = 1000.0 / temporal_resolution / 1000.0#t[1:] - t[:-1]    
    return dx/dt, dy/dt, dxy/dt


def fixup_extrema(freq):
    max_ix_key = "vxy.fc%d.maxima"%(freq)
    min_ix_key = "vxy.fc%d.minima"%(freq)
    klabel = "vxy.fc%d"%(freq)
    
    if len(_dat[min_ix_key]) == len(_dat[max_ix_key]) == 0:
        # no extrema in series
        if _dat[klabel][0] > _dat[klabel][-1]:
            _dat[max_ix_key] = append([0],_dat[max_ix_key])
            _dat[min_ix_key] = append(_dat[min_ix_key],[len(_dat[klabel])-1])
        else:
            _dat[min_ix_key] = append([0],_dat[min_ix_key])
            _dat[max_ix_key] = append(_dat[max_ix_key],[len(_dat[klabel])-1])
    elif len(_dat[min_ix_key]) == 0:
        _dat[min_ix_key] = append([0],_dat[min_ix_key])
        _dat[min_ix_key] = append(_dat[min_ix_key],[len(_dat[klabel])-1])
    elif len(_dat[max_ix_key]) == 0:
        _dat[max_ix_key] = append([0],_dat[max_ix_key])
        _dat[max_ix_key] = append(_dat[max_ix_key],[len(_dat[klabel])-1])
    else:
        # Extrema exist in series
        if _dat[max_ix_key][0] < _dat[min_ix_key][0] and _dat[max_ix_key][0] > 0:
            _dat[min_ix_key] = append([0],_dat[min_ix_key])
        elif _dat[max_ix_key][0] > _dat[min_ix_key][0] and _dat[min_ix_key][0] > 0:
            _dat[max_ix_key] = append([0],_dat[max_ix_key])

        if _dat[max_ix_key][-1] > _dat[min_ix_key][-1] and _dat[max_ix_key][-1] < len(_dat[klabel])-1:
            _dat[min_ix_key] = append(_dat[min_ix_key],[len(_dat[klabel])-1])
        elif _dat[max_ix_key][-1] < _dat[min_ix_key][-1] and _dat[min_ix_key][0] < len(_dat[klabel])-1:
            _dat[max_ix_key] = append(_dat[max_ix_key],[len(_dat[klabel])-1])


def find_nearest(a, v):
    return (abs(a - v)).argmin()


def get_dalpha(freq):
    """
    """
    x_label = 'x.fc%d'%(freq)
    y_label = 'y.fc%d'%(freq)
    sxy_label = 'sxy.fc%d'%(freq)
    
    # Calculate Arc Length between two data points. ####

    sres = spatial_resolution
    dx = diff(_dat[x_label]) / sres
    dy = diff(_dat[y_label]) / sres
    dxy = sqrt(square(dx) + square(dy))
    _dat[sxy_label] = append([0,], cumsum(dxy))  
    
    del dx
    del dy
    del dxy
        
    # get indexes of vxy.fc10 minima for the actual series
    vminsxy = _dat[sxy_label][_dat['vxy.fc%d.minima'%(freq)]]
    
    isd = SETTINGS['stroke_detect_inter_sample_distance'] 
    # find data point of at least inter_sample_distance 
    # spatially distance previous and succeeding        
    def find_pre(x):
        try:
            return where(_dat[sxy_label] >= (x - isd))[0][0] - 1
        except:
            return -1

    def find_it(x):
        try:
            return where(_dat[sxy_label] == x)[0][0]
        except:
            return -1

    def find_post(x):
        try:
            return where(_dat[sxy_label] >= (x + isd))[0][0]
        except:
            return -1

    pre = vectorize(find_pre)(vminsxy)
    # check if pre is always present, if not choose first value in series
    pre[pre==-1] = 0
    
    _dat['vxy.fc10.minima.pre'] = pre
    vmin = vectorize(find_it)(vminsxy)
    
    post = vectorize(find_post)(vminsxy)
    # check if post is always present, if not choose last value in series
    post[post==-1] = len(_dat[sxy_label])-1
    _dat['vxy.fc10.minima.post'] = post

    # angle between x axis and each line between start and 
    # individual point (i.e., index) which is between start and end
    alpha1 = arctan2( _dat[y_label][vmin] - _dat[y_label][pre],
                      _dat[x_label][vmin] - _dat[x_label][pre] ) * ( 180.0 / pi )
    # angle between x axis and each line between individual point
    # (i.e., index) which is between start and end and end
    alpha2 = arctan2(_dat[y_label][post] - _dat[y_label][vmin],
                     _dat[x_label][post] - _dat[x_label][vmin] ) * ( 180.0 / pi )
      
    # change in angle
    dalpha = alpha2 - alpha1
    dalpha[dalpha > 180.0] = dalpha[dalpha > 180.0] - 360.0
    dalpha[dalpha < -180.0] = dalpha[dalpha < -180.0] + 360.0
    
    return dalpha


def assign_stroke_boundaries(series_data, stroke_minima):
    MOTION = 0
    STROKE_PAUSE = 4
        
    # Each element of stroke_boundaries will be a list of:
    # stroke_id    start_ix    end_ix    type
    # where type indicates pause or motion.    
    stroke_boundaries = []
    
    if len(stroke_minima) == 0:
        print("Warning: No minima detected for series.")  
    elif len(stroke_minima) == 1:
        print("TODO: How to handle series with single minima.")
    else:
        # Add start and end boundaries at series start / end
        if stroke_minima[0] != 0:
            stroke_minima = append([0,],stroke_minima)
            #print "Adding start Minima"
        if stroke_minima[-1] != len(series_data)-1:
            #print "Adding end Minima"
            stroke_minima = append(stroke_minima,len(series_data)-1) 

        i = 0
        current_stroke = None
        for minima in stroke_minima[:-1]:
            start_ix = minima
            end_ix = stroke_minima[i+1]
            next_sxy = _dat['sxy.fc10'][end_ix]
            cur_sxy = _dat['sxy.fc10'][start_ix]
            dxy = next_sxy - cur_sxy
            if dxy < SETTINGS['stroke_detect_min_stroke_length']:
                # If stroke distance is less than min_stroke_length thresh,
                # mark it as a PAUSE
                if current_stroke:
                    # Expand current pause.
                    current_stroke[-1] = end_ix
                else:
                    # Start a pause stroke.
                    current_stroke=[len(stroke_boundaries)+1, STROKE_PAUSE, start_ix, end_ix]
            else:
                # Use mean velocity test
                avg_vel = _dat['vxy.fc10'][start_ix:end_ix].mean()
                if avg_vel < SETTINGS['stroke_detect_min_stroke_velocity']:
                    if current_stroke:
                        # Expand current pause.
                        current_stroke[-1] = end_ix
                    else:
                        # Start a pause stroke.
                        current_stroke=[len(stroke_boundaries)+1, STROKE_PAUSE, start_ix, end_ix]
                else:
                    if current_stroke:
                        stroke_boundaries.append(tuple(current_stroke))    
                    current_stroke=[len(stroke_boundaries)+1, MOTION, start_ix, end_ix]
                    stroke_boundaries.append(tuple(current_stroke))    
                    current_stroke = None
            i+=1            
                    
        if current_stroke:
            stroke_boundaries.append(tuple(current_stroke))    

        stroke_dtype = np.dtype({'names': ['id', 'type', 'start_ix', 'end_ix'],
                                 'formats': [np.uint32, np.uint8, np.uint32, np.uint32]})
                                 
        # Convert stroke_boundaries list of lists into an ndarray
        stroke_boundaries = np.asarray(stroke_boundaries,
                                            dtype=stroke_dtype)
                    
        return stroke_boundaries
