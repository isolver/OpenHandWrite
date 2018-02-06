#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.83.02),
    on February 06, 2018, at 10:34
If you publish work using this script please cite the PsychoPy publications:
    Peirce, JW (2007) PsychoPy - Psychophysics software in Python.
        Journal of Neuroscience Methods, 162(1-2), 8-13.
    Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy.
        Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import absolute_import, division
from psychopy import locale_setup, visual, core, data, event, logging, sound, gui
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions
import sys # to get file system encoding

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'iohub wintab demo'  # from the Builder filename that created this script
expInfo = {u'Session Code': u''}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + u'data' + os.sep + expInfo[u'Session Code']

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=False,
    dataFileName=filename)
#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.WARNING)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(size=(1920, 1080), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0.5,0.5,0.5], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='norm')
# store frame rate of monitor if we can measure it successfully
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # couldn't get a reliable measure so guess

# Initialize components for Routine "Init_tablet"
Init_tabletClock = core.Clock()
pen_samples_for_press = 40
display_penpos_during_validation = True
hover_pen_pos_alpha = 0.75
press_pen_pos_alpha = 0.75
hover_pen_pos_color = (0, 0, 1)
press_pen_pos_color = (0, 1, 0)

import wintabgraphics
from wintabgraphics import PenPositionStim, PenTracesStim
from psychopy.iohub.client.wintabtablet import ScreenPositionValidation
from ccutil import *

io = start_iohub(expInfo[u'Session Code'], expName)
tablet = io.devices.tablet

# Check that the tablet device was created without any errors
if tablet.getInterfaceStatus() != "HW_OK":
    print("Error creating Wintab device:", tablet.getInterfaceStatus())
    print("TABLET INIT ERROR:", tablet.getLastInterfaceErrorString())
    io.quit()
    core.quit()
    sys.exit(1)

pen_pos_stim= PenPositionStim(win)
pen_traces_stim= PenTracesStim(win)

pen_pos_stim.autoDraw = False
pen_traces_stim.autoDraw = False
pen_pos_stim.status = NOT_STARTED
pen_traces_stim.status = NOT_STARTED

# Create the iohub datstore condition variables table.
# The following 2 lines of code is a hack, as it does not appear 
# that you can get the order of the column names as found in the
# condition file using any of the Builder generated python code. 
temp_exp_conds, temp_ecnames = data.importConditions('conditions\\trial_conditions.xlsx',returnFieldNames=True)
temptrials = data.TrialHandler(temp_exp_conds,1)
io.createTrialHandlerRecordTable(temptrials, temp_ecnames)
temp_exp_conds =None
temptrials=None

penDotOpacity = 0
penDotPosition = [0,0]
penDotColor = hover_pen_pos_color
penPosInExit = 0

def restPenTraceStim():
    global pen_traces_stim
    pen_traces_stim.clear()
    pen_traces_stim.setAutoDraw(False)
    pen_traces_stim.status = NOT_STARTED

def resetPenPositionGraphic():
    global penPosInExit, penDotPosition, penDotColor, penDotOpacity
    penDotOpacity = 0
    penDotPosition = [0,0]
    penDotColor = hover_pen_pos_color
    penPosInExit = 0


def updatePenPositionGraphic(lsample):
    global penDotPosition, penDotColor, penDotOpacity
    penDotPosition = lsample.getNormPos()
    if lsample.pressure > 0:
        penDotColor = press_pen_pos_color
        penDotOpacity = press_pen_pos_alpha
    else:
        penDotColor = hover_pen_pos_color
        penDotOpacity = hover_pen_pos_alpha


# Initialize components for Routine "validate"
validateClock = core.Clock()


# Initialize components for Routine "instruct"
instructClock = core.Clock()
instrText = visual.TextStim(win=win, ori=0, name='instrText',
    text='Press Any Key To Start Practice Trials.',    font='Arial',
    units='norm', pos=[0, 0], height=.05, wrapWidth=800,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "NoWrite_Audio"
NoWrite_AudioClock = core.Clock()

NO_WRT_BL_5 = visual.ImageStim(win=win, name='NO_WRT_BL_5',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
NO_WRT_TR_5 = visual.ImageStim(win=win, name='NO_WRT_TR_5',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
NO_WRT_TL_5 = visual.ImageStim(win=win, name='NO_WRT_TL_5',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
NO_WRT_BR_5 = visual.ImageStim(win=win, name='NO_WRT_BR_5',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
PenPosPoint_5 = visual.Polygon(win=win, name='PenPosPoint_5',
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=0.9,depth=-5.0, 
interpolate=True)
practice_sound = sound.Sound('A', secs=-1)
practice_sound.setVolume(1)

# Initialize components for Routine "PracticeTrial"
PracticeTrialClock = core.Clock()
white_backgnd_2 = visual.Rect(win=win, name='white_backgnd_2',
    width=[2, 2][0], height=[2, 2][1],
    ori=0, pos=[0, 0],
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1,depth=0.0, 
interpolate=True)
tprac_image = visual.ImageStim(win=win, name='tprac_image',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
trial_end_image_2 = visual.ImageStim(win=win, name='trial_end_image_2',
    image='resources\\next.png', mask=None,
    ori=0, pos=[.8, -0.8], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
penDotStim_2 = visual.Polygon(win=win, name='penDotStim_2',units='norm', 
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=0.9,depth=-3.0, 
interpolate=True)



# Initialize components for Routine "instruct_2"
instruct_2Clock = core.Clock()
instrText_2 = visual.TextStim(win=win, ori=0, name='instrText_2',
    text='Press Any Key To Start Experiment Trials.',    font='Arial',
    units='norm', pos=[0, 0], height=.05, wrapWidth=800,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "Play_AV"
Play_AVClock = core.Clock()

NO_WRT_BL_2 = visual.ImageStim(win=win, name='NO_WRT_BL_2',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
NO_WRT_TR_2 = visual.ImageStim(win=win, name='NO_WRT_TR_2',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
NO_WRT_TL_2 = visual.ImageStim(win=win, name='NO_WRT_TL_2',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
NO_WRT_BR_2 = visual.ImageStim(win=win, name='NO_WRT_BR_2',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
PenPosPoint_2 = visual.Polygon(win=win, name='PenPosPoint_2',
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=0.9,depth=-6.0, 
interpolate=True)
sound_2 = sound.Sound('A', secs=-1)
sound_2.setVolume(1)

# Initialize components for Routine "DisplayCircleCCWImage"
DisplayCircleCCWImageClock = core.Clock()

NO_WRT_BL_6 = visual.ImageStim(win=win, name='NO_WRT_BL_6',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
NO_WRT_TR_6 = visual.ImageStim(win=win, name='NO_WRT_TR_6',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
NO_WRT_TL_6 = visual.ImageStim(win=win, name='NO_WRT_TL_6',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[-.9, .9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
NO_WRT_BR_6 = visual.ImageStim(win=win, name='NO_WRT_BR_6',
    image='resources\\nowriting.jpg', mask=None,
    ori=0, pos=[.9, -.9], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
greendot1_2 = visual.ImageStim(win=win, name='greendot1_2',
    image='resources\\Circle_CCW.png', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-5.0)
PenPosPoint_6 = visual.Polygon(win=win, name='PenPosPoint_6',
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=0.9,depth=-6.0, 
interpolate=True)

# Initialize components for Routine "trial"
trialClock = core.Clock()
white_backgnd = visual.Rect(win=win, name='white_backgnd',
    width=[2, 2][0], height=[2, 2][1],
    ori=0, pos=[0, 0],
    lineWidth=1, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1,depth=0.0, 
interpolate=True)
trial_image = visual.ImageStim(win=win, name='trial_image',units='norm', 
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
trial_end_image = visual.ImageStim(win=win, name='trial_end_image',
    image='resources\\next.png', mask=None,
    ori=0, pos=[.8, -0.8], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
penDotStim = visual.Polygon(win=win, name='penDotStim',units='norm', 
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=0.9,depth=-3.0, 
interpolate=True)



# Initialize components for Routine "thanks"
thanksClock = core.Clock()
thanksText = visual.TextStim(win=win, ori=0, name='thanksText',
    text='This is the end of the experiment.\n\nPress any key to exit.',    font='arial',
    units='norm', pos=[0, 0], height=0.050, wrapWidth=800,
    color=[0.004,-0.498,-0.498], colorSpace='rgb', opacity=1,
    depth=0.0)
PenPointThanks = visual.Polygon(win=win, name='PenPointThanks',
    edges = 90, size=[0.01, 0.01],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=1,depth=-2.0, 
interpolate=True)


# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

#------Prepare to start Routine "Init_tablet"-------
t = 0
Init_tabletClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat

# keep track of which components have finished
Init_tabletComponents = []
for thisComponent in Init_tabletComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "Init_tablet"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = Init_tabletClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in Init_tabletComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "Init_tablet"-------
for thisComponent in Init_tabletComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# the Routine "Init_tablet" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

#------Prepare to start Routine "validate"-------
t = 0
validateClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
# Run the Pen Position Validation Procedure
io.sendMessageEvent(">>> Pen Validation Procedure Started")
val_result = ScreenPositionValidation(win, io,
                                      target_stim = None,
                                      pos_grid = None,
                                      display_pen_pos=display_penpos_during_validation).run()
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
# keep track of which components have finished
validateComponents = []
for thisComponent in validateComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "validate"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = validateClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in validateComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "validate"-------
for thisComponent in validateComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# the Routine "validate" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

#------Prepare to start Routine "instruct"-------
t = 0
instructClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
ready = event.BuilderKeyResponse()  # create an object of type KeyResponse
ready.status = NOT_STARTED
# keep track of which components have finished
instructComponents = []
instructComponents.append(instrText)
instructComponents.append(ready)
for thisComponent in instructComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "instruct"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = instructClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *instrText* updates
    if t >= 0 and instrText.status == NOT_STARTED:
        # keep track of start time/frame for later
        instrText.tStart = t  # underestimates by a little under one frame
        instrText.frameNStart = frameN  # exact frame index
        instrText.setAutoDraw(True)
    
    # *ready* updates
    if t >= 0 and ready.status == NOT_STARTED:
        # keep track of start time/frame for later
        ready.tStart = t  # underestimates by a little under one frame
        ready.frameNStart = frameN  # exact frame index
        ready.status = STARTED
        # keyboard checking is just starting
        event.clearEvents(eventType='keyboard')
    if ready.status == STARTED:
        theseKeys = event.getKeys()
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instructComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "instruct"-------
for thisComponent in instructComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "instruct" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
practice_trials = data.TrialHandler(nReps=1, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('.\\conditions\\trial_conditions.xlsx', selection='0:2'),
    seed=None, name='practice_trials')
thisExp.addLoop(practice_trials)  # add the loop to the experiment
thisPractice_trial = practice_trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb=thisPractice_trial.rgb)
if thisPractice_trial != None:
    for paramName in thisPractice_trial.keys():
        exec(paramName + '= thisPractice_trial.' + paramName)

for thisPractice_trial in practice_trials:
    currentLoop = practice_trials
    # abbreviate parameter names if possible (e.g. rgb = thisPractice_trial.rgb)
    if thisPractice_trial != None:
        for paramName in thisPractice_trial.keys():
            exec(paramName + '= thisPractice_trial.' + paramName)
    
    #------Prepare to start Routine "NoWrite_Audio"-------
    t = 0
    NoWrite_AudioClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    tablet.reporting = True
    tablet.clearEvents()
    
    resetPenPositionGraphic()
    practice_sound.setSound("resources\\"+T_SND, secs=practice_sound.getDuration()+1)
    # keep track of which components have finished
    NoWrite_AudioComponents = []
    NoWrite_AudioComponents.append(NO_WRT_BL_5)
    NoWrite_AudioComponents.append(NO_WRT_TR_5)
    NoWrite_AudioComponents.append(NO_WRT_TL_5)
    NoWrite_AudioComponents.append(NO_WRT_BR_5)
    NoWrite_AudioComponents.append(PenPosPoint_5)
    NoWrite_AudioComponents.append(practice_sound)
    for thisComponent in NoWrite_AudioComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "NoWrite_Audio"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = NoWrite_AudioClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        pen_samples = tablet.getSamples()
        if pen_samples:
            updatePenPositionGraphic(pen_samples[-1])
            
        
        # *NO_WRT_BL_5* updates
        if t >= 0.0 and NO_WRT_BL_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BL_5.tStart = t  # underestimates by a little under one frame
            NO_WRT_BL_5.frameNStart = frameN  # exact frame index
            NO_WRT_BL_5.setAutoDraw(True)
        if NO_WRT_BL_5.status == STARTED and bool(practice_sound.status==FINISHED):
            NO_WRT_BL_5.setAutoDraw(False)
        
        # *NO_WRT_TR_5* updates
        if t >= 0.0 and NO_WRT_TR_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TR_5.tStart = t  # underestimates by a little under one frame
            NO_WRT_TR_5.frameNStart = frameN  # exact frame index
            NO_WRT_TR_5.setAutoDraw(True)
        if NO_WRT_TR_5.status == STARTED and bool(practice_sound.status==FINISHED):
            NO_WRT_TR_5.setAutoDraw(False)
        
        # *NO_WRT_TL_5* updates
        if t >= 0.0 and NO_WRT_TL_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TL_5.tStart = t  # underestimates by a little under one frame
            NO_WRT_TL_5.frameNStart = frameN  # exact frame index
            NO_WRT_TL_5.setAutoDraw(True)
        if NO_WRT_TL_5.status == STARTED and bool(practice_sound.status==FINISHED):
            NO_WRT_TL_5.setAutoDraw(False)
        
        # *NO_WRT_BR_5* updates
        if t >= 0.0 and NO_WRT_BR_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BR_5.tStart = t  # underestimates by a little under one frame
            NO_WRT_BR_5.frameNStart = frameN  # exact frame index
            NO_WRT_BR_5.setAutoDraw(True)
        if NO_WRT_BR_5.status == STARTED and bool(practice_sound.status==FINISHED):
            NO_WRT_BR_5.setAutoDraw(False)
        
        # *PenPosPoint_5* updates
        if t >= 0.0 and PenPosPoint_5.status == NOT_STARTED:
            # keep track of start time/frame for later
            PenPosPoint_5.tStart = t  # underestimates by a little under one frame
            PenPosPoint_5.frameNStart = frameN  # exact frame index
            PenPosPoint_5.setAutoDraw(True)
        if PenPosPoint_5.status == STARTED and bool(practice_sound.status==FINISHED):
            PenPosPoint_5.setAutoDraw(False)
        if PenPosPoint_5.status == STARTED:  # only update if being drawn
            PenPosPoint_5.setFillColor(penDotColor, log=False)
            PenPosPoint_5.setPos(penDotPosition, log=False)
            PenPosPoint_5.setLineColor(penDotColor, log=False)
        # start/stop practice_sound
        if t >= ITI and practice_sound.status == NOT_STARTED:
            # keep track of start time/frame for later
            practice_sound.tStart = t  # underestimates by a little under one frame
            practice_sound.frameNStart = frameN  # exact frame index
            practice_sound.play()  # start the sound (it finishes automatically)
        frameRemains = ITI + practice_sound.getDuration()+1 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if practice_sound.status == STARTED and t >= frameRemains:
            practice_sound.stop()  # stop the sound (if longer than duration)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in NoWrite_AudioComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "NoWrite_Audio"-------
    for thisComponent in NoWrite_AudioComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    practice_sound.stop() #ensure sound has stopped at end of routine
    # the Routine "NoWrite_Audio" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    #------Prepare to start Routine "PracticeTrial"-------
    t = 0
    PracticeTrialClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    tprac_image.setImage("resources\\"+T_IMG)
    restPenTraceStim()
    resetPenPositionGraphic()
    
    
    # keep track of which components have finished
    PracticeTrialComponents = []
    PracticeTrialComponents.append(white_backgnd_2)
    PracticeTrialComponents.append(tprac_image)
    PracticeTrialComponents.append(trial_end_image_2)
    PracticeTrialComponents.append(penDotStim_2)
    for thisComponent in PracticeTrialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "PracticeTrial"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = PracticeTrialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *white_backgnd_2* updates
        if t >= 0.0 and white_backgnd_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            white_backgnd_2.tStart = t  # underestimates by a little under one frame
            white_backgnd_2.frameNStart = frameN  # exact frame index
            white_backgnd_2.setAutoDraw(True)
        
        # *tprac_image* updates
        if t >= 0.0 and tprac_image.status == NOT_STARTED:
            # keep track of start time/frame for later
            tprac_image.tStart = t  # underestimates by a little under one frame
            tprac_image.frameNStart = frameN  # exact frame index
            tprac_image.setAutoDraw(True)
        
        # *trial_end_image_2* updates
        if t >= 0.0 and trial_end_image_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            trial_end_image_2.tStart = t  # underestimates by a little under one frame
            trial_end_image_2.frameNStart = frameN  # exact frame index
            trial_end_image_2.setAutoDraw(True)
        
        # *penDotStim_2* updates
        if t >= 0.0 and penDotStim_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            penDotStim_2.tStart = t  # underestimates by a little under one frame
            penDotStim_2.frameNStart = frameN  # exact frame index
            penDotStim_2.setAutoDraw(True)
        if penDotStim_2.status == STARTED:  # only update if being drawn
            penDotStim_2.setFillColor(penDotColor, log=False)
            penDotStim_2.setPos(penDotPosition, log=False)
            penDotStim_2.setLineColor(penDotColor, log=False)
        
        # *pen_traces_stim* updates
        if t >= 0.0 and pen_traces_stim.status == NOT_STARTED:
            # keep track of start time/frame for later
            pen_traces_stim.tStart = core.getTime()  # underestimates by a little under one frame
            pen_traces_stim.frameNStart = frameN  # exact frame index
            pen_traces_stim.setAutoDraw(True)
        
        
        pen_samples = tablet.getSamples()
        if pen_samples:
            pen_traces_stim.updateFromEvents(pen_samples)
        
            for ps in pen_samples:
                if 'FIRST_ENTER' in ps.status:
                    penPosInExit=0
                
                if ps.pressure > 0 and trial_end_image.contains(ps.getNormPos()):
                    penPosInExit=penPosInExit+1
                else:
                    penPosInExit=max(0,penPosInExit-1)
                
                if penPosInExit>=pen_samples_for_press:
                    pen_traces_stim.tEnd=core.getTime()
                    continueRoutine = False
                    break
        
            updatePenPositionGraphic(pen_samples[-1])
        
        
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in PracticeTrialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "PracticeTrial"-------
    for thisComponent in PracticeTrialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    # >>> iohub Custom Code
    tablet.reporting = False
    
    thisPractice_trial['DV_TRIAL_START']=pen_traces_stim.tStart
    thisPractice_trial['DV_TRIAL_END']=pen_traces_stim.tEnd
    io.addTrialHandlerRecord(thisPractice_trial)
    
    restPenTraceStim()
    
    # <<< iohub Custom Code
    
    
    # the Routine "PracticeTrial" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    thisExp.nextEntry()
    
# completed 1 repeats of 'practice_trials'


#------Prepare to start Routine "instruct_2"-------
t = 0
instruct_2Clock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
ready_2 = event.BuilderKeyResponse()  # create an object of type KeyResponse
ready_2.status = NOT_STARTED
# keep track of which components have finished
instruct_2Components = []
instruct_2Components.append(instrText_2)
instruct_2Components.append(ready_2)
for thisComponent in instruct_2Components:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "instruct_2"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = instruct_2Clock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *instrText_2* updates
    if t >= 0 and instrText_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        instrText_2.tStart = t  # underestimates by a little under one frame
        instrText_2.frameNStart = frameN  # exact frame index
        instrText_2.setAutoDraw(True)
    
    # *ready_2* updates
    if t >= 0 and ready_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        ready_2.tStart = t  # underestimates by a little under one frame
        ready_2.frameNStart = frameN  # exact frame index
        ready_2.status = STARTED
        # keyboard checking is just starting
        event.clearEvents(eventType='keyboard')
    if ready_2.status == STARTED:
        theseKeys = event.getKeys()
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in instruct_2Components:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "instruct_2"-------
for thisComponent in instruct_2Components:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# the Routine "instruct_2" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1.0, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('.\\conditions\\trial_conditions.xlsx', selection='2:6'),
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb=thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial.keys():
        exec(paramName + '= thisTrial.' + paramName)

for thisTrial in trials:
    currentLoop = trials
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial.keys():
            exec(paramName + '= thisTrial.' + paramName)
    
    #------Prepare to start Routine "Play_AV"-------
    t = 0
    Play_AVClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    resetPenPositionGraphic()
    
    tablet.reporting = True
    tablet.clearEvents()
    
    movie_2 = visual.MovieStim3(win=win, name='movie_2',
        filename="resources\\"+T_MOV,
        ori=0, pos=[0, 0], opacity=1,
        depth=-5.0,
        )
    sound_2.setSound("resources\\"+T_SND, secs=sound_2.getDuration()+1)
    # keep track of which components have finished
    Play_AVComponents = []
    Play_AVComponents.append(NO_WRT_BL_2)
    Play_AVComponents.append(NO_WRT_TR_2)
    Play_AVComponents.append(NO_WRT_TL_2)
    Play_AVComponents.append(NO_WRT_BR_2)
    Play_AVComponents.append(movie_2)
    Play_AVComponents.append(PenPosPoint_2)
    Play_AVComponents.append(sound_2)
    for thisComponent in Play_AVComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "Play_AV"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = Play_AVClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        pen_samples = tablet.getSamples()
        if pen_samples:
            updatePenPositionGraphic(pen_samples[-1])
        
        # *NO_WRT_BL_2* updates
        if t >= 0.0 and NO_WRT_BL_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BL_2.tStart = t  # underestimates by a little under one frame
            NO_WRT_BL_2.frameNStart = frameN  # exact frame index
            NO_WRT_BL_2.setAutoDraw(True)
        if NO_WRT_BL_2.status == STARTED and bool(sound_2.status==FINISHED and movie_2.status==FINISHED):
            NO_WRT_BL_2.setAutoDraw(False)
        
        # *NO_WRT_TR_2* updates
        if t >= 0.0 and NO_WRT_TR_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TR_2.tStart = t  # underestimates by a little under one frame
            NO_WRT_TR_2.frameNStart = frameN  # exact frame index
            NO_WRT_TR_2.setAutoDraw(True)
        if NO_WRT_TR_2.status == STARTED and bool(sound_2.status==FINISHED and movie_2.status==FINISHED):
            NO_WRT_TR_2.setAutoDraw(False)
        
        # *NO_WRT_TL_2* updates
        if t >= 0.0 and NO_WRT_TL_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TL_2.tStart = t  # underestimates by a little under one frame
            NO_WRT_TL_2.frameNStart = frameN  # exact frame index
            NO_WRT_TL_2.setAutoDraw(True)
        if NO_WRT_TL_2.status == STARTED and bool(sound_2.status==FINISHED and movie_2.status==FINISHED):
            NO_WRT_TL_2.setAutoDraw(False)
        
        # *NO_WRT_BR_2* updates
        if t >= 0.0 and NO_WRT_BR_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BR_2.tStart = t  # underestimates by a little under one frame
            NO_WRT_BR_2.frameNStart = frameN  # exact frame index
            NO_WRT_BR_2.setAutoDraw(True)
        if NO_WRT_BR_2.status == STARTED and bool(sound_2.status==FINISHED and movie_2.status==FINISHED):
            NO_WRT_BR_2.setAutoDraw(False)
        
        # *movie_2* updates
        if t >= ITI and movie_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            movie_2.tStart = t  # underestimates by a little under one frame
            movie_2.frameNStart = frameN  # exact frame index
            movie_2.setAutoDraw(True)
        
        # *PenPosPoint_2* updates
        if t >= 0.0 and PenPosPoint_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            PenPosPoint_2.tStart = t  # underestimates by a little under one frame
            PenPosPoint_2.frameNStart = frameN  # exact frame index
            PenPosPoint_2.setAutoDraw(True)
        if PenPosPoint_2.status == STARTED and bool(sound_2.status==FINISHED and movie_2.status==FINISHED):
            PenPosPoint_2.setAutoDraw(False)
        if PenPosPoint_2.status == STARTED:  # only update if being drawn
            PenPosPoint_2.setFillColor(penDotColor, log=False)
            PenPosPoint_2.setPos(penDotPosition, log=False)
            PenPosPoint_2.setLineColor(penDotColor, log=False)
        # start/stop sound_2
        if t >= ITI+1.0 and sound_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            sound_2.tStart = t  # underestimates by a little under one frame
            sound_2.frameNStart = frameN  # exact frame index
            sound_2.play()  # start the sound (it finishes automatically)
        frameRemains = ITI+1.0 + sound_2.getDuration()+1 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if sound_2.status == STARTED and t >= frameRemains:
            sound_2.stop()  # stop the sound (if longer than duration)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Play_AVComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "Play_AV"-------
    for thisComponent in Play_AVComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    
    sound_2.stop() #ensure sound has stopped at end of routine
    # the Routine "Play_AV" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    #------Prepare to start Routine "DisplayCircleCCWImage"-------
    t = 0
    DisplayCircleCCWImageClock.reset()  # clock 
    frameN = -1
    routineTimer.add(2.000000)
    # update component parameters for each repeat
    
    # keep track of which components have finished
    DisplayCircleCCWImageComponents = []
    DisplayCircleCCWImageComponents.append(NO_WRT_BL_6)
    DisplayCircleCCWImageComponents.append(NO_WRT_TR_6)
    DisplayCircleCCWImageComponents.append(NO_WRT_TL_6)
    DisplayCircleCCWImageComponents.append(NO_WRT_BR_6)
    DisplayCircleCCWImageComponents.append(greendot1_2)
    DisplayCircleCCWImageComponents.append(PenPosPoint_6)
    for thisComponent in DisplayCircleCCWImageComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "DisplayCircleCCWImage"-------
    continueRoutine = True
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = DisplayCircleCCWImageClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        pen_samples = tablet.getSamples()
        if pen_samples:
            updatePenPositionGraphic(pen_samples[-1])
        
        # *NO_WRT_BL_6* updates
        if t >= 0.0 and NO_WRT_BL_6.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BL_6.tStart = t  # underestimates by a little under one frame
            NO_WRT_BL_6.frameNStart = frameN  # exact frame index
            NO_WRT_BL_6.setAutoDraw(True)
        frameRemains = 0.0 + 2 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if NO_WRT_BL_6.status == STARTED and t >= frameRemains:
            NO_WRT_BL_6.setAutoDraw(False)
        
        # *NO_WRT_TR_6* updates
        if t >= 0.0 and NO_WRT_TR_6.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TR_6.tStart = t  # underestimates by a little under one frame
            NO_WRT_TR_6.frameNStart = frameN  # exact frame index
            NO_WRT_TR_6.setAutoDraw(True)
        frameRemains = 0.0 + 2 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if NO_WRT_TR_6.status == STARTED and t >= frameRemains:
            NO_WRT_TR_6.setAutoDraw(False)
        
        # *NO_WRT_TL_6* updates
        if t >= 0.0 and NO_WRT_TL_6.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_TL_6.tStart = t  # underestimates by a little under one frame
            NO_WRT_TL_6.frameNStart = frameN  # exact frame index
            NO_WRT_TL_6.setAutoDraw(True)
        frameRemains = 0.0 + 2 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if NO_WRT_TL_6.status == STARTED and t >= frameRemains:
            NO_WRT_TL_6.setAutoDraw(False)
        
        # *NO_WRT_BR_6* updates
        if t >= 0.0 and NO_WRT_BR_6.status == NOT_STARTED:
            # keep track of start time/frame for later
            NO_WRT_BR_6.tStart = t  # underestimates by a little under one frame
            NO_WRT_BR_6.frameNStart = frameN  # exact frame index
            NO_WRT_BR_6.setAutoDraw(True)
        frameRemains = 0.0 + 2 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if NO_WRT_BR_6.status == STARTED and t >= frameRemains:
            NO_WRT_BR_6.setAutoDraw(False)
        
        # *greendot1_2* updates
        if t >= 0.0 and greendot1_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            greendot1_2.tStart = t  # underestimates by a little under one frame
            greendot1_2.frameNStart = frameN  # exact frame index
            greendot1_2.setAutoDraw(True)
        frameRemains = 0.0 + 2.0 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if greendot1_2.status == STARTED and t >= frameRemains:
            greendot1_2.setAutoDraw(False)
        
        # *PenPosPoint_6* updates
        if t >= 0.0 and PenPosPoint_6.status == NOT_STARTED:
            # keep track of start time/frame for later
            PenPosPoint_6.tStart = t  # underestimates by a little under one frame
            PenPosPoint_6.frameNStart = frameN  # exact frame index
            PenPosPoint_6.setAutoDraw(True)
        frameRemains = 0.0 + 2 - win.monitorFramePeriod * 0.75  # most of one frame period left
        if PenPosPoint_6.status == STARTED and t >= frameRemains:
            PenPosPoint_6.setAutoDraw(False)
        if PenPosPoint_6.status == STARTED:  # only update if being drawn
            PenPosPoint_6.setFillColor(penDotColor, log=False)
            PenPosPoint_6.setPos(penDotPosition, log=False)
            PenPosPoint_6.setLineColor(penDotColor, log=False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in DisplayCircleCCWImageComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "DisplayCircleCCWImage"-------
    for thisComponent in DisplayCircleCCWImageComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    
    #------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    trial_image.setImage("resources\\"+T_IMG)
    
    restPenTraceStim()
    resetPenPositionGraphic()
    
    # keep track of which components have finished
    trialComponents = []
    trialComponents.append(white_backgnd)
    trialComponents.append(trial_image)
    trialComponents.append(trial_end_image)
    trialComponents.append(penDotStim)
    for thisComponent in trialComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "trial"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = trialClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *white_backgnd* updates
        if t >= 0.0 and white_backgnd.status == NOT_STARTED:
            # keep track of start time/frame for later
            white_backgnd.tStart = t  # underestimates by a little under one frame
            white_backgnd.frameNStart = frameN  # exact frame index
            white_backgnd.setAutoDraw(True)
        
        # *trial_image* updates
        if t >= 0.0 and trial_image.status == NOT_STARTED:
            # keep track of start time/frame for later
            trial_image.tStart = t  # underestimates by a little under one frame
            trial_image.frameNStart = frameN  # exact frame index
            trial_image.setAutoDraw(True)
        
        # *trial_end_image* updates
        if t >= 0.0 and trial_end_image.status == NOT_STARTED:
            # keep track of start time/frame for later
            trial_end_image.tStart = t  # underestimates by a little under one frame
            trial_end_image.frameNStart = frameN  # exact frame index
            trial_end_image.setAutoDraw(True)
        
        # *penDotStim* updates
        if t >= 0.0 and penDotStim.status == NOT_STARTED:
            # keep track of start time/frame for later
            penDotStim.tStart = t  # underestimates by a little under one frame
            penDotStim.frameNStart = frameN  # exact frame index
            penDotStim.setAutoDraw(True)
        if penDotStim.status == STARTED:  # only update if being drawn
            penDotStim.setFillColor(penDotColor, log=False)
            penDotStim.setPos(penDotPosition, log=False)
            penDotStim.setLineColor(penDotColor, log=False)
        # *pen_traces_stim* updates
        if t >= 0.0 and pen_traces_stim.status == NOT_STARTED:
            # keep track of start time/frame for later
            pen_traces_stim.tStart = core.getTime()  # underestimates by a little under one frame
            pen_traces_stim.frameNStart = frameN  # exact frame index
            pen_traces_stim.setAutoDraw(True)
        
        
        pen_samples = tablet.getSamples()
        if pen_samples:
            dsamples = [ps for ps in pen_samples if not trial_end_image.contains(ps.getNormPos())]
            pen_traces_stim.updateFromEvents(dsamples)
        
            for ps in pen_samples:
                if 'FIRST_ENTER' in ps.status:
                    penPosInExit=0
                
                if ps.pressure > 0 and trial_end_image.contains(ps.getNormPos()):
                    penPosInExit=penPosInExit+1
                else:
                    penPosInExit=max(0,penPosInExit-1)
                
                if penPosInExit>=pen_samples_for_press:
                    pen_traces_stim.tEnd=core.getTime()
                    continueRoutine = False
                    break
        
            updatePenPositionGraphic(pen_samples[-1])
        
        
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "trial"-------
    for thisComponent in trialComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    # >>> iohub Custom Code
    tablet.reporting = False
    
    thisTrial['DV_TRIAL_START']=pen_traces_stim.tStart
    thisTrial['DV_TRIAL_END']=pen_traces_stim.tEnd
    io.addTrialHandlerRecord(thisTrial)
    
    restPenTraceStim()
    
    
    # <<< iohub Custom Code
    
    
    # the Routine "trial" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    thisExp.nextEntry()
    
# completed 1.0 repeats of 'trials'


#------Prepare to start Routine "thanks"-------
t = 0
thanksClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
goodbye = event.BuilderKeyResponse()  # create an object of type KeyResponse
goodbye.status = NOT_STARTED
tablet.reporting = True
tablet.clearEvents()
penDotOpacity = 0
# keep track of which components have finished
thanksComponents = []
thanksComponents.append(thanksText)
thanksComponents.append(goodbye)
thanksComponents.append(PenPointThanks)
for thisComponent in thanksComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "thanks"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = thanksClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *thanksText* updates
    if t >= 1.0 and thanksText.status == NOT_STARTED:
        # keep track of start time/frame for later
        thanksText.tStart = t  # underestimates by a little under one frame
        thanksText.frameNStart = frameN  # exact frame index
        thanksText.setAutoDraw(True)
    
    # *goodbye* updates
    if t >= 1.0 and goodbye.status == NOT_STARTED:
        # keep track of start time/frame for later
        goodbye.tStart = t  # underestimates by a little under one frame
        goodbye.frameNStart = frameN  # exact frame index
        goodbye.status = STARTED
        # keyboard checking is just starting
        event.clearEvents(eventType='keyboard')
    if goodbye.status == STARTED:
        theseKeys = event.getKeys()
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            # a response ends the routine
            continueRoutine = False
    
    # *PenPointThanks* updates
    if t >= 0.0 and PenPointThanks.status == NOT_STARTED:
        # keep track of start time/frame for later
        PenPointThanks.tStart = t  # underestimates by a little under one frame
        PenPointThanks.frameNStart = frameN  # exact frame index
        PenPointThanks.setAutoDraw(True)
    if PenPointThanks.status == STARTED:  # only update if being drawn
        PenPointThanks.setFillColor(penDotColor, log=False)
        PenPointThanks.setPos(penDotPosition, log=False)
        PenPointThanks.setLineColor(penDotColor, log=False)
    pen_samples = tablet.getSamples()
    if pen_samples:
        lsample = pen_samples[-1]
        lspos = lsample.getNormPos()
        penDotOpacity = 0.75
        penDotPosition = lspos
        if lsample.pressure > 0:
            penDotColor = [0,1,0]
        else:
            penDotColor = [1,0,0]
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in thanksComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "thanks"-------
for thisComponent in thanksComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
tablet.reporting = False
# the Routine "thanks" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()
io.quit()







win.close()
core.quit()
