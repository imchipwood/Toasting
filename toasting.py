import wx
from library.ui.ToastingGUI import ToastingGUI

if __name__ == "__main__":
	# Create base app
	app = wx.App()

	# Create GUI frame
	view = ToastingGUI(None)
	view.Show()
	app.SetTopWindow(view)

	# Begin GUI main loop
	app.MainLoop()
