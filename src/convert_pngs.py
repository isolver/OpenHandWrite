# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 09:16:38 2017

@author: sol
"""
import os
import pyqtgraph
import markwrite
from pyqtgraph import QtCore, QtGui
from markwrite.util import get_resource_folder_path, getIconFilePath

icon_folder = os.path.join(get_resource_folder_path(),'icons')
ifiles = os.listdir(icon_folder)

for i in ifiles:
    newi = i[1:]
    ipath = getIconFilePath(i)
    print ipath
    image = QtGui.QImage()
    image.load(ipath)
    image.save(getIconFilePath(newi))
