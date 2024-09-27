#!/usr/bin/python
#-----------------------------------------------------------------------------
# Name:        selfprotectionExample1.py
#
# Purpose:     This program is a test case of the process protector to show the 
#              user how 2 malwares use the processProtector to protect each other 
#              to avoid the user forse kill any one of them.
#
# Author:      Yuancheng Liu
#
# Version:     v_0.1
# Created:     2023/10/01
# Copyright:   n.a
# License:     n.a
#-----------------------------------------------------------------------------
""" Related program/file: 
    1. processProtector.py
    2. malware2.py
    3. rcd.txt
"""
import os
import wx
import time
import processWatchDog

PERIODIC = 2000
print("Current working directory is : %s" % os.getcwd())
dirpath = os.path.dirname(__file__)
print("Current source code location : %s" % dirpath)

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
class MyFrame(wx.Frame):    
    def __init__(self):
        super().__init__(parent=None, title='self protection example')
        self.lastPeriodicTime = time.time()
        self.SetBackgroundColour(wx.Colour('BLUE'))
        logoImg = os.path.join(dirpath, 'logo.png')
        # Init the process protector
        tgtFile = os.path.join(dirpath, 'selfprotectionExample2.py')
        rcdFile = os.path.join(dirpath, 'selfprotectRcd.txt')
        targetInfo = {
            'path': tgtFile,    # target file path.
            # target file exeuction cmd
            'execution': 'python C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\selfprotectionExample2.py',  
            'backup': 'C:\\Works\\NCL\\Project\\Malware_Repo\\src\\processWatchDog\\recoveZips\\selfprotectionExample2.zip', # target program zip file
            'rcdIdx': 1 # configured id in record file.
        }
        ownIdx = 0
        self.protector = processWatchDog.processWatchdog(targetInfo, rcdFile, 
                                                         idx=ownIdx, interval=3)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.stTxt = wx.StaticText(self, -1, " Self ID: \n Targt ID: \n Target Running:")
        self.stTxt.SetFont(wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.stTxt)

        if os.path.exists(logoImg):
            bmp = wx.Bitmap(logoImg, wx.BITMAP_TYPE_ANY)
            # create image button using BitMapButton constructor
            button = wx.BitmapButton(self, id = wx.ID_ANY, bitmap = bmp,
                            size =(bmp.GetWidth()+10, bmp.GetHeight()+10))
            sizer.Add(button)

        self.SetSizer(sizer)

        self.statusbar = self.CreateStatusBar(1)
        self.statusbar.SetStatusText('Protect Target File: %s' %str(tgtFile))
        self.timer = wx.Timer(self)
        self.updateLock = False
        self.Bind(wx.EVT_TIMER, self.periodic)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.timer.Start(PERIODIC)  # every 3 second
        self.protector.start()
        self.Show()
        

#-----------------------------------------------------------------------------
    def periodic(self, event):
        """ Call back every periodic time."""
        now = time.time()
        print("main frame update at %s" % str(now))
        dataDict = self.protector.getCrtInfo()
        self.stTxt.SetLabel(" Self ID:%s \n Targt ID:%s \n Target Running:%s " % (
            str(dataDict['ownPid']), str(dataDict['tgtPid']), str(dataDict['tgtRun'])))

#-----------------------------------------------------------------------------
    def onClose(self, event):
        self.timer.Stop()
        self.protector.stop()
        self.Destroy()

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
