#!/usr/bin/python3
import wx
from library.ui.ToastingGUI import ToastingGUI
from definitions import getBaseConfigurationFilePath


if __name__ == "__main__":
	# Create base app
	app = wx.App()

	# Create GUI frame
	view = ToastingGUI(
		parent=None,
		baseConfigurationPath=getBaseConfigurationFilePath()
	)
	view.Show()
	app.SetTopWindow(view)

	# Begin GUI main loop
	app.MainLoop()
