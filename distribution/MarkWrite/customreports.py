# -*- coding: utf-8 -*-
from markwrite.reports import ReportExporter

class RawSampleDataReportExporter(ReportExporter):
    progress_dialog_title = "Saving the Raw Pen Point Sample Report .."
    formating=dict(time=u'{:.3f}')
    def __init__(self):
        ReportExporter.__init__(self)

    @classmethod
    def columnnames(cls):
        # Return the name of each 'column' of the project.pendata
        # numpy array.
        # Note that the report cls has a 'project' attribute
        # that can be used to access the project in use when
        # generating the report
        r = ['index',]
        r.extend(cls.project.pendata.dtype.names)
        r.extend(('series_id','run_id','stroke_id'))
        return r

    @classmethod
    def datarowcount(cls):
        # Return the number of pen samples that will be saved
        # in the report. Each sample will be a report data row.
        return cls.project.pendata.shape[0]

    @classmethod
    def datarows(cls):
        # Iterate through the pen data array, yielding each pen sample
        # as a list.
        getSeriesForSample = cls.project.getSeriesForSample
        getPressedRunForSample = cls.project.getPressedRunForSample
        getStrokeForSample = cls.project.getStrokeForSample

        for i, pensample in enumerate(cls.project.pendata):
            r = [i,]
            r.extend(pensample.tolist())
            r.extend((getSeriesForSample(i),getPressedRunForSample(i),getStrokeForSample(i)))
            yield r
