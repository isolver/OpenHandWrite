# -*- coding: utf-8 -*-
#
# This file is part of the OpenHandWrite project software.
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
#
"""
OpenHandWrite Template Experiment
=================================

An example experiment for capturing data from Pen / Sylus digitizers that
support the Wintab API. Supported input devices include Wacom Intuos4 and
Thinkpad X61 laptops / tablets.

The experiment is written using PsychoPy, with Pen events being collected
by using the psychopy.iohub WintabTablet device. Only Windows 7 / 8 is
supported at this time.

Running
~~~~~~~

The simpliest way to start the experiment template is to double click on the
OpenHandWrite/Run_ExperimentTemplate.bat file.

The experiment template can also be started by openning this file (run.py)
within the Spyder2 IDE bundled in the WinPython folder of OpenHandWrite
and then launching it, or from a WinPython Command Prompt. Type the following
from the command prompt window:

python run.py


Experiment Paridigm
~~~~~~~~~~~~~~~~~~~~~

The TemplateExperiment implements the following runtime fucntionality. When the
ExperimentTemplate/run.py script is started:

1) Display a Session Dialog, allowing participant info entry and
   selection of conditions file.
2) Enter full PsychoPy full screen mode, using the native screen resolution.
3) Instruction / Practice Stage:
    a. Display some instuction graphics and play an audio file.
    b. The current pen position and tilt (if supported) are continuously drawn
       to the screen. Pen traces, created by pressing the pen on the
       digitizer surface, are also drawn.
    c. When the participant is ready to move onto the actual experiment
       trial set, a button in the bottom right hand corner of the screen
       is pressed with the Pen.
4) Experimental Trial Set
    i. After the Practice Stage of the experiment is completed, the participant is
       presented with a series of Experiment Trials:
            * The number of trials run is equal to the number of rows read from the
              Experiment Conditions File (ECF) that was specified in the
              Session Dialog.
            * For more details on the ECF format and definition for this template
              see the Experiment Conditions File Definition section below.
    ii. Each Experiment Trial performs the same sequence of steps. UPPER_CASE
        words refer to IV columns from the ECF.  The Experiment Conditions File
        Definition section has information on supported value types and ranges
        for each IV and DV. A trial runs through the following sequence steps:
            a. Display a blank screen for ITI duration.
            b. STATE 1: Display the trials instruction graphics & audio based on
               INST_VIS and INST_SND. Audio start time with be approx.
               equal to the time the INST_VIS graphics were first displayed.
            c: Exit STATE 1 when INST_TRIG fires, or when the specified audio file
               finishes being played, which ever occurs later.
            d. STATE 2: Display the trials instruction graphics & audio based on
               GO_VIS and GO_SND. Audio start time with be approx.
               equal to the time the GO_VIS graphics were first displayed.
            e: Exit STATE 2 when GO_TRIG fires, or when the specified audio file
               finishes being played, which ever occurs later.
            f. STATE 3: Display the trials instruction graphics & audio based on
               STOP_VIS and STOP_SND. Audio start time with be approx.
               equal to the time the STOP_VIS graphics were first displayed.
            g. Exit STATE 3 when STOP_TRIG fires, or when the specified audio file
               finishes being played, which ever occurs later.
            h. Start the next trial.
        Note that for each of the three trial states, there is a *_SHOWPEN
        variable in the ECF which is used to control the visibility of the pen
        position and traces for that state period. For example, the INST_SHOWPEN
        column controls pen visibility for the first trial state.
5) After all trials have been presented to the participant, an Experiment
   Complete screen is displayed. The experiment is ended by pressing
   the ESCAPE or 'Q' keys.

Experiment Folder Stucture
~~~~~~~~~~~~~~~~~~~~~~~~~~~

ExperimentTemplate : Root Experiment directory
    |
    |- run.py : Main ExperimentTemplate script.
    |           Run this script to start the experiment.
    |
    |- constants.py: Defines constant values and settings used within the
    |                experiment python code.
    |
    |- graphics.py: Contains functions and classes related to creating the
    |               psychopy graphics used in the experiment.
    |
    |- util.py: Misc. utility functions, including starting the ioHub server.
    |
    |- audio.py: A simple .wav file audio player that runs on 64 bit python.
    |
    |- resources
    |   |
    |   |- image : Directory containing any .bmp files used by the experiment
    |   |
    |   |- audio : Directory containing any .wav files used by the experiment
    |
    |- conditions : Directory containing any experiment trial variable files
    |               for use by an experiment session
    |
    |- results : Directory containing iohub .hdf5 files saved for sessions run.
    |            One file per experiment session run.

Experiment Conditions File (ECF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the experiment template is run, an experiment conditions file (ECF) is
specified by the experimenter. The file defines how many trials should be
run in the session, and the value of IVs used within the experiment trial code.

* ECFs must be saved to the ExperimentTemplate/conditions folder of the
  experiment.
* ECFs are saved in Windows Excel 2007 (.xlsx) format. These files can be viewed
  and edited using Excel or the free LibreOffice Calc application.

ECF Structure
``````````````

* First row of an ECF is a header row giving the IV and DV names used by the
  experiment.
* All other rows in the conditions file represent information for each trial
  to be run during the experiment.
* Therefore, if an ECF has 51 rows, 50 trials will be run for sessions using
  that ECF
* The columns in the Experiment Conditions File (ECF) are used to define
  trial level independent and dependant variables (IVs and DVs).
* Each trial uses the same IV and DV names.
* Columns representing IVs specify condition values used in each trial
  of the experiment.
* The DV values in a row of the ECF are used to save runtime information
 that can be used for subsequent event selection and data analysis
 after the experiment is run.

Column Definitions
```````````````````

The following columns are used as trial level IVs within
the Experiment Template:

ROW_INDEX: The non randomized row index for the trial.

DV_TRIAL_ID: The runtime index of the trial within the
             trial set being run for the session.

ITI: The inter trial interval before starting the trial.
     Specified in seconds.msec format.
     A blank screen is displayed during this period.
     Use 0.0 for no ITI.

INST_VIS: The name of the visual stim / graphics to display during the
          first state of the trial sequence.
          If the value ends in ".bmp", it is assumed that the value represents
          an image from the resources\image folder that is to be loaded.
          Otherwise the value is used as the text for a Text Stim that
          will be displayed.
          Use a '.' to indicate that no graphics should be displayed during
          this part of the trial.

INST_VPOS: The PsychoPy screen position to draw the center of any INST_VIS
          stim at. Remember, in PsychoPy [0,0] is screen center.

INST_SND: The name of the .wav audio file ( e.g. 0-0.wav) to play at the
          start of the first state of the trial sequence. The audio file
          must be in the resources\audio folder.
          Use a '.' to indicate that no audio should be played during
          this part of the trial.

INST_TRIG: The trigger information used to determine when to end the first
           state of the trial sequence.
           - Use a '.' to indicate that the trial should immediately
             continue to the next trial state.
           - Use a float to indicate that the trial logic should wait sec.msec
             from the start of the state before continuing.
           - Use a *.bmp name from the resources\image folder to indicate that
             the trial state should continue until the user presses the image
             on the screen with the tablet sylus / digitizing pen.
           - NOTE: If an audio file is specified for the current trial state,
                   then the state will be maintained until the audio file
                   finishes playing, regardless of any trigger that has been
                   defined. Once the audio file completes, any trigger logic
                   will be enabled.

INST_SHOWPEN: Indicates if the Pen Position graphics and / or Pen Trace
              graphics should be displayed during this trial state.
              - Enter a 'P' character if the pen position stim. should be drawn.
              - Enter a 'T' character if the pen trace stim. should be drawn.
              - Enter a 'C' to clear any previous pen trace data from the stim.
              - A value of PT or TP draws both.

GO_VIS:     Same as INST_VIS, applied to the second state of the trial sequence.
GO_VPOS:     Same as INST_VPOS, applied to the second state of the trial sequence.
GO_SND:     Same as INST_SND, applied to the second state of the trial sequence.
GO_TRIG:    Same as INST_TRIG, applied to the second state of the trial sequence.
GO_SHOWPEN: Same as INST_SHOWPEN, applied to the second state of the trial sequence.

STOP_VIS:   Same as INST_VIS, applied to the second state of the trial sequence.
STOP_VPOS:   Same as INST_VPOS, applied to the second state of the trial sequence.
STOP_SND:   Same as INST_SND, applied to the second state of the trial sequence.
STOP_TRIG:  Same as INST_TRIG, applied to the second state of the trial sequence.
STOP_SHOWPEN: Same as INST_SHOWPEN, applied to the second state of the trial sequence.


The following columns are used as trial level DVs within
the Experiment Template:

DV_INST_START: The sec.msec time that the first state of the trial sequence began.

DV_INST_VIS_ONSET: The sec.msec time that any visual stim was shown for the
                   first state of the trial sequence began.

DV_INST_SND_ONSET: The sec.msec time that any audio stim started for the
                   first state of the trial sequence began.

DV_INST_END: The sec.msec time that the first trial state ended.

DV_GO_START: The sec.msec time that the 2nd state of the trial sequence began.

DV_GO_VIS_ONSET: The sec.msec time that any visual stim was shown for the
                   2nd state of the trial sequence began.

DV_GO_SND_ONSET: The sec.msec time that any audio stim started for the
                   2nd state of the trial sequence began.

DV_GO_END: The sec.msec time that the 2nd trial state ended.

DV_STOP_START: The sec.msec time that the 3rd state of the trial sequence began.

DV_STOP_VIS_ONSET: The sec.msec time that any visual stim was shown for the
                   3rd state of the trial sequence began.

DV_STOP_SND_ONSET: The sec.msec time that any audio stim started for the
                   3rd state of the trial sequence began.

DV_STOP_END: The sec.msec time that the 3rd trial state ended.

Results Files
~~~~~~~~~~~~~~

Each time the experiment templates run.py script is started, a new results file
will be saved to the 'results' directory of the experiment. The file name will
be equal to the session code entered by the experimenter at the start of
the session. The file extension is always .hdf5.

Viewing
````````

A result file saved from running the Experiment Template can be openned by the
MarkWrite Pen Data Segmentation & Analysis Program. MarkWrite supports
reading the .hdf5 files directly.

To save a tab delimited text file of the pen position events that were recorded
for each trial of a session, run the hdf2txt.py script found in the
OpenHandWrite\Programs\hdf2txt script.
See the comments at the start of that file for more information.


@author: Sol
"""
from __future__ import print_function

import os, pyglet
pyglet.options['debug_gl'] = False

import time
from util import showSessionInfoDialog, start_iohub, \
                 saveWintabDeviceHardwareInfo, getAudioFilePath,\
                 getImageFilePath, isImageFileCandidate

from graphics import createPsychopyGraphics, addTriggerImage
from audio import PlaySound, PLAYING
from constants import *

from psychopy import core
from psychopy.data import TrialHandler,importConditions
from wintabgraphics import ScreenPositionValidation

def runPracticePeriod(window,
                      io,
                      pen_pos_stim=None,
                      pen_traces_stim=None,
                      audio_file = None,
                      screen_stim = None,
                      timeout= 30.0,
                      exit_keys = (u' ', u'q', u'escape'),
                      exit_stim = None):
    """
    Performs the practice period at the start of an experiment.

    :param window:
    :param io:
    :param pen_pos_stim:
    :param pen_traces_stim:
    :param audio_file:
    :param screen_stim:
    :param timeout:
    :param exit_keys:
    :param exit_stim:
    :return:
    """
    tablet = io.devices.tablet
    keyboard = io.devices.keyboard

    sound = None
    if audio_file:
        if getAudioFilePath(audio_file):
            sound = PlaySound(filename=getAudioFilePath(audio_file))
        else:
            print("WARNING: PracticePeriod: Audio file not found: {}".format(getAudioFilePath(audio_file)))

    if screen_stim:
        for s in screen_stim.values():
            s.draw()

    if sound:
        sound.start()

    practice_start_time = window.flip()

    io.sendMessageEvent(text="PRACTICE_STARTED", sec_time=practice_start_time)

    if sound:
        while sound.starttime is None:
            time.sleep(0.001)
        io.sendMessageEvent(text="PRACTICE_AUDIO_ONSET", sec_time=sound.starttime)

    lps = None
    io.clearEvents()
    # start tablet events
    tablet.reporting = True

    region_pressed = False
    while not region_pressed or (sound and sound.status == PLAYING):
        if exit_keys:
            keys_pressed = [ke.key for ke in keyboard.getPresses()]
            if list(set(exit_keys) & set(keys_pressed)):
                break
        if timeout and core.getTime() - practice_start_time >= timeout:
                break

        if screen_stim:
            for s in screen_stim.values():
                s.draw()

        # Redraw stim based on tablet events
        tab_samples = tablet.getSamples()

        if pen_traces_stim:
            pen_traces_stim.updateFromEvents(tab_samples)
        if tab_samples:
            lps = tab_samples[-1]
            if (not sound or sound.status != PLAYING) and \
                    exit_stim and not region_pressed and \
                    exit_stim.contains(*lps.getNormPos()) and lps.pressure > 0:
                # End practice because pen was pressed on exit button image.
                region_pressed = True
                io.sendMessageEvent(text="REGION_TRIGGER: x:{}, y:{}".format(lps.x, lps.y), sec_time=lps.time)
            if pen_pos_stim and lps:
                pen_pos_stim.updateFromEvent(lps)
        else:
            lps = None

        if pen_traces_stim:
            pen_traces_stim.draw()
        if pen_pos_stim and lps:
            pen_pos_stim.draw()

        flip_time = window.flip()

        if pen_pos_stim and lps:
            io.sendMessageEvent(text="PEN_STIM_CHANGE: x:{}, "
                                     "y:{}, z:{}, pressure:{}, "
                                     "tilt:{}".format(lps.x, lps.y, lps.z,
                                                      lps.pressure, lps.tilt),
                                sec_time=flip_time)

    #  >>> end of practice period <<<<

    # stop tablet events
    tablet.reporting = False

    if sound:
        io.sendMessageEvent(text="PRACTICE_AUDIO_COMPLETE", sec_time=sound.endtime)

    # clear the screen
    flip_time = window.flip()
    io.sendMessageEvent(text="PRACTICE_COMPLETE", sec_time=flip_time)

    if sound:
        sound.closeFile()
        sound = None

    if pen_traces_stim:
        pen_traces_stim.clear()

class StateTrigger(object):
    def __init__(self, state_code, trial_vars):
        self._state_code = state_code
        self._trial_vars = trial_vars
        self.trig_val = None
        if self._state_code:
            self.trig_val = self._trial_vars['%s_TRIG'%(self._state_code)]

    def reset(self):
        pass

    def fired(self, *args):
        return True

    @staticmethod
    def create(state_code, trial_vars, trigger_stim=None):
        trig = StateTrigger(state_code, trial_vars)
        v = trig.trig_val

        if isinstance(v, basestring) and v.lower().endswith('.bmp'):
            # It is a PenButtonPressTrigger
            v = v.lower()[:-4]
            trig = PenButtonPressTrigger(state_code, trial_vars)
            trig.trig_val=trigger_stim[v]
            return trig
        try:
            # test for TimerStateTrigger
            if isinstance(v, basestring) and v.strip()[0].lower() == 'd':
                v = v.strip()[1:].strip()
            trig.trig_val = float(v)
            trig = TimerStateTrigger(state_code, trial_vars)
            return trig
        except:
            pass

        return trig

class TimerStateTrigger(StateTrigger):
    def __init__(self, state_code, trial_vars):
        StateTrigger.__init__(self, state_code, trial_vars)
        self.state_start_time = None
        self.trig_val=float(self.trig_val)

    @property
    def duration(self):
        return self.trig_val

    def reset(self):
        self.state_start_time = self._trial_vars['DV_%s_VIS_ONSET'%(self._state_code)]
        if self.state_start_time <=0:
            self.state_start_time = self._trial_vars['DV_%s_START'%(self._state_code)]
        if self.state_start_time is None:
            self.state_start_time = 0

    def fired(self, *args):
        return core.getTime()-self.state_start_time>=self.duration


class PenButtonPressTrigger(StateTrigger):
    def __init__(self, state_code, trial_vars):
        StateTrigger.__init__(self, state_code, trial_vars)

    def fired(self, *args):
        pen_samples = args[0]
        for lps in pen_samples:
            if self.trig_val.contains(*lps.getNormPos()) and lps.pressure > 0:
                return True
        self.trig_val.draw()
        return False

def terminateExperimentKeyPressed(keyboard):
    global TERMINATE_EXP_REQ
    TERMINATE_EXP_REQ =  keyboard.getPresses(keys=TERMINATE_EXP_KEYS, clear=False)
    return TERMINATE_EXP_REQ

def terminateExperiment(io):
    global TERMINATE_EXP_REQ
    if TERMINATE_EXP_REQ:
        io.sendMessageEvent("User Requested Experiment to Terminate: {}".format(TERMINATE_EXP_REQ))
    if PlaySound._pya:
        PlaySound._pya.terminate()
        PlaySound._pya = None
    io.quit()
    core.quit()

def runTrialState(state_code, trial, myWin, io, all_stim):
    # Init time related DVs for trial to 0
    trial['DV_%s_START'%(state_code)] = 0
    trial['DV_%s_VIS_ONSET'%(state_code)] = 0.0
    trial['DV_%s_SND_ONSET'%(state_code)] = 0
    trial['DV_%s_END'%(state_code)] = 0.0

    state_screen = trial['%s_VIS'%(state_code)]
    if state_screen:
        state_screen=u''+str(state_screen).lower().strip()
        if state_screen == '.':
            state_screen = None

    graphics_pos = trial['%s_VPOS'%(state_code)]
    if graphics_pos:
        if graphics_pos == '.':
            graphics_pos = [0,0]
        if isinstance(graphics_pos, (list, tuple)):
            # reset it to a str for storage in hdf5 file
            trial['%s_VPOS'%(state_code)]=str(graphics_pos)
        else:
            graphics_pos = [0,0]

    state_audio = trial['%s_SND'%(state_code)]
    if state_audio:
        state_audio=u''+str(state_audio).strip()
        if state_audio == '.':
            state_audio = None

    state_end_trig = StateTrigger.create(state_code,trial, all_stim['triggers'])

    show_pen = draw_pen_pos = draw_pen_trace = trial['%s_SHOWPEN'%(state_code)]
    if show_pen:
        draw_pen_pos = show_pen.upper().find('P')>=0
        draw_pen_trace = show_pen.upper().find('T')>=0
        clear_existing_traces =  show_pen.upper().find('C')>=0

    possible_state_stim = all_stim['trial']['%s'%(state_code)]
    actual_state_stim = []

    if state_screen:

        if isImageFileCandidate(state_screen):
            img_stim = possible_state_stim['image']
            img_stim.image = getImageFilePath(state_screen)
            img_stim.pos = graphics_pos
            actual_state_stim.append(img_stim)
        else:
            txt_stim = possible_state_stim['text']
            txt_stim.text = state_screen
            txt_stim.pos = graphics_pos
            actual_state_stim.append(txt_stim)

    if state_audio:
        if state_audio.lower().endswith('.wav'):
            possible_state_stim['sound'].setFile(getAudioFilePath(state_audio))
        else:
            # TODO: Write warning to log file that .wav audio is only supported
            state_audio = None

    if clear_existing_traces:
        all_stim['pen']['traces'].clear()

    # Display any state graphics and play any associated audio file
    if actual_state_stim:
        for stim in actual_state_stim:
            stim.draw()

    if state_audio:
        possible_state_stim['sound'].start()

    # If state has a visual stim, use it's flip time to equal the states
    # start time.
    if actual_state_stim:
        if draw_pen_trace:
            all_stim['pen']['traces'].draw()
        trial['DV_%s_START'%(state_code)] = trial['DV_%s_VIS_ONSET'%(state_code)] = myWin.flip()

    if state_audio:
        while not possible_state_stim['sound'].starttime:
            time.sleep(0.001)
        trial['DV_%s_SND_ONSET'%(state_code)] = possible_state_stim['sound'].starttime
        if trial['DV_%s_START'%(state_code)] == 0:
            # If state has an audio stim, but did not have a visual stim,
            # use the audio stim onset time to equal the states start time.
            trial['DV_%s_START'%(state_code)] = trial['DV_%s_SND_ONSET'%(state_code)]

    # If state had no audio and no visual stim, then use
    # current time as the states start time.
    if trial['DV_%s_START'%(state_code)] == 0:
        trial['DV_%s_START'%(state_code)] = core.getTime()

    io.clearEvents()

    state_end_trig.reset()

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    # Maintain current state for [state_code]_DUR seconds, or until
    # audio_stim has completed playing, whichever comes last.
    sample_evts=[]
    while (state_audio and possible_state_stim['sound'].status == PLAYING) or \
            state_end_trig.fired(sample_evts) is False:

        # Redraw display and flip
        for stim in actual_state_stim:
            stim.draw()

        if draw_pen_pos or draw_pen_trace:
            sample_evts = tablet.getSamples()

            if draw_pen_trace:
                # Redraw stim based on tablet events
                all_stim['pen']['traces'].updateFromEvents(sample_evts)
                all_stim['pen']['traces'].draw()

            if draw_pen_pos and sample_evts:
                last_evt = sample_evts[-1]
                all_stim['pen']['pos'].updateFromEvent(last_evt)
                all_stim['pen']['pos'].draw()

        flip_time=myWin.flip()

        if terminateExperimentKeyPressed(keyboard):
            if state_audio:
                possible_state_stim['sound'].closeFile()
            return False

    if state_audio:
        possible_state_stim['sound'].closeFile()

    trial['DV_%s_END'%(state_code)] = core.getTime()

def doValidation(myWin, io, display_penpos = True):
    # Run the Pen Position Validation Procedure
    io.sendMessageEvent(">>> Pen Validation Procedure Started")
    val_result = ScreenPositionValidation(myWin, io,
                                          target_stim = None,
                                          pos_grid = None,
                                          display_pen_pos=display_penpos).run()
    if val_result is None:
        # This means that validation was terminated by user
        # before completing

        io.sendMessageEvent("Validation Procedure for "
                             "Wintab Device Aborted.")
    io.sendMessageEvent(">>> Pen Validation Procedure Complete")


    if val_result:
        # Save out the validation results to the hdf5 file as messages
        # in case we want to access the data later
        #import pprint
        #pprint.pprint(val_result)
        io.sendMessageEvent(">>> Pen Validation Results")
        for key, val in val_result.items():
            if key is not 'target_data':
                # do not send msg for the dict of arrays of samples
                io.sendMessageEvent("{} : {}".format(key,val))
        io.sendMessageEvent("<<< Pen Validation Results End")

if __name__ == "__main__":
    global TERMINATE_EXP_REQ

    session_info = showSessionInfoDialog()
    if session_info is None:
        # User cancelled session info dialog
        import sys
        sys.exit()

    io = start_iohub(session_info)

    display = io.devices.display
    keyboard = io.devices.keyboard
    mouse = io.devices.mouse
    tablet = io.devices.tablet

    # Check that the tablet device was created without any errors
    if tablet.getInterfaceStatus() != "HW_OK":
        print("Error creating Wintab device:", tablet.getInterfaceStatus())
        print("TABLET INIT ERROR:", tablet.getLastInterfaceErrorString())

    else:
        # Save the wintab device hardware info to the hdf5 file
        # as a set of experiment messages
        saveWintabDeviceHardwareInfo(io)

        # Inform the ioDataStore that the experiment is using a
        # TrialHandler. The ioDataStore will create a table
        # which can be used to record the actual trial variable values (DV or IV)
        # in the order run / collected.
        #
        exp_conditions, ecnames = importConditions(os.path.join(u'conditions',
                                            session_info['Conditions File']),
                                        returnFieldNames=True)
        trials = TrialHandler(exp_conditions,1)
        io.createTrialHandlerRecordTable(trials, ecnames)

        # hide the OS system mouse when on experiment window
        mouse.setPosition((0,0))
        mouse.setSystemCursorVisibility(False)

        # Create the PsychoPy Window and Graphics stim used during the test....
        myWin, all_stim = createPsychopyGraphics(display)

        # Create list of trigger stim images
        for ecrow in exp_conditions:
            for c in ['INST_TRIG','GO_TRIG','STOP_TRIG']:
                trig_val = ecrow[c]
                if trig_val and isinstance(trig_val,basestring) and \
                                trig_val.lower().strip().endswith('.bmp'):
                    addTriggerImage(myWin,all_stim,trig_val.lower().strip())


        for trial_state_stim in all_stim['trial'].values():
            trial_state_stim['sound'] = PlaySound()

        # --> EXPERIMENT START

        # Run the Pen Position Validation Procedure
        doValidation(myWin, io, display_penpos=True)

        # This could really be implemented as a 'trial state',
        # which would reduce a lot of duplicate code that is in
        # runPracticePeriod() and runTrialState()
        runPracticePeriod(myWin,
                      io,
                      screen_stim = all_stim['practice'],
                      pen_pos_stim=all_stim['pen']['pos'],
                      pen_traces_stim=all_stim['pen']['traces'],
                      audio_file = None,
                      exit_stim = all_stim['triggers']['naechster'],
                      timeout= 60.0,
                      exit_keys = (u' ', u'q', u'escape'),
                    )


        if terminateExperimentKeyPressed(keyboard):
            terminateExperiment(io)

        # Ensure tablet device is not reporting events
        tablet.reporting = False

        # Clear all events from the global and device level event buffers.
        io.clearEvents()
        # Run a number of tablet recording /trials/
        #
        for t, trial in enumerate(trials):
            # --> TRIAL START
            trial['DV_TRIAL_ID']=t+1


            # Display cleared screen for ITI seconds. If ITI <= 0,
            # no clear screen ITI is done.
            #
            requested_iti_duration = trial['ITI']-myWin.monitorFramePeriod
            iti_start_time = core.getTime()
            while core.getTime()-iti_start_time < requested_iti_duration:
                myWin.flip()
                if terminateExperimentKeyPressed(keyboard):
                    terminateExperiment(io)

            tablet.reporting = True

            runTrialState('INST', trial, myWin, io, all_stim)
            if TERMINATE_EXP_REQ:
                terminateExperiment(io)

            runTrialState('GO', trial, myWin, io, all_stim)
            if TERMINATE_EXP_REQ:
                terminateExperiment(io)

            runTrialState('STOP', trial, myWin, io, all_stim)
            if TERMINATE_EXP_REQ:
                terminateExperiment(io)

            tablet.reporting = False

            io.addTrialHandlerRecord(trial)

            io.clearEvents()
            # <-- TRIAL END
        # <-- EXPERIMENT END

        [end_stim.draw() for end_stim in all_stim['exp_end'].values()]
        exp_end_time = myWin.flip()

        while core.getTime() - exp_end_time < 60.0:
            keys_pressed = [ke.key for ke in keyboard.getPresses()]
            if list(set(['escape','q']) & set(keys_pressed)):
                break
            io.wait(0.25)

        terminateExperiment(io)
        ### End of experiment logic