#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.83.01), November 17, 2015, at 11:10
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import locale_setup, visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
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
if dlg.OK == False: core.quit()  # user pressed cancel
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
    monitor='testMonitor', color=[0.506,0.506,0.506], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='norm')
# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/round(expInfo['frameRate'])
else:
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Initialize components for Routine "instruct"
instructClock = core.Clock()
instrText = visual.TextStim(win=win, ori=0, name='instrText',
    text='Press Any Key To Start Experiment.',    font='Arial',
    units='norm', pos=[0, 0], height=.05, wrapWidth=800,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=0.0)

# >>> iohub Custom Code
try:
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

    from psychopy.iohub.client.wintabtablet import PenPositionStim, PenTracesStim
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
    
except Exception, e:
    import sys
    print "!! Error starting ioHub: ",e," Exiting..."
    core.quit()
    sys.exit(1)
# <<< iohub Custom Code

# Initialize components for Routine "practice"
practiceClock = core.Clock()
practice_instruct = visual.TextStim(win=win, ori=0, name='practice_instruct',
    text="Press the 'space' key to begin the experiment.",    font='Arial',
    pos=[0, -.9], height=0.05, wrapWidth=None,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=0.0)
use_pen_instruct_txt_2 = visual.TextStim(win=win, ori=0, name='use_pen_instruct_txt_2',
    text='Use this screen to practice using the Tablet Sylus / Pen.',    font='Arial',
    pos=[0, 0.9], height=0.05, wrapWidth=None,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=-2.0)
practice_image = visual.ImageStim(win=win, name='practice_image',
    image='3Lines.png', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)



# Initialize components for Routine "trial"
trialClock = core.Clock()
trial_question_txt = visual.TextStim(win=win, ori=0, name='trial_question_txt',
    text='default text',    font='Arial',
    pos=[0, 0.9], height=0.05, wrapWidth=None,
    color=[-1.000,-1.000,-1.000], colorSpace='rgb', opacity=1,
    depth=0.0)
trial_image = visual.ImageStim(win=win, name='trial_image',units='norm', 
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
trial_end_image = visual.ImageStim(win=win, name='trial_end_image',
    image='but_stop.bmp', mask=None,
    ori=0, pos=[.8, -0.8], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)


penDotStim = visual.Polygon(win=win, name='penDotStim',units='norm', 
    edges = 90, size=[0.02, 0.02],
    ori=0, pos=[0,0],
    lineWidth=1, lineColor=1.0, lineColorSpace='rgb',
    fillColor=1.0, fillColorSpace='rgb',
    opacity=1.0,depth=-4.0, 
interpolate=True)

# Initialize components for Routine "thanks"
thanksClock = core.Clock()
thanksText = visual.TextStim(win=win, ori=0, name='thanksText',
    text='This is the end of the experiment.\n\nThanks!',    font='arial',
    units='pix', pos=[0, 0], height=0.050, wrapWidth=800,
    color=[1, 1, 1], colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

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

#------Prepare to start Routine "practice"-------
t = 0
practiceClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
practice_screen_exit_key = event.BuilderKeyResponse()  # create an object of type KeyResponse
practice_screen_exit_key.status = NOT_STARTED

# >>> iohub Custom Code

pen_traces_stim.setAutoDraw(False)
pen_pos_stim.setAutoDraw(False)
pen_traces_stim.status = NOT_STARTED
pen_pos_stim.status = NOT_STARTED

io.clearEvents()
io.sendMessageEvent("Started Pen Practice Period")
tablet.reporting = True

# <<< iohub Custom Code


# keep track of which components have finished
practiceComponents = []
practiceComponents.append(practice_instruct)
practiceComponents.append(practice_screen_exit_key)
practiceComponents.append(use_pen_instruct_txt_2)
practiceComponents.append(practice_image)
for thisComponent in practiceComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "practice"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = practiceClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *practice_instruct* updates
    if t >= 0 and practice_instruct.status == NOT_STARTED:
        # keep track of start time/frame for later
        practice_instruct.tStart = t  # underestimates by a little under one frame
        practice_instruct.frameNStart = frameN  # exact frame index
        practice_instruct.setAutoDraw(True)
    
    # *practice_screen_exit_key* updates
    if t >= 0.0 and practice_screen_exit_key.status == NOT_STARTED:
        # keep track of start time/frame for later
        practice_screen_exit_key.tStart = t  # underestimates by a little under one frame
        practice_screen_exit_key.frameNStart = frameN  # exact frame index
        practice_screen_exit_key.status = STARTED
        # keyboard checking is just starting
        event.clearEvents(eventType='keyboard')
    if practice_screen_exit_key.status == STARTED:
        theseKeys = event.getKeys(keyList=['space'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            # a response ends the routine
            continueRoutine = False
    
    # *use_pen_instruct_txt_2* updates
    if t >= 0.0 and use_pen_instruct_txt_2.status == NOT_STARTED:
        # keep track of start time/frame for later
        use_pen_instruct_txt_2.tStart = t  # underestimates by a little under one frame
        use_pen_instruct_txt_2.frameNStart = frameN  # exact frame index
        use_pen_instruct_txt_2.setAutoDraw(True)
    
    # *practice_image* updates
    if t >= 0.0 and practice_image.status == NOT_STARTED:
        # keep track of start time/frame for later
        practice_image.tStart = t  # underestimates by a little under one frame
        practice_image.frameNStart = frameN  # exact frame index
        practice_image.setAutoDraw(True)
    
    # >>> iohub Custom Code
    
    # *pen_traces_stim* updates
    if t >= 0.0 and pen_traces_stim.status == NOT_STARTED:
        # keep track of start time/frame for later
        pen_traces_stim.tStart = t  # underestimates by a little under one frame
        pen_traces_stim.frameNStart = frameN  # exact frame index
        pen_traces_stim.setAutoDraw(True)
    
    # *pen_pos_stim* updates
    if t >= 0.0 and pen_pos_stim.status == NOT_STARTED:
        # keep track of start time/frame for later
        pen_pos_stim.tStart = t  # underestimates by a little under one frame
        pen_pos_stim.frameNStart = frameN  # exact frame index
        pen_pos_stim.setAutoDraw(True)
    
    pen_samples = tablet.getSamples()
    if pen_samples:
        pen_traces_stim.updateFromEvents(pen_samples)
        pen_pos_stim.updateFromEvent(pen_samples[-1])
    
    # <<< iohub Custom Code
    
    
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in practiceComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()

#-------Ending Routine "practice"-------
for thisComponent in practiceComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)

# >>> iohub Custom Code
tablet.reporting = False
io.clearEvents()
io.sendMessageEvent("End Pen Practice Period")

pen_pos_stim.clear()
pen_traces_stim.clear()
pen_traces_stim.setAutoDraw(False)
pen_pos_stim.setAutoDraw(False)
pen_traces_stim.status = NOT_STARTED
pen_pos_stim.status = NOT_STARTED

# <<< iohub Custom Code


# the Routine "practice" was not non-slip safe, so reset the non-slip timer
routineTimer.reset()

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1.0, method='random', 
    extraInfo=expInfo, originPath=-1,
    trialList=data.importConditions('conditions\\trial_conditions.xlsx'),
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
    
    #------Prepare to start Routine "trial"-------
    t = 0
    trialClock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    trial_question_txt.setText(T_TEXT)
    trial_image.setImage(T_IMG)
    
    # >>> iohub Custom Code
    pen_traces_stim.clear()
    pen_traces_stim.setAutoDraw(False)
    pen_traces_stim.status = NOT_STARTED
    
    io.clearEvents()
    
    penDotOpacity = 0
    penDotPosition = [0,0]
    penDotColor = [1,0,0]
    
    penPosInExitStimThresh = 10
    penPosInExit = 0
    
    tablet.reporting = True
    # <<< iohub Custom Code
    
    
    key_resp_2 = event.BuilderKeyResponse()  # create an object of type KeyResponse
    key_resp_2.status = NOT_STARTED
    # keep track of which components have finished
    trialComponents = []
    trialComponents.append(trial_question_txt)
    trialComponents.append(trial_image)
    trialComponents.append(trial_end_image)
    trialComponents.append(penDotStim)
    trialComponents.append(key_resp_2)
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
        
        # *trial_question_txt* updates
        if t >= 0 and trial_question_txt.status == NOT_STARTED:
            # keep track of start time/frame for later
            trial_question_txt.tStart = t  # underestimates by a little under one frame
            trial_question_txt.frameNStart = frameN  # exact frame index
            trial_question_txt.setAutoDraw(True)
        
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
        
        # >>> iohub Custom Code
        
        # *pen_traces_stim* updates
        if t >= 0.0 and pen_traces_stim.status == NOT_STARTED:
            # keep track of start time/frame for later
            pen_traces_stim.tStart = t  # underestimates by a little under one frame
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
                if penPosInExit>=penPosInExitStimThresh:
                    continueRoutine = False
                    break
        
            lsample = pen_samples[-1]
            lspos = lsample.getNormPos()
            penDotOpacity = 0.75
            penDotPosition = lspos
            if lsample.pressure > 0:
                penDotColor = [0,1,0]
            else:
                penDotColor = [1,0,0]
        # <<< iohub Custom Code
        
        
        
        # *penDotStim* updates
        if t >= 0.0 and penDotStim.status == NOT_STARTED:
            # keep track of start time/frame for later
            penDotStim.tStart = t  # underestimates by a little under one frame
            penDotStim.frameNStart = frameN  # exact frame index
            penDotStim.setAutoDraw(True)
        if penDotStim.status == STARTED:  # only update if being drawn
            penDotStim.setOpacity(penDotOpacity, log=False)
            penDotStim.setFillColor(penDotColor, log=False)
            penDotStim.setPos(penDotPosition, log=False)
            penDotStim.setLineColor(penDotColor, log=False)
        
        # *key_resp_2* updates
        if t >= 0.0 and key_resp_2.status == NOT_STARTED:
            # keep track of start time/frame for later
            key_resp_2.tStart = t  # underestimates by a little under one frame
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            event.clearEvents(eventType='keyboard')
        if key_resp_2.status == STARTED:
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
    io.clearEvents()
    
    pen_traces_stim.clear()
    pen_traces_stim.setAutoDraw(False)
    pen_traces_stim.status = NOT_STARTED
    
    penDotOpacity = 0
    
    io.addTrialHandlerRecord(thisTrial)
    # <<< iohub Custom Code
    
    
    # the Routine "trial" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    thisExp.nextEntry()
    
# completed 1.0 repeats of 'trials'


#------Prepare to start Routine "thanks"-------
t = 0
thanksClock.reset()  # clock 
frameN = -1
routineTimer.add(2.000000)
# update component parameters for each repeat
# keep track of which components have finished
thanksComponents = []
thanksComponents.append(thanksText)
for thisComponent in thanksComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "thanks"-------
continueRoutine = True
while continueRoutine and routineTimer.getTime() > 0:
    # get current time
    t = thanksClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *thanksText* updates
    if t >= 0.0 and thanksText.status == NOT_STARTED:
        # keep track of start time/frame for later
        thanksText.tStart = t  # underestimates by a little under one frame
        thanksText.frameNStart = frameN  # exact frame index
        thanksText.setAutoDraw(True)
    if thanksText.status == STARTED and t >= (0.0 + (2.0-win.monitorFramePeriod*0.75)): #most of one frame period left
        thanksText.setAutoDraw(False)
    
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

# >>> iohub Custom Code
io.quit()
# <<< iohub Custom Code




win.close()
core.quit()
