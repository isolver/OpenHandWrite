__author__ = 'Sol'

# filter data
from .sample_filter import filter_pen_sample_series
from .sample_va import calculate_velocity
from .detect_peaks import detect_peaks
from .parse_strokes import parse_using_sample_field, parse_velocity_and_curvature