# OpenHandWrite
Link to the [Wiki](https://github.com/isolver/OpenHandWrite/wiki)

OpenHandWrite is a suite of programs designed to provide behavioural scientists with **tools for capturing and analysing pen movement**. These programs provide accurately timed capture of pen movement data from digitising tablets and tabletPCs, and a markup and analysis tool that allows users to manually segment the pen trace into meaningful units (sentences, words, syllables, letters, lines, strokes) and then computes by-segment summary statistics. OpenHandWrite comprises...

[**GetWrite**](https://github.com/isolver/OpenHandWrite/wiki/GetWrite) - a Wintab interface for PsychoPy, and template experiments.
  
[**MarkWrite**](https://github.com/isolver/OpenHandWrite/wiki/MarkWrite-Walkthrough) - a segmentation and analysis GUI.

OpenHandWrite is targeted particularly at researchers **exploring the cognitive processes underlying written production**, but could also be used to study drawing. It differs from existing solutions ([Ductus](http://link.springer.com/article/10.3758%2FBRM.42.1.326), [HandSpy](http://daar.up.pt/index.php/pt/handspy), [Eye and Pen](http://www.eyeandpen.net/?lng=en)) by bringing together the following features:
* Pen sample timing uses a parallel event-handeling technology ([ioHub](http://www.psychopy.org/api/iohub.html)) that avoids quantising issues associated with windows swap and USB polling, therefore giving very accurate sample timing and more or less no sample skipping.

* Integration into an existing flexible and fully-featured experiment development environment ([PsychoPy] (http://www.psychopy.org/)). 

* Capture of zero-pressure pen traces. These occur when the pen hovers above the tablet surface as in the case, for example, between words when producing continuous text.

* An approach to analysis based on identifying behaviourally-meaningful pen trace segments, rather than on locating and counting pen-lifts over a particular threshold duration ("pauses").

* Free and open source.

**Further informations (download, installation instructions, detailed descriptions and documentation, a walkthrough, examples, further tools, hard- and sofware requirements, etc.) can be found in the project's [Wiki](https://github.com/isolver/OpenHandWrite/wiki).**


# Credits & License

This version is being distributed for beta testing and use. It is open source and can be modified and distributed under the terms of the GNU General Public License. We think you'll find it useful, but it is distributed without any warranty and without even the implied warranty of merchantability (whatever that is) or fitness for purpose.

Coding by [Sol Simpson](http://www.isolver-software.com/). Design by Sol, [Guido Nottbusch](http://www.uni-potsdam.de/gsp-deutsch/prof-dr-guido-nottbusch.html) and [Mark Torrance](https://www.ntu.ac.uk/apps/staff_profiles/staff_directory/125084-0/26/Mark_Torrance.aspx). Funding from the School of Social Sciences, Nottingham Trent University, UK and University of Potsdam, Germany.

GNU General Public License (GPL) Version 3

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

