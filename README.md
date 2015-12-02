# OpenHandWrite
[TODO: Project overview to be added]

OpenHandWrite consists of GetWrite and MarkWrite.

# GetWrite
GetWrite is the set of software tools and examples used for capturing pen data from within an experiment. 

[TODO: GetWrite overview to be added]

## Required Software and Hardware
[TODO: List of needed software and hardware to be added]

## Test Script
[TODO: Overview to be added]

## Experiment Examples
[TODO: Overview to be added]

## HDF2TXT Tool 
[TODO: Overview to be added]

---

# MarkWrite

MarkWrite is a tool for the inspection and segmentation of digitized writing data 
from pen tablet type devices. MarkWrite is part of the OpenHandWrite Project.

![MarkWrite screenshot](https://github.com/isolver/OpenHandWrite/blob/master/markwrite/MarkWriteApp_sm.png)

# Status
MarkWrite 0.1 was released on May 2nd, 2015. Although there is a large 
'wish list' of unimplemented functionality, the application should be of use
to people wanting to segment digitized pen data into sentences, words, letters,
... 

[Documentation](https://github.com/isolver/OpenHandWrite/blob/master/docs/MarkWrite 0.1 User Guide.pdf) is currently available in PDF format.

# Installation / Running
Currently only Windows 7 / 8 have been tested with the app; 
other environments may work but who knows.

## Windows 7 / 8 Executable

Standalone versions of MarkWrite for Windows 7/8 [32bit](https://github.com/isolver/OpenHandWrite/releases/download/v0.1.0/MarkWrite.0.1.32bit.zip) and [64bit](https://github.com/isolver/OpenHandWrite/releases/download/v0.1.0/MarkWrite.0.1.64bit.zip)
are available. In this case Python does not need to be installed
on the computer being used; it is included in the MarkWrite program folder. 
To use the exe, download one of the .zip archived MarkWrite program folders, 
uncompress it, and then launch MarkWrite.exe in the folder.

## Running from Source
The source code can be downloaded and MarkWrite can be run from a 
Python 2.7 32 or 64 bit environment. 

The following Python packages must be installed for MarkWrite to run:

1. numpy 1.9
2. pyqtgraph 0.9.10
3. PyQt 4.9

There is no need to install a 'markwrite' package, simply start the runapp.py 
script.

Note: Ensure the directory runapp.py is in is included in your 
python path. If the runapp.py script is run from it's folder, then most python 
env's will include the './' folder in the path by default.

# Credits

Initial development was funded by School of Social Sciences, Nottingham Trent University, UK.

# License

GNU General Public License (GPL) Version 3

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
