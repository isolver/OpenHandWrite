# -*- coding: utf-8 -*-
from __future__ import print_function
from psychopy.iohub import OrderedDict,launchHubServer
#
### Misc. functions used by the Builder project's custom code.
#

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

def start_iohub(session_code, experiment_name):
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

    save_to = os.path.join(os.path.dirname(__file__),u'data',
                           session_code)
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

    kwargs={'experiment_code':experiment_name,
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

