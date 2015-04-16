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
from operator import attrgetter
from weakref import proxy, ProxyType,WeakValueDictionary
import numpy as np
from markwrite.gui.projectsettings import SETTINGS

class PenDataSegmentCategory(object):
    _nextid=0
    totalsegmentcount=0
    id2obj=WeakValueDictionary()
    _project = None
    def __init__(self, name=None, parent=None, clear_lookup=True, project = None):
        self._name=name
        if name is None:
            self._name = u"Default Segment Category"

        self._id = self.nextid
        if clear_lookup:
            self.id2obj.clear()
        self.id2obj[self._id]=self
        # weakref.proxy to this segment's parent segment.
        # If segment is child of project node in gui tree, then parent
        # should be None.
        # Get using parent property.
        self._parent = None
        if parent:
            if isinstance(parent,ProxyType):
                self._parent = parent
            else:
                self._parent = proxy(parent)
        # List of 0 - N child (sub) segments associated with this segment.
        # If segment has no children, then _childsegments should be [].
        # Get childsegments property.
        self._childsegments = []
        self._childsegment_ids=[]

        if project:
            if isinstance(project,ProxyType):
                PenDataSegmentCategory._project = project
            else:
                PenDataSegmentCategory._project = proxy(project)

    @classmethod
    def clearSegmentCache(cls):
        cls._id=0
        cls.id2obj.clear()
        cls.project=None
        PenDataSegmentCategory.totalsegmentcount=0

    @property
    def nextid(self):
        nid = PenDataSegmentCategory._nextid
        PenDataSegmentCategory._nextid+=1
        return nid

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
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def children(self):
        return self._childsegments

    def getChildIndex(self, segment):
        return self._childsegment_ids.index(segment.id)

    def addChild(self, s):
        self._childsegments.append(s)
        self._childsegments = sorted(self._childsegments, key=attrgetter('starttime'))
        self._childsegment_ids.insert(self._childsegments.index(s),s.id)
        PenDataSegmentCategory.totalsegmentcount+=1

    def removeChild(self, s):
        seg_index = self._childsegment_ids.index(s.id)
        self._childsegment_ids.remove(s.id)
        self._childsegments.pop(seg_index)
        PenDataSegmentCategory.totalsegmentcount-=1

    @property
    def parent(self):
        return self._parent

    @property
    def project(self):
        return self._project

    @parent.setter
    def parent(self, s):
        self._parent = s

    def hasChildren(self):
        return len(self.children)>0

    def isRoot(self):
        return self.parent is None

    def getRoot(self):
        p = self
        while p.parent is not None:
            p=p.parent
        return p

    def _args2kwargs(self, args, kwargs={}):
        for a in args:
            arghandled = True
            if isinstance(a, (float, np.float, np.float32, np.float64)):
                kwargs.setdefault('time',a)
            elif isinstance(a, (int, long, np.int, np.int16, np.int32, np.int64)):
                kwargs.setdefault('pressure',a)
            elif isinstance(a, PenDataSegment):
                kwargs.setdefault('child',a)
            elif isinstance(a, basestring):
                kwargs.setdefault('tag',a)
            elif isinstance(a, (list, tuple)):
                if len(a)==2:
                    i,j=a
                    if isinstance(i, (float, np.float, np.float32, np.float64)):
                        kwargs.setdefault('timeperiod',(i,j))
                    elif isinstance(i, (int, long, np.int, np.int16, np.int32, np.int64)):
                        kwargs.setdefault('position',(i,j))
                    else:
                        arghandled=False
                else:
                    arghandled=False
            else:
                arghandled=False

            if not arghandled:
                print "Error: Segment.contains ambigious arg: ",a
        return kwargs

    def contains(self, *args, **kwargs):
        kwargs = self._args2kwargs(args,kwargs)
        for k,v in kwargs.items():
            if k == 'time':
                return self.starttime <= v <= self.endtime
            elif k == 'position':
                x, y = v
                return np.any(self.pendata['x']==x & self.pendata['y']==y)
            elif k == 'pressure':
                return np.any(self.pendata['pressure']==v)
            elif k == 'timeperiod':
                stime, etime = v
                return stime > self.starttime and etime < self.endtime
            elif k == 'tag':
                return self.name is v
            elif k == 'child':
                return v.id in self._childsegment_ids
            else:
                print "Error: Segment.contains ambigious kwarg: ",k,':',v
                return False
    @property
    def level(self):
        lvl = 0
        p = self.parent
        while p is not None:
            lvl+=1
            p = p.parent
        return lvl

    def getLevelCount(self, curlvl=None, visitedlvls=[]):
        if curlvl is None:
            curlvl=self.level

        if curlvl not in visitedlvls:
            visitedlvls.append(curlvl)

        for c in self.children:
            c.getLevelCount(curlvl+1,visitedlvls)
        return max(visitedlvls)

    def getLeveledSegments(self, curlvl=None, segsbylvl=None):
        if segsbylvl is None:
            segsbylvl = OrderedDict()
        if curlvl is None:
            curlvl=self.level+1

        if not segsbylvl.has_key(curlvl):
            if self.parent:
                lsegs=[]
                for c in self.parent.children:
                    lsegs+=c.children
                segsbylvl[curlvl] = lsegs
            else:
                segsbylvl[curlvl]=list(self.children)

        for c in self.children:
            c.getLeveledSegments(curlvl+1,segsbylvl)

        return segsbylvl

    @property
    def pendata(self):
        return self._project._pendata

    @property
    def starttime(self):
        return self.pendata['time'][0]

    @property
    def endtime(self):
        return self.pendata['time'][-1]

    @property
    def timerange(self):
        return self.pendata['time'][[0,-1]]


    @property
    def pointcount(self):
        return self.pendata.shape[0]

    @classmethod
    def calculateTrimmedSegmentIndexBoundsFromTimeRange(cls, starttime, endtime):
        """
        Calculates the first and last array indices in the full projects
        pen data that wuld be used for creating a segment with the uncorrected time range
        provided by starttime, endtime.
        :param startt:
        :param endt:
        :return:
        """
        pendata = cls._project._pendata
        mask = None
        if SETTINGS['new_segment_trim_0_pressure_points']:
            mask = (pendata['time'] >= starttime) & (pendata['time'] <=endtime) & (pendata['pressure'] > 0)
        else:
            mask = (pendata['time'] >= starttime) & (pendata['time'] <= endtime)
        return np.nonzero(mask)[0][[0,-1]]

    def propertiesTableData(self):
        """
        Return a dict of segment properties to display in the Selected Project
        Tree Node Object Properties Table.

        :return: dict of segmentcategory properties to display
        """

        project_properties = OrderedDict()
        project_properties['Name'] = dict(val=self.name)
        project_properties['ID'] = dict(val=self.id)
        project_properties['Start Time'] = dict(val=self.starttime)
        project_properties['End Time'] = dict(val=self.endtime)
        project_properties['Point Count'] = dict(val=self.pointcount)
        project_properties['level'] = dict(val=self.level)
        return project_properties

class PenDataSegment(PenDataSegmentCategory):
    def __init__(self, name=None, pendata=None, parent=None):
        """

        :param name:
        :param pendata:
        :return:
        """
        PenDataSegmentCategory.__init__(self,name, parent, False)


        if self._name is None:
            self._name="Segment %d"%(self._id)

        self._pendata=pendata
        parent.addChild(self)

    @property
    def pendata(self):
        return self._pendata

    @pendata.setter
    def pendata(self, n):
        self._pendata = n

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
        project_properties['level'] = dict(val=self.level)
        return project_properties
