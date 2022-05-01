#!/usr/bin/python3
import wx
from library.ui.ToastingGUI import ToastingGUI
from definitions import get_base_configuration_file_path


if __name__ == "__main__":
	# Create base app
	app = wx.App()

	# Create GUI frame
	view = ToastingGUI(base_configuration_path=get_base_configuration_file_path())
	view.Show()
	app.SetTopWindow(view)

	# Begin GUI main loop
	app.MainLoop()
