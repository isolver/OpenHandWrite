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

# dir location

software_directory=module_directory(getTime)
resource_dir_path=os.path.abspath(os.path.join(software_directory,'./resources'))
icon_dir_path=os.path.abspath(os.path.join(resource_dir_path,'icons'))
tag_files_dir_path=os.path.abspath(os.path.join(resource_dir_path,'tags'))

def getIconFilePath(icon_file_name):
    return os.path.join(icon_dir_path,icon_file_name)

def getResourceFilePath(resource_file_name):
    return os.path.join(resource_dir_path,resource_file_name)

def getIconFile(iname,size=32,itype='png'):
    return os.path.join(getResourceFilePath(),u"%s_icon&%d.%s"%(iname,size,itype))

def getSegmentTagsFilePath(tags_file_name=u'default.tag'):
    return os.path.join(tag_files_dir_path,tags_file_name)
