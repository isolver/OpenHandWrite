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

import os, inspect

# time
from timeit import default_timer
import sys
import numpy as np

def getTime():
    return default_timer()

def module_path(local_function):
    """ returns the module path without the use of __file__.  Requires a function defined
   locally in the module. from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module"""
    return os.path.abspath(inspect.getsourcefile(local_function))

def module_directory(local_function):
    mp=module_path(local_function)
    moduleDirectory,mname=os.path.split(mp)
    return moduleDirectory

def get_resource_folder_path():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.join(os.path.dirname(sys.executable),u'resources')
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.join(module_directory(getTime),u'resources')

    return datadir
# dir location

def getIconFilePath(icon_file_name):
    return os.path.join(get_resource_folder_path(),'icons',icon_file_name)

def getIconFile(iname,size=32,itype='png'):
    return getIconFilePath(u"%s_icon&%d.%s"%(iname,size,itype))

def getSegmentTagsFilePath(tags_file_name=u'default.tag'):
    return os.path.join(get_resource_folder_path(),'tags',tags_file_name)

# numpy array manipulation related

def contiguous_regions(condition):
    """Finds contiguous True regions of the boolean array "condition". Returns
    three 1d arrays:  start indicies, stop indicies and lengths of contigous regions
    """

    d = np.diff(condition)
    idx, = d.nonzero()
    idx += 1 # need to shift indices because of diff

    if condition[0]:
        # If the start of condition is True prepend a 0
        idx = np.r_[0, idx]

    if condition[-1]:
        # If the end of condition is True, append the length of the array
        idx = np.r_[idx, condition.size] # Edit

    starts = idx[0::2]
    stops = idx[1::2]
    lengths = stops - starts

    return starts, stops, lengths