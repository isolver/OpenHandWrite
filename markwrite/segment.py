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

from collections import OrderedDict

class PenDataSegment(object):
    _nextid=1
    def __init__(self, name=None, pendata=None):
        """

        :param name:
        :param pendata:
        :return:
        """
        self._id = self.nextid

        self._name=name
        if self._name is None:
            self._name="Segment %d"%(self._id)

        self._pendata=pendata

        # weakref.proxy to this segment's parent segment.
        # If segment is child of project node in gui tree, then parentsegment
        # should be None.
        # Get / Set using parentsegment property.
        #
        # TODO: If this segment has a parent segment, then this segments pendata
        # must be a subset of the parent segments pendata.
        #
        # CONSIDER: Should this be the parent segment's id property
        # instead of a ref to parent segment object?
        self._parentsegment = None

    @property
    def nextid(self):
        nid = PenDataSegment._nextid
        PenDataSegment._nextid+=1
        return nid

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def id(self):
        """

        :return:
        """
        return self._id

    @id.setter
    def id(self, n):
        """
        TODO: Ensure id being set is not already in use by another segment in
              the project.

        :param n:
        :return:
        """
        self._id = n

    @property
    def pendata(self):
        return self._pendata

    @pendata.setter
    def pendata(self, n):
        self._pendata = n

    @property
    def starttime(self):
        return self._pendata['time'][0]

    @property
    def endtime(self):
        return self._pendata['time'][-1]

    @property
    def parentsegment(self):
        return self._parentsegment

    @parentsegment.setter
    def parentsegment(self, s):
        self._parentsegment = s

    @property
    def pointcount(self):
        return self._pendata.shape[0]

    def propertiesTableData(self):
        """
        Return a dict of segment properties to display in the MarkWrite
        Application Project Properties Table.

        :return: dict of segment properties to display
        """

        project_properties = OrderedDict()
        project_properties['Name'] = dict(val=self.name)
        project_properties['ID'] = dict(val=self.id)
        project_properties['Start Time'] = dict(val=self.starttime)
        project_properties['End Time'] = dict(val=self.endtime)
        project_properties['Point Count'] = dict(val=self.pointcount)
        return project_properties