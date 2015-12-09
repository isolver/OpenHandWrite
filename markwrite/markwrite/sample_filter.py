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

# The length of the filter window (i.e. the number of coefficients).
# window_length must be a positive odd integer.
window_length = 13
# The order of the polynomial used to fit the samples.
# polyorder must be less than window_length.
polyorder = 9

def filter_pen_sample_series(project, series):
    """
    Given the pen samples ndarray in series, perform filtering on the
    x, y, and pressure values, updating the associated 'filter_X' fields
    with the filter results.
    :param project: markwrite project containing the all sample data.
    :param series: markwrite sample ndarray for the series to be filtered.
    :return:
    """

    # Initial filter will use scipy.signal.savgol_filter, commonly used in
    # eye tracking data, as it does not phase shift the data and does
    # a good job of smoothing out noise while maintaining signal.
    # See http://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter

    series['x_filtered'] = savgol_filter(series['x'], window_length, polyorder)
    series['y_filtered'] = savgol_filter(series['y'], window_length, polyorder)
    series['pressure_filtered'] =  savgol_filter(series['pressure_filtered'], window_length, polyorder)