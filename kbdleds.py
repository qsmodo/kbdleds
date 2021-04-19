#   trayleds.py, systray application to monitor CapsLock, ScrLock and NumLock
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.

import wx.adv
import pathlib
import subprocess
import re

HOME=str(pathlib.Path.home())
PATH=HOME+'/.local/share/kbdleds/'

#Defines the systray application
class TaskBarIcon(wx.adv.TaskBarIcon):
  def __init__(self,frame):
    self.frame=frame
    self.state=kbdleds()
    wx.adv.TaskBarIcon.__init__(self)
    #Start querying xset repeteadly
    self.OnTimer(wx.EVT_MENU)
    #Set the initial icon based on initial kbd state
    self.OnSetIcon(PATH+''.join(self.state)+".png")

  #Menu which shows up when the tray icon is right-clicked
  def CreatePopupMenu(self):
    menu=wx.Menu()
    quitm=wx.MenuItem(menu,wx.NewId(),'Quit')
    menu.Bind(wx.EVT_MENU,self.OnQuit,id=quitm.GetId())
    menu.Append(quitm)
    return(menu)

  #Set the icon. The hovering dialog is always the same
  def OnSetIcon(self,path):
    icon=wx.Icon(path)
    self.SetIcon(icon,'C: CapsLock\nS: ScrollLock\nN: NumLock')

  #Toggle the icon.
  def OnToggle(self,event):
    use_icon=PATH+''.join(self.state)+".png"
    self.OnSetIcon(use_icon)

  #Defines the time between each kbd state query
  def OnTimer(self,event):
    self.timer=wx.Timer(self)
    self.Bind(wx.EVT_TIMER,self.OnInUseTimer)
    self.timer.Start(500)

  #Triggered by OnTimer, checks if the current kbd state differs from the
  #previous kbd state, in which case it issues a icon toggle event
  def OnInUseTimer(self,event):
    inds=kbdleds()
    if inds!=self.state:
      self.state=inds
      self.OnToggle(None)

  #What to do when Quit option is selected in the menu
  def OnQuit(self,event):
    self.RemoveIcon()
    wx.CallAfter(self.Destroy)
    self.frame.Close()

#Returns the state of keyboard leds using xset
#Regexes are used to extract the on/off for each led
def kbdleds():
  xsetcmd=['xset','q']
  xset=subprocess.run(xsetcmd,stdout=subprocess.PIPE)
  output=xset.stdout.decode('utf-8')
  caps=re.search('Caps Lock: +([a-z]+) +01',output)
  num=re.search('Mouse Keys: +([a-z]+)',output)
  scrlk=re.search('Scroll Lock: +([a-z]+)',output)
  if caps and num and scrlk:
    caps=caps.group(1)
    num=num.group(1)
    scrlk=scrlk.group(1)
    return(str(int(caps=='on')),str(int(scrlk=='on')),str(int(num=='on')))

if __name__=='__main__':
  app=wx.App()
  frame=wx.Frame(None)
  TaskBarIcon(frame)
  app.MainLoop()
