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
from __future__ import division

import scipy
from scipy.signal import savgol_filter
import numpy as np
# The length of the filter window (i.e. the number of coefficients).
# window_length must be a positive odd integer.
window_length = 13
# The order of the polynomial used to fit the samples.
# polyorder must be less than window_length.
polyorder = 9

def calculate_velocity(project, series):
    """
    Given the pen samples ndarray in series, calculate velocity for x and y
    fields, updating the associated '*_velocity' fields
    with the calculated result.
    :param project: markwrite project containing the all sample data.
    :param series: markwrite sample ndarray.
    :return:
    """

    # Calculate velocity using 1st deriv scipy.signal.savgol_filter,
    # as it does not phase shift the data and does a good job of
    # smoothing out noise with minimal signal distortion.
    # See http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter
    #dt = series['time'][1:]-series['time'][0:-1]
    #delta = dt.mean()
    series['x_velocity'] = savgol_filter(series['x'], window_length, polyorder,
                                         deriv=1, delta=1.0)
    series['y_velocity'] = savgol_filter(series['y'], window_length, polyorder,
                                         deriv=1, delta=1.0)

    dx = series['x_filtered'][1:]-series['x_filtered'][0:-1]
    dy = series['y_filtered'][1:]-series['y_filtered'][0:-1]

    series['xy_velocity'][1:] = savgol_filter(np.hypot(dx,dy), window_length, polyorder)
    series['xy_velocity'][0] = 0


