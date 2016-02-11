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
from markwrite.gui import X_FIELD, Y_FIELD

class PenDataSegmentCategory(object):
    '''
    PenDataSegmentCategory is the root of a MarkWriteProject segment tree.
    Currently MarkWrite only supports a single root segment node, which covers
    the all pendata samples.

    When a user creates a Segment in the MarkWrite GUI App, a PenDataSegment
    is created, which is a subclass of this class.
    '''
    _nextid=0
    totalsegmentcount=0
    id2obj=WeakValueDictionary()
    _project = None
    _serialize_attributes=(
                            '_name',
                            'id',
                            '_childsegment_ids',
                            'timerange',
                            #'children', # children is filled directly by toDict()
                            '_locked',
                            'totalsegmentcount'
                          )
    def __init__(self, name=None, parent=None, clear_lookup=True, project = None, id=None):
        self._name=name
        if name is None:
            self._name = u"Default Segment Category"

        if id is not None:
            self.id = id
        else:
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

        # If a segment is locked, it can not be deleted or modified.
        self._locked=False

        self._cond_vars=None
        
        if project:
            if isinstance(project,ProxyType):
                PenDataSegmentCategory._project = project
            else:
                PenDataSegmentCategory._project = proxy(project)

    @classmethod
    def _clearSegmentCache(cls):
        cls._id=0
        cls.id2obj.clear()
        cls._project=None
        PenDataSegmentCategory.totalsegmentcount=0

    @property
    def nextid(self):
        nid = PenDataSegmentCategory._nextid
        PenDataSegmentCategory._nextid+=1
        return nid

    @property
    def id(self):
        """
        A unique positive int value identifying the segment.

        :return: int
        """
        return self._id

    @id.setter
    def id(self, n):
        """
        TODO: Ensure id being set is not already in use by another segment in
              the project.
        :param n:
        :return: None
        """
        self._id = n
        if self._nextid <= n:
            PenDataSegmentCategory._nextid = n+1

    @property
    def name(self):
        '''
        Return the segment's name / label.

        :return: basestring
        '''
        return self._name

    @name.setter
    def name(self, n):
        '''
        Set the segment's name / label.


        :param n:
        :return:
        '''
        self._name = n

    @property
    def locked(self):
        '''
        Return whether the segment is in a locked state or not.
        If a segment is locked, it can not be deleted from the project and it's
        name can not be set.

        :return: bool
        '''
        return self._locked

    @locked.setter
    def locked(self, l):
        '''
        Set whether the segment is locked or not. When a
        segment is locked (l = True), it can not be deleted from the project
        and it's name can not be changed.

        :param l: bool
        :return: None
        '''
        self._locked = l

    @property
    def cond_vars(self):
        '''
        The property is of of use when the current project was created from
        loading an ioHub HDF5 file.

        Returns the experiment condition variables associated with the
        Trial Segment (l1seg) of the current segment's (which maybe self).

        :return: PenDataSegment
        '''
        if self._cond_vars:
            return self._cond_vars
        if self.l1seg:
            return self.l1seg._cond_vars

    @cond_vars.setter
    def cond_vars(self, cv):
        '''
        cond_vars property setter. To be used by MarkWrite GUI app only.

        :param cv:
        :return: None
        '''
        self._cond_vars = cv
        
    @property
    def children(self):
        '''
        If the current segment has children, return them as a list of
        PenDataSegment objects. Child segments are returned sorted
        by segment start time.

        :return: list of 0 to N PenDataSegment objects
        '''
        return self._childsegments

    def getChildIndex(self, segment):
        '''
        Return the index of `segment` within the current segments children.

        :param segment: PenDataSegment
        :return: int
        '''
        return self._childsegment_ids.index(segment.id)

    def addChild(self, s):
        '''
        This method can only be used by the MarkWrite GUI app.

        :param s:
        :return:
        '''
        self._childsegments.append(s)
        self._childsegments = sorted(self._childsegments, key=attrgetter('starttime'))
        self._childsegment_ids.insert(self._childsegments.index(s),s.id)
        PenDataSegmentCategory.totalsegmentcount+=1

    def removeChild(self, s):
        '''
        This method can only be used by the MarkWrite GUI app.

        Remove the PenDataSegment `s` from the current segments children.
        :param s: PenDataSegment
        :return: None
        '''
        seg_index = self._childsegment_ids.index(s.id)
        self._childsegment_ids.remove(s.id)
        self._childsegments.pop(seg_index)
        PenDataSegmentCategory.totalsegmentcount-=1

    @property
    def parent(self):
        '''
        Return the parent of the current segment, or None if the current segment
        is the root segment of the project.

        :return: PenDataSegment or None
        '''
        return self._parent

    @parent.setter
    def parent(self, s):
        self._parent = s

    def hasChildren(self):
        '''
        Return True if the current segment has >= 1 child segment.

        :return: bool
        '''
        return len(self.children)>0

    def isRoot(self):
        '''
        Return True if the current segment is the top level, root, segment
        of the project.

        If True, then the current segment will equal the project.segmenttree
        object.

        :return: bool

        '''
        return self.parent is None

    def getRoot(self):
        '''
        Return the root segment for the project.

        :return: PenDataSegmentCategory
        '''
        p = self
        while p.parent is not None:
            p=p.parent
        return p

    @property
    def project(self):
        '''
        Return a weakref to the MarkWriteProject that the segment is part of.

        :return: MarkWriteProject
        '''
        return self._project

    @property
    def path(self):
        '''
        Return a list of segment names, representing the current segments
        position within the project's segment hierarchy. The first element of
        the path list is always the project's root segment name. The last
        element of the path list is the current parent segment's name.

        :return: list of basestrings
        '''
        spath=[]
        p = self.parent
        while p is not None:
            spath.append(p.name)
            p=p.parent
        return spath[::-1]

    @property
    def tree(self):
        '''
        Return a list of PenDataSegments. The first element of
        the list is the parent of the current segment. The last
        element of the list is always the root segment.

        :return: list of PenDataSegments
        '''
        spath=[]
        p = self.parent
        while p is not None:
            spath.append(p)
            p=p.parent
        return spath

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
        '''
        Returns True if all arguments passed to the method evaluate to be
        'within' the current segment. The definition of 'within' depends on the
        argument data type or kwarg name.

        | arg data types | kwarg name | evaluation |
        | float, np.float, np.float32, np.float64 | time       | self.starttime <= time <= self.endtime |
        | list or tuple of two floats | position   | np.any(self.pendata[X_FIELD]==x & self.pendata[Y_FIELD]==y) |
        | int, long, np.int, np.int16, np.int32, np.int64 | pressure   | np.any(self.pendata['pressure']==v) |
        | list or tuple of two ints | timeperiod | timeperiod[0] > self.starttime and timeperiod[1] < self.endtime |
        | basestring | tag        | self.name is tag |
        | PenDataSegment | child      | child.id in self._childsegment_ids|

        :return: bool
        '''
        kwargs = self._args2kwargs(args,kwargs)
        for k,v in kwargs.items():
            if k == 'time':
                return self.starttime <= v <= self.endtime
            elif k == 'position':
                x, y = v
                return np.any(self.pendata[X_FIELD]==x & self.pendata[Y_FIELD]==y)
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
        '''
        The number of parent segments to reach the root segment.
        The root segment has level == 0.

        :return: int
        '''
        lvl = 0
        p = self.parent
        while p is not None:
            lvl+=1
            p = p.parent
        return lvl

    def getLevelCount(self, curlvl=None, visitedlvls=[]):
        '''
        Return the maximum level depth in the project segment tree.

        :return: int
        '''
        if curlvl is None:
            curlvl=self.level

        if curlvl not in visitedlvls:
            visitedlvls.append(curlvl)

        for c in self.children:
            c.getLevelCount(curlvl+1,visitedlvls)
        return max(visitedlvls)

    def getLeveledSegments(self, curlvl=None, segsbylvl=None):
        '''
        Return a dict with all segment levels as the keys,
        and a list of all the PenDataSegments at a given level,
        regardless of parent, as the dict values.

        :return: dict
        '''
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
    def l1seg(self):
        '''
        Return the current segment's level 1 parent.

        :return: PenDataSegment
        '''
        segtree=self.tree
        if len(segtree) == 1:
            return self
        elif len(segtree) > 1:
            return segtree[-2]
            
    @property
    def pendata(self):
        '''
        Return the pen samples contained within the segment time period.

        :return: ndarray
        '''
        return self._project.pendata

    @property
    def starttime(self):
        '''
        Return the current segment's sec.msec start time.
        This will be equal to `self.pendata['time'][0]`.

        :return: float
        '''
        return self.pendata['time'][0]

    @property
    def endtime(self):
        '''
        Return the current segment's sec.msec end time.
        This will be equal to `self.pendata['time'][-1]`.

        :return: float
        '''
        return self.pendata['time'][-1]

    @property
    def duration(self):
        '''
        Return the sec.msec duration of the segment, which is equal to
        self.endtime - self.starttime.

        :return: float
        '''
        return self.pendata['time'][-1] - self.pendata['time'][0]

    @property
    def timerange(self):
        '''
        Return the segment's starttime, endtime as an array of two sec.msec
        times.

        :return:
        '''
        return self.pendata['time'][[0,-1]]

    @timerange.setter
    def timerange(self, v):
        pass

    @property
    def pointcount(self):
        '''
        Return the number of pen samples that are contained in the segment.

        :return: int
        '''
        return self.pendata.shape[0]

    @property
    def nonzeropressurependata(self):
        '''
        Return the pen samples contained within the segment time period where
        the samples pressure value is greater than 0.

        :return: ndarray
        '''
        return self.pendata[self.pendata['pressure']>0]

    @property
    def zeropressurependata(self):
        '''
        Return the pen samples contained within the segment time period where
        the samples pressure value is equal to 0.

        :return: ndarray
        '''
        return self.pendata[self.pendata['pressure']==0]

    @classmethod
    def calculateTrimmedSegmentIndexBoundsFromTimeRange(cls, starttime, endtime):
        """
        This method should only be used by the MarkWrite GUI app.

        Calculates the first and last array indices in self.project.pendata
        that would be used for creating a segment with the uncorrected
        time range provided by starttime, endtime.

        :param startt:
        :param endt:
        :return:
        """
        pendata = cls._project.pendata
        mask = None
        if SETTINGS['new_segment_trim_0_pressure_points']:
            mask = (pendata['time'] >= starttime) & (pendata['time'] <=endtime) & (pendata['pressure'] > 0)
        else:
            mask = (pendata['time'] >= starttime) & (pendata['time'] <= endtime)
        nonzero_ixs=np.nonzero(mask)[0]
        if nonzero_ixs.shape[0]>0:
            return nonzero_ixs[[0,-1]]
        return []

    def toDict(self):
        '''
        Returns a dict representation of the segment, suitable for serialization
        as part of a serializable markwrite project representation.

        :return: dict
        '''
        segdict = dict()
        for a in self._serialize_attributes:
            if hasattr(self, a):
                pa = getattr(self,a)
                if callable(pa):
                    pa = pa()
                if hasattr(pa, 'toDict'):
                    pa = pa.toDict()
                segdict[a] = pa
            else:
                print "### Segment.toDict Error: %s is not a member of the segment class"%a

        segdict['child_segments']=[]
        for cs in self.children:
            segdict['child_segments'].append(cs.toDict())
        return segdict

    @classmethod
    def fromDict(cls, d, project=None, parent = None):
        '''
        This method should only be used by the MarkWrite GUI app.

        Return a PenDataSegmentCategory or PenDataSegment instance given the
        data provided in `d`.

        :return: PenDataSegment
        '''
        if parent is None:
            seg = PenDataSegmentCategory(name=d['_name'], project=project, id=d['id'])
            PenDataSegmentCategory.totalsegmentcount=d['totalsegmentcount']
        else:
            pd = parent.project.getPenDataForTimePeriod(*d['timerange'])
            seg = PenDataSegment(name=d['_name'], pendata=pd, parent=parent, fulltimerange=d['timerange'], id=d['id'])

        seg._childsegment_ids=d['_childsegment_ids']
        seg._locked=d['_locked']

        for cs in d['child_segments']:
           seg._childsegments.append(PenDataSegment.fromDict(cs, project, seg))

        return seg

    def propertiesTableData(self):
        """
        This method should only be used by the MarkWrite GUI app.

        Return a dict of segment properties to display in the Selected Project
        Tree Node Object Properties Table.

        :return: dict of segmentcategory properties to display
        """
        project_properties = OrderedDict()
        project_properties['Name'] = [self.name,]
        project_properties['ID'] = [self.id,]
        project_properties['Start Time'] = ["%.3f"%self.starttime,]
        project_properties['End Time'] = ["%.3f"%self.endtime,]
        project_properties['Duration'] = ["%.3f"%self.duration,]
        project_properties['# Total Samples'] = [self.pointcount,]
        project_properties['# No Pressure Samples'] = [self.zeropressurependata.shape[0],]
        project_properties['# Runs'] = ['TODO',]
        project_properties['Preceding Pen-Lift Duration'] = ['TODO',]
        project_properties['Hierarchy Path'] = [self.path,]
        project_properties['Hierarchy Level'] = [self.level,]
        project_properties['Child Count'] = [len(self.children),]
        return project_properties

class PenDataSegment(PenDataSegmentCategory):
    def __init__(self, name=None, pendata=None, parent=None, fulltimerange=None, id=None):
        """

        :param name:
        :param pendata:
        :return:
        """
        PenDataSegmentCategory.__init__(self,name, parent, False, id=id)

        if fulltimerange is None:
            fulltimerange = pendata['time'][[0,-1]]
        self._timerange = fulltimerange

        if self._name is None:
            self._name="Segment %d"%(self._id)

        self._pendata=pendata

        self.tableprops = None

        parent.addChild(self)

    @property
    def pendata(self):
        return self._pendata

    @property
    def starttime(self):
        '''
        TODO: DOCSTR

        :return:
        '''
        return self._timerange[0]

    @property
    def endtime(self):
        '''
        TODO: DOCSTR

        :return:
        '''
        return self._timerange[1]

    @property
    def duration(self):
        return self._timerange[1]-self._timerange[0]

    @property
    def timerange(self):
        return self._timerange

    @timerange.setter
    def timerange(self, tr):
        self._timerange = tr

    @pendata.setter
    def pendata(self, n):
        self._pendata = n

    def propertiesTableData(self):
        """
        Return a dict of segment properties to display in the Selected Project
        Tree Node Object Properties Table.

        :return: dict of segmentcategory properties to display
        """
        ix_bounds = self.calculateTrimmedSegmentIndexBoundsFromTimeRange(self.starttime, self.endtime)
        min_ix, max_ix = 'N/A','N/A'
        period_count = 0
        if len(ix_bounds)>0:
            min_ix, max_ix = ix_bounds
            start_ixs,stop_ixs,lengths=PenDataSegmentCategory._project.nonzero_region_ix
            period_count = np.nonzero(np.logical_and(start_ixs<max_ix,start_ixs>=min_ix))[0].shape[0]
        project_properties = OrderedDict()
        project_properties['Name'] = [self.name,]
        project_properties['ID'] = [self.id,]
        project_properties['Start Time'] = ["%.3f"%self.starttime,]
        project_properties['End Time'] = ["%.3f"%self.endtime,]
        project_properties['Duration'] = ["%.3f"%self.duration,]
        project_properties['Start / End Index'] = [(min_ix,max_ix)]
        project_properties['# Total Samples'] = [self.pointcount,]
        project_properties['# No Pressure Samples'] = [self.zeropressurependata.shape[0],]
        project_properties['# Runs'] = [period_count,]
        #project_properties['Last Pen-Lift Duration'] = ['TODO',]
        if self.l1seg and self.l1seg.locked:
            project_properties['Current Trial'] = [self.l1seg.name,]
        project_properties['Hierarchy Path'] = [u"->".join(self.path[1:]),]
        project_properties['Hierarchy Level'] = [self.level,]
        project_properties['Child Count'] = [len(self.children),]
        return project_properties