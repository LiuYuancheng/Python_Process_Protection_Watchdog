#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        processWatchdog.py
#
# Purpose:     This module is used to protect a program's execution to avoid the 
#              user to stop it via close UI/terminal or kill its process. It will 
#              create an independent twin process to form a dead loop protection 
#              algorithm to monitor each other's execution state. 
#
# Author:      Yuancheng Liu
#
# Version:     v_1.0.1
# Created:     2023/09/29
# Copyright:   Copyright (c) 2023 LiuYuancheng
# License:     MIT License  
#-----------------------------------------------------------------------------
""" Protection Algorithm Design : 
    Assume we have 2 python programs A and B both hook with the watchdog. A's 
    watchdog thread will keep checking the program running process P(B)'s state: 
    - If P(B) not exist or killed by user P(A) will execute the program again 
        and update its new P(B) record. 
    - If Program B's code is deleted by user, P(A) will recover program B from its
        backup zip file.
    For P(B), the function is same, so if the check frequency reaches to n times/ sec
    unless the user kill P(A) and P(B) exactly at the same time, otherwise the protected 
    program will keep running.
"""

import os
import time
import psutil
import subprocess
import zipfile
import threading

DEFAULT_WAIT = 1 # default wait time to start the watchdog thread.

# Define the target program's info dict()'s key
TGT_PATH_KEY = 'path'
TGT_EXE_KEY = 'execution'
TGT_BACK_KEY = 'backup'
TGT_RIDX_KEY = 'rcdIdx'

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class processWatchdog(threading.Thread):
    """ Main watchdog thread program."""
    
    def __init__(self, targetInfo, rcdPath, idx=0, interval=5) -> None:
        """ Init example: protector = processWatchdog(<targetInfo dict>, <record file path>,
                                                idx=<0 or 1>, checkInterval)
            Args:
                targetInfo (dict): watchdog target information dictionary.
                    example :
                        targetInfo = {
                            'path': 'C:\\User\\test\test.py',   # target file path.
                            # target file exeuction cmd, it need to be a raw string. if you use the 
                            # python <os.path.join> to pass in the file path, the cmd will through execution error.
                            'execution': 'python3 C:\\User\\test\test.py',  
                            'backup': 'C:\\User\\test\test.zip',    # target program zip file
                            'rcdIdx': 0                             # configured id in record file.
                        }
                rcdPath (str): process ID record file path.
                idx (int, optional): self id idx in the record file. Defaults to 0.
                interval (int, optional): Interval to check the protect process ID (sec). 
                            Defaults to 5 sec.
        """
        threading.Thread.__init__(self)
        self.tgtInfo = targetInfo   # target information dict()
        self.tgtPid = -1            # target process ID.
        self.ownPid = os.getpid()   # self process ID.
        self.ownPIdx = idx          # self process ID idx in the record file.
        self.rcdFile = rcdPath
        self.checkInterval = interval
        self.termate = False
        print("Watchdog init finished.")

#-----------------------------------------------------------------------------
    def run(self):
        """ main target check loop, will be execute when start() function is called."""
        # delay x second to want parent program finish init.
        time.sleep(DEFAULT_WAIT)
        print("Start to run the process watchdog.")
        while not self.termate:
            self.checkProtectTarget()
            time.sleep(self.checkInterval)
        print("Process watchdog stop.")

#-----------------------------------------------------------------------------
    def checkProtectTarget(self, autoRestart=True):
        """ Load the protected program's process ID from record file, then check
            whether the program is running.
            Args:
                autoRestart (bool, optional): auto restart the target program if it
                is not running. Defaults to True.
            Returns:
                bool: whether the target program is running.
        """
        if os.path.exists(self.rcdFile):
            try:
                with open(self.rcdFile, 'r') as fh:
                    pids = str(fh.readline()).strip()
                    idlist = pids.split(';')
                    idx = self.tgtInfo[TGT_RIDX_KEY]
                    self.tgtPid = int(idlist[idx])
                if psutil.pid_exists(self.tgtPid):
                    print("checkProtectTarget(): Protect target running.")
                    return True
            except Exception as err:
                print("Exception to check the target, error : %s" % str(err))
                print("Watchdog expects the target is not running.")
    
        if autoRestart:
            print("Auto resetart the target program...")
            if not os.path.exists(self.tgtInfo[TGT_PATH_KEY]):
                print("Redeploy program from backup")
                self.redeployTgtProgram()
            self.restartTgtProgram()
            return True
        else:
            print("Target program is killed")
            return False

#-----------------------------------------------------------------------------
    def getCrtInfo(self):
        """ Get the current process watchdog's information."""
        infoDict = {
            'ownPid':   self.ownPid, 
            'ownPidx' : self.ownPIdx,
            'tgtFile':  self.tgtInfo[TGT_PATH_KEY],
            'tgtPid':   self.tgtPid,
            'tgtPIdx':  self.tgtInfo[TGT_RIDX_KEY],
            'tgtRun':   psutil.pid_exists(self.tgtPid),
        }
        return infoDict

#-----------------------------------------------------------------------------
    def redeployTgtProgram(self):
        """ Redeploy the protect program from the backup zip file if it is deleted
            by the user or anti-malware.
        """
        if os.path.exists(self.tgtInfo[TGT_PATH_KEY]): return True
        backupzip = self.tgtInfo[TGT_BACK_KEY]
        if backupzip and os.path.exists(backupzip):
            tgtDir = os.path.dirname(self.tgtInfo[TGT_PATH_KEY])
            if not os.path.exists(tgtDir): os.mkdir(tgtDir)
            with zipfile.ZipFile(backupzip, 'r') as zipobj:
                zipobj.extractall(tgtDir)
            print("redeployTgtProgram() : success recorver the file.")
        else:
            print("Target backup file is not exist: %s" %str(backupzip))

#-----------------------------------------------------------------------------
    def restartTgtProgram(self):
        """ restart the protect target program if it is not running."""
        filePath = self.tgtInfo[TGT_PATH_KEY]
        print("Start program: %s" %str(filePath))
        if os.path.exists(filePath):
            cmd = self.tgtInfo[TGT_EXE_KEY]
            print(cmd)
            tgtProcess = subprocess.Popen(cmd, start_new_session=True)
            self.tgtPid = tgtProcess.pid
            # record the process ID.
            try:
                with open(self.rcdFile, 'w') as fh:
                    processInfo = ';'.join((str(self.ownPid), str(self.tgtPid))) if self.ownPIdx==0 else ';'.join((str(self.tgtPid), str(self.ownPid)))
                    fh.write(processInfo)
            except Exception as err:
                print("Record process ID error: %s" %str(err))
        return True if psutil.pid_exists(self.tgtPid) else False

    #-----------------------------------------------------------------------------
    def stop(self):
        self.termate = True

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
def main():
    print("Current working directory is : %s" % os.getcwd())
    dirpath = os.path.dirname(__file__)
    print("Current source code location : %s" % dirpath)
    tgtFile = os.path.join(dirpath, 'selfprotectionExample1.py')
    rcdFile = os.path.join(dirpath, 'selfprotectRcd.txt')
    targetInfo = {
        'path': tgtFile,    # target file path.
        # target file exeuction cmd
        'execution': 'python C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\selfprotectionExample1.py',
        # target program zip file
        'backup': 'C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\recoverZips\\selfprotectionExample1.zip',
        'rcdIdx': 0  # configured id in record file.
    }
    ownIdx = 1
    protector = processWatchdog(targetInfo, rcdFile, idx=ownIdx)
    protector.start()

#-----------------------------------------------------------------------------
if __name__ == "__main__":
    main()