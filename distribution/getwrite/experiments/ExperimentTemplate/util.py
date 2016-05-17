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
from __future__ import print_function

from collections import OrderedDict

from psychopy import gui
from psychopy.iohub.client import launchHubServer
from constants import *

#
### Misc. utility functions used by the python experiment template.
#

def getImageFilePath(file_name):
    '''
    Returns the full, absolute, path to the image named file_name. file_name
    must be an image file located in the resources\image folder of the project.
    If the file can not be found, None is returned.

    :param file_name: image file name
    :return: full path to image file in project, or None if file not found.
    '''
    pth = os.path.join(IMAGE_FOLDER,file_name)
    if os.path.exists(pth):
        return pth
    return None

def getAudioFilePath(file_name):
    '''
    Returns the full, absolute, path to the audio file named file_name.
    file_name must be an audio file located in the resources\audio
    folder of the project. If the file can not be found, None is returned.

    :param file_name: audio file name
    :return: full path to audio file in project, or None if file not found.
    '''
    pth = os.path.join(AUDIO_FOLDER,file_name)
    if os.path.exists(pth):
        return pth
    return None

def getAvailableConditionsFileNames():
    '''
    Return a list of all .xlsx experiment condition file names that are in the
    projects conditions subfolder.
    :return: list of condition file name str
    '''
    if os.path.exists(CONDITIONS_FOLDER):
        import glob
        cvfile_paths = glob.glob(CONDITIONS_FOLDER+os.path.sep+'*.xlsx')
        return [ os.path.split(fpath)[1] for fpath in glob.glob(CONDITIONS_FOLDER+os.path.sep+'*.xlsx')]
    return []

def isImageFileCandidate(file_name):
    '''
    Returns True if the file_name str should be considered an image file name
    for use by an image stim graphic in the experiment. Otherwise returns False.
    :param file_name: candidate image name string
    :return: boolean
    '''
    try:
        fname, fext = file_name.rsplit('.')
        if fext in ACCEPTED_IMAGE_FORMATS:
            return True
        return False
    except:
        return False

def showSessionInfoDialog():
    '''
    Display a dialog to collect session or participant level information
    at the start of an experiment.

    If the dialog OK button is pressed, a dictionary with the values entered
    for each dialog input is returned. If thew dialogs Cancel button is pressed,
    None is returned.
    :return: dict of session info, or None if dialog was cancelled
    '''
    info = OrderedDict()
    info['Session Code'] = DEFAULT_SESSION_CODE
    info['Conditions File'] = getAvailableConditionsFileNames()
#    info['ExpName'] =EXP_NAME
#    info['ExpVersion'] = EXP_VERSION
    infoDlg = gui.DlgFromDict(dictionary=info,
                              title='{} (v{})'.format(EXP_NAME, EXP_VERSION),
                              order = info.keys(),
                              )
                              # fixed=['ExpName','ExpVersion'])
    if infoDlg.OK:
        return info
    return None

def start_iohub(sess_info):
    '''
    Starts the iohub server process, using data from the dict returned by
    showSessionInfoDialog() to create the hdf5 file name. If the file
    already exists, the existing file is renamed so that it is not
    overwritten by the current sessions data.

    iohub device configuration information is read from an
    'iohub_config.yaml' file which must be in the same folder as this file.

    The created ioHubConnection object is returned after the iohub
    server has started and is ready for interaction with the experiment
    runtime.

    :param sess_info: dict returned from showSessionInfoDialog()
    :return:  ioHubConnection object
    '''
    import os, shutil

    save_to = os.path.join(os.path.dirname(__file__),u'results',
                           sess_info['Session Code'])
    save_to = os.path.normpath(save_to)
    if not save_to.endswith('.hdf5'):
        save_to = save_to+u'.hdf5'

    fdir, sess_code = os.path.split(save_to)
    if not os.path.exists(fdir):
        os.mkdir(fdir)

    #TODO: Ask if file should be overwritten, or new session code entered.
    si = 1
    save_dest = save_to
    while os.path.exists(save_dest):
        sname, sext = sess_code.rsplit(u'.',1)
        save_dest = os.path.join(fdir, u"{}_{}.{}".format(sname,si,sext))
        si+=1

    if save_dest is not save_to:
        shutil.move(save_to,save_dest)

    sess_code=sess_code[0:min(len(sess_code),24)]
    if sess_code.endswith(u'.hdf5'):
        sess_code = sess_code[:-5]
    if save_to.endswith(u'.hdf5'):
        save_to = save_to[:-5]

    kwargs={'experiment_code':EXP_NAME,
            'session_code':sess_code,
            'datastore_name':save_to,
            'iohub_config_name': 'iohub_config.yaml'
    }
    return launchHubServer(**kwargs)

def saveWintabDeviceHardwareInfo(io):
    '''
    Save all available wintab device hardware information to the sessions .hdf5
    file as a series of experiment message events. This function is called at
    the start of the experiment, after the start_iohub() function has returned
    the created iohub connection object.

    The following areas of information are saved:

    * wintab device hardware model information
    * the availability, data range, etc,  for each axis of the wintab device
    * wintab context values read from the C CONTEXT struct at device init

    :param io: ioHubConnection instance
    :return: None
    '''
    wtdev = io.devices.tablet

    io.sendMessageEvent(text="START WINTAB HW MODEL INFO")
    for k, v in wtdev.model.items():
        io.sendMessageEvent(text="{}: {}".format(k,v))
    io.sendMessageEvent(text="STOP WINTAB HW MODEL INFO")

    io.sendMessageEvent(text="START WINTAB AXIS INFO")
    for axname, axinfo in wtdev.axis.items():
        io.sendMessageEvent(text="{} Axis:".format(axname))
        for k, v in axinfo.items():
            io.sendMessageEvent(text="{}: {}".format(k,v))
    io.sendMessageEvent(text="END WINTAB AXIS INFO")

    io.sendMessageEvent(text="START WINTAB CONTEXT INFO")
    for k, v in wtdev.context.items():
        io.sendMessageEvent(text="{}: {}".format(k,v))
    io.sendMessageEvent(text="END WINTAB CONTEXT INFO")

