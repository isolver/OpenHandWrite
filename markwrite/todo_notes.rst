Notes on MarkWrite Feature Requests
====================================

This is a temporary file, and is for my own (Sol's) benefit only,
trying to keep info on functionality agreements made outside github issue tracker.

Autosegment hdf5 file trials
`````````````````````````````

See issue on github for latest agreement on how to implement.

Internal:

- no need to internally merge trial tables with sample table or segment class,
 this only needs to be done at report creation level.

Pen Sample Filtering
``````````````````````

1. markwrite should apply a filter to data when it is loaded. filter can be fixed for now, so it is applied once and that is it.
2. put filter func. in seperate .py file so it can be changed by Guido if desired without need to find a function in a huige source file.
3. keep unfiltered x,y, pressure data as well as the filtered version. So maybe just add extra columns to sample table.
4. filter is to be applied individually to each sequence of pen samples that do not have a gap between any sample times.
5. Perhaps filter func should take in the data for just one sample series at a time, having markwrite iterate over all series, calling func for each.

Velocity / Accelleration
``````````````````````````

1. markwrite should calculate this when it is loaded. alg's can be fixed for now, so it is applied once and that is it.
2. put vel and accell calc func. in separate .py file so it can be changed by Guido if desired without need to find a function in a huge source file.
3. vel / accell is to be applied individually to each sequence of pen samples that do not have a gap between any sample times.
4. Perhaps accell / vell func should take in the data for just one sample series at a time, having markwrite iterate over all series, calling func for each.
5. have project setting to calculate vel. / accell when data is loaded, so it can be turned on / off
6. Add ability to plot accell / velocity traces in time series view.

Creating custom report variables
``````````````````````````````````

1. Update segment.py report to use model of having a dict with column names as keys and ptr to func that will return segment level value for that column.
2. New column can be added by adding new key to dict and providing function ptr.
3. Segment report columns should be accessible via segment object as obj. properties. (maybe override segment __getattr__)
4. segment obj. should cache calculated value so they only need to be updated if segment heirarchy changes.

Accellerator for finding next pen stroke segment
```````````````````````````````````````````````````````

* See emails from guido.
* basic idea is to use velocity / accell data to find key stroke boundaries.
* user can press a key to have markwrite select next pen stroke found by auto detection.
* user can then create segment for this if wanted, or manually tweeak it first.


