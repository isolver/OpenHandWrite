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

from weakref import proxy
import time
import os
import glob
import numpy as np
import codecs

from pyqtgraph import OrderedDict
from pyqtgraph.Qt import QtGui
from file_io import EyePenDataImporter, XmlDataImporter
from segment import PenDataSegmentSet

class MarkWriteProject(object):
    project_file_extension = u'mwp'
    input_file_loaders=dict(xml=XmlDataImporter,
                            txyp=EyePenDataImporter)
    def __init__(self, name=u"New", file_path=None):
        """
        The MarkWriteProject class represents a MarkWrite project created using
        the MarkWrite Application. Information about imported data, etc. (TBD)
        is stored in the class for use while MarkWrite is running.

        A MarkWriteProject instance can be saved to a .wmpd file. The
        saved .wmpd file can be reopened from within the MarkWrite application
        at a later time to continue working on the project.

        The MarkWrite Application supports a single MarkWriteProject open
        at a time. To switch between different MarkWriteProject's, use File->Open
        and select the .wmpd file to open.

        :param name: str
        :param kwargs: dict
        :return: MarkWriteProject instance
        """
        self._pendata = None
        self._selectedtimeperiod=[0,0]
        self._selectedpendata=[0,0]
        self._segmentset=None
        self.autodetected_segment_tags=[]
        self._name = u"Unknown"
        self._original_timebase_offset=0

        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
            dir_path, file_name = os.path.split(file_path)
            # Load raw data from file for use in project
            fname, fext=file_name.rsplit(u'.',1)
            fimporter = self.input_file_loaders.get(fext)
            if fimporter:
                self.createNewProject(fname, fimporter.asarray(file_path))
                self.autodetected_segment_tags=self.detectAutoAssociatedSegmentTags(dir_path,fname,fext)
            elif file_name.lower().endswith(self.project_file_extension):
                self.openExistingProject(file_path)
            else:
                print "Unsupported file type:",file_path
        else:
            raise IOError("Invalid File Path: %s"%(file_path))

    def detectAutoAssociatedSegmentTags(self,dir_path,fname,fext):
        tag_list=[]
        same_named_files = glob.glob(os.path.join(dir_path,fname+u'.*'))
        if len(same_named_files)<2:
            return tag_list

        same_named_files=[f for f in same_named_files if not f.endswith(fext)]
        if len(same_named_files)<1:
            return tag_list

        with codecs.open(same_named_files[0], "r", "utf-8") as f:
            for seg_line in f:
                seg_line=seg_line.splitlines()[-1].strip()
                if seg_line:
                    tag_list.append(seg_line)
        return tag_list

    def createNewProject(self, file_name, pen_data):
            # TODO : Define MarkWrite project setting and implement GUI for editing
            self._project_settings = OrderedDict()
            self._name = file_name

            # Normalize pen sample times so first sample starts at 0.0 sec.
            self._original_timebase_offset=pen_data[0]['time']
            pen_data['time']-=self._original_timebase_offset
            pen_data['time']=pen_data['time']/1000.0

            self._pendata = pen_data
            self._selectedtimeperiod=[0,0]
            self._selectedpendata=None
            self._segmentset=PenDataSegmentSet()
            self._project_file_path = u''
            self._modified = True
            self._created_date = time.strftime("%c")
            self._modified_date = self._created_date

            #self._project_tree = None
            #self.projectTreeNode()

    def openExistingProject(self, file_path):
        print "Reloading a saved MarkWrite Project is not implemented."
        dir_path, file_name = os.path.split(file_path)
        self._name = file_name
        self._pendata = None #TODO: Load from proj file.
        self._selectedtimeperiod=None #TODO: Load from proj file.
        self._selectedpendata=None #TODO: Load from proj file.
        self._segmentset=None #TODO: Load from proj file.
        self._project_settings = OrderedDict() #TODO: Load from proj file.
        self._project_file_path = file_path
        self._modified = False
        self._created_date = u"READ FROM PROJ FILE"
        self._modified_date = u"READ FROM PROJ FILE"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def created_date(self):
        """
        A string representing the date and time that the project was
        first created.

        :return: str
        """
        return self._created_date

    @property
    def modified_date(self):
        """
        A string representing the last date and time that the project was
        modified and saved.

        :return: str
        """
        return self._modified_date

    @property
    def modified(self):
        """
        True if the project has been modified since it was last saved; False
        otherwise.

        :return: bool
        """
        return self._modified

    @property
    def pendata(self):
        return self._pendata

    @property
    def allpendata(self):
        return self._pendata

    @property
    def unsegmentedpendata(self):
        return self._pendata[self._pendata['segmented']==0]

    @property
    def segmentedpendata(self):
        return self._pendata[self._pendata['segmented']>0]

    @property
    def selectedtimeperiod(self):
        return self._selectedtimeperiod

    @selectedtimeperiod.setter
    def selectedtimeperiod(self, n):
        self._selectedtimeperiod = n

    @property
    def selectedpendata(self):
        return self._selectedpendata

    @selectedpendata.setter
    def selectedpendata(self, n):
        self._selectedpendata = n

    @property
    def segmentset(self):
        return self._segmentset

    def save(self):
        """
        Save the this MarkWrite project to self.file_path.
        Return True is the project was saved, otherwise return False.

        :return: bool
        """
        # TODO : Implement MarkWrite project saving
        # To Save:
        #    1) TBD
        print 'MarkWriteProject save not implemented'
        if self._project_file_path is None:
            print 'Should be calling saveas, not save.'
        print 'Should save project file'
        print '------'
        self._modified=False
        self._modified_date = time.strftime("%c")
        return False

    def saveAs(self,path):
        """
        Save a copy of this MarkWrite project to the file system absolute path given
        by path. Any modifications made to the project since it was last opened
        are not saved to the original project file and are instead saved in
        the new project file.

        Return True is the project was saved, otherwise return False.

        :param path: str
        :return: bool
        """
        # TODO : Implement MarkWrite project saveAs
        print 'MarkWriteProject saveAs not implemented'
        print 'Should prompt for directory to save project file'
        print 'Should save project file'
        print '------'
        self._modified=False
        self._created_date = time.strftime("%c")
        self._modified_date = self._created_date

    def close(self):
        """
        Close the MarkWrite project, including closing any imported data files.
        Return a bool indicating if the close operation was successful or not.

        :return: bool
        """
        self._modified = False
        self._pendata = None
        return True

    def propertiesTableData(self):
        """
        Return a dict of project properties to display in the MarkWrite
        Application Project Properties Table.

        :return: dict of project properties to display
        """

        project_properties = OrderedDict()
        project_properties['Name'] = dict(val=self.name)
        project_properties['Pen Points Count'] = dict(val=self._pendata.shape[0])
        project_properties['Created On'] = dict(val=self.created_date)
        project_properties['Last Saved'] = dict(val=self.modified_date)
        project_properties['Currently Modified'] = dict(val=self.modified)
        return project_properties
