import wx


def info_message(parent, message, caption=None):
	"""
	Display an info message to the user
	@param parent: parent frame
	@type parent: wx.Frame
	@param message: message to display
	@type message: str
	@param caption: Caption for dialog (optional)
	@type caption: str
	"""
	dialog = wx.MessageDialog(
		parent=parent,
		message=message,
		caption=caption if caption else "Info",
		style=wx.OK | wx.ICON_INFORMATION
	)
	dialog.ShowModal()
	dialog.Destroy()


def yes_no_message(parent, message, caption=None):
	"""
	Prompt user to answer a yes/no question
	@param parent: parent frame
	@type parent: wx.Frame
	@param message: message to display
	@type message: str
	@param caption: Caption for dialog (optional)
	@type caption: str
	@return: Whether or not user said "yes"
	@rtype: bool
	"""
	dialog = wx.MessageDialog(
		parent=parent,
		message=message,
		caption=caption if caption else "Toasting needs your attention!",
		style=wx.YES_NO | wx.ICON_INFORMATION
	)
	result = dialog.ShowModal()
	dialog.Destroy()
	return result == wx.ID_YES


def error_message(parent, message, caption=None):
	"""
	Display an error message to the user
	@param parent: parent frame
	@type parent: wx.Frame
	@param message: message to display
	@type message: str
	@param caption: Caption for dialog (optional)
	@type caption: str
	"""
	dialog = wx.MessageDialog(
		parent=parent,
		message=message,
		caption=caption if caption else "Error!",
		style=wx.OK | wx.ICON_ERROR
	)
	dialog.ShowModal()
	dialog.Destroy()


def warning_message(parent, message, caption=None):
	"""
	Display a warning message to the user
	@param parent: parent frame
	@type parent: wx.Frame
	@param message: message to display
	@type message: str
	@param caption: Caption for dialog (optional)
	@type caption: str
	"""
	dialog = wx.MessageDialog(
		parent=parent,
		message=message,
		caption=caption if caption else "Warning!",
		style=wx.OK | wx.ICON_WARNING
	)
	dialog.ShowModal()
	dialog.Destroy()
