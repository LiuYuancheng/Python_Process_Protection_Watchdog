#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        selfprotectionWatchdog.py
#
# Purpose:     This program is the process protection watch dog to protect the
#              execution of <selfprotectionExample1.py>.
#
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/11/30
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License
#-----------------------------------------------------------------------------
""" Related program / file : 
    1. processWatchDog.py
    2. selfprotectionExample.py
    3. selfprotectRcd.txt
    4. recoverZips/selfprotectionWatchdog.zip
"""

import os
import processWatchDog

print("Current working directory is : %s" % os.getcwd())
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)

tgtFile = os.path.join(dirpath, 'selfprotectionExample.py')
rcdFile = os.path.join(dirpath, 'selfprotectRcd.txt')
targetInfo = {
    'path': tgtFile,    # target file path.
    # target file exeuction cmd
    'execution': 'python C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\selfprotectionExample.py',
    # target program zip file
    'backup': 'C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\recoverZips\\selfprotectionExample.zip',
    'rcdIdx': 0  # configured id in record file.
}
ownIdx = 1
protector = processWatchDog.processWatchdog(targetInfo, rcdFile, idx=ownIdx, interval=1)
protector.start()
