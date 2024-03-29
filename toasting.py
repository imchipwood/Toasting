#!/usr/bin/python3
import wx
from library.ui.ToastingGUI import ToastingGUI
from definitions import GetBaseConfigurationFilePath


if __name__ == "__main__":
	# Create base app
	app = wx.App()

	# Create GUI frame
	view = ToastingGUI(baseConfigurationPath=GetBaseConfigurationFilePath())
	view.Show()
	app.SetTopWindow(view)

	# Begin GUI main loop
	app.MainLoop()
