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

from __future__ import print_function, division
import math
import psychopy
from psychopy import visual, core
from constants import *
from util import getImageFilePath
import wintabgraphics

def addTriggerImage(win, all_stim, image_file):
    img_path = getImageFilePath(image_file)
    if img_path:
        trig_img_key = image_file[:-4]
        if trig_img_key not in all_stim['triggers']:
            all_stim['triggers'][trig_img_key] = visual.ImageStim(win,
                                    image=img_path,
                                    units='norm',
                                    pos=(0.8, -0.8))
            print("Created TRIG: {} for image file: {}".format(trig_img_key, img_path))
    else:
        print("ERROR: Trigger Image File not found: ", img_path)

def createPsychopyGraphics(display):
    #
    # Initialize Graphics
    #

    display_resolution=display.getPixelResolution()
    psychopy_monitor=display.getPsychopyMonitorName()
    unit_type=display.getCoordinateType()
    screen_index=display.getIndex()

    # Create a psychopy window, full screen resolution, full screen mode.
    myWin=visual.Window(display_resolution,
                        monitor=psychopy_monitor,
                        units=unit_type,
                        color=DEFAULT_SCREEN_COLOR,
                        colorSpace='rgb255',
                        fullscr=True,
                        allowGUI=False,
                        screen=screen_index)

    all_stim = dict()

    all_stim['pen'] = {
                    'pos': wintabgraphics.PenPositionStim(myWin,
                                              PEN_POS_GFX_MIN_OPACITY,
                                              PEN_POS_HOVER_COLOR,
                                              PEN_POS_TOUCHING_COLOR,
                                              PEN_POS_ANGLE_COLOR,
                                              PEN_POS_ANGLE_WIDTH,
                                              PEN_POS_GFX_MIN_SIZE,
                                              PEN_POS_GFX_SIZE_RANGE,
                                              PEN_POS_TILTLINE_SCALAR),
                    'traces': wintabgraphics.PenTracesStim(myWin,
                                             PEN_TRACE_LINE_WIDTH,
                                             PEN_TRACE_LINE_COLOR,
                                             PEN_TRACE_LINE_OPACITY)
                    }

    all_stim['triggers']=dict()
    all_stim['triggers']['naechster'] = visual.ImageStim(myWin,
                                image=getImageFilePath('naechster.bmp'),
                                units='norm',
                                pos=(0.8, -0.8))

    all_stim['practice']=dict()
    prac_text_stim = visual.TextStim(myWin, units='norm', pos=(0, .9),
                        height = DEFAULT_TEXT_STIM_HEIGHT,
                        text="Practice using the tablet pen on this screen.\n"
                               "Tap the 'Continue...' button when done.")
    all_stim['practice']['text'] = prac_text_stim
    all_stim['practice']['naechster'] = all_stim['triggers']['naechster']

    all_stim['trial']=dict()
    all_stim['trial']['INST']=dict()
    all_stim['trial']['INST']['text'] = visual.TextStim(myWin,
                                        units='norm',
                                        pos=(0, 0),
                                        height = DEFAULT_TEXT_STIM_HEIGHT,
                                        text="Default Trial Instruction"
                                             " State Text.")
    all_stim['trial']['INST']['image'] = visual.ImageStim(myWin,
                                image=getImageFilePath('button_cont_large.png'),
                                units='norm',
                                pos=(0.0, 0.0))

    all_stim['trial']['GO']=dict()
    all_stim['trial']['GO']['text'] = visual.TextStim(myWin,
                                        units='norm',
                                        pos=(0, 0),
                                        height = DEFAULT_TEXT_STIM_HEIGHT,
                                        text="Default Trial Go"
                                             " State Text.")
    all_stim['trial']['GO']['image'] = visual.ImageStim(myWin,
                                image=getImageFilePath('button_cont_large.png'),
                                units='norm',
                                pos=(0.0, 0.0))

    all_stim['trial']['STOP']=dict()
    all_stim['trial']['STOP']['text'] = visual.TextStim(myWin,
                                        units='norm',
                                        pos=(0, 0),
                                        height = DEFAULT_TEXT_STIM_HEIGHT,
                                        text="Default Trial Instruction"
                                             " State Text.")
    all_stim['trial']['STOP']['image'] = visual.ImageStim(myWin,
                                image=getImageFilePath('button_cont_large.png'),
                                units='norm',
                                pos=(0.0, 0.0))

    all_stim['exp_end'] = dict()
    all_stim['exp_end']['txt'] = visual.TextStim(myWin,
                                        units='norm',
                                        pos=(0, -0.9),
                                        height = DEFAULT_TEXT_STIM_HEIGHT,
                                        text="Press ESCAPE or 'q' to exit.")

    all_stim['exp_end']['img'] = visual.ImageStim(myWin,
                                image=getImageFilePath('ende.bmp'),
                                units='norm',
                                pos=(0.0, 0.0))


    return myWin, all_stim

