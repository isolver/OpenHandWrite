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
import numpy as np

from pyqtgraph import OrderedDict
from pyqtgraph.Qt import QtGui
from file_io import EyePenDataImporter, XmlDataImporter

class MarkWriteProject(object):
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
        self._segments=[]
        self._segment_ids=[]

        self._name = u"Unknown"

        if file_path and os.path.exists(file_path) and os.path.isfile(file_path):
            dir_path, file_name = os.path.split(file_path)
            # Load raw data from file for use in project
            if file_name[-3:].lower() == u'xml':
                self.createNewProject(file_name,XmlDataImporter.asarray(file_path))
            elif file_name[-3:].lower() == u'txt':
                self.createNewProject(file_name, EyePenDataImporter.asarray(file_path))
            elif file_name[-4:].lower() == u'wmpd':
                self.openExistingProject(file_path)
            else:
                print "Unsupported file type:",file_path
        else:
            raise IOError("Invalid File Path: %s"%(file_path))

    def createNewProject(self, file_name, pen_data):
            # TODO : Define MarkWrite project setting and implement GUI for editing
            self._project_settings = OrderedDict()
            self._name = file_name
            self._pendata = pen_data
            self._selectedtimeperiod=[0,0]
            self._selectedpendata=None
            self._segments=[]
            self._segment_ids=[]
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
        self._segments=None #TODO: Load from proj file.
        self._segment_ids=None #TODO: Load from proj file.
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
    def segments(self):
        return self._segments

    def getSegmentIndex(self, segment):
        return self._segment_ids.index(segment.id)

    def addSegment(self, s):
        from operator import attrgetter
        self._segments.append(s)
        self._segments = sorted(self._segments, key=attrgetter('starttime'))
        self._segment_ids.insert(self._segments.index(s),s.id)

    def removeSegment(self, s):
        seg_index = self._segment_ids.index(s.id)
        self._segment_ids.remove(s.id)
        self._segments.pop(seg_index)

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
