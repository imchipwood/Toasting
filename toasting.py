import os
import wx
from library.ui.ToastingGUI import ToastingGUI
from definitions import CONFIG_DIR

BASE_CONFIG_PATH = os.path.join(CONFIG_DIR, "baseConfig.json")


if __name__ == "__main__":
	# Create base app
	app = wx.App()

	# Create GUI frame
	view = ToastingGUI(
		parent=None,
		baseConfigurationPath=BASE_CONFIG_PATH
	)
	view.Show()
	app.SetTopWindow(view)

	# Begin GUI main loop
	app.MainLoop()
